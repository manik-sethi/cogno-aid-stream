import asyncio
import logging
import json
import aiohttp
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with Large Language Models (OpenAI, etc.)."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4-vision-preview"  # For image analysis
        self.text_model = "gpt-4"  # For text analysis
        self.max_tokens = 500
        self.temperature = 0.7
        
        # Mock mode for development without API key
        self.mock_mode = self.api_key == "your-api-key-here"
        
    async def analyze_image(self, image_base64: str, prompt: str = None) -> Dict:
        """
        Analyze an image using vision-capable LLM.
        
        Args:
            image_base64: Base64 encoded image
            prompt: Optional custom prompt for analysis
            
        Returns:
            Analysis results
        """
        try:
            if self.mock_mode:
                return await self._mock_image_analysis(image_base64, prompt)
            
            if not prompt:
                prompt = """
                Analyze this screenshot and describe:
                1. What type of content is shown (educational, work, entertainment, etc.)
                2. Any text or UI elements visible
                3. The overall context and what the user might be working on
                4. Any potential areas of difficulty or confusion
                
                Be specific and educational-focused in your analysis.
                """
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        return {
                            "content": content,
                            "model": self.model,
                            "timestamp": asyncio.get_event_loop().time()
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"LLM API error: {response.status} - {error_text}")
                        return await self._mock_image_analysis(image_base64, prompt)
            
        except Exception as e:
            logger.error(f"Error analyzing image with LLM: {e}")
            return await self._mock_image_analysis(image_base64, prompt)
    
    async def analyze_text(self, prompt: str, context: str = None) -> Any:
        """
        Analyze text using LLM.
        
        Args:
            prompt: Text prompt for analysis
            context: Additional context information
            
        Returns:
            Analysis results
        """
        try:
            if self.mock_mode:
                return await self._mock_text_analysis(prompt, context)
            
            messages = [{"role": "user", "content": prompt}]
            
            if context:
                messages.insert(0, {"role": "system", "content": f"Context: {context}"})
            
            payload = {
                "model": self.text_model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        # Try to parse as JSON if it looks like JSON
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError:
                            return content
                    else:
                        error_text = await response.text()
                        logger.error(f"LLM API error: {response.status} - {error_text}")
                        return await self._mock_text_analysis(prompt, context)
            
        except Exception as e:
            logger.error(f"Error analyzing text with LLM: {e}")
            return await self._mock_text_analysis(prompt, context)
    
    async def generate_help_suggestions(self, context: Dict, confusion_level: float) -> List[str]:
        """Generate contextual help suggestions."""
        prompt = f"""
        Generate 2-3 helpful learning suggestions for a student experiencing confusion level {confusion_level:.2f}/1.0.
        
        Context: {json.dumps(context)}
        
        Guidelines:
        - Don't give direct answers
        - Encourage learning process
        - Be specific to the context
        - Keep suggestions under 100 characters each
        
        Return as JSON array of strings.
        """
        
        response = await self.analyze_text(prompt)
        
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and "suggestions" in response:
            return response["suggestions"]
        else:
            # Fallback suggestions
            return [
                "Break the problem into smaller steps.",
                "Review the relevant concepts first.",
                "Try a simpler example to build understanding."
            ]
    
    async def _mock_image_analysis(self, image_base64: str, prompt: str = None) -> Dict:
        """Mock image analysis for development."""
        # Simulate analysis delay
        await asyncio.sleep(0.5)
        
        return {
            "content": """
            This appears to be an educational screen showing a mathematics problem or programming exercise. 
            The interface includes text fields for input, some instructional content, and what looks like 
            a problem-solving environment. The user seems to be working on equations or code that requires 
            step-by-step thinking. Common areas of confusion might include understanding the problem 
            requirements, applying the correct methodology, or making computational errors.
            """,
            "model": "mock-vision-model",
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def _mock_text_analysis(self, prompt: str, context: str = None) -> Any:
        """Mock text analysis for development."""
        # Simulate analysis delay
        await asyncio.sleep(0.3)
        
        # Simple keyword-based mock responses
        prompt_lower = prompt.lower()
        
        if "suggestion" in prompt_lower or "help" in prompt_lower:
            return [
                "Take a step back and identify the core concept.",
                "Work through the problem methodically.",
                "Don't hesitate to review the fundamentals."
            ]
        elif "json" in prompt_lower:
            return {
                "subject": "mathematics",
                "difficulty": "intermediate",
                "suggestions": ["Break it down step by step", "Check your work carefully"]
            }
        else:
            return "This is a mock response. In production, this would be generated by the LLM based on your prompt."
    
    def set_api_key(self, api_key: str):
        """Set the OpenAI API key."""
        self.api_key = api_key
        self.mock_mode = api_key == "your-api-key-here"
        logger.info(f"LLM client configured. Mock mode: {self.mock_mode}")
    
    def get_status(self) -> Dict:
        """Get LLM client status."""
        return {
            "mock_mode": self.mock_mode,
            "model": self.model,
            "text_model": self.text_model,
            "base_url": self.base_url,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }