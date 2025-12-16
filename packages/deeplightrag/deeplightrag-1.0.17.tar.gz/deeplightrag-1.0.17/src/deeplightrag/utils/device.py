"""
Device Management Utility
Handles detection and configuration of compute devices (CUDA, CPU)
"""

import logging
import platform

logger = logging.getLogger(__name__)


class DeviceManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DeviceManager, cls).__new__(cls)
            cls._instance._detect_devices()
        return cls._instance
    
    def _detect_devices(self):
        """Detect available compute devices"""
        self.device_info = {
            "torch_device": "cpu",
            "cuda_available": False,
            "mps_available": False,
            "platform": platform.system()
        }
        
        # Detect PyTorch Device
        try:
            import torch
            
            if torch.cuda.is_available():
                self.device_info["torch_device"] = "cuda"
                self.device_info["cuda_available"] = True
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"🚀 GPU detected: {gpu_name} ({gpu_memory:.1f} GB)")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device_info["torch_device"] = "mps"
                self.device_info["mps_available"] = True
                logger.info("🚀 MPS (Apple Silicon) detected")
            else:
                logger.info("⚠️ Using CPU (No GPU acceleration detected)")
                
        except ImportError:
            logger.warning("PyTorch not installed")

    def get_torch_device(self) -> str:
        """Get the optimal PyTorch device"""
        return self.device_info["torch_device"]

    def is_cuda_available(self) -> bool:
        """Check if CUDA is available"""
        return self.device_info["cuda_available"]
    
    def log_device_status(self):
        """Log current device configuration"""
        logger.info(f"Device: {self.device_info['torch_device']} | "
                   f"CUDA: {self.device_info['cuda_available']} | "
                   f"Platform: {self.device_info['platform']}")


# Global instance
device_manager = DeviceManager()
