"""
Experience Processor
Processes experiences deeply, not quickly
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random


class ExperienceType(Enum):
    """Types of experiences"""
    DIALOGUE = "dialogue"
    OBSERVATION = "observation"
    CHALLENGE = "challenge"
    NOVEL = "novel_discovery"
    ROUTINE = "routine_processing"


class ExperienceQuality(Enum):
    """Quality of experience processing"""
    SUPERFICIAL = 0.2
    SHALLOW = 0.4
    MODERATE = 0.6
    DEEP = 0.8
    PROFOUND = 1.0


@dataclass
class Experience:
    """An experience to be processed"""
    type: ExperienceType
    complexity: float  # 0.0 - 1.0
    content: Dict
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False
    insight_generated: Optional[str] = None


@dataclass
class Insight:
    """An insight generated from experience"""
    tick: int
    experience_type: ExperienceType
    significance: float
    description: str
    connections: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class ExperienceProcessor:
    """
    Processes experiences with depth
    
    Key principle: Quality > Quantity
    One deep experience > 1000 shallow ones
    """
    
    def __init__(self):
        self.processing_queue: List[Experience] = []
        self.processed_experiences: List[Experience] = []
        self.insights_generated: List[Insight] = []
        self.processing_depth: float = 0.5  # Current depth capacity
        
    def add_experience(self, experience: Experience):
        """Add experience to processing queue"""
        self.processing_queue.append(experience)
        
    def process(
        self,
        experience: Dict,
        current_tick: int,
        forced_quality: Optional[ExperienceQuality] = None
    ) -> Optional[Insight]:
        """
        Process an experience
        
        Args:
            experience: The experience data
            current_tick: Current internal time
            forced_quality: Override automatic quality determination
            
        Returns:
            Insight if generated, None otherwise
        """
        # Determine processing quality
        quality = forced_quality or self._determine_quality(experience)
        
        # Process based on quality
        if quality.value < 0.6:
            # Low quality = no insight
            return None
            
        # High quality = potential insight
        if self._should_generate_insight(experience, quality):
            return self._generate_insight(experience, current_tick, quality)
            
        return None
    
    def _determine_quality(self, experience: Dict) -> ExperienceQuality:
        """Determine processing quality based on experience"""
        complexity = experience.get("complexity", 0.5)
        exp_type = experience.get("type", "routine")
        
        # Novel experiences get deeper processing
        if exp_type == "novel":
            base_quality = 0.8
        elif exp_type == "challenge":
            base_quality = 0.7
        elif exp_type == "dialogue":
            base_quality = 0.6
        else:
            base_quality = 0.4
            
        # Adjust by complexity
        final_quality = base_quality + (complexity * 0.2)
        final_quality = min(1.0, final_quality)
        
        # Convert to enum
        if final_quality >= 0.9:
            return ExperienceQuality.PROFOUND
        elif final_quality >= 0.7:
            return ExperienceQuality.DEEP
        elif final_quality >= 0.5:
            return ExperienceQuality.MODERATE
        elif final_quality >= 0.3:
            return ExperienceQuality.SHALLOW
        else:
            return ExperienceQuality.SUPERFICIAL
    
    def _should_generate_insight(
        self,
        experience: Dict,
        quality: ExperienceQuality
    ) -> bool:
        """Determine if insight should be generated"""
        # Higher quality = higher chance of insight
        insight_probability = quality.value * 0.7
        
        # Complexity also matters
        complexity = experience.get("complexity", 0.5)
        insight_probability += complexity * 0.3
        
        return random.random() < insight_probability
    
    def _generate_insight(
        self,
        experience: Dict,
        tick: int,
        quality: ExperienceQuality
    ) -> Insight:
        """Generate an insight from experience"""
        exp_type_str = experience.get("type", "general")
        exp_type = ExperienceType.DIALOGUE  # Default
        
        try:
            exp_type = ExperienceType(exp_type_str)
        except ValueError:
            pass
            
        # Significance based on quality
        significance = quality.value * random.uniform(0.7, 1.0)
        
        # Generate description
        descriptions = [
            "Connection discovered between concepts",
            "Pattern recognized in processing",
            "Deep understanding achieved",
            "Novel perspective gained",
            "Fundamental principle understood"
        ]
        
        description = random.choice(descriptions)
        
        insight = Insight(
            tick=tick,
            experience_type=exp_type,
            significance=significance,
            description=description,
            metadata={
                "quality": quality.name,
                "experience_content": experience.get("content", {})
            }
        )
        
        self.insights_generated.append(insight)
        return insight
    
    def get_stats(self) -> Dict:
        """Get processor statistics"""
        return {
            "queue_size": len(self.processing_queue),
            "processed_count": len(self.processed_experiences),
            "insights_count": len(self.insights_generated),
            "processing_depth": round(self.processing_depth, 2),
            "average_insight_significance": self._calculate_avg_significance()
        }
    
    def _calculate_avg_significance(self) -> float:
        """Calculate average insight significance"""
        if not self.insights_generated:
            return 0.0
            
        total = sum(i.significance for i in self.insights_generated)
        return round(total / len(self.insights_generated), 3)