"""
ScrollProphet AI Assistant
Provides intelligent insights and recommendations using OpenAI's GPT model
"""

import os
from typing import Dict, Any, List, Optional
import openai
from datetime import datetime
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrollProphet:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize ScrollProphet with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        openai.api_key = self.api_key
        self.model = "gpt-4-turbo-preview"
        self.memory_file = Path("prophet_memory.json")
        self.memory: Dict[str, Any] = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """Load conversation memory from file."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading memory: {e}")
                return {"conversations": [], "insights": []}
        return {"conversations": [], "insights": []}

    def _save_memory(self):
        """Save conversation memory to file."""
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")

    async def get_insights(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI-powered insights based on the current context.
        
        Args:
            context: Dictionary containing current session/analysis context
            
        Returns:
            Dictionary containing insights and recommendations
        """
        try:
            # Prepare the prompt
            prompt = self._prepare_insight_prompt(context)
            
            # Get response from OpenAI
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are ScrollProphet, an AI assistant specialized in data analysis and visualization. Provide concise, actionable insights and recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract and structure the response
            insights = self._parse_insights(response.choices[0].message.content)
            
            # Store in memory
            self.memory["insights"].append({
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "insights": insights
            })
            self._save_memory()
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return {
                "error": str(e),
                "insights": [],
                "recommendations": []
            }

    async def get_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """
        Get AI-powered recommendations for data analysis.
        
        Args:
            data: Dictionary containing data to analyze
            
        Returns:
            List of recommendations
        """
        try:
            # Prepare the prompt
            prompt = self._prepare_recommendation_prompt(data)
            
            # Get response from OpenAI
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are ScrollProphet, an AI assistant specialized in data analysis. Provide specific, actionable recommendations for data analysis and visualization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            # Parse recommendations
            recommendations = self._parse_recommendations(response.choices[0].message.content)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []

    def _prepare_insight_prompt(self, context: Dict[str, Any]) -> str:
        """Prepare the prompt for getting insights."""
        return f"""
        Based on the following context, provide insights and recommendations:
        
        Domain: {context.get('domain', 'Unknown')}
        Data Type: {context.get('data_type', 'Unknown')}
        Metrics: {context.get('metrics', [])}
        Recent Activity: {context.get('recent_activity', [])}
        
        Please provide:
        1. Key insights about the data
        2. Potential areas for deeper analysis
        3. Recommended visualizations
        4. Action items
        """

    def _prepare_recommendation_prompt(self, data: Dict[str, Any]) -> str:
        """Prepare the prompt for getting recommendations."""
        return f"""
        Based on the following data, provide specific recommendations:
        
        Data Summary:
        - Type: {data.get('type', 'Unknown')}
        - Size: {data.get('size', 'Unknown')}
        - Key Metrics: {data.get('metrics', [])}
        
        Please provide specific recommendations for:
        1. Data analysis approaches
        2. Visualization techniques
        3. Potential insights to explore
        """

    def _parse_insights(self, content: str) -> Dict[str, Any]:
        """Parse the AI response into structured insights."""
        try:
            # Split content into sections
            sections = content.split("\n\n")
            insights = {
                "key_insights": [],
                "analysis_areas": [],
                "visualizations": [],
                "action_items": []
            }
            
            current_section = None
            for section in sections:
                if "Key insights" in section:
                    current_section = "key_insights"
                elif "Potential areas" in section:
                    current_section = "analysis_areas"
                elif "Recommended visualizations" in section:
                    current_section = "visualizations"
                elif "Action items" in section:
                    current_section = "action_items"
                elif current_section and section.strip():
                    insights[current_section].append(section.strip())
            
            return insights
            
        except Exception as e:
            logger.error(f"Error parsing insights: {e}")
            return {
                "key_insights": ["Error parsing insights"],
                "analysis_areas": [],
                "visualizations": [],
                "action_items": []
            }

    def _parse_recommendations(self, content: str) -> List[str]:
        """Parse the AI response into a list of recommendations."""
        try:
            # Split content into lines and filter out empty lines
            recommendations = [
                line.strip() for line in content.split("\n")
                if line.strip() and not line.startswith(("1.", "2.", "3."))
            ]
            return recommendations
            
        except Exception as e:
            logger.error(f"Error parsing recommendations: {e}")
            return ["Error parsing recommendations"]

# Create global instance
scroll_prophet = ScrollProphet() 