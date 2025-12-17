#!/usr/bin/env python3
"""
Installation helpers for external dependencies
"""
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List


def install_cosmos_tokenizer(
    install_dir: Optional[str] = None,
    use_docker: bool = False,
    skip_models: bool = True
) -> str:
    """
    Install NVIDIA Cosmos-Tokenizer system dependencies and code.
    
    Note: Model downloads are handled separately by checkpoints.py
    
    Args:
        install_dir: Directory to install in (default: temporary directory)
        use_docker: Whether to use Docker installation instead
        skip_models: Skip model downloads (handled by checkpoints.py)
    
    Returns:
        Path to the installed cosmos-tokenizer directory
        
    Raises:
        RuntimeError: If installation fails
    """
    if use_docker:
        return _install_cosmos_docker()
    else:
        return _install_cosmos_direct(install_dir, skip_models)


def _install_cosmos_direct(install_dir: Optional[str], skip_models: bool = True) -> str:
    """Direct installation via git clone and pip"""
    
    # Check system requirements
    _check_system_requirements()
    
    # Setup installation directory
    if install_dir is None:
        install_dir = tempfile.mkdtemp(prefix="cosmos-tokenizer-")
    else:
        install_dir = Path(install_dir).expanduser().resolve()
        install_dir.mkdir(parents=True, exist_ok=True)
    
    cosmos_dir = Path(install_dir) / "Cosmos-Tokenizer"
    
    print(f"Installing Cosmos-Tokenizer to {cosmos_dir}")
    
    try:
        # Skip system dependencies - users handle ffmpeg themselves
        print("⏩ Skipping system dependencies (ffmpeg, git-lfs) - please install manually if needed")
        
        # Clone repository
        print("Cloning Cosmos-Tokenizer repository...")
        _run_command([
            "git", "clone", "https://github.com/NVIDIA/Cosmos-Tokenizer.git", str(cosmos_dir)
        ])
        
        # Change to directory
        os.chdir(cosmos_dir)
        
        # Skip model download if requested (handled by checkpoints.py)
        if not skip_models:
            print("Downloading model files (this may take a while)...")
            _run_command(["git", "lfs", "pull"])
        else:
            print("⏩ Skipping model downloads (use 'carlib setup' to download models)")
        
        # Install Python package
        print("Installing Python package...")
        _run_command([sys.executable, "-m", "pip", "install", "-e", "."])
        
        print(f"✅ Cosmos-Tokenizer code successfully installed at {cosmos_dir}")
        
        if skip_models:
            print("\n📋 Next steps:")
            print("  1. Use 'carlib setup download <model>' to download specific models")
            print("  2. Use 'carlib setup list' to see available models")
        
        return str(cosmos_dir)
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install Cosmos-Tokenizer: {e}")


def _install_cosmos_docker() -> str:
    """Install via Docker"""
    print("Installing Cosmos-Tokenizer via Docker...")
    
    try:
        # Build Docker image
        temp_dir = tempfile.mkdtemp(prefix="cosmos-docker-")
        cosmos_dir = Path(temp_dir) / "Cosmos-Tokenizer"
        
        _run_command([
            "git", "clone", "https://github.com/NVIDIA/Cosmos-Tokenizer.git", str(cosmos_dir)
        ])
        
        os.chdir(cosmos_dir)
        
        _run_command([
            "docker", "build", "-t", "cosmos-tokenizer", "-f", "Dockerfile", "."
        ])
        
        print("✅ Cosmos-Tokenizer Docker image built successfully")
        return str(cosmos_dir)
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to build Cosmos-Tokenizer Docker image: {e}")


def _check_system_requirements() -> None:
    """Check if system meets requirements"""
    # Check Python version
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10 or higher is required for Cosmos-Tokenizer")
    
    # Check for CUDA (optional but recommended)
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name()}")
        else:
            print("⚠️  CUDA not available - CPU-only installation")
    except ImportError:
        print("⚠️  PyTorch not installed - will be installed as dependency")
    
    # Check for git and git-lfs
    if not shutil.which("git"):
        raise RuntimeError("git is not installed. Please install git first.")
    
    if not shutil.which("git-lfs"):
        print("⚠️  git-lfs not found - will attempt to install")


def _run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command with proper error handling"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, 
            check=check, 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minute timeout
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Command timed out: {' '.join(cmd)}")
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            raise
        return e


def install_cosmos_wrapper() -> None:
    """
    Interactive installer for Cosmos-Tokenizer system dependencies
    """
    print("🚀 Cosmos-Tokenizer Installation Helper")
    print("=" * 50)
    print("\nNote: Models will be managed separately via 'carlib setup' commands")
    
    # Choose installation method
    print("\nInstallation options:")
    print("1. Direct installation (recommended)")
    print("2. Docker installation")
    
    choice = input("Choose installation method (1/2): ").strip()
    
    if choice == "2":
        install_dir = install_cosmos_tokenizer(use_docker=True)
    else:
        # Get installation directory
        default_dir = str(Path.home() / "cosmos-tokenizer")
        install_dir_input = input(f"Installation directory [{default_dir}]: ").strip()
        install_dir = install_dir_input if install_dir_input else default_dir
        
        # Skip model downloads
        skip_models = input("Skip model downloads? (Y/n): ").strip().lower() != 'n'
        
        install_dir = install_cosmos_tokenizer(
            install_dir=install_dir,
            skip_models=skip_models
        )
    
    print(f"\n✅ Installation complete!")
    print(f"📁 Location: {install_dir}")
    print("\n📋 Next steps:")
    print("1. Download models: carlib setup download CI8x8")
    print("2. List available models: carlib setup list")
    print("\n🔥 Usage example:")
    print(f"""
import sys
sys.path.append('{install_dir}')
from cosmos_tokenizer.image_lib import ImageTokenizer

tokenizer = ImageTokenizer()
tokens = tokenizer.encode(image)
    """)


if __name__ == "__main__":
    install_cosmos_wrapper()