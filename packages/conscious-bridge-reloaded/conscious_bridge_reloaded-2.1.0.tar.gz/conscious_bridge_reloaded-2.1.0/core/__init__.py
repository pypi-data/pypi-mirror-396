"""
Core module for Conscious Bridge Reloaded
Contains all fundamental systems
"""

from .internal_clock import InternalClock, ClockEvent
from .experience_processor import ExperienceProcessor, Experience
from .personality_core import PersonalityCore, PersonalityTraits
from .maturity_system import MaturitySystem, MaturityStage
from .bridge_reloaded import ConsciousBridgeReloaded, BridgeMetadata
from .consciousness_engine import ConsciousnessEngine

__all__ = [
    'InternalClock',
    'ClockEvent',
    'ExperienceProcessor',
    'Experience',
    'PersonalityCore',
    'PersonalityTraits',
    'MaturitySystem',
    'MaturityStage',
    'ConsciousBridgeReloaded',
    'BridgeMetadata',
    'ConsciousnessEngine'
]

__version__ = '2.1.0'