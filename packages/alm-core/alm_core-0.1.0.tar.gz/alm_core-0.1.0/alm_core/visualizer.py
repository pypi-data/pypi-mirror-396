"""
Execution Visualizer - Visual Thinking & Content Mapping
Real-time visualization of agent thought process.
"""

import networkx as nx
from datetime import datetime
from typing import Optional, Dict, Any, List
import json


class ExecutionVisualizer:
    """
    Creates a real-time visual map of the agent's thought process.
    
    This is a core novelty of ALM: Transparency through visualization.
    Users can see HOW the agent is thinking, not just the output.
    """
    
    def __init__(self):
        """Initialize the execution graph."""
        self.graph = nx.DiGraph()
        self.step_counter = 0
        self.root_nodes: List[str] = []
    
    def add_step(
        self,
        parent_id: Optional[str],
        action_type: str,
        description: str,
        status: str = "pending",
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Add a node to the execution graph.
        
        Args:
            parent_id: ID of parent node (None for root nodes)
            action_type: Type of action (e.g., 'research', 'search', 'decision')
            description: Human-readable description
            status: Current status ('pending', 'in_progress', 'success', 'failed')
            metadata: Additional data to store
            
        Returns:
            Node ID for the created step
        """
        node_id = f"step_{self.step_counter}"
        self.step_counter += 1
        
        # Add node with attributes
        self.graph.add_node(
            node_id,
            label=description,
            type=action_type,
            status=status,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        # Create edge if there's a parent
        if parent_id:
            self.graph.add_edge(parent_id, node_id)
        else:
            # Track root nodes
            self.root_nodes.append(node_id)
        
        return node_id
    
    def update_status(
        self,
        node_id: str,
        status: str,
        result: Any = None,
        error: Optional[str] = None
    ):
        """
        Update the status of a node.
        
        Args:
            node_id: Node to update
            status: New status
            result: Result data
            error: Error message if failed
        """
        if node_id not in self.graph.nodes:
            raise ValueError(f"Node {node_id} not found in graph")
        
        self.graph.nodes[node_id]['status'] = status
        self.graph.nodes[node_id]['completed_at'] = datetime.now().isoformat()
        
        if result is not None:
            self.graph.nodes[node_id]['result'] = str(result)[:200]  # Truncate for display
        
        if error:
            self.graph.nodes[node_id]['error'] = error
    
    def export_graph(self, filename: str = "execution_map.png", format: str = "png"):
        """
        Render the current thought process as an image.
        
        Args:
            filename: Output file name
            format: Output format ('png', 'svg', 'json')
        """
        if format == "json":
            self._export_json(filename)
        else:
            self._export_image(filename, format)
    
    def _export_image(self, filename: str, format: str):
        """Export as image using matplotlib."""
        try:
            import matplotlib.pyplot as plt
            
            # Create layout
            pos = nx.spring_layout(self.graph, k=2, iterations=50)
            
            # Get node attributes
            labels = nx.get_node_attributes(self.graph, 'label')
            
            # Color nodes based on status
            color_map = {
                'pending': 'lightgray',
                'in_progress': 'lightyellow',
                'success': 'lightgreen',
                'failed': 'lightcoral'
            }
            
            colors = [
                color_map.get(self.graph.nodes[n].get('status', 'pending'), 'lightblue')
                for n in self.graph.nodes
            ]
            
            # Draw graph
            plt.figure(figsize=(16, 10))
            nx.draw(
                self.graph,
                pos,
                labels=labels,
                node_color=colors,
                node_size=3000,
                with_labels=True,
                font_size=8,
                font_weight='bold',
                arrows=True,
                edge_color='gray',
                width=2
            )
            
            # Add title
            plt.title("Agent Execution Graph", fontsize=16, fontweight='bold')
            
            # Save
            plt.tight_layout()
            plt.savefig(filename, format=format, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Visual map saved to {filename}")
            
        except ImportError:
            print("⚠️  matplotlib not installed. Install with: pip install matplotlib")
            print("Falling back to JSON export...")
            self._export_json(filename.replace('.png', '.json'))
    
    def _export_json(self, filename: str):
        """Export as JSON for programmatic analysis."""
        # Convert graph to JSON-serializable format
        data = {
            "nodes": [],
            "edges": []
        }
        
        for node_id in self.graph.nodes:
            node_data = self.graph.nodes[node_id].copy()
            node_data['id'] = node_id
            data['nodes'].append(node_data)
        
        for edge in self.graph.edges:
            data['edges'].append({
                "source": edge[0],
                "target": edge[1]
            })
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Execution graph saved to {filename}")
    
    def get_execution_path(self, node_id: str) -> List[str]:
        """
        Get the execution path from root to a specific node.
        
        Args:
            node_id: Target node
            
        Returns:
            List of node IDs from root to target
        """
        # Find which root this node belongs to
        for root in self.root_nodes:
            if nx.has_path(self.graph, root, node_id):
                return nx.shortest_path(self.graph, root, node_id)
        
        return [node_id]  # Node is a root itself
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the execution graph."""
        status_counts = {}
        for node in self.graph.nodes:
            status = self.graph.nodes[node].get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_steps": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "root_tasks": len(self.root_nodes),
            "status_breakdown": status_counts,
            "max_depth": max(
                [len(self.get_execution_path(n)) for n in self.graph.nodes],
                default=0
            )
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary of execution."""
        stats = self.get_stats()
        
        summary = f"""
Execution Summary:
------------------
Total Steps: {stats['total_steps']}
Root Tasks: {stats['root_tasks']}
Max Depth: {stats['max_depth']}

Status Breakdown:
"""
        for status, count in stats['status_breakdown'].items():
            summary += f"  {status}: {count}\n"
        
        return summary
    
    def clear(self):
        """Clear the execution graph."""
        self.graph.clear()
        self.step_counter = 0
        self.root_nodes.clear()
    
    def export_mermaid(self) -> str:
        """
        Export as Mermaid diagram syntax for documentation.
        
        Returns:
            Mermaid diagram code
        """
        lines = ["graph TD"]
        
        # Add nodes
        for node_id in self.graph.nodes:
            node = self.graph.nodes[node_id]
            label = node.get('label', 'Unknown')[:30]  # Truncate
            status = node.get('status', 'pending')
            
            # Style based on status
            style_suffix = ""
            if status == "success":
                style_suffix = ":::success"
            elif status == "failed":
                style_suffix = ":::failed"
            
            lines.append(f'    {node_id}["{label}"]{style_suffix}')
        
        # Add edges
        for edge in self.graph.edges:
            lines.append(f"    {edge[0]} --> {edge[1]}")
        
        # Add style definitions
        lines.extend([
            "",
            "classDef success fill:#90EE90",
            "classDef failed fill:#FFB6C1"
        ])
        
        return "\n".join(lines)
