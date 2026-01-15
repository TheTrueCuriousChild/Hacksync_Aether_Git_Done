"""
backend/agents/supportive_agent.py
Generates supportive arguments for each factor
"""
from typing import Dict, Any, Optional, List
from base import BaseAgent
import json

class SupportiveAgent(BaseAgent):
    """Advocates for positive aspects and strengths of each factor"""
    
    def __init__(self, llm_client, config: Dict[str, Any]):
        super().__init__("SupportiveAgent", llm_client, config)
        
    async def process(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate supportive arguments for a factor
        
        Args:
            input_data: {
                "factor": {
                    "id": str,
                    "statement": str,
                    "category": str,
                    "context": str
                },
                "canonical_text": str (original report for reference),
                "web_agent": WebAgent instance (optional),
                "opposing_rebuttals": list (optional - for reply mechanism)
            }
            
        Returns:
            {
                "factor_id": str,
                "arguments": [
                    {
                        "argument": str,
                        "evidence": str,
                        "strength": float,
                        "category": str
                    }
                ],
                "overall_position": str,
                "confidence": float,
                "web_evidence": dict (if web search used),
                "replies_to_opposing": list (if responding to rebuttals)
            }
        """
        factor = input_data.get("factor", {})
        canonical_text = input_data.get("canonical_text", "")
        web_agent = input_data.get("web_agent")
        opposing_rebuttals = input_data.get("opposing_rebuttals", [])
        
        self.log_execution("start_supportive_analysis", {"factor_id": factor.get("id")})
        
        # Use web search for additional evidence if available
        web_evidence = None
        if web_agent:
            try:
                web_evidence = await web_agent.search_for_evidence(factor, perspective="supportive")
                self.log_execution("web_search_used", {
                    "sources": len(web_evidence.get("sources", []))
                })
            except Exception as e:
                self.log_execution("web_search_failed", str(e))
        
        # Generate supportive arguments (with web context if available)
        arguments = await self._generate_supportive_arguments(
            factor, 
            canonical_text, 
            context,
            web_evidence
        )
        
        # Generate replies to opposing agent's rebuttals if any
        replies = []
        if opposing_rebuttals:
            replies = await self._generate_replies_to_opposing(opposing_rebuttals, factor, arguments)
        
        result = {
            "factor_id": factor.get("id"),
            "agent": self.name,
            "arguments": arguments,
            "overall_position": await self._generate_overall_position(factor, arguments),
            "confidence": self._calculate_confidence(arguments),
            "web_evidence": web_evidence,
            "replies_to_opposing": replies,
            "timestamp": self._get_timestamp()
        }
        
        self.log_execution("supportive_complete", {
            "num_arguments": len(arguments),
            "confidence": result["confidence"],
            "web_sources": len(web_evidence.get("sources", [])) if web_evidence else 0,
            "replies_generated": len(replies)
        })
        
        return result
    
    async def _generate_supportive_arguments(
        self, 
        factor: Dict[str, Any], 
        canonical_text: str,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate 3-5 supportive arguments using LLM"""
        
        # Build context from opposing arguments if available
        opposing_context = ""
        if context and "opposing_arguments" in context:
            opposing_context = f"""
Previous Opposing Arguments to Consider:
{self._format_opposing_arguments(context["opposing_arguments"])}
"""
        
        prompt = f"""You are a supportive advocate analyzing this factor from a report.

FACTOR TO SUPPORT:
{factor.get("statement")}

CONTEXT:
{factor.get("context", "N/A")}

ORIGINAL REPORT EXCERPT:
{canonical_text[:1500]}

{opposing_context}

Your task: Generate 3-5 strong supportive arguments that defend this factor's validity, effectiveness, or positive impact.

For each argument:
1. State the argument clearly
2. Provide specific evidence or reasoning
3. Assess its strength (1-10)
4. Categorize it (empirical, logical, contextual, outcomes-based)

Respond in JSON:
{{
  "arguments": [
    {{
      "argument": "clear supportive claim",
      "evidence": "specific evidence or reasoning",
      "strength": 8,
      "category": "empirical"
    }}
  ]
}}

JSON Response:"""

        system_prompt = """You are a skilled advocate who builds strong, evidence-based supportive cases. 
You identify strengths, positive outcomes, and valid justifications. You acknowledge context and constraints. 
You are thorough but honest, focusing on legitimate positive aspects."""

        response = await self._call_llm(prompt, system_prompt, temperature=0.6)
        
        try:
            data = json.loads(response)
            return data.get("arguments", [])
        except json.JSONDecodeError:
            return self._fallback_parse_arguments(response)
    
    async def _generate_overall_position(self, factor: Dict[str, Any], arguments: List[Dict[str, Any]]) -> str:
        """Synthesize overall supportive position"""
        args_summary = "\n".join([f"- {arg['argument']}" for arg in arguments[:3]])
        
        prompt = f"""Based on these supportive arguments for the factor "{factor.get('statement')}":

{args_summary}

Write a concise 2-3 sentence overall supportive position that synthesizes these arguments.

Position:"""

        response = await self._call_llm(prompt, temperature=0.5)
        return response.strip()
    
    def _calculate_confidence(self, arguments: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence based on argument strengths"""
        if not arguments:
            return 0.0
        avg_strength = sum(arg.get("strength", 5) for arg in arguments) / len(arguments)
        return round(avg_strength / 10, 2)
    
    def _format_opposing_arguments(self, opposing_args: List[Dict[str, Any]]) -> str:
        """Format opposing arguments for context"""
        return "\n".join([f"- {arg.get('argument', '')}" for arg in opposing_args[:3]])
    
    def _fallback_parse_arguments(self, text: str) -> List[Dict[str, Any]]:
        """Fallback parsing if JSON fails"""
        return [{
            "argument": "Supportive analysis generated",
            "evidence": text[:200],
            "strength": 6.0,
            "category": "general"
        }]
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    async def respond_to_challenge(self, challenge: Dict[str, Any]) -> Dict[str, Any]:
        """Respond to opposing agent's challenge"""
        prompt = f"""You previously argued: {challenge.get('original_argument')}

The opposing agent challenges with: {challenge.get('challenge')}

Provide a direct rebuttal that:
1. Addresses the challenge head-on
2. Reinforces your original position
3. Provides additional evidence if available

Rebuttal:"""

        system_prompt = "You are defending your supportive position. Be direct, evidence-based, and maintain intellectual honesty."
        
        rebuttal = await self._call_llm(prompt, system_prompt, temperature=0.6)
        
        return {
            "rebuttal": rebuttal.strip(),
            "challenge_id": challenge.get("id"),
            "agent": self.name
        }
 # ============================
# Direct execution entrypoint
# ============================

if __name__ == "__main__":
    import asyncio
    import sys
    import json

    async def main():
        """
        Run SupportiveAgent using JSON input from STDIN.
        This is the SAME execution path used in orchestration.
        """

        try:
            raw_input = sys.stdin.read().strip()
            if not raw_input:
                raise ValueError("No JSON input provided")

            input_data = json.loads(raw_input)

        except Exception as e:
            print(json.dumps({
                "error": "Invalid input",
                "details": str(e),
                "expected_format": {
                    "factor": {
                        "id": "string",
                        "statement": "string",
                        "category": "string",
                        "context": "string"
                    },
                    "canonical_text": "string"
                }
            }, indent=2))
            sys.exit(1)

        agent = SupportiveAgent(
            llm_client=None,
            config={
                "model": "openai/gpt-4o-mini"
            }
        )

        result = await agent.process(input_data)

        print(json.dumps(result, indent=2))

    asyncio.run(main())
