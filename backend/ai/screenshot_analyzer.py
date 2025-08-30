import asyncio
import logging
import base64
import tempfile
import os
from typing import Dict, List, Optional
from PIL import ImageGrab, Image
import io

from .llm_client import LLMClient

logger = logging.getLogger(__name__)

class ScreenshotAnalyzer:
    """Handles screen capture and AI analysis for contextual help generation."""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.screenshot_history = []
        self.max_history = 10
        
    async def capture_screen(self) -> str:
        """
        Capture a screenshot of the user's screen.
        
        Returns:
            Path to the saved screenshot file
        """
        try:
            # Create temporary file for screenshot
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            screenshot_path = temp_file.name
            temp_file.close()
            
            # Capture screenshot using PIL
            screenshot = ImageGrab.grab()
            
            # Resize if too large (for faster processing)
            max_size = (1920, 1080)
            if screenshot.size[0] > max_size[0] or screenshot.size[1] > max_size[1]:
                screenshot.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save screenshot
            screenshot.save(screenshot_path, 'PNG', optimize=True)
            
            logger.info(f"Screenshot captured: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return ""
    
    async def analyze_screenshot(self, screenshot_path: str) -> Dict:
        """
        Analyze screenshot using computer vision and LLM to understand context.
        
        Args:
            screenshot_path: Path to the screenshot file
            
        Returns:
            Analysis results including detected content and context
        """
        try:
            if not screenshot_path or not os.path.exists(screenshot_path):
                return {"error": "Screenshot not found"}
            
            # Convert screenshot to base64 for LLM analysis
            screenshot_b64 = await self._encode_image_to_base64(screenshot_path)
            
            # Analyze with LLM
            analysis = await self.llm_client.analyze_image(screenshot_b64)
            
            # Extract specific educational content
            educational_context = await self._extract_educational_content(analysis)
            
            # Store in history
            analysis_result = {
                "timestamp": asyncio.get_event_loop().time(),
                "screenshot_path": screenshot_path,
                "general_analysis": analysis,
                "educational_context": educational_context,
                "detected_elements": await self._detect_ui_elements(analysis)
            }
            
            self.screenshot_history.append(analysis_result)
            if len(self.screenshot_history) > self.max_history:
                # Clean up old screenshot
                old_analysis = self.screenshot_history.pop(0)
                await self._cleanup_screenshot(old_analysis.get("screenshot_path"))
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def _encode_image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 for LLM processing."""
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_string = base64.b64encode(image_data).decode('utf-8')
                return base64_string
        except Exception as e:
            logger.error(f"Error encoding image to base64: {e}")
            return ""
    
    async def _extract_educational_content(self, analysis: Dict) -> Dict:
        """Extract educational content from general analysis."""
        content = analysis.get("content", "")
        
        educational_context = {
            "subject": "unknown",
            "difficulty_level": "unknown",
            "content_type": "unknown",
            "key_concepts": [],
            "potential_confusion_points": []
        }
        
        try:
            # Use LLM to extract educational context
            educational_prompt = f"""
            Analyze this screen content for educational context:
            {content}
            
            Identify:
            1. Subject area (math, science, programming, etc.)
            2. Difficulty level (beginner, intermediate, advanced)
            3. Content type (problem, tutorial, documentation, etc.)
            4. Key concepts being taught
            5. Common points of confusion for students
            
            Return as JSON format.
            """
            
            educational_analysis = await self.llm_client.analyze_text(educational_prompt)
            
            # Parse educational analysis (simplified for demo)
            if "math" in content.lower():
                educational_context["subject"] = "mathematics"
                educational_context["content_type"] = "math_problem"
                educational_context["key_concepts"] = ["equations", "algebra", "problem_solving"]
                educational_context["potential_confusion_points"] = [
                    "order_of_operations", 
                    "variable_manipulation", 
                    "step_sequencing"
                ]
            elif "code" in content.lower() or "programming" in content.lower():
                educational_context["subject"] = "programming"
                educational_context["content_type"] = "code"
                educational_context["key_concepts"] = ["algorithms", "syntax", "logic"]
                educational_context["potential_confusion_points"] = [
                    "syntax_errors", 
                    "logic_flow", 
                    "variable_scope"
                ]
            
        except Exception as e:
            logger.error(f"Error extracting educational content: {e}")
        
        return educational_context
    
    async def _detect_ui_elements(self, analysis: Dict) -> List[Dict]:
        """Detect and categorize UI elements in the screenshot."""
        elements = []
        content = analysis.get("content", "").lower()
        
        # Simple UI element detection based on content analysis
        if "button" in content:
            elements.append({"type": "button", "description": "Interactive button detected"})
        if "text field" in content or "input" in content:
            elements.append({"type": "input", "description": "Text input field detected"})
        if "equation" in content or "formula" in content:
            elements.append({"type": "equation", "description": "Mathematical equation detected"})
        if "code" in content:
            elements.append({"type": "code", "description": "Code snippet detected"})
        if "diagram" in content or "chart" in content:
            elements.append({"type": "visual", "description": "Visual element detected"})
        
        return elements
    
    async def _cleanup_screenshot(self, screenshot_path: str):
        """Clean up old screenshot files."""
        try:
            if screenshot_path and os.path.exists(screenshot_path):
                os.unlink(screenshot_path)
                logger.debug(f"Cleaned up screenshot: {screenshot_path}")
        except Exception as e:
            logger.error(f"Error cleaning up screenshot: {e}")
    
    def get_recent_analysis(self, count: int = 3) -> List[Dict]:
        """Get recent screenshot analyses."""
        return self.screenshot_history[-count:] if self.screenshot_history else []
    
    async def cleanup_all_screenshots(self):
        """Clean up all stored screenshots."""
        for analysis in self.screenshot_history:
            await self._cleanup_screenshot(analysis.get("screenshot_path"))
        self.screenshot_history.clear()
        logger.info("All screenshots cleaned up")