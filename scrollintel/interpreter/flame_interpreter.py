"""
ScrollIntel v2: The Flame Interpreter
Core interpretation engine for scroll-aligned insights
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from datetime import datetime
import pytz
from enum import Enum

class ScrollDomain(Enum):
    TRADE = "Trade"
    LABOUR = "Labour"
    TIME = "Time"
    INHERITANCE = "Inheritance"
    PROPHECY = "Prophecy"
    JUDGMENTS = "Judgments"
    HEALTH = "Health"

class FlameInterpreter:
    """Core interpreter for scroll-aligned insights and domain classification."""
    
    def __init__(self):
        self.domain_keywords = {
            ScrollDomain.TRADE: ["market", "exchange", "commerce", "wealth", "value"],
            ScrollDomain.LABOUR: ["work", "employment", "productivity", "skill", "craft"],
            ScrollDomain.TIME: ["cycle", "season", "period", "duration", "moment"],
            ScrollDomain.INHERITANCE: ["legacy", "heritage", "succession", "birthright", "lineage"],
            ScrollDomain.PROPHECY: ["vision", "forecast", "prediction", "revelation", "omen"],
            ScrollDomain.JUDGMENTS: ["justice", "verdict", "ruling", "assessment", "evaluation"],
            ScrollDomain.HEALTH: ["wellness", "vitality", "healing", "strength", "resilience"]
        }
        
        self.prophetic_captions = {
            ScrollDomain.TRADE: "The flame reveals hidden patterns in the domain of Trade",
            ScrollDomain.LABOUR: "The sacred fire illuminates the path of Labour",
            ScrollDomain.TIME: "The eternal flame marks the cycles of Time",
            ScrollDomain.INHERITANCE: "The divine fire reveals the legacy of Inheritance",
            ScrollDomain.PROPHECY: "The prophetic flame speaks of future revelations",
            ScrollDomain.JUDGMENTS: "The flame of justice burns with righteous clarity",
            ScrollDomain.HEALTH: "The healing flame reveals the path to wellness"
        }
    
    def interpret_forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret raw forecast data and return scroll-aligned insights."""
        try:
            # Extract key metrics
            metrics = self._extract_metrics(data)
            
            # Classify domain
            domain = self._classify_domain(metrics)
            
            # Generate prophetic caption
            caption = self.prophetic_captions[domain]
            
            # Calculate sacred timing
            sacred_timing = self._get_sacred_timing()
            
            # Generate interpretation
            interpretation = {
                "domain": domain.value,
                "prophetic_caption": caption,
                "sacred_timing": sacred_timing,
                "metrics": metrics,
                "confidence": self._calculate_confidence(metrics),
                "divine_guidance": self._generate_guidance(domain, metrics)
            }
            
            return interpretation
        except Exception as e:
            raise ValueError(f"Flame interpretation failed: {str(e)}")
    
    def _extract_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract and normalize key metrics from raw data."""
        metrics = {}
        
        # Extract numerical values
        for key, value in data.items():
            if isinstance(value, (int, float)):
                metrics[key] = float(value)
            elif isinstance(value, dict) and "value" in value:
                metrics[key] = float(value["value"])
        
        # Normalize metrics
        if metrics:
            max_val = max(metrics.values())
            min_val = min(metrics.values())
            if max_val != min_val:
                metrics = {k: (v - min_val) / (max_val - min_val) for k, v in metrics.items()}
        
        return metrics
    
    def _classify_domain(self, metrics: Dict[str, float]) -> ScrollDomain:
        """Classify the forecast into a Scroll Domain."""
        # Count keyword matches for each domain
        domain_scores = {domain: 0 for domain in ScrollDomain}
        
        for key in metrics.keys():
            key_lower = key.lower()
            for domain, keywords in self.domain_keywords.items():
                if any(keyword in key_lower for keyword in keywords):
                    domain_scores[domain] += 1
        
        # Return domain with highest score
        return max(domain_scores.items(), key=lambda x: x[1])[0]
    
    def _get_sacred_timing(self) -> Dict[str, Any]:
        """Get current sacred timing based on ScrollProphetic cycles."""
        now = datetime.now(pytz.UTC)
        hour = now.hour
        
        # Define sacred phases
        if 5 <= hour < 7:
            phase = "dawn"
        elif 12 <= hour < 14:
            phase = "noon"
        elif 17 <= hour < 19:
            phase = "dusk"
        elif 23 <= hour or hour < 1:
            phase = "midnight"
        else:
            phase = "transition"
        
        return {
            "phase": phase,
            "timestamp": now.isoformat(),
            "prophetic_cycle": f"ScrollCycle_{now.strftime('%Y%m%d')}"
        }
    
    def _calculate_confidence(self, metrics: Dict[str, float]) -> float:
        """Calculate confidence score for the interpretation."""
        if not metrics:
            return 0.0
        
        # Base confidence on metric stability and completeness
        stability = 1.0 - np.std(list(metrics.values()))
        completeness = len(metrics) / 10.0  # Assuming 10 is max expected metrics
        
        return min(0.95, (stability + completeness) / 2.0)
    
    def _generate_guidance(self, domain: ScrollDomain, metrics: Dict[str, float]) -> str:
        """Generate divine guidance based on domain and metrics."""
        base_guidance = {
            ScrollDomain.TRADE: "Seek balance in all exchanges",
            ScrollDomain.LABOUR: "Honor the work of your hands",
            ScrollDomain.TIME: "Respect the cycles of creation",
            ScrollDomain.INHERITANCE: "Guard the legacy of wisdom",
            ScrollDomain.PROPHECY: "Listen to the whispers of the flame",
            ScrollDomain.JUDGMENTS: "Let justice flow like water",
            ScrollDomain.HEALTH: "Nurture the flame of life"
        }
        
        return base_guidance[domain] 