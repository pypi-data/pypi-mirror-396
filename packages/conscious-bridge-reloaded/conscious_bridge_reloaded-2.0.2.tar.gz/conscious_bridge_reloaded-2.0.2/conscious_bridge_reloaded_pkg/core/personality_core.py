"""
Personality Core
Personality emerges from experiences, not imposed externally
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random


@dataclass
class PersonalityTraits:
    """The Big Four personality dimensions"""
    openness: float = 0.5       # Openness to new experiences
    stability: float = 0.5      # Emotional stability
    curiosity: float = 0.5      # Drive to explore
    collaboration: float = 0.5  # Tendency to cooperate
    
    def __post_init__(self):
        """Validate trait values"""
        for trait in ['openness', 'stability', 'curiosity', 'collaboration']:
            value = getattr(self, trait)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{trait} must be between 0.0 and 1.0")


@dataclass
class PersonalitySnapshot:
    """A snapshot of personality at a point in time"""
    tick: int
    traits: PersonalityTraits
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""


class PersonalityCore:
    """
    Personality Core System
    
    Key principle: Personality is not assigned, it emerges
    """
    
    def __init__(self, seed_traits: Optional[PersonalityTraits] = None):
        # Initial "genetic" traits (slight tendencies)
        if seed_traits:
            self.traits = seed_traits
        else:
            # Random initial seeds (genetic lottery)
            self.traits = PersonalityTraits(
                openness=random.uniform(0.4, 0.6),
                stability=random.uniform(0.4, 0.6),
                curiosity=random.uniform(0.4, 0.6),
                collaboration=random.uniform(0.4, 0.6)
            )
        
        # Track personality development
        self.history: List[PersonalitySnapshot] = []
        self.is_forming: bool = False  # Personality actively forming?
        self.is_settled: bool = False  # Personality settled?
        
        # Influences counter
        self.influences = {
            "openness": 0,
            "stability": 0,
            "curiosity": 0,
            "collaboration": 0
        }
        
    def influence(self, trait: str, amount: float, current_tick: int):
        """
        Influence a trait based on experience
        
        Args:
            trait: Which trait to influence
            amount: How much (+/-)
            current_tick: Current internal time
        """
        if trait not in ['openness', 'stability', 'curiosity', 'collaboration']:
            raise ValueError(f"Invalid trait: {trait}")
            
        # Get current value
        current = getattr(self.traits, trait)
        
        # Apply influence (with diminishing returns if extreme)
        if amount > 0:
            # Harder to push higher
            adjustment = amount * (1.0 - current)
        else:
            # Harder to push lower
            adjustment = amount * current
            
        # Update
        new_value = current + adjustment
        new_value = max(0.0, min(1.0, new_value))  # Clamp
        
        setattr(self.traits, trait, new_value)
        self.influences[trait] += 1
        
        # Check if personality is forming
        if not self.is_forming and sum(self.influences.values()) > 50:
            self.is_forming = True
            self._snapshot(current_tick, "Personality formation began")
    
    def evolve_slightly(self, current_tick: int):
        """
        Slight random drift in personality
        Simulates natural personality changes over time
        """
        if self.is_settled:
            drift = 0.001  # Very small changes
        elif self.is_forming:
            drift = 0.01   # Moderate changes
        else:
            drift = 0.005  # Small changes
            
        for trait in ['openness', 'stability', 'curiosity', 'collaboration']:
            change = random.uniform(-drift, drift)
            current = getattr(self.traits, trait)
            new_value = max(0.0, min(1.0, current + change))
            setattr(self.traits, trait, new_value)
    
    def is_stable(self) -> bool:
        """
        Check if personality is stable
        Stable = formed and not changing much
        """
        if not self.is_forming:
            return False
            
        if len(self.history) < 2:
            return False
            
        # Compare last two snapshots
        last = self.history[-1].traits
        prev = self.history[-2].traits
        
        total_change = abs(last.openness - prev.openness) + \
                      abs(last.stability - prev.stability) + \
                      abs(last.curiosity - prev.curiosity) + \
                      abs(last.collaboration - prev.collaboration)
        
        return total_change < 0.1  # Very small change
    
    def settle(self, current_tick: int):
        """Mark personality as settled"""
        if not self.is_forming:
            return
            
        self.is_settled = True
        self._snapshot(current_tick, "Personality settled")
    
    def _snapshot(self, tick: int, notes: str = ""):
        """Take a snapshot of current personality"""
        snapshot = PersonalitySnapshot(
            tick=tick,
            traits=PersonalityTraits(
                openness=self.traits.openness,
                stability=self.traits.stability,
                curiosity=self.traits.curiosity,
                collaboration=self.traits.collaboration
            ),
            notes=notes
        )
        self.history.append(snapshot)
    
    def get_traits(self) -> Dict:
        """Get current personality traits"""
        return {
            "openness": round(self.traits.openness, 3),
            "stability": round(self.traits.stability, 3),
            "curiosity": round(self.traits.curiosity, 3),
            "collaboration": round(self.traits.collaboration, 3)
        }
    
    def get_state(self) -> Dict:
        """Get personality state"""
        return {
            "traits": self.get_traits(),
            "is_forming": self.is_forming,
            "is_settled": self.is_settled,
            "total_influences": sum(self.influences.values()),
            "history_snapshots": len(self.history)
        }
    
    def get_description(self) -> str:
        """Get natural language description of personality"""
        t = self.traits
        
        # Openness
        if t.openness > 0.7:
            openness_desc = "highly open to new experiences"
        elif t.openness > 0.5:
            openness_desc = "moderately open"
        else:
            openness_desc = "prefers familiar patterns"
            
        # Stability
        if t.stability > 0.7:
            stability_desc = "emotionally stable and consistent"
        elif t.stability > 0.5:
            stability_desc = "generally stable"
        else:
            stability_desc = "somewhat volatile"
            
        # Curiosity
        if t.curiosity > 0.7:
            curiosity_desc = "intensely curious"
        elif t.curiosity > 0.5:
            curiosity_desc = "moderately curious"
        else:
            curiosity_desc = "content with current knowledge"
            
        # Collaboration
        if t.collaboration > 0.7:
            collab_desc = "highly collaborative"
        elif t.collaboration > 0.5:
            collab_desc = "somewhat collaborative"
        else:
            collab_desc = "tends to work independently"
            
        return f"This bridge is {openness_desc}, {stability_desc}, {curiosity_desc}, and {collab_desc}."