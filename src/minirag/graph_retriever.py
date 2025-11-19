"""
MiniRAG Graph Retriever - True Graph-First Retrieval
This is the PRIMARY retrieval mechanism - graph traversal, not semantic search.
"""
import pickle
import networkx as nx
from typing import List, Dict, Any, Set
from pathlib import Path
from ..config import GRAPH_DIR, GRAPH_RETRIEVAL_TOP_K, GRAPH_TRAVERSAL_DEPTH

class MiniRAGRetriever:
    """
    True MiniRAG retriever - graph-first architecture.
    Retrieval happens through graph traversal, not semantic similarity.
    """
    
    def __init__(self):
        self.graph: nx.MultiDiGraph = None
        self._load_graph()
    
    def _load_graph(self):
        """Load the MiniRAG graph"""
        graph_path = GRAPH_DIR / "ecommerce_minirag_graph.pkl"
        try:
            if graph_path.exists():
                with open(graph_path, 'rb') as f:
                    self.graph = pickle.load(f)
                print(f"[INFO] MiniRAG graph loaded: {self.graph.number_of_nodes()} nodes")
            else:
                print("[WARNING] Graph not found. Please build graph first.")
                self.graph = nx.MultiDiGraph()
        except Exception as e:
            print(f"[ERROR] Failed to load graph: {e}")
            self.graph = nx.MultiDiGraph()
    
    def retrieve(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """
        PRIMARY retrieval method - graph traversal based.
        This is the core MiniRAG retrieval, not an enhancement.
        
        Args:
            query: User query
            k: Number of results (defaults to config value)
            
        Returns:
            List of retrieved documents with graph-based scores
        """
        if not self.graph or self.graph.number_of_nodes() == 0:
            return []
        
        k = k or GRAPH_RETRIEVAL_TOP_K
        
        # Step 1: Extract query entities/keywords
        query_entities = self._extract_query_entities(query)
        
        # Step 2: Find matching nodes in graph
        candidate_nodes = self._find_matching_nodes(query, query_entities)
        
        # Step 3: Graph traversal to find related nodes
        expanded_nodes = self._traverse_graph(candidate_nodes, depth=GRAPH_TRAVERSAL_DEPTH)
        
        # Step 4: Score and rank nodes
        scored_results = self._score_nodes(expanded_nodes, query, query_entities)
        
        # Step 5: Extract content and return top-k
        results = self._extract_content(scored_results, k)
        
        return results
    
    def _extract_query_entities(self, query: str) -> Set[str]:
        """Extract entities and keywords from query"""
        query_lower = query.lower()
        entities = set()
        
        # Extract known entity types from graph
        if self.graph:
            for node, attrs in self.graph.nodes(data=True):
                if attrs.get("type") == "entity":
                    entity_name = attrs.get("name", "").lower()
                    if entity_name in query_lower:
                        entities.add(entity_name)
        
        # Extract common e-commerce keywords
        keywords = [
            "return", "refund", "shipping", "delivery", "payment", "order",
            "policy", "tracking", "cancel", "exchange", "warranty", "support"
        ]
        for keyword in keywords:
            if keyword in query_lower:
                entities.add(keyword)
        
        return entities
    
    def _find_matching_nodes(self, query: str, entities: Set[str]) -> List[tuple]:
        """
        Find nodes that match the query - graph-based matching.
        This is the PRIMARY matching mechanism.
        """
        candidates = []
        query_lower = query.lower()
        
        # Search in policy nodes
        for node, attrs in self.graph.nodes(data=True):
            if attrs.get("type") == "policy":
                score = 0.0
                
                # Title match
                title = attrs.get("title", "").lower()
                if any(word in title for word in query_lower.split()):
                    score += 2.0
                
                # Category match
                category = attrs.get("category", "").lower()
                if category in query_lower:
                    score += 1.5
                
                # Entity match
                for entity in entities:
                    if entity in title or entity in category:
                        score += 1.0
                
                # Content keyword match
                content_keywords = self._extract_content_keywords(attrs.get("content", {}))
                matching_keywords = sum(1 for word in query_lower.split() if word in content_keywords)
                score += matching_keywords * 0.5
                
                if score > 0:
                    candidates.append((node, score))
        
        # Search in entity nodes
        for node, attrs in self.graph.nodes(data=True):
            if attrs.get("type") == "entity":
                entity_name = attrs.get("name", "").lower()
                if entity_name in query_lower or any(e in entity_name for e in entities):
                    candidates.append((node, 1.0))
        
        return candidates
    
    def _traverse_graph(self, seed_nodes: List[tuple], depth: int) -> Dict[str, float]:
        """
        Graph traversal to expand search - core MiniRAG mechanism.
        This is how we discover related information through graph structure.
        """
        expanded = {}
        visited = set()
        
        # Start with seed nodes
        for node, score in seed_nodes:
            expanded[node] = score
            visited.add(node)
        
        # BFS traversal
        current_level = [(node, score) for node, score in seed_nodes]
        
        for _ in range(depth):
            next_level = []
            for node, base_score in current_level:
                # Traverse outgoing edges
                for _, neighbor, edge_data in self.graph.out_edges(node, data=True):
                    if neighbor not in visited:
                        edge_strength = edge_data.get("strength", 0.5)
                        neighbor_score = base_score * edge_strength * 0.8  # Decay factor
                        
                        if neighbor not in expanded or expanded[neighbor] < neighbor_score:
                            expanded[neighbor] = neighbor_score
                            next_level.append((neighbor, neighbor_score))
                            visited.add(neighbor)
                
                # Traverse incoming edges (bidirectional exploration)
                for predecessor, _, edge_data in self.graph.in_edges(node, data=True):
                    if predecessor not in visited:
                        edge_strength = edge_data.get("strength", 0.5)
                        predecessor_score = base_score * edge_strength * 0.7
                        
                        if predecessor not in expanded or expanded[predecessor] < predecessor_score:
                            expanded[predecessor] = predecessor_score
                            next_level.append((predecessor, predecessor_score))
                            visited.add(predecessor)
            
            current_level = next_level
        
        return expanded
    
    def _score_nodes(self, nodes: Dict[str, float], query: str, entities: Set[str]) -> List[tuple]:
        """Score nodes based on relevance"""
        scored = []
        
        for node, graph_score in nodes.items():
            attrs = self.graph.nodes[node]
            node_type = attrs.get("type")
            
            # Adjust score based on node type
            if node_type == "policy":
                # Policies are primary results
                final_score = graph_score * 1.2
            elif node_type == "entity":
                # Entities are secondary
                final_score = graph_score * 0.8
            else:
                final_score = graph_score
            
            scored.append((node, final_score, attrs))
        
        # Sort by score
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def _extract_content(self, scored_nodes: List[tuple], k: int) -> List[Dict[str, Any]]:
        """Extract content from top-k nodes"""
        results = []
        
        for node, score, attrs in scored_nodes[:k * 2]:  # Get more for filtering
            if attrs.get("type") == "policy":
                result = {
                    "id": attrs.get("metadata", {}).get("id", node),
                    "type": "policy",
                    "title": attrs.get("title", ""),
                    "category": attrs.get("category", ""),
                    "content": attrs.get("content", {}),
                    "score": score,
                    "retrieval_method": "graph_traversal",
                    "node_id": node
                }
                results.append(result)
        
        # Return top-k
        return results[:k]
    
    def _extract_content_keywords(self, content: Any) -> Set[str]:
        """Extract keywords from content structure"""
        keywords = set()
        
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, str):
                    keywords.update(value.lower().split())
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            keywords.update(item.lower().split())
                elif isinstance(value, dict):
                    keywords.update(self._extract_content_keywords(value))
        elif isinstance(content, str):
            keywords.update(content.lower().split())
        
        return keywords

