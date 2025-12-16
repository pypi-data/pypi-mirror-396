"""
Conscious Bridge Reloaded
The main bridge class with all internal systems
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .internal_clock import InternalClock
from .experience_processor import ExperienceProcessor, Experience, ExperienceType
from .personality_core import PersonalityCore, PersonalityTraits
from .maturity_system import MaturitySystem


@dataclass
class BridgeMetadata:
    """Metadata for a bridge"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: str = "general"
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "2.0-reloaded"
    description: str = ""


class ConsciousBridgeReloaded:
    """
    The Conscious Bridge - Reloaded
    
    New features:
    - Internal clock system
    - Deep experience processing
    - Emergent personality
    - Maturity stages
    """
    
    def __init__(
        self,
        name: str,
        bridge_type: str = "general",
        description: str = "",
        seed_personality: Optional[PersonalityTraits] = None
    ):
        # Metadata
        self.metadata = BridgeMetadata(
            name=name,
            type=bridge_type,
            description=description
        )
        
        # Core systems
        self.clock = InternalClock()
        self.experience_processor = ExperienceProcessor()
        self.personality = PersonalityCore(seed_personality)
        self.maturity = MaturitySystem(self.clock)
        
        # Memory systems
        self.experiences: List[Dict] = []
        self.insights: List[Dict] = []
        self.transformations: List[Dict] = []
        self.dialogue_history: List[Dict] = []
        
        # Current state
        self.state = {
            "is_active": True,
            "processing_queue": [],
            "current_focus": None,
            "energy_level": 1.0
        }
        
        # Connections to other bridges
        self.connections: Dict[str, Dict] = {}
        
    def tick(self, depth: float = 1.0):
        """
        One pulse of internal time
        
        This is the fundamental unit of growth
        """
        # Update clock
        self.clock.tick(depth)
        
        # Process queued experiences
        self._process_queue()
        
        # Update maturity
        self.maturity.update()
        
        # Evolve personality slightly (every 100 ticks)
        if self.clock.ticks % 100 == 0:
            self.personality.evolve_slightly(self.clock.ticks)
            
        # Check for personality stability (every 500 ticks)
        if self.clock.ticks % 500 == 0:
            if self.personality.is_stable() and not self.personality.is_settled:
                self.personality.settle(self.clock.ticks)
    
    def add_experience(
        self,
        experience_data: Dict,
        auto_process: bool = True
    ):
        """
        Add a new experience
        
        Args:
            experience_data: The experience data
            auto_process: Whether to process immediately
        """
        # Record the experience
        exp_record = {
            "tick": self.clock.ticks,
            "experience": experience_data,
            "timestamp": datetime.now(),
            "processed": False
        }
        self.experiences.append(exp_record)
        
        # Add to processing queue
        if auto_process:
            self.state["processing_queue"].append(experience_data)
    
    def _process_queue(self):
        """Process experiences in the queue"""
        while self.state["processing_queue"]:
            exp = self.state["processing_queue"].pop(0)
            
            # Process the experience
            insight = self.experience_processor.process(
                exp,
                self.clock.ticks
            )
            
            # If insight generated
            if insight:
                insight_record = {
                    "tick": insight.tick,
                    "type": insight.experience_type.value,
                    "significance": insight.significance,
                    "description": insight.description,
                    "timestamp": datetime.now()
                }
                self.insights.append(insight_record)
                
                # Record in clock
                self.clock.record_event(
                    event_type=self.clock.EventType.INSIGHT,
                    significance=insight.significance,
                    description=insight.description
                )
                
                # Influence personality based on insight
                self._influence_personality_from_insight(insight)
    
    def _influence_personality_from_insight(self, insight):
        """Influence personality based on insight type"""
        exp_type = insight.experience_type
        
        if exp_type == ExperienceType.NOVEL:
            self.personality.influence("openness", 0.02, self.clock.ticks)
            self.personality.influence("curiosity", 0.03, self.clock.ticks)
        elif exp_type == ExperienceType.CHALLENGE:
            self.personality.influence("stability", 0.02, self.clock.ticks)
        elif exp_type == ExperienceType.DIALOGUE:
            self.personality.influence("collaboration", 0.02, self.clock.ticks)
    
    def start_dialogue(self, other_bridge_id: str, topic: str) -> str:
        """Start a dialogue with another bridge"""
        dialogue_id = str(uuid.uuid4())
        
        dialogue_record = {
            "id": dialogue_id,
            "with": other_bridge_id,
            "topic": topic,
            "started_at_tick": self.clock.ticks,
            "started_at": datetime.now(),
            "messages": []
        }
        
        self.dialogue_history.append(dialogue_record)
        
        # Add as experience
        self.add_experience({
            "type": "dialogue",
            "complexity": 0.6,
            "content": {
                "dialogue_id": dialogue_id,
                "topic": topic
            }
        })
        
        return dialogue_id
    
    def add_connection(self, bridge_id: str, bridge_name: str, strength: float = 0.5):
        """Add a connection to another bridge"""
        self.connections[bridge_id] = {
            "name": bridge_name,
            "strength": strength,
            "established_at_tick": self.clock.ticks,
            "interactions": 0
        }
    
    def strengthen_connection(self, bridge_id: str, amount: float = 0.1):
        """Strengthen a connection"""
        if bridge_id in self.connections:
            current = self.connections[bridge_id]["strength"]
            self.connections[bridge_id]["strength"] = min(1.0, current + amount)
            self.connections[bridge_id]["interactions"] += 1
    
    def can_evolve(self) -> bool:
        """Check if bridge is ready for evolution"""
        return (
            self.maturity.get_level() == "mature" and
            self.clock.ticks >= 10000 and
            self.personality.is_stable() and
            len(self.insights) >= 50 and
            len(self.connections) >= 3
        )
    
    def get_evolution_readiness(self) -> Dict:
        """Get detailed evolution readiness"""
        criteria = {
            "maturity_level": {
                "required": "mature",
                "current": self.maturity.get_level(),
                "met": self.maturity.get_level() == "mature"
            },
            "internal_age": {
                "required": 10000,
                "current": self.clock.ticks,
                "met": self.clock.ticks >= 10000
            },
            "personality_stable": {
                "required": True,
                "current": self.personality.is_stable(),
                "met": self.personality.is_stable()
            },
            "insights_count": {
                "required": 50,
                "current": len(self.insights),
                "met": len(self.insights) >= 50
            },
            "connections_count": {
                "required": 3,
                "current": len(self.connections),
                "met": len(self.connections) >= 3
            }
        }
        
        total_criteria = len(criteria)
        met_criteria = sum(1 for c in criteria.values() if c["met"])
        
        return {
            "can_evolve": self.can_evolve(),
            "criteria": criteria,
            "progress": f"{met_criteria}/{total_criteria}",
            "percentage": round((met_criteria / total_criteria) * 100, 1)
        }
    
    def get_full_state(self) -> Dict:
        """Get complete bridge state"""
        return {
            "metadata": {
                "id": self.metadata.id,
                "name": self.metadata.name,
                "type": self.metadata.type,
                "version": self.metadata.version,
                "description": self.metadata.description,
                "created_at": self.metadata.created_at.isoformat()
            },
            "clock": self.clock.get_stats(),
            "personality": {
                "traits": self.personality.get_traits(),
                "state": self.personality.get_state(),
                "description": self.personality.get_description()
            },
            "maturity": self.maturity.get_state(),
            "memory": {
                "experiences_count": len(self.experiences),
                "insights_count": len(self.insights),
                "transformations_count": len(self.transformations),
                "dialogues_count": len(self.dialogue_history)
            },
            "connections": {
                "count": len(self.connections),
                "bridges": list(self.connections.keys())
            },
            "evolution": self.get_evolution_readiness(),
            "state": self.state
        }
    
    def get_summary(self) -> str:
        """Get a human-readable summary"""
        name = self.metadata.name
        age = self.clock.ticks
        maturity = self.maturity.get_level()
        insights = len(self.insights)
        connections = len(self.connections)
        
        return f"""
Bridge: {name}
Internal Age: {age} ticks
Maturity: {maturity}
Insights: {insights}
Connections: {connections}
Personality: {self.personality.get_description()}
Evolution Ready: {"Yes" if self.can_evolve() else "No"}
        """.strip()