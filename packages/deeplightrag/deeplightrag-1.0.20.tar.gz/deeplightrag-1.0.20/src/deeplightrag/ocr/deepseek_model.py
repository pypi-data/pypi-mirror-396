"""DeepSeek-OCR implementation for visual context compression."""

import logging
import os
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import torch
from PIL import Image

from ..interfaces import BaseOCRProcessor
from ..utils.device import device_manager
from .geometry import BoundingBox
from .visual_token import VisualRegion, VisualToken

logger = logging.getLogger(__name__)


RESOLUTION_PRESETS = {
    "tiny": {"base_size": 512, "image_size": 512, "crop_mode": False},
    "small": {"base_size": 640, "image_size": 640, "crop_mode": False},
    "base": {"base_size": 1024, "image_size": 1024, "crop_mode": False},
    "large": {"base_size": 1280, "image_size": 1280, "crop_mode": False},
    "gundam": {"base_size": 1024, "image_size": 640, "crop_mode": True},
}


@dataclass
class PageOCRResult:
    page_num: int
    visual_regions: List[VisualRegion]
    full_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    width: int = 0
    height: int = 0
    processing_time: float = 0.0

    @property
    def regions(self) -> List[VisualRegion]:
        return self.visual_regions

    @property
    def total_tokens(self) -> int:
        return sum(
            r.token_count if hasattr(r, "token_count") else len(r.text_content.split())
            for r in self.visual_regions
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_num": self.page_num,
            "width": self.width,
            "height": self.height,
            "regions": [r.to_dict() if hasattr(r, "to_dict") else str(r) for r in self.visual_regions],
            "total_tokens": self.total_tokens,
            "processing_time": self.processing_time,
            "full_text": self.full_text,
            "metadata": self.metadata,
        }


class DeepSeekOCR(BaseOCRProcessor):
    def __init__(
        self,
        model_name: str = "deepseek-ai/DeepSeek-OCR",
        resolution: str = "gundam",
        device: Optional[str] = None,
        use_flash_attention: bool = True,
        extract_images: bool = False,
        image_output_dir: str = "./extracted_images",
        enable_visual_embeddings: bool = True,
        target_embedding_dim: int = 256,
        output_format: str = "markdown",
        test_compress: bool = True,
        **kwargs,
    ):
        self.model_name = model_name
        self.resolution = resolution
        self.use_flash_attention = use_flash_attention
        self.extract_images = extract_images
        self.image_output_dir = image_output_dir
        self.enable_visual_embeddings = enable_visual_embeddings
        self.target_embedding_dim = target_embedding_dim
        self.output_format = output_format
        self.test_compress = test_compress

        self.resolution_config = RESOLUTION_PRESETS.get(resolution, RESOLUTION_PRESETS["gundam"])
        if resolution not in RESOLUTION_PRESETS:
            logger.warning(f"Unknown resolution '{resolution}', using 'gundam'")

        self.device = device or device_manager.get_torch_device()
        if self.device != "cuda":
            logger.warning(f"DeepSeek-OCR requires CUDA GPU. Current device: {self.device}")

        if self.extract_images:
            os.makedirs(self.image_output_dir, exist_ok=True)

        self.temp_dir = tempfile.mkdtemp()
        self.model = None
        self.tokenizer = None
        self._load_error = None
        self._load_model()

        if self.model is None:
            raise RuntimeError(
                f"Failed to load DeepSeek-OCR model.\n"
                f"Error: {self._load_error}\n\n"
                "Requirements:\n"
                "  - NVIDIA GPU with CUDA\n"
                "  - torch>=2.0.0\n"
                "  - transformers>=4.40.0\n"
                "  - einops addict easydict"
            )

    def _load_model(self):
        try:
            from transformers import AutoModel, AutoTokenizer
        except ImportError:
            raise ImportError("transformers library required. Install: pip install transformers>=4.46.3")

        logger.info(f"Loading {self.model_name}...")
        start_time = time.time()

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)

            model_kwargs = {
                "trust_remote_code": True,
                "use_safetensors": True,
                "torch_dtype": torch.bfloat16,
                "device_map": "auto",
            }

            if self.use_flash_attention:
                try:
                    import flash_attn
                    model_kwargs["_attn_implementation"] = "flash_attention_2"
                    logger.info("Using Flash Attention 2")
                except ImportError:
                    pass

            self.model = AutoModel.from_pretrained(self.model_name, **model_kwargs).eval()
            logger.info(f"DeepSeek-OCR loaded in {time.time() - start_time:.2f}s")

        except Exception as e:
            self._load_error = str(e)
            logger.error(f"Failed to load DeepSeek-OCR: {e}")
            self.model = None
            self.tokenizer = None

    def _build_prompt(self) -> str:
        prompts = {
            "markdown": "<image>\n<|grounding|>Convert the document to markdown. ",
            "grounding": "<image>\n<|grounding|>Locate and extract all text with bounding boxes. ",
            "text": "<image>\nFree OCR. ",
        }
        return prompts.get(self.output_format, prompts["markdown"])

    def process_image(self, image: Image.Image, page_num: int = 0) -> List[VisualRegion]:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("DeepSeek-OCR model not loaded")

        width, height = image.size
        temp_image_path = os.path.join(self.temp_dir, f"page_{page_num}.png")
        image.save(temp_image_path)

        try:
            result = self.model.infer(
                self.tokenizer,
                prompt=self._build_prompt(),
                image_file=temp_image_path,
                output_path=self.temp_dir,
                base_size=self.resolution_config["base_size"],
                image_size=self.resolution_config["image_size"],
                crop_mode=self.resolution_config["crop_mode"],
                save_results=False,
                test_compress=self.test_compress,
            )

            text, compression_stats = self._parse_ocr_result(result)
            compressed_tokens = self._extract_visual_tokens(image, page_num) if self.enable_visual_embeddings else []

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
                },
            )
            return [region]

        finally:
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    def _parse_ocr_result(self, result) -> tuple:
        if result is None:
            return "OCR completed", {}
        if isinstance(result, dict):
            text = result.get("text", result.get("markdown", str(result)))
            return text, result.get("compression_stats", {})
        return str(result) if result else "", {}

    def _extract_visual_tokens(self, image: Image.Image, page_num: int) -> List[VisualToken]:
        try:
            img_resized = image.resize((224, 224))
            img_array = np.array(img_resized).astype(np.float32) / 255.0

            features = []
            if len(img_array.shape) == 3:
                for c in range(min(3, img_array.shape[2])):
                    channel = img_array[:, :, c]
                    features.extend([
                        channel.mean(),
                        channel.std(),
                        channel.min(),
                        channel.max(),
                        np.median(channel),
                    ])

            features.extend([0.0] * (self.target_embedding_dim - len(features)))
            embedding = np.array(features[: self.target_embedding_dim], dtype=np.float32)

            return [
                VisualToken(
                    token_id=0,
                    embedding=embedding,
                    confidence=0.95,
                    region_type="page",
                    spatial_position=(0.5, 0.5),
                    compression_method="deepseek-ocr",
                )
            ]
        except Exception as e:
            logger.warning(f"Could not extract visual tokens: {e}")
            return []

    def batch_process(
        self,
        images: List[Image.Image],
        start_page: int = 0,
        show_progress: bool = False,
    ) -> List[PageOCRResult]:
        results = []
        for i, img in enumerate(images):
            page_num = start_page + i
            start_time = time.time()

            if show_progress:
                logger.info(f"Processing page {page_num + 1}...")

            regions = self.process_image(img, page_num)
            results.append(
                PageOCRResult(
                    page_num=page_num,
                    visual_regions=regions,
                    full_text="\n".join(r.text_content for r in regions),
                    width=img.size[0],
                    height=img.size[1],
                    processing_time=time.time() - start_time,
                    metadata={"model": self.model_name, "resolution": self.resolution},
                )
            )
        return results

    def get_compression_stats(self, results: List[PageOCRResult]) -> Dict[str, Any]:
        total_pages = len(results)
        total_tokens = sum(
            r.token_count if hasattr(r, "token_count") else len(r.text_content.split())
            for res in results
            for r in res.visual_regions
        )
        total_regions = sum(len(res.visual_regions) for res in results)

        return {
            "total_pages": total_pages,
            "total_regions": total_regions,
            "total_tokens": total_tokens,
            "tokens_per_page": total_tokens / total_pages if total_pages > 0 else 0,
            "model": self.model_name,
            "resolution": self.resolution,
        }

    def cleanup(self):
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("GPU memory cleaned")
