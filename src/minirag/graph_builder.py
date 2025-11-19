"""
MiniRAG Graph Builder - True Graph-First Architecture
Builds heterogeneous knowledge graph from e-commerce knowledge base.
Graph is the PRIMARY indexing mechanism, not an enhancement.
"""
import json
import networkx as nx
import pickle
import pathlib
from typing import Dict, List, Any
from tqdm import tqdm
from ..config import DATA_DIR, GRAPH_DIR

class MiniRAGGraphBuilder:
    """
    Builds a heterogeneous knowledge graph for MiniRAG architecture.
    This is the PRIMARY indexing mechanism - not an enhancement.
    """
    
    def __init__(self):
        self.graph = nx.MultiDiGraph(name="ecommerce_minirag_graph")
        self.knowledge_base = None
        
    def load_knowledge_base(self) -> Dict:
        """Load e-commerce knowledge base from multiple JSON files"""
        try:
            # Load from separate JSON files
            policies_path = DATA_DIR / "policies.json"
            entities_path = DATA_DIR / "entities.json"
            relationships_path = DATA_DIR / "relationships.json"
            guardrails_path = DATA_DIR / "guardrails.json"
            
            knowledge_base = {}
            
            # Load policies
            if policies_path.exists():
                with open(policies_path, 'r', encoding='utf-8') as f:
                    policies_data = json.load(f)
                    knowledge_base["policies"] = policies_data.get("policies", {})
            
            # Load entities
            if entities_path.exists():
                with open(entities_path, 'r', encoding='utf-8') as f:
                    entities_data = json.load(f)
                    knowledge_base["entities"] = entities_data.get("entities", {})
            
            # Load relationships
            if relationships_path.exists():
                with open(relationships_path, 'r', encoding='utf-8') as f:
                    relationships_data = json.load(f)
                    knowledge_base["relationships"] = relationships_data.get("relationships", {})
            
            # Load guardrails
            if guardrails_path.exists():
                with open(guardrails_path, 'r', encoding='utf-8') as f:
                    guardrails_data = json.load(f)
                    knowledge_base["guardrails"] = guardrails_data.get("guardrails", {})
            
            self.knowledge_base = knowledge_base
            return self.knowledge_base
        except Exception as e:
            print(f"[ERROR] Failed to load knowledge base: {e}")
            return {}
    
    def build_graph(self) -> pathlib.Path:
        """
        Build heterogeneous graph from knowledge base.
        This is the PRIMARY index - all retrieval happens through graph traversal.
        """
        if not self.knowledge_base:
            self.load_knowledge_base()
        
        if not self.knowledge_base:
            print("[ERROR] No knowledge base loaded")
            return None
        
        print("[INFO] Building MiniRAG graph (PRIMARY index)...")
        
        # Add policy nodes
        policies = self.knowledge_base.get("policies", {})
        for policy_id, policy_data in tqdm(policies.items(), desc="Adding policies"):
            policy_node = f"policy::{policy_id}"
            self.graph.add_node(
                policy_node,
                type="policy",
                title=policy_data.get("title", ""),
                category=policy_data.get("category", ""),
                content=policy_data.get("content", {}),
                metadata={"id": policy_data.get("id", "")}
            )
        
        # Add entity nodes
        entities = self.knowledge_base.get("entities", {})
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                entity_node = f"entity::{entity_type}::{entity}"
                self.graph.add_node(
                    entity_node,
                    type="entity",
                    entity_type=entity_type,
                    name=entity
                )
        
        # Add relationships from knowledge base
        relationships = self.knowledge_base.get("relationships", {})
        
        # Policy connections
        policy_connections = relationships.get("policy_connections", [])
        for conn in policy_connections:
            from_node = f"policy::{conn['from']}"
            to_node = f"policy::{conn['to']}"
            if self.graph.has_node(from_node) and self.graph.has_node(to_node):
                self.graph.add_edge(
                    from_node,
                    to_node,
                    relation=conn.get("relation", "related_to"),
                    strength=conn.get("strength", 0.5)
                )
        
        # Entity connections
        entity_connections = relationships.get("entity_connections", [])
        for conn in entity_connections:
            from_node = self._resolve_entity_node(conn['from'])
            to_node = f"policy::{conn['to']}"
            if from_node and self.graph.has_node(to_node):
                self.graph.add_edge(
                    from_node,
                    to_node,
                    relation=conn.get("relation", "governed_by"),
                    strength=conn.get("strength", 0.5)
                )
        
        # Build content-based relationships (extract keywords and connect)
        self._build_content_relationships()
        
        # Build entity-policy connections from content
        self._build_entity_policy_connections()
        
        # Save graph
        GRAPH_DIR.mkdir(parents=True, exist_ok=True)
        graph_path = GRAPH_DIR / "ecommerce_minirag_graph.pkl"
        
        with open(graph_path, 'wb') as f:
            pickle.dump(self.graph, f)
        
        print(f"[INFO] MiniRAG graph built: {self.graph.number_of_nodes()} nodes, "
              f"{self.graph.number_of_edges()} edges")
        
        return graph_path
    
    def _resolve_entity_node(self, entity_name: str) -> str:
        """Resolve entity name to node identifier"""
        entities = self.knowledge_base.get("entities", {})
        for entity_type, entity_list in entities.items():
            if entity_name in entity_list:
                return f"entity::{entity_type}::{entity_name}"
        return None
    
    def _build_content_relationships(self):
        """Build relationships based on content similarity"""
        policy_nodes = [
            node for node, attrs in self.graph.nodes(data=True)
            if attrs.get("type") == "policy"
        ]
        
        # Extract keywords from policy content
        for i, node_a in enumerate(policy_nodes):
            content_a = self._extract_keywords(node_a)
            for node_b in policy_nodes[i+1:]:
                content_b = self._extract_keywords(node_b)
                similarity = self._calculate_similarity(content_a, content_b)
                if similarity > 0.3:  # Threshold for content similarity
                    self.graph.add_edge(
                        node_a,
                        node_b,
                        relation="content_similar",
                        strength=similarity
                    )
    
    def _extract_keywords(self, node: str) -> set:
        """Extract keywords from policy node"""
        attrs = self.graph.nodes[node]
        content = attrs.get("content", {})
        keywords = set()
        
        # Extract from title
        title = attrs.get("title", "").lower().split()
        keywords.update(title)
        
        # Extract from content (flatten nested dict)
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, str):
                    keywords.update(value.lower().split())
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            keywords.update(item.lower().split())
        
        return keywords
    
    def _calculate_similarity(self, set_a: set, set_b: set) -> float:
        """Calculate Jaccard similarity between keyword sets"""
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0
    
    def _build_entity_policy_connections(self):
        """Connect entities to policies based on content"""
        entity_nodes = [
            node for node, attrs in self.graph.nodes(data=True)
            if attrs.get("type") == "entity"
        ]
        
        policy_nodes = [
            node for node, attrs in self.graph.nodes(data=True)
            if attrs.get("type") == "policy"
        ]
        
        for entity_node in entity_nodes:
            entity_name = self.graph.nodes[entity_node].get("name", "").lower()
            for policy_node in policy_nodes:
                content = self._extract_keywords(policy_node)
                if entity_name in content or any(
                    entity_name in str(v).lower() for v in content
                ):
                    self.graph.add_edge(
                        entity_node,
                        policy_node,
                        relation="mentioned_in",
                        strength=0.6
                    )
    
    def get_graph(self) -> nx.MultiDiGraph:
        """Get the built graph"""
        return self.graph

