"""Dual-Layer Graph: Visual-Spatial + Entity-Relationship with cross-layer connections."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import numpy as np

from ..ocr.deepseek_ocr import PageOCRResult
from .entity_relationship import Entity, EntityRelationshipGraph
from .visual_spatial import VisualNode, VisualSpatialGraph

logger = logging.getLogger(__name__)


class DualLayerGraph:
    def __init__(
        self,
        device: str = "cpu",
        enable_gpu_acceleration: bool = False,
        ner_config: Optional[Dict] = None,
        re_config: Optional[Dict] = None,
        llm=None,
    ):
        self.visual_spatial = VisualSpatialGraph()
        self.entity_relationship = EntityRelationshipGraph(
            device=device, ner_config=ner_config, re_config=re_config, llm=llm
        )

        self.entity_to_regions: Dict[str, List[str]] = {}
        self.region_to_entities: Dict[str, List[str]] = {}
        self.figure_caption_links: Dict[str, str] = {}
        self.image_to_entities: Dict[str, List[str]] = {}
        self.entity_to_images: Dict[str, List[str]] = {}

    def build_from_ocr_results(self, ocr_results: List[PageOCRResult]):
        logger.info("Building Dual-Layer Graph")

        self.visual_spatial.build_from_ocr_results(ocr_results)
        self.entity_relationship.extract_entities_from_ocr(ocr_results)
        self.entity_relationship.extract_relationships(ocr_results)
        self._build_cross_layer_connections()
        self._log_statistics()

    def _build_cross_layer_connections(self):
        valid_region_ids = set(self.visual_spatial.nodes.keys())

        for entity_id, entity in self.entity_relationship.entities.items():
            valid_regions = [rid for rid in entity.source_visual_regions if rid in valid_region_ids]
            entity.source_visual_regions = valid_regions
            self.entity_to_regions[entity_id] = valid_regions

            for region_id in valid_regions:
                if region_id not in self.region_to_entities:
                    self.region_to_entities[region_id] = []
                if entity_id not in self.region_to_entities[region_id]:
                    self.region_to_entities[region_id].append(entity_id)

        for region_id, entity_ids in self.region_to_entities.items():
            if region_id in self.visual_spatial.nodes:
                self.visual_spatial.nodes[region_id].entity_ids = entity_ids

        try:
            self._link_figures_to_captions()
        except Exception as e:
            logger.warning(f"Failed to link figures with captions: {e}")

        try:
            self._link_images_to_entities()
        except Exception as e:
            logger.warning(f"Failed to build image connections: {e}")

    def _link_figures_to_captions(self):
        for page_num, node_ids in self.visual_spatial.page_nodes.items():
            figures = []
            captions = []

            for node_id in node_ids:
                node = self.visual_spatial.nodes[node_id]
                if node.region.block_type == "figure":
                    figures.append(node)
                elif node.region.block_type == "caption":
                    captions.append(node)

            for figure in figures:
                best_caption = None
                min_distance = float("inf")

                for caption in captions:
                    y_distance = caption.position[1] - figure.position[1]
                    x_distance = abs(caption.position[0] - figure.position[0])

                    if 0 < y_distance < 0.2 and x_distance < 0.3:
                        distance = np.sqrt(y_distance**2 + x_distance**2)
                        if distance < min_distance:
                            min_distance = distance
                            best_caption = caption

                if best_caption:
                    self.figure_caption_links[figure.node_id] = best_caption.node_id

    def _link_images_to_entities(self):
        for node_id, node in self.visual_spatial.nodes.items():
            if not (node.region.image_path and node.region.extracted_image):
                continue

            image_path = node.region.image_path
            entity_ids = self.region_to_entities.get(node_id, [])

            if entity_ids:
                self.image_to_entities[image_path] = entity_ids
                for entity_id in entity_ids:
                    if entity_id not in self.entity_to_images:
                        self.entity_to_images[entity_id] = []
                    if image_path not in self.entity_to_images[entity_id]:
                        self.entity_to_images[entity_id].append(image_path)
            else:
                nearby_entities = self._find_nearby_entities(node)
                if nearby_entities:
                    self.image_to_entities[image_path] = list(set(nearby_entities))
                    for entity_id in nearby_entities:
                        if entity_id not in self.entity_to_images:
                            self.entity_to_images[entity_id] = []
                        if image_path not in self.entity_to_images[entity_id]:
                            self.entity_to_images[entity_id].append(image_path)

    def _find_nearby_entities(self, node: VisualNode) -> List[str]:
        if node.page_num not in self.visual_spatial.page_nodes:
            return []

        nearby_entities = []
        for nearby_region_id in self.visual_spatial.page_nodes[node.page_num]:
            if nearby_region_id == node.node_id:
                continue
            nearby_node = self.visual_spatial.nodes[nearby_region_id]
            if abs(nearby_node.position[1] - node.position[1]) < 0.15:
                nearby_entities.extend(self.region_to_entities.get(nearby_region_id, []))
        return nearby_entities

    def get_regions_for_entity(self, entity_id: str) -> List[VisualNode]:
        region_ids = self.entity_to_regions.get(entity_id, [])
        return [self.visual_spatial.nodes[rid] for rid in region_ids if rid in self.visual_spatial.nodes]

    def get_entities_for_region(self, region_id: str) -> List[Entity]:
        entity_ids = self.region_to_entities.get(region_id, [])
        return [
            self.entity_relationship.entities[eid]
            for eid in entity_ids
            if eid in self.entity_relationship.entities
        ]

    def get_caption_for_figure(self, figure_node_id: str) -> Optional[VisualNode]:
        caption_id = self.figure_caption_links.get(figure_node_id)
        return self.visual_spatial.nodes.get(caption_id) if caption_id else None

    def query_hybrid(
        self, query_entities: List[str], query_regions: List[str], hop_distance: int = 2
    ) -> Dict[str, Any]:
        results = {"entities": set(), "regions": set(), "relationships": [], "spatial_edges": []}

        for entity_id in query_entities:
            related = self.entity_relationship.get_related_entities(entity_id, hop_distance=hop_distance)
            results["entities"].update(related)
            results["entities"].add(entity_id)

            for eid in list(results["entities"]):
                results["regions"].update(self.entity_to_regions.get(eid, []))

        for region_id in query_regions:
            neighbors = self.visual_spatial.get_neighbors(region_id, hop_distance=hop_distance)
            results["regions"].update(neighbors)
            results["regions"].add(region_id)

            for rid in list(results["regions"]):
                results["entities"].update(self.region_to_entities.get(rid, []))

        for eid in results["entities"]:
            for rel in self.entity_relationship.relationships:
                if rel.source_entity in results["entities"] and rel.target_entity in results["entities"]:
                    if rel.source_entity == eid or rel.target_entity == eid:
                        results["relationships"].append(rel.to_dict())

        for rid in results["regions"]:
            for edge in self.visual_spatial.edges:
                if edge.source_id in results["regions"] and edge.target_id in results["regions"]:
                    if edge.source_id == rid or edge.target_id == rid:
                        results["spatial_edges"].append(edge.to_dict())

        results["entities"] = list(results["entities"])
        results["regions"] = list(results["regions"])
        return results

    def get_context_for_query(self, query: str, max_tokens: int = 6000) -> str:
        relevant_entities = self.entity_relationship.search_entities(query, top_k=10)
        context_parts = ["## Relevant Entities\n"]

        for entity in relevant_entities:
            context_parts.append(f"- **{entity.name}** ({entity.entity_type}): {entity.description}\n")
            related = self.entity_relationship.get_related_entities(entity.entity_id, hop_distance=1)
            for related_id in related[:3]:
                related_entity = self.entity_relationship.get_entity(related_id)
                if related_entity:
                    context_parts.append(f"  - Related: {related_entity.name}\n")

        context_parts.append("\n## Source Regions\n")
        seen_regions = set()
        for entity in relevant_entities[:5]:
            for region in self.get_regions_for_entity(entity.entity_id)[:2]:
                if region.node_id not in seen_regions:
                    seen_regions.add(region.node_id)
                    context_parts.append(
                        f"**[{region.region.block_type.upper()}] Page {region.page_num}:**\n"
                        f"{region.region.markdown_content}\n"
                    )

        context = "".join(context_parts)
        if len(context) / 4 > max_tokens:
            context = context[: int(max_tokens * 4)] + "\n... [truncated]"
        return context

    def _log_statistics(self):
        vs_stats = self.visual_spatial.get_statistics()
        er_stats = self.entity_relationship.get_statistics()
        total_tokens = sum(node.region.token_count for node in self.visual_spatial.nodes.values())
        compression = (vs_stats["num_pages"] * 2500) / total_tokens if total_tokens > 0 else 0

        logger.info(
            f"Graph built: {vs_stats['num_nodes']} visual nodes, "
            f"{er_stats['num_entities']} entities, "
            f"{er_stats['num_relationships']} relationships, "
            f"{compression:.1f}x compression"
        )

    def save(self, directory: str):
        os.makedirs(directory, exist_ok=True)
        self.visual_spatial.save(os.path.join(directory, "visual_spatial.json"))
        self.entity_relationship.save(os.path.join(directory, "entity_relationship.json"))

        cross_layer_data = {
            "entity_to_regions": self.entity_to_regions,
            "region_to_entities": self.region_to_entities,
            "figure_caption_links": self.figure_caption_links,
        }
        with open(os.path.join(directory, "cross_layer.json"), "w") as f:
            json.dump(cross_layer_data, f, indent=2)
        logger.info(f"Graph saved to {directory}")

    def load(self, directory: str):
        visual_spatial_path = os.path.join(directory, "visual_spatial.json")
        if os.path.exists(visual_spatial_path):
            self.visual_spatial.load(visual_spatial_path)
        else:
            logger.warning(f"visual_spatial.json not found in {directory}")

        entity_relationship_path = os.path.join(directory, "entity_relationship.json")
        if os.path.exists(entity_relationship_path):
            self.entity_relationship.load(entity_relationship_path)
        else:
            logger.warning(f"entity_relationship.json not found in {directory}")

        cross_layer_path = os.path.join(directory, "cross_layer.json")
        if os.path.exists(cross_layer_path):
            with open(cross_layer_path, "r") as f:
                cross_layer_data = json.load(f)
            self.entity_to_regions = cross_layer_data["entity_to_regions"]
            self.region_to_entities = cross_layer_data["region_to_entities"]
            self.figure_caption_links = cross_layer_data["figure_caption_links"]
        else:
            logger.warning(f"cross_layer.json not found in {directory}")

        logger.info(f"Graph loaded from {directory}")

    def to_dict(self) -> Dict:
        return {
            "visual_spatial": self.visual_spatial.to_dict(),
            "entity_relationship": self.entity_relationship.to_dict(),
            "cross_layer": {
                "entity_to_regions": self.entity_to_regions,
                "region_to_entities": self.region_to_entities,
                "figure_caption_links": self.figure_caption_links,
            },
        }
