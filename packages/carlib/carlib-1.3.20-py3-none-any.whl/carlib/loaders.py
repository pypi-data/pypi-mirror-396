"""
CAR format loaders for PyTorch and JAX
"""
import os
import torch
import mmap
import weakref
from pathlib import Path
from typing import Dict, Any, Optional, List, Iterator, Tuple
from torch.utils.data import Dataset, DataLoader, IterableDataset
import glob
from .processors.utils import CARHandler

try:
    import jax.numpy as jnp
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False
    jnp = None

try:
    import grain
    GRAIN_AVAILABLE = True
except ImportError:
    GRAIN_AVAILABLE = False
    grain = None



class CARDataset(Dataset):
    """PyTorch Dataset for loading CAR files with optimized caching"""
    
    def __init__(
        self, 
        car_dir: str, 
        pattern: str = "*.car",
        transform: Optional[callable] = None,
        cache_in_memory: bool = False,
        modality: Optional[str] = None,
        use_mmap: bool = True,
        max_cache_size: int = 1000
    ):
        """
        Initialize CAR dataset
        
        Args:
            car_dir: Directory containing CAR files
            pattern: Glob pattern for CAR files
            transform: Optional transform function to apply to data
            cache_in_memory: Whether to cache loaded data in memory
            modality: Filter by modality (audio, image, video)
            use_mmap: Whether to use memory-mapped files for large files
            max_cache_size: Maximum number of files to cache in memory
        """
        self.car_dir = Path(car_dir)
        self.transform = transform
        self.cache_in_memory = cache_in_memory
        self.modality = modality
        self.use_mmap = use_mmap
        self.max_cache_size = max_cache_size
        self._cache = {} if cache_in_memory else None
        self._mmap_cache = weakref.WeakValueDictionary() if use_mmap else None
        self._access_count = {}
        
        # Find all CAR files
        self.car_files = list(glob.glob(str(self.car_dir / pattern)))
        
        # Filter by modality if specified
        if modality:
            filtered_files = []
            for car_file in self.car_files:
                try:
                    _, metadata = self._load_car_file(car_file)
                    if metadata.get('target_modality') == modality:
                        filtered_files.append(car_file)
                except:
                    continue  # Skip files that can't be loaded
            self.car_files = filtered_files
        
        if not self.car_files:
            raise ValueError(f"No CAR files found in {car_dir} with pattern {pattern}")
    
    def _load_car_file(self, car_path: str) -> Tuple[Dict[str, Any], dict]:
        """Load a single CAR file with optimized caching"""
        # Check memory cache first
        if self.cache_in_memory and car_path in self._cache:
            return self._cache[car_path]
        
        # Try memory-mapped loading for large files
        if self.use_mmap:
            try:
                return self._load_with_mmap(car_path)
            except Exception:
                pass  # Fall back to regular loading
        
        # Regular file loading
        with open(car_path, 'rb') as f:
            car_data = f.read()
        
        data, metadata = CARHandler.car_to_np(car_data)
        
        # Cache management with LRU-like eviction
        if self.cache_in_memory:
            if len(self._cache) >= self.max_cache_size:
                # Evict least recently accessed item
                lru_key = min(self._access_count.keys(), key=self._access_count.get)
                del self._cache[lru_key]
                del self._access_count[lru_key]
            
            self._cache[car_path] = (data, metadata)
            self._access_count[car_path] = self._access_count.get(car_path, 0) + 1
        
        return data, metadata
    
    def _load_with_mmap(self, car_path: str) -> Tuple[Dict[str, Any], dict]:
        """Load CAR file using memory mapping for better performance"""
        if car_path in self._mmap_cache:
            mmap_obj = self._mmap_cache[car_path]
            car_data = mmap_obj.read()
            mmap_obj.seek(0)  # Reset position
        else:
            f = open(car_path, 'rb')
            mmap_obj = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            self._mmap_cache[car_path] = mmap_obj
            car_data = mmap_obj.read()
            mmap_obj.seek(0)
        
        return CARHandler.car_to_np(car_data)
    
    def __len__(self) -> int:
        return len(self.car_files)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        car_path = self.car_files[idx]
        data, metadata = self._load_car_file(car_path)
        
        result = {
            'data': data,
            'metadata': metadata,
            'file_path': car_path
        }
        
        if self.transform:
            result = self.transform(result)
        
        return result


class CARIterableDataset(IterableDataset):
    """PyTorch IterableDataset for streaming CAR files"""
    
    def __init__(
        self,
        car_dir: str,
        pattern: str = "*.car",
        transform: Optional[callable] = None,
        shuffle: bool = False,
        modality: Optional[str] = None
    ):
        """
        Initialize streaming CAR dataset
        
        Args:
            car_dir: Directory containing CAR files
            pattern: Glob pattern for CAR files
            transform: Optional transform function
            shuffle: Whether to shuffle files
            modality: Filter by modality (audio, image, video)
        """
        self.car_dir = Path(car_dir)
        self.pattern = pattern
        self.transform = transform
        self.shuffle = shuffle
        self.modality = modality
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        car_files = list(glob.glob(str(self.car_dir / self.pattern)))
        
        if self.shuffle:
            import random
            random.shuffle(car_files)
        
        for car_path in car_files:
            try:
                # Use memory-mapped loading for better performance
                try:
                    with open(car_path, 'rb') as f:
                        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                            car_data = mm.read()
                except (OSError, ValueError):
                    # Fallback to regular file loading if mmap fails
                    with open(car_path, 'rb') as f:
                        car_data = f.read()
                
                data, metadata = CARHandler.car_to_np(car_data)
                
                # Filter by modality if specified
                if self.modality and metadata.get('target_modality') != self.modality:
                    continue
                
                result = {
                    'data': data,
                    'metadata': metadata,
                    'file_path': car_path
                }
                
                if self.transform:
                    result = self.transform(result)
                
                yield result
                
            except Exception as e:
                print(f"Warning: Failed to load {car_path}: {e}")
                continue


class CARLoader:
    """High-level CAR file loader with PyTorch DataLoader integration"""
    
    def __init__(
        self,
        car_dir: str,
        batch_size: int = 32,
        shuffle: bool = True,
        num_workers: int = 0,
        pattern: str = "*.car",
        transform: Optional[callable] = None,
        cache_in_memory: bool = False,
        modality: Optional[str] = None,
        streaming: bool = False
    ):
        """
        Initialize CAR loader
        
        Args:
            car_dir: Directory containing CAR files
            batch_size: Batch size for DataLoader
            shuffle: Whether to shuffle data
            num_workers: Number of worker processes
            pattern: Glob pattern for CAR files
            transform: Optional transform function
            cache_in_memory: Whether to cache data in memory
            modality: Filter by modality (audio, image, video)
            streaming: Use streaming dataset (IterableDataset)
        """
        if streaming:
            self.dataset = CARIterableDataset(
                car_dir=car_dir,
                pattern=pattern,
                transform=transform,
                shuffle=shuffle,
                modality=modality
            )
        else:
            self.dataset = CARDataset(
                car_dir=car_dir,
                pattern=pattern,
                transform=transform,
                cache_in_memory=cache_in_memory,
                modality=modality
            )
        
        # Ensure num_workers > 0 for performance (prefetching)
        if num_workers == 0:
            print("⚠️  Warning: num_workers=0 may cause GPU idle time. Consider using num_workers=4 for better performance.")
        
        self.dataloader = DataLoader(
            self.dataset,
            batch_size=batch_size,
            shuffle=shuffle if not streaming else False,
            num_workers=num_workers,
            collate_fn=self._collate_fn,
            pin_memory=True,  # Enable pinned memory for faster GPU transfers
            persistent_workers=num_workers > 0,  # Keep workers alive between epochs
            prefetch_factor=2 if num_workers > 0 else 2  # Prefetch 2 batches per worker
        )
    
    def _collate_fn(self, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimized collate function with proper device handling"""
        # Group data by keys
        data_keys = set()
        for item in batch:
            if 'data' in item:
                data_keys.update(item['data'].keys())
        
        batched_data = {}
        for key in data_keys:
            tensors = []
            for item in batch:
                if 'data' in item and key in item['data']:
                    tensor = item['data'][key]
                    # Ensure tensor is on CPU during collation - move to device later
                    if isinstance(tensor, torch.Tensor) and tensor.is_cuda:
                        tensor = tensor.cpu()
                    tensors.append(tensor)
            
            if tensors:
                try:
                    # Try to stack tensors
                    stacked = torch.stack(tensors)
                    batched_data[key] = stacked
                except Exception:
                    # If stacking fails, return list
                    batched_data[key] = tensors
        
        return {
            'data': batched_data,
            'metadata': [item['metadata'] for item in batch],
            'file_paths': [item['file_path'] for item in batch]
        }
    
    def __iter__(self):
        return iter(self.dataloader)
    
    def __len__(self):
        return len(self.dataloader)
    
    def to_device(self, batch: Dict[str, Any], device: torch.device, non_blocking: bool = True) -> Dict[str, Any]:
        """Efficiently move batch to device after collation"""
        if 'data' not in batch:
            return batch
        
        # Move all tensors in data dict to device at once
        device_data = {}
        for key, value in batch['data'].items():
            if isinstance(value, torch.Tensor):
                device_data[key] = value.to(device, non_blocking=non_blocking)
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], torch.Tensor):
                # Handle list of tensors
                device_data[key] = [t.to(device, non_blocking=non_blocking) for t in value]
            else:
                device_data[key] = value
        
        return {
            'data': device_data,
            'metadata': batch['metadata'],
            'file_paths': batch['file_paths']
        }


if JAX_AVAILABLE:
    class JAXCARLoader:
        """JAX-compatible CAR file loader"""
        
        def __init__(
            self,
            car_dir: str,
            pattern: str = "*.car",
            modality: Optional[str] = None
        ):
            """
            Initialize JAX CAR loader
            
            Args:
                car_dir: Directory containing CAR files
                pattern: Glob pattern for CAR files
                modality: Filter by modality (audio, image, video)
            """
            self.car_dir = Path(car_dir)
            self.pattern = pattern
            self.modality = modality
            
            # Find all CAR files
            self.car_files = list(glob.glob(str(self.car_dir / pattern)))
            
            if not self.car_files:
                raise ValueError(f"No CAR files found in {car_dir} with pattern {pattern}")
        
        def load_single(self, car_path: str) -> Dict[str, Any]:
            """Load a single CAR file and convert to JAX arrays"""
            with open(car_path, 'rb') as f:
                car_data = f.read()
            
            data, metadata = CARHandler.car_to_np(car_data)
            
            # Convert PyTorch tensors to JAX arrays
            jax_data = {}
            for key, tensor in data.items():
                if isinstance(tensor, torch.Tensor):
                    numpy_array = tensor.cpu().numpy()
                    jax_data[key] = jnp.array(numpy_array)
                else:
                    jax_data[key] = jnp.array(tensor)
            
            return {
                'data': jax_data,
                'metadata': metadata,
                'file_path': car_path
            }
        
        def load_batch(self, car_paths: List[str]) -> Dict[str, Any]:
            """Load multiple CAR files as a batch"""
            batch_data = []
            batch_metadata = []
            batch_paths = []
            
            for car_path in car_paths:
                try:
                    result = self.load_single(car_path)
                    
                    # Filter by modality if specified
                    if self.modality and result['metadata'].get('target_modality') != self.modality:
                        continue
                    
                    batch_data.append(result['data'])
                    batch_metadata.append(result['metadata'])
                    batch_paths.append(result['file_path'])
                    
                except Exception as e:
                    print(f"Warning: Failed to load {car_path}: {e}")
                    continue
            
            if not batch_data:
                return {'data': {}, 'metadata': [], 'file_paths': []}
            
            # Stack data by keys
            stacked_data = {}
            data_keys = set()
            for data in batch_data:
                data_keys.update(data.keys())
            
            for key in data_keys:
                arrays = []
                for data in batch_data:
                    if key in data:
                        arrays.append(data[key])
                
                if arrays:
                    try:
                        # Try to stack arrays
                        stacked_data[key] = jnp.stack(arrays)
                    except:
                        # If stacking fails, return list
                        stacked_data[key] = arrays
            
            return {
                'data': stacked_data,
                'metadata': batch_metadata,
                'file_paths': batch_paths
            }
        
        def __iter__(self):
            """Iterate over all CAR files"""
            for car_path in self.car_files:
                try:
                    yield self.load_single(car_path)
                except Exception as e:
                    print(f"Warning: Failed to load {car_path}: {e}")
                    continue
        
        def __len__(self):
            return len(self.car_files)

else:
    class JAXCARLoader:
        """Placeholder when JAX is not available"""
        def __init__(self, car_dir, **_kwargs):
            del car_dir, _kwargs  # Suppress unused variable warnings
            raise ImportError("JAX is not available. Please install JAX to use JAXCARLoader.")


# Grain integration for enhanced JAX data loading
if JAX_AVAILABLE and GRAIN_AVAILABLE:
    class GrainCARDataSource:
        """
        Grain-compatible CAR format data source for high-performance JAX training.
        
        Provides true global shuffling, deterministic data loading, and enterprise-scale
        performance optimized for JAX workflows.
        """
        
        def __init__(
            self, 
            car_directory: str, 
            pattern: str = "*.car",
            modality: Optional[str] = None,
            cache_metadata: bool = True
        ):
            """
            Initialize Grain CAR data source
            
            Args:
                car_directory: Directory containing CAR files
                pattern: Glob pattern for CAR files  
                modality: Filter by modality (audio, image, video)
                cache_metadata: Whether to cache metadata for filtering
            """
            self.car_directory = Path(car_directory)
            self.pattern = pattern
            self.modality = modality
            self.cache_metadata = cache_metadata
            self._metadata_cache = {} if cache_metadata else None
            
            # Find all CAR files
            self.car_files = list(glob.glob(str(self.car_directory / pattern)))
            
            if not self.car_files:
                raise ValueError(f"No CAR files found in {car_directory} with pattern {pattern}")
            
            # Filter by modality if specified
            if modality:
                self._filter_by_modality()
        
        def _filter_by_modality(self):
            """Filter CAR files by target modality"""
            filtered_files = []
            
            for car_file in self.car_files:
                try:
                    metadata = self._get_metadata(car_file)
                    if metadata.get('target_modality') == self.modality:
                        filtered_files.append(car_file)
                except Exception as e:
                    print(f"Warning: Failed to read metadata from {car_file}: {e}")
                    continue
            
            self.car_files = filtered_files
            
            if not self.car_files:
                raise ValueError(f"No CAR files found with modality '{self.modality}'")
        
        def _get_metadata(self, car_file: str) -> dict:
            """Get metadata from CAR file (with optional caching)"""
            if self.cache_metadata and car_file in self._metadata_cache:
                return self._metadata_cache[car_file]
            
            try:
                with open(car_file, 'rb') as f:
                    car_data = f.read()
                
                _, metadata = CARHandler.car_to_np(car_data)
                
                if self.cache_metadata:
                    self._metadata_cache[car_file] = metadata
                
                return metadata
            except Exception as e:
                raise ValueError(f"Failed to read metadata from {car_file}: {e}")
        
        def __len__(self) -> int:
            """Return number of CAR files in the dataset"""
            return len(self.car_files)
        
        def __getitem__(self, index: int) -> Dict[str, Any]:
            """
            Load and return a CAR file as JAX arrays
            
            Args:
                index: Index of the CAR file to load
                
            Returns:
                Dictionary containing JAX arrays, metadata, and file path
            """
            if index >= len(self.car_files):
                raise IndexError(f"Index {index} out of range for {len(self.car_files)} files")
            
            car_path = self.car_files[index]
            
            try:
                # Load CAR file using existing handler
                with open(car_path, 'rb') as f:
                    car_data = f.read()
                
                data, metadata = CARHandler.car_to_np(car_data)
                
                # Convert PyTorch tensors to JAX arrays
                jax_data = {}
                for key, tensor in data.items():
                    if isinstance(tensor, torch.Tensor):
                        # Convert to numpy first, then to JAX array
                        numpy_array = tensor.cpu().numpy()
                        jax_data[key] = jnp.array(numpy_array)
                    else:
                        # Handle numpy arrays or other array types
                        jax_data[key] = jnp.array(tensor)
                
                return {
                    'data': jax_data,
                    'metadata': metadata,
                    'file_path': car_path,
                    'index': index
                }
                
            except Exception as e:
                raise RuntimeError(f"Failed to load CAR file {car_path}: {e}")


    class GrainCARLoader:
        """
        High-performance Grain-based CAR loader for JAX training.
        
        Provides enterprise-scale data loading with true global shuffling,
        deterministic processing, and optimized performance for JAX workflows.
        """
        
        def __init__(
            self,
            car_directory: str,
            batch_size: int = 32,
            shuffle: bool = True,
            seed: Optional[int] = None,
            pattern: str = "*.car",
            modality: Optional[str] = None,
            num_threads: Optional[int] = None,
            prefetch_buffer_size: Optional[int] = None,
            cache_metadata: bool = True,
            transform_fn: Optional[callable] = None
        ):
            """
            Initialize Grain-based CAR loader
            
            Args:
                car_directory: Directory containing CAR files
                batch_size: Batch size for training
                shuffle: Whether to globally shuffle the dataset
                seed: Random seed for shuffling (for reproducibility)
                pattern: Glob pattern for CAR files
                modality: Filter by modality (audio, image, video)
                num_threads: Number of threads for data loading
                prefetch_buffer_size: Size of prefetch buffer
                cache_metadata: Whether to cache metadata for filtering
                transform_fn: Optional transformation function to apply to each sample
            """
            if not JAX_AVAILABLE:
                raise ImportError("JAX is not available. Please install JAX to use GrainCARLoader.")
            if not GRAIN_AVAILABLE:
                raise ImportError("Grain is not available. Please install grain to use GrainCARLoader.")
            
            self.car_directory = car_directory
            self.batch_size = batch_size
            self.shuffle = shuffle
            self.seed = seed or 42
            self.pattern = pattern
            self.modality = modality
            self.cache_metadata = cache_metadata
            self.transform_fn = transform_fn
            
            # Create data source
            self.data_source = GrainCARDataSource(
                car_directory=car_directory,
                pattern=pattern,
                modality=modality,
                cache_metadata=cache_metadata
            )
            
            # Create Grain dataset
            self.dataset = grain.MapDataset.source(self.data_source)
            
            # Apply shuffling if requested
            if shuffle:
                self.dataset = self.dataset.shuffle(seed=self.seed)
            
            # Apply transformation if provided
            if transform_fn:
                self.dataset = self.dataset.map(transform_fn)
            
            # Batch the data
            self.dataset = self.dataset.batch(batch_size=batch_size)
            
            # Configure read options for performance
            read_options = grain.ReadOptions()
            if num_threads is not None:
                read_options.num_threads = num_threads
            if prefetch_buffer_size is not None:
                read_options.prefetch_buffer_size = prefetch_buffer_size
            
            # Convert to iterable dataset
            self.iter_dataset = self.dataset.to_iter_dataset(read_options=read_options)
        
        def __iter__(self):
            """Return iterator over batched CAR data"""
            return iter(self.iter_dataset)
        
        def __len__(self):
            """Return number of batches in the dataset"""
            return (len(self.data_source) + self.batch_size - 1) // self.batch_size
        
        def get_stats(self) -> Dict[str, Any]:
            """Get dataset statistics"""
            return {
                'num_files': len(self.data_source),
                'num_batches': len(self),
                'batch_size': self.batch_size,
                'modality': self.modality,
                'pattern': self.pattern,
                'shuffle': self.shuffle,
                'seed': self.seed
            }

elif JAX_AVAILABLE and not GRAIN_AVAILABLE:
    class GrainCARDataSource:
        """Placeholder when Grain is not available"""
        def __init__(self, car_directory, **_kwargs):
            del car_directory, _kwargs
            raise ImportError("Grain is not available. Please install grain with: pip install grain")
    
    class GrainCARLoader:
        """Placeholder when Grain is not available"""
        def __init__(self, car_directory, **_kwargs):
            del car_directory, _kwargs
            raise ImportError("Grain is not available. Please install grain with: pip install grain")

else:
    class GrainCARDataSource:
        """Placeholder when JAX/Grain are not available"""
        def __init__(self, car_directory, **_kwargs):
            del car_directory, _kwargs
            raise ImportError("JAX and Grain are required. Please install with: pip install jax grain")
    
    class GrainCARLoader:
        """Placeholder when JAX/Grain are not available"""
        def __init__(self, car_directory, **_kwargs):
            del car_directory, _kwargs
            raise ImportError("JAX and Grain are required. Please install with: pip install jax grain")


# Convenience functions
def load_car_pytorch(
    car_dir: str,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 0,
    modality: Optional[str] = None,
    **kwargs
) -> CARLoader:
    """Convenience function to create a PyTorch CAR loader"""
    return CARLoader(
        car_dir=car_dir,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        modality=modality,
        **kwargs
    )


def load_car_jax(
    car_dir: str,
    modality: Optional[str] = None,
    use_grain: bool = None,
    **kwargs
) -> 'JAXCARLoader':
    """
    Convenience function to create a JAX CAR loader
    
    Args:
        car_dir: Directory containing CAR files
        modality: Filter by modality (audio, image, video)
        use_grain: Whether to use Grain loader (auto-detected if None)
        **kwargs: Additional arguments passed to the loader
    
    Returns:
        JAXCARLoader or GrainCARLoader depending on availability and preference
    """
    # Auto-detect Grain availability if not specified
    if use_grain is None:
        use_grain = GRAIN_AVAILABLE
    
    # Use Grain loader if available and requested
    if use_grain and GRAIN_AVAILABLE:
        return GrainCARLoader(
            car_directory=car_dir,
            modality=modality,
            **kwargs
        )
    else:
        # Fall back to basic JAX loader
        return JAXCARLoader(
            car_dir=car_dir,
            modality=modality,
            **kwargs
        )


def load_car_grain(
    car_directory: str,
    batch_size: int = 32,
    shuffle: bool = True,
    seed: Optional[int] = None,
    modality: Optional[str] = None,
    **kwargs
) -> 'GrainCARLoader':
    """
    Convenience function to create a Grain-based CAR loader for JAX training
    
    Args:
        car_directory: Directory containing CAR files
        batch_size: Batch size for training
        shuffle: Whether to globally shuffle the dataset
        seed: Random seed for shuffling (for reproducibility)
        modality: Filter by modality (audio, image, video)
        **kwargs: Additional arguments passed to GrainCARLoader
    
    Returns:
        GrainCARLoader instance
    """
    return GrainCARLoader(
        car_directory=car_directory,
        batch_size=batch_size,
        shuffle=shuffle,
        seed=seed,
        modality=modality,
        **kwargs
    )


def load_single_car(car_path: str, framework: str = 'pytorch') -> Dict[str, Any]:
    """
    Load a single CAR file
    
    Args:
        car_path: Path to CAR file
        framework: 'pytorch' or 'jax'
    
    Returns:
        Dictionary with data, metadata, and file_path
    """
    if framework == 'pytorch':
        with open(car_path, 'rb') as f:
            car_data = f.read()
        
        data, metadata = CARHandler.car_to_np(car_data)
        
        return {
            'data': data,
            'metadata': metadata,
            'file_path': car_path
        }
    
    elif framework == 'jax':
        if not JAX_AVAILABLE:
            raise ImportError("JAX is not available")
        
        loader = JAXCARLoader(os.path.dirname(car_path))
        return loader.load_single(car_path)
    
    else:
        raise ValueError(f"Unknown framework: {framework}. Use 'pytorch' or 'jax'")