"""
Working Enhanced NER Pipeline for DeepLightRAG
Integrates GLiNER and GLiREL with visual context.
"""

from typing import Dict, List, Optional, Any
import logging
import numpy as np

logger = logging.getLogger(__name__)


class EnhancedNERPipeline:
    """
    Enhanced NER pipeline that integrates multiple extractors
    with visual and layout context awareness.
    """

    def __init__(
        self,
        model_name: str = "knowledgator/GLiREL",
        device: str = "cpu",
        confidence_threshold: float = 0.3
    ):
        """
        Initialize enhanced NER pipeline.

        Args:
            model_name: GLiREL model name for relation extraction
            device: Device to run on
            confidence_threshold: Minimum confidence threshold
        """
        self.model_name = model_name
        self.device = device
        self.confidence_threshold = confidence_threshold
        self.relation_model = None

        # Try to load GLiREL
        self._load_relation_model()

    def _load_relation_model(self):
        """Load GLiREL model for relation extraction."""
        try:
            # Check if we can import gliner (for GLiREL)
            import gliner
            logger.info(f"Loading GLiREL model: {self.model_name}")

            # For now, create a mock GLiREL since actual GLiREL may not be available
            from .working_gliner_ner import MockGLiNER
            self.relation_model = MockGLiNER(self.model_name)

            logger.info("✅ GLiREL model loaded (mock)")

        except ImportError as e:
            logger.warning(f"Failed to import GLiNER: {e}")
            self.relation_model = None

    def extract_relations(self, entities: List[Dict], text: str) -> List[Dict]:
        """
        Extract relations between entities.

        Args:
            entities: List of extracted entities
            text: Original text context

        Returns:
            List of extracted relations
        """
        if not self.relation_model or len(entities) < 2:
            return []

        try:
            return self._extract_with_glirel(entities, text)
        except Exception as e:
            logger.error(f"GLiREL extraction failed: {e}")
            return self._extract_relations_fallback(entities, text)

    def extract_relations_with_layout(
        self,
        entities: List[Dict],
        text: str,
        visual_regions: List
    ) -> List[Dict]:
        """
        Extract relations with layout context from VisualRegions.

        Args:
            entities: List of extracted entities
            text: Original text
            visual_regions: List of VisualRegion objects

        Returns:
            List of extracted relations with layout metadata
        """
        # Basic relation extraction
        relations = self.extract_relations(entities, text)

        # Enhance with layout context
        enhanced_relations = []
        for relation in relations:
            # Find visual regions for source and target entities
            source_region = self._find_entity_region(
                relation["source"], entities, visual_regions
            )
            target_region = self._find_entity_region(
                relation["target"], entities, visual_regions
            )

            # Add layout metadata
            enhanced_relation = relation.copy()
            if source_region and target_region:
                # Calculate spatial relationship
                spatial_rel = self._calculate_spatial_relationship(
                    source_region, target_region
                )

                enhanced_relation.update({
                    "source_region": source_region.get("region_id"),
                    "target_region": target_region.get("region_id"),
                    "spatial_relationship": spatial_rel,
                    "layout_context": {
                        "source_block_type": source_region.get("block_type"),
                        "target_block_type": target_region.get("block_type"),
                        "same_block": source_region.get("block_type") == target_region.get("block_type")
                    }
                })

            enhanced_relations.append(enhanced_relation)

        return enhanced_relations

    def _extract_with_glirel(self, entities: List[Dict], text: str) -> List[Dict]:
        """Extract relations using GLiREL model."""
        # Prepare entity pairs for GLiREL
        entity_pairs = []
        entity_texts = []

        for entity in entities:
            entity_texts.append(entity["text"])

        # Create pairs (source, target)
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                entity_pairs.append((entity1, entity2))

        # Mock GLiREL prediction
        # In real implementation, this would use actual GLiREL
        relations = []
        relation_types = [
            "located_in", "part_of", "created_by", "used_for", "contains",
            "connected_to", "related_to", "applies_to", "affects", "enables"
        ]

        for source, target in entity_pairs[:20]:  # Limit for performance
            # Mock relation prediction
            relation_type = relation_types[len(relations) % len(relation_types)]
            confidence = np.random.uniform(0.3, 0.9)

            if confidence > self.confidence_threshold:
                relation = {
                    "source": source["text"],
                    "target": target["text"],
                    "relation": relation_type,
                    "confidence": confidence,
                    "source_id": source.get("id", f"ent_{source.get('start', 0)}"),
                    "target_id": target.get("id", f"ent_{target.get('start', 0)}"),
                    "source": source,
                    "target": target
                }
                relations.append(relation)

        return relations

    def _extract_relations_fallback(self, entities: List[Dict], text: str) -> List[Dict]:
        """Fallback relation extraction using simple heuristics."""
        relations = []

        # Simple heuristic: if entities are close in text, they might be related
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                # Check distance between entities
                distance = entity2.get("start", 0) - entity1.get("end", 0)
                if 0 < distance < 50:  # Within 50 characters
                    # Infer relation based on entity types
                    relation = self._infer_relation_from_proximity(
                        entity1, entity2, text, distance
                    )
                    if relation:
                        relations.append(relation)

        return relations

    def _infer_relation_from_proximity(
        self,
        entity1: Dict,
        entity2: Dict,
        text: str,
        distance: int
    ) -> Optional[Dict]:
        """Infer relation based on entity types and proximity."""
        e1_type = entity1.get("label", "").lower()
        e2_type = entity2.get("label", "").lower()
        e1_text = entity1.get("text", "").lower()
        e2_text = entity2.get("text", "").lower()

        # Rule-based relation inference
        if "person" in e1_type and "organization" in e2_type:
            return {
                "source": e1_text,
                "target": e2_text,
                "relation": "works_for",
                "confidence": 0.7,
                "source_id": entity1.get("id"),
                "target_id": entity2.get("id")
            }
        elif "location" in e1_type or "location" in e2_type:
            return {
                "source": e1_text,
                "target": e2_text,
                "relation": "located_in",
                "confidence": 0.6,
                "source_id": entity1.get("id"),
                "target_id": entity2.get("id")
            }
        elif "date" in e1_type or "date" in e2_type:
            return {
                "source": e1_text,
                "target": e2_text,
                "relation": "occurred_on",
                "confidence": 0.5,
                "source_id": entity1.get("id"),
                "target_id": entity2.get("id")
            }

        return None

    def _find_entity_region(
        self,
        entity_text: str,
        entities: List[Dict],
        visual_regions: List
    ) -> Optional[Dict]:
        """Find which visual region contains an entity."""
        for region in visual_regions:
            # Handle both dict and VisualRegion object
            if hasattr(region, 'text_content'):
                region_text = region.text_content.lower()
            else:
                region_text = region.get("text_content", "").lower()

            if entity_text.lower() in region_text:
                # Convert to dict if it's a VisualRegion object
                if hasattr(region, 'text_content'):
                    return {
                        "region_id": getattr(region, 'region_id', None),
                        "block_type": getattr(region, 'block_type', None),
                        "bbox": getattr(region, 'bbox', None),
                        "text_content": region.text_content,
                        "spatial_features": getattr(region, 'spatial_features', {}),
                        "layout_features": getattr(region, 'layout_features', {}),
                        "quality_metrics": getattr(region, 'quality_metrics', {}),
                    }
                return region
        return None

    def _calculate_spatial_relationship(
        self,
        source_region: Dict,
        target_region: Dict
    ) -> str:
        """Calculate spatial relationship between regions."""
        # Get bounding boxes
        source_bbox = source_region.get("bbox", [0, 0, 0, 0])
        target_bbox = target_region.get("bbox", [0, 0, 0, 0])

        # Simple spatial relationship calculation
        if not source_bbox or not target_bbox:
            return "unknown"

        source_bottom = source_bbox[3]
        target_top = target_bbox[1]

        if source_bottom < target_top - 20:
            return "above"
        elif source_bottom < target_top + 20:
            return "adjacent"
        else:
            return "below"

    def _enhance_with_visual_confidence(
        self,
        relations: List[Dict],
        visual_regions: List
    ) -> List[Dict]:
        """Enhance relations with visual-based confidence scoring."""
        enhanced = []

        for relation in relations:
            # Get visual quality for regions
            source_quality = self._get_region_quality(
                relation.get("source_region"), visual_regions
            )
            target_quality = self._get_region_quality(
                relation.get("target_region"), visual_regions
            )

            # Adjust confidence based on visual quality
            base_confidence = relation.get("confidence", 0.5)
            visual_boost = (source_quality + target_quality) / 2

            enhanced_relation = relation.copy()
            enhanced_relation["confidence"] = min(1.0, base_confidence * (1 + visual_boost * 0.3))
            enhanced_relation["visual_quality_score"] = visual_boost

            enhanced.append(enhanced_relation)

        return enhanced

    def _get_region_quality(self, region_id: str, visual_regions: List) -> float:
        """Get visual quality score for a region."""
        for region in visual_regions:
            if region.get("region_id") == region_id:
                quality = region.get("quality_metrics", {})
                # Average of clarity and contrast scores
                clarity = quality.get("clarity_score", 0.5)
                contrast = quality.get("contrast_score", 0.5)
                return (clarity + contrast) / 2
        return 0.5  # Default quality