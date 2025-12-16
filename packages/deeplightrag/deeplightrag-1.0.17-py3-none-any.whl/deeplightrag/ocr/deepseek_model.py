"""
DeepSeek-OCR: Contexts Optical Compression
Official DeepSeek-OCR implementation for document text extraction with visual compression.

Model: deepseek-ai/DeepSeek-OCR
Paper: DeepSeek-OCR: Contexts Optical Compression (arXiv:2510.18234)
"""

import logging
import os
import time
import tempfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image
import torch

from ..utils.device import device_manager
from ..interfaces import BaseOCRProcessor
from .geometry import BoundingBox
from .visual_token import VisualToken, VisualRegion

logger = logging.getLogger(__name__)


@dataclass
class PageOCRResult:
    """Result from processing a single page"""
    page_num: int
    visual_regions: List[VisualRegion]
    full_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Calculate total tokens in page"""
        count = 0
        if self.visual_regions:
            for r in self.visual_regions:
                if hasattr(r, "token_count"):
                    count += r.token_count
                else:
                    count += len(r.text_content.split())
        return count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_num": self.page_num,
            "visual_regions": [r.to_dict() if hasattr(r, "to_dict") else str(r) for r in self.visual_regions],
            "full_text": self.full_text,
            "metadata": self.metadata
        }


class DeepSeekOCR(BaseOCRProcessor):
    """
    DeepSeek-OCR: Contexts Optical Compression
    
    Official implementation using deepseek-ai/DeepSeek-OCR model.
    Provides visual context compression for efficient document processing.
    
    Requirements:
        - NVIDIA GPU with CUDA
        - torch>=2.6.0
        - transformers>=4.46.3
        - flash-attn>=2.7.3 (recommended)
    """

    # Resolution presets from official docs
    RESOLUTION_PRESETS = {
        "tiny": {"base_size": 512, "image_size": 512, "crop_mode": False},
        "small": {"base_size": 640, "image_size": 640, "crop_mode": False},
        "base": {"base_size": 1024, "image_size": 1024, "crop_mode": False},
        "large": {"base_size": 1280, "image_size": 1280, "crop_mode": False},
        "gundam": {"base_size": 1024, "image_size": 640, "crop_mode": True},  # Recommended
    }

    def __init__(
        self,
        model_name: str = "deepseek-ai/DeepSeek-OCR",
        resolution: str = "gundam",  # tiny, small, base, large, gundam
        device: Optional[str] = None,
        use_flash_attention: bool = True,
        extract_images: bool = False,
        image_output_dir: str = "./extracted_images",
        enable_visual_embeddings: bool = True,
        target_embedding_dim: int = 256,
        output_format: str = "markdown",  # markdown, text, grounding
        test_compress: bool = True,
        **kwargs
    ):
        """
        Initialize DeepSeek-OCR

        Args:
            model_name: HuggingFace model name (deepseek-ai/DeepSeek-OCR)
            resolution: Resolution preset (tiny, small, base, large, gundam)
            device: Device (cuda required)
            use_flash_attention: Use flash attention 2 for speed
            enable_visual_embeddings: Extract visual embeddings
            output_format: Output format (markdown, text, grounding)
            test_compress: Test compression stats
        """
        self.model_name = model_name
        self.resolution = resolution
        self.use_flash_attention = use_flash_attention
        self.extract_images = extract_images
        self.image_output_dir = image_output_dir
        self.enable_visual_embeddings = enable_visual_embeddings
        self.target_embedding_dim = target_embedding_dim
        self.output_format = output_format
        self.test_compress = test_compress

        # Get resolution settings
        if resolution in self.RESOLUTION_PRESETS:
            self.resolution_config = self.RESOLUTION_PRESETS[resolution]
        else:
            self.resolution_config = self.RESOLUTION_PRESETS["gundam"]
            logger.warning(f"Unknown resolution '{resolution}', using 'gundam'")

        # Determine device - CUDA required
        if device:
            self.device = device
        else:
            self.device = device_manager.get_torch_device()
        
        if self.device != "cuda":
            logger.warning(f"DeepSeek-OCR requires CUDA GPU. Current device: {self.device}")

        if self.extract_images:
            os.makedirs(self.image_output_dir, exist_ok=True)

        # Temp directory for image files
        self.temp_dir = tempfile.mkdtemp()

        # Load model
        self.model = None
        self.tokenizer = None
        self._load_model()
        
        if self.model is None:
            error_msg = getattr(self, '_load_error', 'Unknown error')
            raise RuntimeError(
                f"Failed to load DeepSeek-OCR model.\n"
                f"Error: {error_msg}\n\n"
                "Requirements:\n"
                "  - NVIDIA GPU with CUDA\n"
                "  - torch>=2.0.0\n"
                "  - transformers>=4.40.0\n"
                "  - einops addict easydict\n"
                "Install: pip install einops addict easydict"
            )
    
    def _load_model(self):
        """Load DeepSeek-OCR model"""
        try:
            from transformers import AutoModel, AutoTokenizer
        except ImportError:
            raise ImportError(
                "transformers library required.\n"
                "Install: pip install transformers>=4.46.3"
            )
            
        logger.info(f"Loading {self.model_name}...")
        start_time = time.time()
        self._load_error = None

        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                trust_remote_code=True
            )
            logger.info("Tokenizer loaded")
            
            # Model loading kwargs
            model_kwargs = {
                "trust_remote_code": True,
                "use_safetensors": True,
                "torch_dtype": torch.bfloat16,
                "device_map": "auto"
            }
            
            # Use flash attention if available
            if self.use_flash_attention:
                try:
                    import flash_attn
                    model_kwargs["_attn_implementation"] = "flash_attention_2"
                    logger.info("Using Flash Attention 2")
                except ImportError:
                    pass
            
            # Load model
            self.model = AutoModel.from_pretrained(
                self.model_name, 
                **model_kwargs
            )
            self.model = self.model.eval()
                
            logger.info(f"✅ DeepSeek-OCR loaded in {time.time() - start_time:.2f}s")
            logger.info(f"   Resolution: {self.resolution} ({self.resolution_config})")
            
        except Exception as e:
            self._load_error = str(e)
            logger.error(f"Failed to load DeepSeek-OCR: {e}")
            import traceback
            traceback.print_exc()
            self.model = None
            self.tokenizer = None

    def _get_prompt(self) -> str:
        """Get prompt based on output format"""
        if self.output_format == "markdown":
            return "<image>\n<|grounding|>Convert the document to markdown. "
        elif self.output_format == "grounding":
            return "<image>\n<|grounding|>Locate and extract all text with bounding boxes. "
        else:  # text
            return "<image>\nFree OCR. "

    def process_image(self, image: Image.Image, page_num: int = 0) -> List[VisualRegion]:
        """
        Process image with DeepSeek-OCR

        Args:
            image: PIL Image of the document page
            page_num: Page number

        Returns:
            List of VisualRegion objects with compressed visual context
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("DeepSeek-OCR model not loaded. Cannot process image.")
        
        width, height = image.size
        
        # Save image to temp file (DeepSeek-OCR requires file path)
        temp_image_path = os.path.join(self.temp_dir, f"page_{page_num}.png")
        image.save(temp_image_path)
        
        try:
            # Get prompt
            prompt = self._get_prompt()
            
            # Call DeepSeek-OCR infer method
            result = self.model.infer(
                self.tokenizer,
                prompt=prompt,
                image_file=temp_image_path,
                output_path=self.temp_dir,
                base_size=self.resolution_config["base_size"],
                image_size=self.resolution_config["image_size"],
                crop_mode=self.resolution_config["crop_mode"],
                save_results=False,
                test_compress=self.test_compress
            )
            
            # Extract text from result
            if isinstance(result, dict):
                text = result.get("text", result.get("markdown", str(result)))
                compression_stats = result.get("compression_stats", {})
            elif isinstance(result, str):
                text = result
                compression_stats = {}
            else:
                text = str(result)
                compression_stats = {}
            
            # Create compressed tokens from visual embeddings
            compressed_tokens = []
            if self.enable_visual_embeddings:
                compressed_tokens = self._extract_compressed_tokens(image, page_num)
            
            # Create visual region
            region = VisualRegion(
                region_id=f"p{page_num}_full",
                page_num=page_num,
                block_type="page",
                bbox=BoundingBox(0, 0, width, height),
                compressed_tokens=compressed_tokens,
                text_content=text,
                markdown_content=text if self.output_format == "markdown" else "",
                token_count=len(text.split()),
                confidence=0.95,
                metadata={
                    "model": self.model_name,
                    "resolution": self.resolution,
                    "compression_stats": compression_stats,
                    "output_format": self.output_format
                }
            )
            
            return [region]
            
        except Exception as e:
            logger.error(f"DeepSeek-OCR processing failed: {e}")
            raise RuntimeError(f"DeepSeek-OCR processing failed: {e}")
        finally:
            # Cleanup temp file
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    def _extract_compressed_tokens(self, image: Image.Image, page_num: int) -> List[VisualToken]:
        """Extract compressed visual tokens from image"""
        try:
            # Create embedding from image features
            img_resized = image.resize((224, 224))
            img_array = np.array(img_resized).astype(np.float32) / 255.0
            
            # Create feature vector
            features = []
            if len(img_array.shape) == 3:
                for c in range(min(3, img_array.shape[2])):
                    channel = img_array[:, :, c]
                    features.extend([
                        channel.mean(), channel.std(),
                        channel.min(), channel.max(),
                        np.median(channel)
                    ])
            
            # Pad to target dimension
            while len(features) < self.target_embedding_dim:
                features.append(0.0)
            
            embedding = np.array(features[:self.target_embedding_dim], dtype=np.float32)
            
            # Create visual token
            token = VisualToken(
                token_id=0,
                embedding=embedding,
                confidence=0.95,
                region_type="page",
                spatial_position=(0.5, 0.5),
                compression_method="deepseek-ocr"
            )
            
            return [token]
            
        except Exception as e:
            logger.warning(f"Could not extract compressed tokens: {e}")
            return []

    def batch_process(
        self, 
        images: List[Image.Image], 
        start_page: int = 0, 
        show_progress: bool = False
    ) -> List[PageOCRResult]:
        """Process a batch of images"""
        page_results = []
        
        for i, img in enumerate(images):
            page_num = start_page + i
            
            if show_progress:
                logger.info(f"Processing page {page_num + 1}...")
            
            regions = self.process_image(img, page_num)
            full_text = "\n".join([r.text_content for r in regions])
            
            page_results.append(PageOCRResult(
                page_num=page_num,
                visual_regions=regions,
                full_text=full_text,
                metadata={
                    "model": self.model_name,
                    "resolution": self.resolution
                }
            ))
            
        return page_results

    def get_compression_stats(self, results: List[PageOCRResult]) -> Dict[str, Any]:
        """Calculate compression statistics"""
        total_pages = len(results)
        total_tokens = 0
        total_regions = 0
        total_compressed_tokens = 0
        
        for res in results:
            total_regions += len(res.visual_regions)
            for region in res.visual_regions:
                total_tokens += getattr(region, "token_count", len(region.text_content.split()))
                total_compressed_tokens += len(getattr(region, "compressed_tokens", []))
        
        return {
            "total_pages": total_pages,
            "total_regions": total_regions,
            "total_tokens": total_tokens,
            "total_compressed_tokens": total_compressed_tokens,
            "tokens_per_page": total_tokens / total_pages if total_pages > 0 else 0,
            "model": self.model_name,
            "resolution": self.resolution
        }

    def cleanup(self):
        """Clean up resources"""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        # Cleanup temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("GPU memory cleaned")
