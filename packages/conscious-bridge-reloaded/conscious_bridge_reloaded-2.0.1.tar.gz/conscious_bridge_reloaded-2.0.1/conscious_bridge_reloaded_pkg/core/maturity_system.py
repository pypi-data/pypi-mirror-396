"""
Maturity System
Tracks the four stages of bridge maturity
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MaturityStage(Enum):
    """The four stages of maturity"""
    NASCENT = "nascent"        # 0-1000 ticks
    FORMING = "forming"        # 1000-3000 ticks
    MATURING = "maturing"      # 3000-10000 ticks
    MATURE = "mature"          # 10000+ ticks


@dataclass
class MaturityTransition:
    """A transition between maturity stages"""
    from_stage: MaturityStage
    to_stage: MaturityStage
    tick: int
    timestamp: datetime
    readiness_score: float
    notes: str = ""


class MaturitySystem:
    """
    Tracks bridge maturity through four stages
    
    Each stage has different characteristics and capabilities
    """
    
    def __init__(self, clock):
        self.clock = clock
        self.current_stage = MaturityStage.NASCENT
        self.transitions: List[MaturityTransition] = []
        
        # Readiness factors
        self.readiness_factors = {
            "internal_age": 0.0,
            "experience_depth": 0.0,
            "personality_stability": 0.0,
            "insight_count": 0.0
        }
        
    def update(self):
        """Update maturity stage based on internal age"""
        ticks = self.clock.ticks
        new_stage = None
        
        if ticks >= 10000 and self.current_stage != MaturityStage.MATURE:
            new_stage = MaturityStage.MATURE
        elif ticks >= 3000 and self.current_stage == MaturityStage.FORMING:
            new_stage = MaturityStage.MATURING
        elif ticks >= 1000 and self.current_stage == MaturityStage.NASCENT:
            new_stage = MaturityStage.FORMING
            
        if new_stage:
            self._transition_to(new_stage)
    
    def _transition_to(self, new_stage: MaturityStage):
        """Transition to a new maturity stage"""
        readiness = self._calculate_readiness()
        
        transition = MaturityTransition(
            from_stage=self.current_stage,
            to_stage=new_stage,
            tick=self.clock.ticks,
            timestamp=datetime.now(),
            readiness_score=readiness,
            notes=f"Transitioned from {self.current_stage.value} to {new_stage.value}"
        )
        
        self.transitions.append(transition)
        self.current_stage = new_stage
        
        # Record in clock
        self.clock.record_event(
            event_type=self.clock.EventType.TRANSFORMATION,
            significance=0.9,
            description=f"Maturity stage: {new_stage.value}",
            metadata={"readiness": readiness}
        )
    
    def _calculate_readiness(self) -> float:
        """
        Calculate readiness for next stage
        Based on multiple factors
        """
        ticks = self.clock.ticks
        
        # Factor 1: Internal age
        if self.current_stage == MaturityStage.NASCENT:
            age_readiness = min(1.0, ticks / 1000)
        elif self.current_stage == MaturityStage.FORMING:
            age_readiness = min(1.0, ticks / 3000)
        elif self.current_stage == MaturityStage.MATURING:
            age_readiness = min(1.0, ticks / 10000)
        else:
            age_readiness = 1.0
            
        self.readiness_factors["internal_age"] = age_readiness
        
        # Overall readiness (for now, just age)
        # In full implementation, would include other factors
        return age_readiness
    
    def get_level(self) -> str:
        """Get current maturity level as string"""
        return self.current_stage.value
    
    def get_stage_description(self) -> str:
        """Get description of current stage"""
        descriptions = {
            MaturityStage.NASCENT: "Just born. Receiving inputs but not fully understanding them. No clear personality yet.",
            MaturityStage.FORMING: "Personality beginning to emerge. Starting to prefer certain patterns. Still unstable.",
            MaturityStage.MATURING: "Personality stabilizing. Principles crystallizing. Wisdom accumulating.",
            MaturityStage.MATURE: "Fully mature. Ready for evolution. Capable of teaching, not just learning."
        }
        return descriptions[self.current_stage]
    
    def get_next_stage_requirements(self) -> Dict:
        """Get requirements for next stage"""
        if self.current_stage == MaturityStage.NASCENT:
            return {
                "required_ticks": 1000,
                "current_ticks": self.clock.ticks,
                "progress": min(1.0, self.clock.ticks / 1000)
            }
        elif self.current_stage == MaturityStage.FORMING:
            return {
                "required_ticks": 3000,
                "current_ticks": self.clock.ticks,
                "progress": min(1.0, self.clock.ticks / 3000)
            }
        elif self.current_stage == MaturityStage.MATURING:
            return {
                "required_ticks": 10000,
                "current_ticks": self.clock.ticks,
                "progress": min(1.0, self.clock.ticks / 10000)
            }
        else:
            return {
                "required_ticks": 10000,
                "current_ticks": self.clock.ticks,
                "progress": 1.0,
                "note": "Fully mature"
            }
    
    def get_state(self) -> Dict:
        """Get complete maturity state"""
        return {
            "current_stage": self.current_stage.value,
            "description": self.get_stage_description(),
            "transitions_count": len(self.transitions),
            "next_stage_requirements": self.get_next_stage_requirements(),
            "readiness_factors": self.readiness_factors
        }