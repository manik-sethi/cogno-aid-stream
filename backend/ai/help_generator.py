import asyncio
import logging
from typing import Dict, List, Optional
import json

from .llm_client import LLMClient

logger = logging.getLogger(__name__)

class HelpGenerator:
    """Generates contextual help suggestions based on confusion levels and screen analysis."""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.help_history = []
        self.max_history = 20
        
        # Help templates for different subjects
        self.help_templates = {
            "mathematics": {
                "low_confusion": [
                    "You're doing well! Take your time with each step.",
                    "Consider double-checking your work so far.",
                    "Try writing out intermediate steps clearly."
                ],
                "medium_confusion": [
                    "Break this problem into smaller steps.",
                    "Review the relevant formulas or concepts.",
                    "Try working through a similar, simpler example first."
                ],
                "high_confusion": [
                    "Take a step back and identify what the problem is asking.",
                    "Look for patterns or keywords that indicate the approach needed.",
                    "Consider reviewing the underlying concepts before continuing."
                ]
            },
            "programming": {
                "low_confusion": [
                    "Good progress! Consider adding comments to clarify your logic.",
                    "Test your code incrementally as you build.",
                    "Think about edge cases for your solution."
                ],
                "medium_confusion": [
                    "Break down the problem into smaller functions.",
                    "Use print statements or debugger to trace execution.",
                    "Review the documentation for methods you're using."
                ],
                "high_confusion": [
                    "Start with pseudocode to plan your approach.",
                    "Look for similar examples or patterns online.",
                    "Consider asking for help with the specific concept you're stuck on."
                ]
            },
            "general": {
                "low_confusion": [
                    "You're on the right track! Keep going.",
                    "Take a moment to organize your thoughts.",
                    "Consider reviewing what you've learned so far."
                ],
                "medium_confusion": [
                    "Try explaining the problem to yourself out loud.",
                    "Look for connections to concepts you already know.",
                    "Take a short break and come back with fresh eyes."
                ],
                "high_confusion": [
                    "Don't worry - confusion is part of learning!",
                    "Try to identify exactly what's confusing you.",
                    "Consider seeking help from a teacher or peer."
                ]
            }
        }
    
    async def generate_help(self, screen_analysis: Dict, confusion_level: float, context: Dict = None) -> List[str]:
        """
        Generate contextual help suggestions based on screen analysis and confusion level.
        
        Args:
            screen_analysis: Analysis of user's screen content
            confusion_level: Current confusion level (0.0 to 1.0)
            context: Additional context information
            
        Returns:
            List of help suggestions
        """
        try:
            # Extract educational context
            educational_context = screen_analysis.get("educational_context", {})
            subject = educational_context.get("subject", "general")
            content = screen_analysis.get("general_analysis", {}).get("content", "")
            
            # Determine confusion category
            confusion_category = self._categorize_confusion(confusion_level)
            
            # Generate AI-powered suggestions
            ai_suggestions = await self._generate_ai_suggestions(
                content, subject, confusion_level, educational_context
            )
            
            # Get template-based suggestions as fallback
            template_suggestions = self._get_template_suggestions(subject, confusion_category)
            
            # Combine and rank suggestions
            all_suggestions = ai_suggestions + template_suggestions
            final_suggestions = await self._rank_and_filter_suggestions(
                all_suggestions, confusion_level, educational_context
            )
            
            # Store in history
            help_entry = {
                "timestamp": asyncio.get_event_loop().time(),
                "confusion_level": confusion_level,
                "subject": subject,
                "suggestions": final_suggestions,
                "context": educational_context
            }
            
            self.help_history.append(help_entry)
            if len(self.help_history) > self.max_history:
                self.help_history.pop(0)
            
            return final_suggestions[:3]  # Return top 3 suggestions
            
        except Exception as e:
            logger.error(f"Error generating help: {e}")
            return ["Take a moment to breathe and approach this step by step."]
    
    async def _generate_ai_suggestions(self, content: str, subject: str, confusion_level: float, 
                                     educational_context: Dict) -> List[str]:
        """Generate AI-powered help suggestions."""
        try:
            prompt = f"""
            You are an AI tutor helping a student who is experiencing confusion (level: {confusion_level:.2f}/1.0).
            
            Screen content analysis: {content}
            Subject: {subject}
            Educational context: {json.dumps(educational_context)}
            
            Generate 2-3 helpful, encouraging suggestions that:
            1. Don't give away the answer directly
            2. Help guide the student's thinking process
            3. Are appropriate for the confusion level
            4. Are specific to the content they're working on
            
            Format as a JSON array of strings.
            Keep suggestions concise (under 100 characters each).
            """
            
            response = await self.llm_client.analyze_text(prompt)
            
            # Parse AI response (simplified parsing for demo)
            suggestions = []
            if isinstance(response, dict) and "suggestions" in response:
                suggestions = response["suggestions"]
            elif isinstance(response, list):
                suggestions = response
            else:
                # Try to extract suggestions from text response
                response_text = str(response)
                if "break" in response_text.lower():
                    suggestions.append("Try breaking this into smaller, manageable steps.")
                if "concept" in response_text.lower():
                    suggestions.append("Review the underlying concepts before continuing.")
                if "example" in response_text.lower():
                    suggestions.append("Work through a simpler example first.")
            
            return suggestions[:2]  # Limit AI suggestions
            
        except Exception as e:
            logger.error(f"Error generating AI suggestions: {e}")
            return []
    
    def _get_template_suggestions(self, subject: str, confusion_category: str) -> List[str]:
        """Get template-based suggestions as fallback."""
        templates = self.help_templates.get(subject, self.help_templates["general"])
        return templates.get(confusion_category, templates["medium_confusion"])
    
    def _categorize_confusion(self, confusion_level: float) -> str:
        """Categorize confusion level into low, medium, high."""
        if confusion_level < 0.3:
            return "low_confusion"
        elif confusion_level < 0.7:
            return "medium_confusion"
        else:
            return "high_confusion"
    
    async def _rank_and_filter_suggestions(self, suggestions: List[str], confusion_level: float, 
                                         context: Dict) -> List[str]:
        """Rank and filter suggestions based on relevance and context."""
        try:
            # Remove duplicates while preserving order
            unique_suggestions = []
            seen = set()
            
            for suggestion in suggestions:
                if suggestion not in seen:
                    unique_suggestions.append(suggestion)
                    seen.add(suggestion)
            
            # Simple ranking based on confusion level and keywords
            ranked_suggestions = []
            
            for suggestion in unique_suggestions:
                score = 0
                suggestion_lower = suggestion.lower()
                
                # Boost suggestions based on confusion level
                if confusion_level > 0.7:  # High confusion
                    if any(word in suggestion_lower for word in ["break", "step", "simpler"]):
                        score += 2
                elif confusion_level < 0.3:  # Low confusion
                    if any(word in suggestion_lower for word in ["double-check", "test", "consider"]):
                        score += 2
                
                # Boost subject-specific suggestions
                subject = context.get("subject", "")
                if subject == "mathematics" and any(word in suggestion_lower for word in ["formula", "equation", "calculate"]):
                    score += 1
                elif subject == "programming" and any(word in suggestion_lower for word in ["debug", "code", "function"]):
                    score += 1
                
                ranked_suggestions.append((suggestion, score))
            
            # Sort by score (descending) and return suggestions only
            ranked_suggestions.sort(key=lambda x: x[1], reverse=True)
            return [suggestion for suggestion, score in ranked_suggestions]
            
        except Exception as e:
            logger.error(f"Error ranking suggestions: {e}")
            return suggestions
    
    def get_help_history(self, count: int = 5) -> List[Dict]:
        """Get recent help generation history."""
        return self.help_history[-count:] if self.help_history else []
    
    def get_help_statistics(self) -> Dict:
        """Get statistics about help generation."""
        if not self.help_history:
            return {}
        
        confusion_levels = [entry["confusion_level"] for entry in self.help_history]
        subjects = [entry["subject"] for entry in self.help_history]
        
        return {
            "total_help_sessions": len(self.help_history),
            "average_confusion_level": sum(confusion_levels) / len(confusion_levels),
            "max_confusion_level": max(confusion_levels),
            "subjects_helped": list(set(subjects)),
            "recent_activity": len([e for e in self.help_history 
                                  if asyncio.get_event_loop().time() - e["timestamp"] < 3600])  # Last hour
        }