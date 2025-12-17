"""
CarLib Checkpoint Manager

Automatic checkpoint downloading and management for CarLib models.
This module handles downloading model checkpoints from a public S3 bucket,
making CarLib installation completely permissionless and friction-free.

The checkpoints are downloaded to ~/.carlib/checkpoints/ by default,
but this can be configured via environment variables.
"""

import os
import requests
import zipfile
from pathlib import Path
from typing import Dict, Optional, Union, List
from tqdm import tqdm
import yaml

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


# Cloudflare R2 Configuration - all values must come from config file

# Model registry - maps model names to their R2 directory paths
MODEL_REGISTRY = {
    # Continuous Video Tokenizers
    "CV4x8x8": "checkpoints/pretrained_ckpts/Cosmos-0.1-Tokenizer-CV4x8x8",
    "CV8x8x8": "checkpoints/pretrained_ckpts/Cosmos-0.1-Tokenizer-CV8x8x8", 
    "CV8x16x16": "checkpoints/pretrained_ckpts/Cosmos-0.1-Tokenizer-CV8x16x16",
    "CV8x8x8_v1": "checkpoints/pretrained_ckpts/Cosmos-1.0-Tokenizer-CV8x8x8",
    
    # Discrete Video Tokenizers
    "DV4x8x8": "checkpoints/pretrained_ckpts/Cosmos-0.1-Tokenizer-DV4x8x8",
    "DV8x8x8": "checkpoints/pretrained_ckpts/Cosmos-0.1-Tokenizer-DV8x8x8",
    "DV8x16x16": "checkpoints/pretrained_ckpts/Cosmos-0.1-Tokenizer-DV8x16x16",
    "DV8x16x16_v1": "checkpoints/pretrained_ckpts/Cosmos-1.0-Tokenizer-DV8x16x16",
    
    # Continuous Image Tokenizers  
    "CI8x8": "checkpoints/pretrained_ckpts/Cosmos-0.1-Tokenizer-CI8x8",
    "CI16x16": "checkpoints/pretrained_ckpts/Cosmos-0.1-Tokenizer-CI16x16",
    
    # Discrete Image Tokenizers
    "DI8x8": "checkpoints/pretrained_ckpts/Cosmos-0.1-Tokenizer-DI8x8", 
    "DI16x16": "checkpoints/pretrained_ckpts/Cosmos-0.1-Tokenizer-DI16x16",
}

# Model type mapping for easy lookup
MODEL_TYPES = {
    # Video models
    "CV4x8x8": "video", "CV8x8x8": "video", "CV8x16x16": "video", "CV8x8x8_v1": "video",
    "DV4x8x8": "video", "DV8x8x8": "video", "DV8x16x16": "video", "DV8x16x16_v1": "video",
    # Image models  
    "CI8x8": "image", "CI16x16": "image",
    "DI8x8": "image", "DI16x16": "image",
}

def download_with_progress(url: str, destination: Path) -> bool:
    """Download a file from URL with progress bar"""
    try:
        response = requests.head(url, timeout=30)
        if response.status_code != 200:
            return False
            
        file_size = int(response.headers.get('content-length', 0))
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(destination, 'wb') as f:
            if file_size > 0:
                with tqdm(total=file_size, unit='B', unit_scale=True, desc=destination.name) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            else:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        
        return True
        
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def extract_checkpoint_zip(zip_path: Path, extract_to: Path) -> bool:
    """Extract checkpoint zip file"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False

def load_r2_config(config_path: Optional[Union[str, Path]] = None) -> Dict[str, str]:
    """
    Load R2 configuration from YAML file
    
    Args:
        config_path: Path to config file. If None, looks for standard locations
        
    Returns:
        Dictionary with R2 configuration
    """
    # Standard config file locations to check
    if config_path is None:
        # Get the carlib package directory
        carlib_dir = Path(__file__).parent
        config_locations = [
            carlib_dir / "configs" / "r2_config.yaml",
            carlib_dir / "configs" / "config.yaml", 
            Path.home() / ".carlib" / "config.yaml",
            Path.home() / ".carlib" / "r2_config.yaml", 
            Path("r2_config.yaml"),
            Path("config.yaml")
        ]
    else:
        config_locations = [Path(config_path)]
    
    for config_file in config_locations:
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Extract R2 config section
                r2_config = config.get('r2', {})
                if not r2_config:
                    r2_config = config.get('cloudflare_r2', {})
                
                # Return the config if it has required keys
                if 'access_key_id' in r2_config and 'secret_access_key' in r2_config:
                    print(f"✅ Loaded R2 config from: {config_file}")
                    return r2_config
                    
            except Exception as e:
                print(f"❌ Failed to load config from {config_file}: {e}")
                continue
    
    return {}

class CheckpointManager:
    """Manages automatic checkpoint downloads and caching from R2"""
    
    def __init__(self, cache_dir: Optional[Union[str, Path]] = None, 
                 r2_access_key_id: Optional[str] = None,
                 r2_secret_access_key: Optional[str] = None,
                 r2_endpoint_url: Optional[str] = None,
                 r2_bucket_name: Optional[str] = None,
                 config_path: Optional[Union[str, Path]] = None):
        """
        Initialize checkpoint manager
        
        Args:
            cache_dir: Directory to store checkpoints. Defaults to ~/.carlib/checkpoints
            r2_access_key_id: R2 access key ID (overrides config file and env vars)
            r2_secret_access_key: R2 secret access key (overrides config file and env vars)
            r2_endpoint_url: R2 endpoint URL (defaults to standard R2 endpoint)
            r2_bucket_name: R2 bucket name (defaults to 'car-load')
            config_path: Path to YAML config file with R2 credentials
        """
        # Cache directory with environment variable support
        if cache_dir is None:
            cache_dir = os.environ.get("CARLIB_CACHE_DIR")
            if cache_dir is None:
                # Use user's home directory by default
                self.cache_dir = Path.home() / ".carlib" / "checkpoints"
            else:
                self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(cache_dir)
            
        # Also check for legacy pretrained_ckpts directory
        self.legacy_dir = Path("pretrained_ckpts")
        
        # Load R2 configuration from YAML file first, then env vars, then parameters
        r2_config = load_r2_config(config_path)
        
        # Priority: parameters > env vars > config file > defaults
        self.r2_access_key_id = (
            r2_access_key_id or 
            os.environ.get("CARLIB_R2_ACCESS_KEY_ID") or 
            r2_config.get("access_key_id")
        )
        self.r2_secret_access_key = (
            r2_secret_access_key or 
            os.environ.get("CARLIB_R2_SECRET_ACCESS_KEY") or 
            r2_config.get("secret_access_key")
        )
        self.r2_endpoint_url = (
            r2_endpoint_url or 
            os.environ.get("CARLIB_R2_ENDPOINT_URL") or 
            r2_config.get("endpoint_url")
        )
        self.r2_bucket_name = (
            r2_bucket_name or 
            os.environ.get("CARLIB_R2_BUCKET_NAME") or 
            r2_config.get("bucket_name")
        )
        
        # Validate that all required R2 configuration is available
        if not all([self.r2_access_key_id, self.r2_secret_access_key, self.r2_endpoint_url, self.r2_bucket_name]):
            missing = []
            if not self.r2_access_key_id:
                missing.append("access_key_id")
            if not self.r2_secret_access_key:
                missing.append("secret_access_key")
            if not self.r2_endpoint_url:
                missing.append("endpoint_url")
            if not self.r2_bucket_name:
                missing.append("bucket_name")
            
            raise ValueError(
                f"Missing required R2 configuration: {', '.join(missing)}. "
                "Please provide them in carlib/configs/r2_config.yaml, environment variables, or as parameters."
            )
        
        # Initialize S3 client for R2 if credentials are available
        self.s3_client = None
        if BOTO3_AVAILABLE and self.r2_access_key_id and self.r2_secret_access_key:
            try:
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=self.r2_endpoint_url,
                    aws_access_key_id=self.r2_access_key_id,
                    aws_secret_access_key=self.r2_secret_access_key,
                    region_name='auto'
                )
                print(f"🔗 Connected to R2 bucket: {self.r2_bucket_name}")
            except Exception as e:
                print(f"⚠️  Failed to initialize R2 client: {e}")
                self.s3_client = None
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Track downloaded models to avoid re-downloading
        self._downloaded = set()
    def _get_model_prefix(self, model_name: str) -> str:
        """Get R2 prefix path for a model"""
        if model_name not in MODEL_REGISTRY:
            raise ValueError(f"Unknown model: {model_name}")
            
        return MODEL_REGISTRY[model_name]
    
    def _get_expected_model_files(self, model_name: str) -> List[str]:
        """Get expected files for a model based on standard structure"""
        model_prefix = self._get_model_prefix(model_name)
        
        # Standard files present in all models
        standard_files = [
            ".gitattributes",
            "README.md", 
            "model_config.yaml",
            "config.json",
            "decoder.jit",
            "encoder.jit",
            "autoencoder.jit"
        ]
        
        # Some models have additional files
        optional_files = [
            "mean_std.pt"  # Present in some newer models
        ]
        
        # Build full file paths
        files = []
        for filename in standard_files:
            files.append(f"{model_prefix}/{filename}")
        
        # Check if optional files exist using S3 client if available
        if self.s3_client:
            for filename in optional_files:
                file_path = f"{model_prefix}/{filename}"
                try:
                    self.s3_client.head_object(Bucket=self.r2_bucket_name, Key=file_path)
                    files.append(file_path)
                except ClientError:
                    pass  # File doesn't exist, skip it
        
        return files
    
    def _download_file_from_r2(self, remote_key: str, local_path: Path) -> bool:
        """Download a single file from R2 using S3 client"""
        if not self.s3_client:
            print(f"❌ No R2 client available for downloading {remote_key}")
            return False
        
        try:
            # Get file size for progress bar
            try:
                head_response = self.s3_client.head_object(Bucket=self.r2_bucket_name, Key=remote_key)
                file_size = head_response.get('ContentLength', 0)
            except:
                file_size = 0
            
            # Download with progress callback
            if file_size > 1024 * 1024:  # Show progress for files > 1MB
                with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Downloading {local_path.name}") as pbar:
                    def callback(bytes_transferred):
                        pbar.update(bytes_transferred)
                    
                    self.s3_client.download_file(
                        self.r2_bucket_name,
                        remote_key,
                        str(local_path),
                        Callback=callback
                    )
            else:
                # Simple download for smaller files
                self.s3_client.download_file(
                    self.r2_bucket_name,
                    remote_key,
                    str(local_path)
                )
            
            return True
            
        except (ClientError, NoCredentialsError) as e:
            print(f"❌ Failed to download {remote_key}: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error downloading {remote_key}: {e}")
            return False
            
    def get_checkpoint_path(self, model_name: str) -> Path:
        """
        Get the local path where a model checkpoint should be stored
        
        Args:
            model_name: Model name (e.g., 'CV8x8x8', 'CI8x8')
            
        Returns:
            Path to model checkpoint directory
        """
        # Check legacy location first (for backward compatibility)
        legacy_path = self.legacy_dir / f"Cosmos-0.1-Tokenizer-{model_name}"
        if legacy_path.exists():
            return legacy_path
            
        # Use new cache location
        return self.cache_dir / model_name
        
    def is_checkpoint_available(self, model_name: str) -> bool:
        """
        Check if a checkpoint is available locally
        
        Args:
            model_name: Model name to check
            
        Returns:
            True if checkpoint exists locally
        """
        checkpoint_path = self.get_checkpoint_path(model_name)
        return checkpoint_path.exists() and any(checkpoint_path.iterdir())
        
    def download_checkpoint(self, model_name: str, force: bool = False) -> bool:
        """
        Download a specific checkpoint from S3
        
        Args:
            model_name: Model name to download
            force: Force re-download even if already exists
            
        Returns:
            True if download successful, False otherwise
        """
        if model_name not in MODEL_REGISTRY:
            print(f"❌ Unknown model: {model_name}")
            print(f"   Available models: {list(MODEL_REGISTRY.keys())}")
            return False
            
        checkpoint_path = self.get_checkpoint_path(model_name)
        
        # Skip if already downloaded (unless forced)
        if not force and self.is_checkpoint_available(model_name):
            print(f"✅ Checkpoint {model_name} already available at {checkpoint_path}")
            return True
            
        try:
            print(f"📥 Downloading {model_name}...")
            print(f"   Destination: {checkpoint_path}")
            
            # Get expected files for this model
            print(f"🔍 Getting expected files for {model_name}...")
            files = self._get_expected_model_files(model_name)
            
            if not files:
                print(f"❌ No files found for {model_name}")
                return False
            
            print(f"📄 Found {len(files)} files to download")
            
            # Create directory
            checkpoint_path.mkdir(parents=True, exist_ok=True)
            
            # Download each file
            success_count = 0
            for file_key in tqdm(files, desc="Downloading files"):
                # Calculate local path (preserve directory structure)
                model_prefix = self._get_model_prefix(model_name)
                relative_path = file_key.replace(model_prefix + "/", "")
                local_file_path = checkpoint_path / relative_path
                
                # Create parent directory if needed
                local_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download file using R2 client
                if self._download_file_from_r2(file_key, local_file_path):
                    success_count += 1
                else:
                    print(f"❌ Failed to download {file_key}")
            
            print(f"📊 Downloaded {success_count}/{len(files)} files successfully")
            
            # Verify download worked
            if success_count == 0:
                print(f"❌ No files downloaded for {model_name}")
                return False
            
            if not self.is_checkpoint_available(model_name):
                print(f"❌ Checkpoint verification failed for {model_name}")
                return False
            
            self._downloaded.add(model_name)
            print(f"✅ Successfully downloaded {model_name} ({success_count} files)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {model_name}: {e}")
            # Clean up partial download
            if checkpoint_path.exists():
                import shutil
                shutil.rmtree(checkpoint_path, ignore_errors=True)
            return False
            
    def download_all_checkpoints(self, model_type: Optional[str] = None) -> Dict[str, bool]:
        """
        Download all available checkpoints
        
        Args:
            model_type: Filter by model type ('image', 'video', or None for all)
            
        Returns:
            Dictionary mapping model names to download success status
        """
        models_to_download = []
        
        if model_type:
            models_to_download = [name for name, mtype in MODEL_TYPES.items() if mtype == model_type]
        else:
            models_to_download = list(MODEL_REGISTRY.keys())
            
        results = {}
        print(f"📦 Downloading {len(models_to_download)} checkpoints...")
        
        for model_name in models_to_download:
            results[model_name] = self.download_checkpoint(model_name)
            
        successful = sum(results.values())
        print(f"\n📊 Download Summary: {successful}/{len(models_to_download)} successful")
        
        return results
        
    def ensure_checkpoint(self, model_name: str) -> str:
        """
        Ensure a checkpoint is available, downloading if necessary
        
        Args:
            model_name: Model name to ensure is available
            
        Returns:
            Path to checkpoint directory
            
        Raises:
            RuntimeError: If checkpoint cannot be made available
        """
        if self.is_checkpoint_available(model_name):
            return str(self.get_checkpoint_path(model_name))
            
        print(f"🔄 Checkpoint {model_name} not found locally, downloading...")
        
        if not self.download_checkpoint(model_name):
            raise RuntimeError(f"Failed to download checkpoint: {model_name}")
            
        return str(self.get_checkpoint_path(model_name))
        
    def list_available_models(self) -> Dict[str, Dict[str, Union[str, bool]]]:
        """
        List all available models and their status
        
        Returns:
            Dictionary with model info and availability status
        """
        models = {}
        for model_name in MODEL_REGISTRY:
            models[model_name] = {
                "type": MODEL_TYPES.get(model_name, "unknown"),
                "r2_prefix": MODEL_REGISTRY[model_name],
                "r2_bucket": self.r2_bucket_name,
                "available": self.is_checkpoint_available(model_name),
                "path": str(self.get_checkpoint_path(model_name))
            }
        return models
        
    def cleanup_cache(self, keep_recent: int = 5) -> int:
        """
        Clean up old cached checkpoints
        
        Args:
            keep_recent: Number of most recently used checkpoints to keep
            
        Returns:
            Number of checkpoints removed
        """
        # This is a placeholder - could implement LRU-based cleanup
        print("ℹ️  Cache cleanup not yet implemented")
        return 0

# Global instance
_checkpoint_manager = None

def get_checkpoint_manager() -> CheckpointManager:
    """Get the global checkpoint manager instance"""
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager

def ensure_checkpoint(model_name: str) -> str:
    """
    Convenience function to ensure a checkpoint is available
    
    Args:
        model_name: Model name to ensure is available
        
    Returns:
        Path to checkpoint directory
    """
    return get_checkpoint_manager().ensure_checkpoint(model_name)

def list_models() -> Dict[str, Dict[str, Union[str, bool]]]:
    """List all available models and their status"""
    return get_checkpoint_manager().list_available_models()

def download_model(model_name: str, force: bool = False) -> bool:
    """Download a specific model"""
    return get_checkpoint_manager().download_checkpoint(model_name, force=force)

def download_all(model_type: Optional[str] = None) -> Dict[str, bool]:
    """Download all models of a specific type"""
    return get_checkpoint_manager().download_all_checkpoints(model_type=model_type)