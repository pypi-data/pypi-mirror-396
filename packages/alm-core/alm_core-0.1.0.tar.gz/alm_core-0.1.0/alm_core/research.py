"""
Deep Research Engine - Recursive Knowledge Acquisition
Time-based recursive research with knowledge graph building.
"""

import time
from typing import Dict, Any, List, Set, Optional
from datetime import datetime

from .controller import ALMController
from .visualizer import ExecutionVisualizer


class DeepResearcher:
    """
    Implements recursive deep research with saturation detection.
    
    This is a core capability of ALM: The agent doesn't just answer,
    it researches deeply until it has comprehensive understanding.
    """
    
    def __init__(
        self,
        controller: ALMController,
        visualizer: ExecutionVisualizer
    ):
        """
        Initialize the research engine.
        
        Args:
            controller: ALM controller for task execution
            visualizer: Execution visualizer for tracking progress
        """
        self.controller = controller
        self.visualizer = visualizer
        self.knowledge_graph: Dict[str, Any] = {}
        self.research_history: List[Dict[str, Any]] = []
    
    def conduct_research(
        self,
        topic: str,
        duration_minutes: int = 5,
        max_depth: int = 3,
        sources_per_topic: int = 3
    ) -> Dict[str, Any]:
        """
        Perform recursive research for a fixed time window.
        
        Args:
            topic: Main research topic
            duration_minutes: How long to research
            max_depth: Maximum recursion depth
            sources_per_topic: How many sources to gather per subtopic
            
        Returns:
            Knowledge graph with findings
        """
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Create root node in visualization
        root_node = self.visualizer.add_step(
            None,
            "research_root",
            f"Deep Research: {topic}",
            status="in_progress"
        )
        
        # Initialize search queue with main topic
        search_queue: List[Dict[str, Any]] = [{
            "topic": topic,
            "depth": 0,
            "parent_node": root_node
        }]
        
        visited_topics: Set[str] = set()
        findings_count = 0
        
        # Research loop
        while time.time() < end_time and search_queue:
            current = search_queue.pop(0)
            current_topic = current["topic"]
            current_depth = current["depth"]
            parent_node = current["parent_node"]
            
            # Skip if already researched or too deep
            if current_topic.lower() in visited_topics or current_depth >= max_depth:
                continue
            
            # Mark as visited
            visited_topics.add(current_topic.lower())
            
            # Visualize this research step
            step_id = self.visualizer.add_step(
                parent_node,
                "search",
                f"Researching: {current_topic}",
                status="in_progress",
                metadata={"depth": current_depth}
            )
            
            # Execute search
            try:
                findings = self._search_topic(current_topic, sources_per_topic)
                findings_count += len(findings)
                
                # Store in knowledge graph
                self.knowledge_graph[current_topic] = {
                    "findings": findings,
                    "depth": current_depth,
                    "timestamp": datetime.now().isoformat(),
                    "source_count": len(findings)
                }
                
                # Update visualization
                self.visualizer.update_status(
                    step_id,
                    "success",
                    result=f"Found {len(findings)} sources"
                )
                
                # Identify subtopics to explore
                if current_depth < max_depth - 1:
                    subtopics = self._identify_subtopics(current_topic, findings)
                    
                    # Add subtopics to queue
                    for subtopic in subtopics[:3]:  # Limit branching
                        search_queue.append({
                            "topic": subtopic,
                            "depth": current_depth + 1,
                            "parent_node": step_id
                        })
                
            except Exception as e:
                self.visualizer.update_status(
                    step_id,
                    "failed",
                    error=str(e)
                )
                continue
        
        # Finalize research
        research_duration = time.time() - start_time
        
        # Update root node
        self.visualizer.update_status(
            root_node,
            "success",
            result=f"Researched {len(visited_topics)} topics, {findings_count} sources"
        )
        
        # Export visualization
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '_')).strip()
        self.visualizer.export_graph(f"research_map_{safe_topic}.png")
        
        # Generate summary
        summary = self._generate_research_summary(topic)
        
        # Store research session
        session = {
            "topic": topic,
            "duration_seconds": research_duration,
            "topics_explored": len(visited_topics),
            "total_sources": findings_count,
            "knowledge_graph": self.knowledge_graph,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
        self.research_history.append(session)
        
        return session
    
    def _search_topic(self, topic: str, max_sources: int) -> List[Dict[str, Any]]:
        """
        Search for information about a topic.
        
        Args:
            topic: Topic to search
            max_sources: Maximum number of sources to return
            
        Returns:
            List of findings
        """
        # Use controller to execute search
        # In a real implementation, this would use browser tool or API
        search_query = f"Find detailed information about {topic}"
        
        # Simulate search results (in production, use actual search)
        # The controller would use browser or API tools here
        result = self.controller.execute_task(search_query)
        
        # Parse results (simplified for demonstration)
        findings = [{
            "content": result,
            "source": "search_engine",
            "timestamp": datetime.now().isoformat(),
            "relevance_score": 1.0
        }]
        
        return findings[:max_sources]
    
    def _identify_subtopics(
        self,
        parent_topic: str,
        findings: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Use LLM to identify relevant subtopics from findings.
        
        Args:
            parent_topic: The topic that was researched
            findings: Research findings
            
        Returns:
            List of subtopic strings
        """
        # Combine findings into context
        context_text = "\n\n".join([f["content"][:500] for f in findings])
        
        # Ask LLM for subtopics
        prompt = f"""Based on this research about "{parent_topic}":

{context_text}

What are 3 important related subtopics that would deepen understanding?
Respond with a JSON array of strings, e.g., ["subtopic1", "subtopic2", "subtopic3"]"""
        
        try:
            response = self.controller.llm.generate_structured(
                messages=[{"role": "user", "content": prompt}],
                schema={
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 3
                }
            )
            
            # Handle both array and object responses
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and "subtopics" in response:
                return response["subtopics"]
            else:
                return []
                
        except Exception as e:
            print(f"⚠️  Failed to identify subtopics: {e}")
            return []
    
    def _generate_research_summary(self, main_topic: str) -> str:
        """
        Generate a comprehensive summary of research findings.
        
        Args:
            main_topic: The main research topic
            
        Returns:
            Summary text
        """
        # Collect all findings
        all_findings = []
        for topic, data in self.knowledge_graph.items():
            all_findings.extend(data["findings"])
        
        # Build context for summary
        context_text = "\n\n".join([
            f"Topic: {topic}\nFindings: {data['findings'][0]['content'][:300]}..."
            for topic, data in self.knowledge_graph.items()
        ])
        
        # Ask LLM to synthesize
        prompt = f"""Synthesize this research on "{main_topic}" into a comprehensive summary:

{context_text}

Provide:
1. Key findings
2. Main themes
3. Important connections
4. Knowledge gaps (if any)"""
        
        try:
            summary = self.controller.llm.generate(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a research synthesizer. Create clear, structured summaries."
            )
            return summary
        except Exception as e:
            return f"Summary generation failed: {e}"
    
    def get_knowledge_on(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve knowledge about a specific topic.
        
        Args:
            topic: Topic to retrieve
            
        Returns:
            Knowledge entry or None
        """
        return self.knowledge_graph.get(topic)
    
    def export_knowledge_graph(self, filename: str = "knowledge_graph.json"):
        """
        Export the knowledge graph to a file.
        
        Args:
            filename: Output filename
        """
        import json
        
        with open(filename, 'w') as f:
            json.dump(self.knowledge_graph, f, indent=2)
        
        print(f"✅ Knowledge graph saved to {filename}")
    
    def get_research_stats(self) -> Dict[str, Any]:
        """Get statistics about research sessions."""
        if not self.research_history:
            return {"total_sessions": 0}
        
        return {
            "total_sessions": len(self.research_history),
            "total_topics_explored": sum(s["topics_explored"] for s in self.research_history),
            "total_sources_gathered": sum(s["total_sources"] for s in self.research_history),
            "average_duration": sum(s["duration_seconds"] for s in self.research_history) / len(self.research_history),
            "recent_topics": [s["topic"] for s in self.research_history[-5:]]
        }
