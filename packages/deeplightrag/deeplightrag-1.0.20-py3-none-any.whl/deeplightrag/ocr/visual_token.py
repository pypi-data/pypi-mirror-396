"""Visual Token and Region data structures for OCR output."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .geometry import BoundingBox


@dataclass
class VisualToken:
    token_id: int
    embedding: np.ndarray
    confidence: float
    region_type: str = "general"
    spatial_position: Tuple[float, float] = (0.0, 0.0)
    compression_method: str = "none"
    original_dims: int = 768

    def get_embedding_size_kb(self) -> float:
        return self.embedding.nbytes / 1024

    def compress(self, method: str = "pca", target_dim: int = 256) -> "VisualToken":
        compressed_embedding = self.embedding[:target_dim]
        return VisualToken(
            token_id=self.token_id,
            embedding=compressed_embedding,
            confidence=self.confidence,
            region_type=self.region_type,
            spatial_position=self.spatial_position,
            compression_method=method,
            original_dims=len(self.embedding),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "confidence": self.confidence,
            "region_type": self.region_type,
            "spatial_position": list(self.spatial_position),
            "compression_method": self.compression_method,
            "original_dims": self.original_dims,
        }


@dataclass
class VisualRegion:
    region_id: str
    page_num: int
    block_type: str
    bbox: BoundingBox
    compressed_tokens: List[VisualToken]
    text_content: str
    markdown_content: str
    token_count: int
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    region_embedding: Optional[np.ndarray] = None
    embedding_confidence: float = 0.0
    visual_complexity: float = 0.0
    text_to_visual_ratio: float = 1.0

    global_page_embedding: Optional[np.ndarray] = None
    local_context_embedding: Optional[np.ndarray] = None
    spatial_features: Optional[Dict[str, float]] = None
    layout_features: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, float]] = None
    readability_metrics: Optional[Dict[str, float]] = None

    table_structure: Optional[Dict[str, Any]] = None
    figure_analysis: Optional[Dict[str, Any]] = None
    formula_features: Optional[Dict[str, Any]] = None

    spatial_neighbors: List[str] = field(default_factory=list)
    visual_hierarchy: Optional[str] = None
    content_flow: Optional[List[str]] = None

    multi_scale_embeddings: Optional[Dict[str, np.ndarray]] = None
    semantic_embedding: Optional[np.ndarray] = None
    structural_embedding: Optional[np.ndarray] = None

    image_path: Optional[str] = None
    extracted_image: bool = False
    image_embedding: Optional[np.ndarray] = None
    image_format: str = "png"
    image_size: Optional[Tuple[int, int]] = None

    def is_visual_content(self) -> bool:
        return self.block_type in {"table", "figure", "formula", "chart"}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "region_id": self.region_id,
            "page_num": self.page_num,
            "block_type": self.block_type,
            "bbox": self.bbox.to_list() if self.bbox else None,
            "text_content": self.text_content,
            "markdown_content": self.markdown_content,
            "token_count": self.token_count,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "visual_complexity": self.visual_complexity,
            "spatial_features": self.spatial_features,
            "layout_features": self.layout_features,
            "image_path": self.image_path,
            "image_format": self.image_format,
            "image_size": list(self.image_size) if self.image_size else None,
        }
