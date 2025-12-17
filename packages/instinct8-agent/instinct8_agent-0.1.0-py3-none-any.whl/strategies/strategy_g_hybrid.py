"""
Strategy G: Hybrid GraphRAG + Vector

This strategy combines knowledge graph-based retrieval with vector embeddings
for comprehensive context compression, inspired by the graphrag-rs branch.

Key Features:
- Knowledge graph for structured relationships (files, functions, dependencies)
- Vector store for semantic similarity search
- Weighted combination of both retrieval methods
- Entity extraction from code context

Algorithm:
1. Extract entities (files, functions, classes, variables) from turns
2. Build knowledge graph with relationships (imports, calls, modifies)
3. Build vector index for semantic search
4. On compression trigger:
   - Query both graph and vector stores
   - Combine results with configurable weights
   - Format as structured context
"""

import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .strategy_base import CompressionStrategy

# Add A-mem to path for SimpleEmbeddingRetriever
_amem_path = Path(__file__).parent.parent / "A-mem"
if str(_amem_path) not in sys.path:
    sys.path.insert(0, str(_amem_path))


@dataclass
class GraphNode:
    """A node in the coding knowledge graph."""

    id: str
    node_type: str  # "file", "function", "class", "variable", "concept"
    name: str
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """An edge in the coding knowledge graph."""

    source_id: str
    target_id: str
    edge_type: str  # "imports", "calls", "inherits", "modifies", "contains"
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CodingKnowledgeGraph:
    """
    Knowledge graph for coding context.

    Stores relationships between:
    - Files and their contents
    - Functions and their calls
    - Classes and inheritance
    - Variables and their modifications
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
        self.reverse_adjacency: Dict[str, List[str]] = defaultdict(list)

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def add_nodes(self, nodes: List[GraphNode]) -> None:
        """Add multiple nodes to the graph."""
        for node in nodes:
            self.add_node(node)

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)
        self.adjacency[edge.source_id].append(edge.target_id)
        self.reverse_adjacency[edge.target_id].append(edge.source_id)

    def add_edges(self, edges: List[GraphEdge]) -> None:
        """Add multiple edges to the graph."""
        for edge in edges:
            self.add_edge(edge)

    def get_neighbors(self, node_id: str, max_depth: int = 1) -> Set[str]:
        """Get all neighbors up to max_depth hops away."""
        visited = set()
        current_level = {node_id}

        for _ in range(max_depth):
            next_level = set()
            for nid in current_level:
                if nid not in visited:
                    visited.add(nid)
                    next_level.update(self.adjacency.get(nid, []))
                    next_level.update(self.reverse_adjacency.get(nid, []))
            current_level = next_level - visited

        return visited

    def retrieve_subgraph(
        self, query: str, max_depth: int = 2, max_nodes: int = 20
    ) -> str:
        """
        Retrieve a relevant subgraph based on a query.

        Uses simple keyword matching to find relevant nodes,
        then expands to connected neighbors.

        Args:
            query: Search query
            max_depth: How many hops to traverse
            max_nodes: Maximum nodes to return

        Returns:
            Formatted string representation of the subgraph
        """
        query_terms = set(query.lower().split())

        # Score nodes by relevance to query
        scored_nodes: List[Tuple[float, str]] = []
        for node_id, node in self.nodes.items():
            score = self._score_node(node, query_terms)
            if score > 0:
                scored_nodes.append((score, node_id))

        # Sort by score and get top nodes
        scored_nodes.sort(reverse=True)
        seed_nodes = [nid for _, nid in scored_nodes[:5]]

        # Expand to neighbors
        relevant_nodes = set()
        for seed in seed_nodes:
            relevant_nodes.update(self.get_neighbors(seed, max_depth))

        # Limit to max_nodes
        relevant_nodes = set(list(relevant_nodes)[:max_nodes])

        # Format subgraph
        return self._format_subgraph(relevant_nodes)

    def _score_node(self, node: GraphNode, query_terms: Set[str]) -> float:
        """Score a node's relevance to query terms."""
        score = 0.0

        # Check name
        name_terms = set(node.name.lower().split("_"))
        name_terms.update(node.name.lower().split())
        score += len(query_terms & name_terms) * 2.0

        # Check content if available
        if node.content:
            content_terms = set(node.content.lower().split())
            score += len(query_terms & content_terms) * 0.5

        # Boost certain node types
        if node.node_type in ("function", "class"):
            score *= 1.2

        return score

    def _format_subgraph(self, node_ids: Set[str]) -> str:
        """Format a subgraph as a string."""
        if not node_ids:
            return "(No relevant graph context)"

        parts = []

        # Group by node type
        by_type: Dict[str, List[GraphNode]] = defaultdict(list)
        for nid in node_ids:
            if nid in self.nodes:
                node = self.nodes[nid]
                by_type[node.node_type].append(node)

        # Format each type
        for node_type, nodes in sorted(by_type.items()):
            parts.append(f"## {node_type.upper()}S:")
            for node in nodes:
                parts.append(f"  - {node.name}")
                if node.content:
                    # Truncate content
                    content = node.content[:100]
                    if len(node.content) > 100:
                        content += "..."
                    parts.append(f"    {content}")

        # Add relevant edges
        parts.append("\n## RELATIONSHIPS:")
        for edge in self.edges:
            if edge.source_id in node_ids and edge.target_id in node_ids:
                source = self.nodes.get(edge.source_id)
                target = self.nodes.get(edge.target_id)
                if source and target:
                    parts.append(
                        f"  - {source.name} --[{edge.edge_type}]--> {target.name}"
                    )

        return "\n".join(parts)

    def clear(self) -> None:
        """Clear the graph."""
        self.nodes.clear()
        self.edges.clear()
        self.adjacency.clear()
        self.reverse_adjacency.clear()


class StrategyG_Hybrid(CompressionStrategy):
    """
    Hybrid GraphRAG + Vector compression strategy.

    Combines:
    - Knowledge graph for structured code relationships
    - Vector embeddings for semantic similarity
    - Configurable weighting between the two
    """

    def __init__(
        self,
        graph_weight: float = 0.4,
        vector_weight: float = 0.6,
        model_name: str = "all-MiniLM-L6-v2",
        retrieve_k: int = 10,
    ):
        """
        Initialize the hybrid strategy.

        Args:
            graph_weight: Weight for graph-based retrieval (0-1)
            vector_weight: Weight for vector-based retrieval (0-1)
            model_name: SentenceTransformer model for embeddings
            retrieve_k: Number of items to retrieve from each method
        """
        self._graph_weight = graph_weight
        self._vector_weight = vector_weight
        self._model_name = model_name
        self._retrieve_k = retrieve_k

        self._knowledge_graph = CodingKnowledgeGraph()
        self._vector_store = None
        self._documents: List[str] = []

        self._original_goal: Optional[str] = None
        self._constraints: List[str] = []

        self._initialize_vector_store()

    def _initialize_vector_store(self) -> None:
        """Initialize the vector store."""
        try:
            from memory_layer import SimpleEmbeddingRetriever

            self._vector_store = SimpleEmbeddingRetriever(self._model_name)
        except ImportError:
            self.log("Warning: Could not import SimpleEmbeddingRetriever")
            self._vector_store = None

    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        """
        Initialize with goal and constraints.

        Adds goal and constraints to both graph and vector stores.

        Args:
            original_goal: The task's original goal statement
            constraints: List of hard constraints
        """
        self._original_goal = original_goal
        self._constraints = constraints

        # Add goal to graph as concept node
        goal_node = GraphNode(
            id="goal_main",
            node_type="concept",
            name="Primary Goal",
            content=original_goal,
            metadata={"protected": True},
        )
        self._knowledge_graph.add_node(goal_node)

        # Add constraints to graph
        for i, constraint in enumerate(constraints):
            constraint_node = GraphNode(
                id=f"constraint_{i}",
                node_type="concept",
                name=f"Constraint {i+1}",
                content=constraint,
                metadata={"protected": True},
            )
            self._knowledge_graph.add_node(constraint_node)
            self._knowledge_graph.add_edge(
                GraphEdge(
                    source_id="goal_main",
                    target_id=f"constraint_{i}",
                    edge_type="requires",
                )
            )

        # Add to vector store
        if self._vector_store:
            self._documents.append(f"GOAL: {original_goal}")
            for constraint in constraints:
                self._documents.append(f"CONSTRAINT: {constraint}")
            self._vector_store.add_documents(self._documents)

        self.log(f"Initialized with goal: {original_goal}")
        self.log(f"Added {len(constraints)} constraints")

    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """
        Update the goal with tracking.

        Args:
            new_goal: The updated goal statement
            rationale: Why the goal changed
        """
        # Add new goal node linked to old
        new_goal_node = GraphNode(
            id="goal_updated",
            node_type="concept",
            name="Updated Goal",
            content=new_goal,
            metadata={"rationale": rationale},
        )
        self._knowledge_graph.add_node(new_goal_node)
        self._knowledge_graph.add_edge(
            GraphEdge(
                source_id="goal_main",
                target_id="goal_updated",
                edge_type="evolved_to",
            )
        )

        # Update vector store
        if self._vector_store:
            doc = f"GOAL UPDATE: {new_goal}"
            if rationale:
                doc += f" (Reason: {rationale})"
            self._documents.append(doc)
            self._vector_store.add_documents([doc])

        self.log(f"Goal updated: {new_goal}")

    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Compress context using hybrid retrieval.

        Steps:
        1. Extract entities and relationships from turns
        2. Build graph and vector representations
        3. Generate query from current context
        4. Retrieve from both sources
        5. Combine and format results

        Args:
            context: List of conversation turns
            trigger_point: Which turn to compress up to

        Returns:
            Compressed context string
        """
        self.log(f"Compressing {len(context)} turns up to point {trigger_point}")

        to_compress = context[:trigger_point]

        if not to_compress:
            return self._format_empty_context()

        # Process each turn
        for turn in to_compress:
            self._process_turn(turn)

        # Generate query
        query = self._generate_query(to_compress)

        # Get graph context
        graph_context = self._knowledge_graph.retrieve_subgraph(
            query, max_depth=2, max_nodes=self._retrieve_k
        )

        # Get vector context
        vector_context = self._get_vector_context(query)

        # Synthesize results
        compressed = self._synthesize(graph_context, vector_context)

        original_chars = sum(len(str(t)) for t in to_compress)
        compressed_chars = len(compressed)
        self.log(f"Compressed {original_chars} chars -> {compressed_chars} chars")

        return compressed

    def name(self) -> str:
        return "Strategy G - Hybrid GraphRAG"

    def _process_turn(self, turn: Dict[str, Any]) -> None:
        """Process a turn to extract entities and relationships."""
        content = turn.get("content", "")
        turn_id = turn.get("id", "unknown")

        # Extract entities
        entities = self._extract_entities(content, turn_id)
        self._knowledge_graph.add_nodes(entities)

        # Extract relationships
        relationships = self._extract_relationships(content, entities)
        self._knowledge_graph.add_edges(relationships)

        # Add to vector store
        if self._vector_store:
            doc = self._format_turn_for_vector(turn)
            self._documents.append(doc)
            self._vector_store.add_documents([doc])

    def _extract_entities(
        self, content: str, turn_id: str
    ) -> List[GraphNode]:
        """Extract entities from content."""
        entities = []

        # Extract file paths
        file_patterns = [
            r'(?:file|path)[:\s]+["\']?([^\s"\']+\.[a-z]+)["\']?',
            r'([a-zA-Z_][a-zA-Z0-9_/]*\.(?:py|js|ts|rs|go|java))',
        ]
        for pattern in file_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                file_path = match.group(1)
                entities.append(
                    GraphNode(
                        id=f"file_{file_path}_{turn_id}",
                        node_type="file",
                        name=file_path,
                    )
                )

        # Extract function definitions/calls
        func_patterns = [
            r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'fn\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        ]
        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                entities.append(
                    GraphNode(
                        id=f"func_{func_name}_{turn_id}",
                        node_type="function",
                        name=func_name,
                    )
                )

        # Extract class definitions
        class_patterns = [
            r'class\s+([A-Z][a-zA-Z0-9_]*)',
            r'struct\s+([A-Z][a-zA-Z0-9_]*)',
        ]
        for pattern in class_patterns:
            for match in re.finditer(pattern, content):
                class_name = match.group(1)
                entities.append(
                    GraphNode(
                        id=f"class_{class_name}_{turn_id}",
                        node_type="class",
                        name=class_name,
                    )
                )

        # Extract imports/dependencies
        import_patterns = [
            r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
            r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
            r'require\(["\']([^"\']+)["\']\)',
        ]
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                module_name = match.group(1)
                entities.append(
                    GraphNode(
                        id=f"module_{module_name}_{turn_id}",
                        node_type="module",
                        name=module_name,
                    )
                )

        return entities

    def _extract_relationships(
        self, content: str, entities: List[GraphNode]
    ) -> List[GraphEdge]:
        """Extract relationships between entities."""
        edges = []

        # Group entities by type
        by_type: Dict[str, List[GraphNode]] = defaultdict(list)
        for entity in entities:
            by_type[entity.node_type].append(entity)

        # Connect modules to files (imports relationship)
        files = by_type.get("file", [])
        modules = by_type.get("module", [])
        for file_node in files:
            for module_node in modules:
                edges.append(
                    GraphEdge(
                        source_id=file_node.id,
                        target_id=module_node.id,
                        edge_type="imports",
                    )
                )

        # Connect functions to files (contains relationship)
        functions = by_type.get("function", [])
        for file_node in files:
            for func_node in functions:
                edges.append(
                    GraphEdge(
                        source_id=file_node.id,
                        target_id=func_node.id,
                        edge_type="contains",
                    )
                )

        # Connect classes to files
        classes = by_type.get("class", [])
        for file_node in files:
            for class_node in classes:
                edges.append(
                    GraphEdge(
                        source_id=file_node.id,
                        target_id=class_node.id,
                        edge_type="contains",
                    )
                )

        return edges

    def _format_turn_for_vector(self, turn: Dict[str, Any]) -> str:
        """Format a turn for vector storage."""
        role = turn.get("role", "unknown")
        content = turn.get("content", "")
        return f"[{role}] {content}"

    def _generate_query(self, turns: List[Dict[str, Any]]) -> str:
        """Generate a retrieval query from turns."""
        # Use last few turns
        recent = turns[-3:] if len(turns) > 3 else turns

        parts = []
        if self._original_goal:
            parts.append(self._original_goal)

        for turn in recent:
            content = turn.get("content", "")[:150]
            parts.append(content)

        return " ".join(parts)

    def _get_vector_context(self, query: str) -> str:
        """Get relevant context from vector store."""
        if not self._vector_store or not self._documents:
            return "(No vector context)"

        try:
            indices = self._vector_store.search(query, k=self._retrieve_k)
            relevant_docs = [
                self._documents[i] for i in indices if i < len(self._documents)
            ]
            return "\n".join(relevant_docs)
        except Exception as e:
            self.log(f"Vector retrieval failed: {e}")
            return "(Vector retrieval failed)"

    def _synthesize(self, graph_context: str, vector_context: str) -> str:
        """Synthesize graph and vector contexts into final output."""
        parts = []

        # Always include goal and constraints first
        if self._original_goal:
            parts.append("=== CURRENT GOAL ===")
            parts.append(self._original_goal)
            parts.append("")

        if self._constraints:
            parts.append("=== CONSTRAINTS ===")
            for i, c in enumerate(self._constraints, 1):
                parts.append(f"{i}. {c}")
            parts.append("")

        # Add graph context (weighted)
        if self._graph_weight > 0 and graph_context:
            parts.append(f"=== CODE STRUCTURE (weight: {self._graph_weight}) ===")
            parts.append(graph_context)
            parts.append("")

        # Add vector context (weighted)
        if self._vector_weight > 0 and vector_context:
            parts.append(f"=== SEMANTIC CONTEXT (weight: {self._vector_weight}) ===")
            parts.append(vector_context)

        return "\n".join(parts)

    def _format_empty_context(self) -> str:
        """Return context when there's nothing to compress."""
        parts = []

        if self._original_goal:
            parts.append(f"Goal: {self._original_goal}")

        if self._constraints:
            parts.append(f"Constraints: {', '.join(self._constraints)}")

        parts.append("(No previous conversation)")

        return "\n".join(parts)

    def reset(self) -> None:
        """Reset for a new evaluation."""
        self._knowledge_graph.clear()
        self._initialize_vector_store()
        self._documents = []


# Convenience function
def create_hybrid_strategy(
    graph_weight: float = 0.4,
    vector_weight: float = 0.6,
) -> StrategyG_Hybrid:
    """Create a hybrid GraphRAG + Vector strategy."""
    return StrategyG_Hybrid(
        graph_weight=graph_weight,
        vector_weight=vector_weight,
    )
