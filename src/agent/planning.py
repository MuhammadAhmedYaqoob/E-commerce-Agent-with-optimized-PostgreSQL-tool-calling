"""
Planning and Reasoning Module for Agentic System
Explicit planning logic with scratchpad for complex reasoning
"""
from typing import Dict, Any, List
from datetime import datetime


class PlanningScratchpad:
    """
    Scratchpad for agent reasoning and planning.
    Tracks reasoning steps, decisions, and uncertainty.
    """
    
    def __init__(self):
        self.reasoning_steps: List[Dict[str, Any]] = []
        self.decisions: List[Dict[str, Any]] = []
        self.uncertainty_levels: Dict[str, float] = {}
        self.alternative_plans: List[Dict[str, Any]] = []
    
    def add_reasoning_step(self, step: str, reasoning: str, confidence: float = 1.0):
        """Add a reasoning step to scratchpad"""
        self.reasoning_steps.append({
            "step": step,
            "reasoning": reasoning,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_decision(self, decision: str, rationale: str, alternatives: List[str] = None):
        """Record a decision with rationale"""
        self.decisions.append({
            "decision": decision,
            "rationale": rationale,
            "alternatives": alternatives or [],
            "timestamp": datetime.now().isoformat()
        })
    
    def set_uncertainty(self, aspect: str, level: float):
        """
        Set uncertainty level for an aspect (0.0 = certain, 1.0 = very uncertain)
        
        Args:
            aspect: Aspect of uncertainty (e.g., "tool_selection", "query_understanding")
            level: Uncertainty level (0.0-1.0)
        """
        self.uncertainty_levels[aspect] = level
    
    def add_alternative_plan(self, plan: Dict[str, Any], reason: str):
        """Add an alternative plan that was considered"""
        self.alternative_plans.append({
            "plan": plan,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_reasoning_chain(self) -> str:
        """Get formatted reasoning chain"""
        chain = []
        for i, step in enumerate(self.reasoning_steps, 1):
            chain.append(f"Step {i}: {step['step']}")
            chain.append(f"  Reasoning: {step['reasoning']}")
            chain.append(f"  Confidence: {step['confidence']:.2f}")
        return "\n".join(chain)
    
    def get_uncertainty_summary(self) -> Dict[str, float]:
        """Get summary of uncertainty levels"""
        return self.uncertainty_levels.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scratchpad to dictionary"""
        return {
            "reasoning_steps": self.reasoning_steps,
            "decisions": self.decisions,
            "uncertainty_levels": self.uncertainty_levels,
            "alternative_plans": self.alternative_plans
        }


class PlanningModule:
    """
    Planning module for autonomous decision-making.
    Handles uncertainty and generates action plans.
    """
    
    def __init__(self):
        self.scratchpad = PlanningScratchpad()
    
    def plan_action_sequence(
        self,
        query: str,
        context: List[Dict[str, Any]],
        available_tools: List[str],
        previous_state: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Plan a sequence of actions to answer the query.
        
        Args:
            query: User query
            context: Retrieved context
            available_tools: Available tools
            previous_state: Previous conversation state
            
        Returns:
            Action plan with steps and uncertainty
        """
        # Analyze query complexity
        complexity = self._assess_complexity(query, context)
        
        # Assess uncertainty
        uncertainty = self._assess_uncertainty(query, context, previous_state)
        self.scratchpad.set_uncertainty("query_understanding", uncertainty)
        
        # Generate action plan
        plan = self._generate_plan(query, context, available_tools, complexity, uncertainty)
        
        # Record planning decision
        self.scratchpad.add_decision(
            decision=f"Execute plan: {plan['primary_action']}",
            rationale=f"Complexity: {complexity}, Uncertainty: {uncertainty:.2f}",
            alternatives=[alt["action"] for alt in plan.get("alternatives", [])]
        )
        
        return plan
    
    def _assess_complexity(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Assess query complexity"""
        # Simple heuristics for complexity
        if any(word in query.lower() for word in ["and", "also", "then", "first", "after"]):
            return "high"
        elif len(context) > 3:
            return "medium"
        else:
            return "low"
    
    def _assess_uncertainty(
        self,
        query: str,
        context: List[Dict[str, Any]],
        previous_state: Dict[str, Any] = None
    ) -> float:
        """
        Assess uncertainty level (0.0 = certain, 1.0 = very uncertain)
        
        Args:
            query: User query
            context: Retrieved context
            previous_state: Previous state
            
        Returns:
            Uncertainty level (0.0-1.0)
        """
        uncertainty = 0.0
        
        # No context = high uncertainty
        if not context:
            uncertainty += 0.4
        
        # Ambiguous query = uncertainty
        ambiguous_words = ["maybe", "perhaps", "might", "could", "possibly"]
        if any(word in query.lower() for word in ambiguous_words):
            uncertainty += 0.3
        
        # Missing previous context = uncertainty
        if previous_state and not previous_state.get("retrieved_context"):
            uncertainty += 0.2
        
        # Multiple possible tools = uncertainty
        if len(context) > 5:
            uncertainty += 0.1
        
        return min(uncertainty, 1.0)
    
    def _generate_plan(
        self,
        query: str,
        context: List[Dict[str, Any]],
        available_tools: List[str],
        complexity: str,
        uncertainty: float
    ) -> Dict[str, Any]:
        """Generate action plan"""
        
        # Determine primary action
        if "order" in query.lower() and "status" in query.lower():
            primary_action = "get_order"
        elif "return" in query.lower() or "refund" in query.lower():
            primary_action = "retrieve_policy"
        elif "verify" in query.lower() or "2fa" in query.lower():
            primary_action = "verify_2fa"
        elif "notify" in query.lower() or "send" in query.lower():
            primary_action = "send_notification"
        else:
            primary_action = "retrieve_policy"
        
        plan = {
            "primary_action": primary_action,
            "complexity": complexity,
            "uncertainty": uncertainty,
            "steps": [
                {"action": "retrieve_context", "tool": "MiniRAG"},
                {"action": primary_action, "tool": primary_action}
            ],
            "alternatives": []
        }
        
        # Add alternatives if uncertainty is high
        if uncertainty > 0.5:
            plan["alternatives"].append({
                "action": "retrieve_policy",
                "reason": "High uncertainty, retrieve more context"
            })
        
        return plan
    
    def update_plan_based_on_results(
        self,
        plan: Dict[str, Any],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update plan based on intermediate results"""
        # If primary action failed, try alternatives
        if not results.get("success", True):
            if plan.get("alternatives"):
                plan["primary_action"] = plan["alternatives"][0]["action"]
                self.scratchpad.add_reasoning_step(
                    step="Plan adjustment",
                    reasoning=f"Primary action failed, switching to alternative: {plan['primary_action']}",
                    confidence=0.7
                )
        
        return plan
    
    def get_scratchpad(self) -> PlanningScratchpad:
        """Get the scratchpad"""
        return self.scratchpad

