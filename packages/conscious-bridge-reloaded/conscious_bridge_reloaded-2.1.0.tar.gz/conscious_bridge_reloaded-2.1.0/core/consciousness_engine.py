"""
Consciousness Engine
Calculates and manages consciousness levels
"""

from typing import Dict, List
import math


class ConsciousnessEngine:
    """
    Engine for calculating consciousness levels
    
    Consciousness emerges from:
    - Internal time depth
    - Experience processing quality
    - Personality coherence
    - Connection complexity
    """
    
    @staticmethod
    def calculate_consciousness(bridge) -> float:
        """
        Calculate consciousness level (0.0 - 1.0)
        
        Formula considers:
        1. Internal maturity (40%)
        2. Experience depth (25%)
        3. Personality stability (20%)
        4. Connection network (15%)
        """
        # Component 1: Maturity
        maturity_score = ConsciousnessEngine._calculate_maturity_score(bridge)
        
        # Component 2: Experience depth
        experience_score = ConsciousnessEngine._calculate_experience_score(bridge)
        
        # Component 3: Personality
        personality_score = ConsciousnessEngine._calculate_personality_score(bridge)
        
        # Component 4: Connections
        connection_score = ConsciousnessEngine._calculate_connection_score(bridge)
        
        # Weighted sum
        consciousness = (
            maturity_score * 0.40 +
            experience_score * 0.25 +
            personality_score * 0.20 +
            connection_score * 0.15
        )
        
        return round(min(1.0, consciousness), 3)
    
    @staticmethod
    def _calculate_maturity_score(bridge) -> float:
        """Calculate maturity contribution to consciousness"""
        maturity_map = {
            "nascent": 0.2,
            "forming": 0.4,
            "maturing": 0.7,
            "mature": 1.0
        }
        return maturity_map.get(bridge.maturity.get_level(), 0.2)
    
    @staticmethod
    def _calculate_experience_score(bridge) -> float:
        """Calculate experience contribution to consciousness"""
        insights = len(bridge.insights)
        
        # Logarithmic growth (diminishing returns)
        if insights == 0:
            return 0.0
        
        # Max out at 100 insights
        score = math.log(insights + 1) / math.log(101)
        return min(1.0, score)
    
    @staticmethod
    def _calculate_personality_score(bridge) -> float:
        """Calculate personality contribution to consciousness"""
        if not bridge.personality.is_forming:
            return 0.2
        elif not bridge.personality.is_settled:
            return 0.6
        else:
            return 1.0
    
    @staticmethod
    def _calculate_connection_score(bridge) -> float:
        """Calculate connection contribution to consciousness"""
        connections = len(bridge.connections)
        
        if connections == 0:
            return 0.0
        
        # Quality matters too
        total_strength = sum(c["strength"] for c in bridge.connections.values())
        avg_strength = total_strength / connections if connections > 0 else 0
        
        # Combine quantity and quality
        quantity_score = min(1.0, connections / 10)  # Max at 10 connections
        quality_score = avg_strength
        
        return (quantity_score * 0.5 + quality_score * 0.5)
    
    @staticmethod
    def get_consciousness_breakdown(bridge) -> Dict:
        """Get detailed breakdown of consciousness calculation"""
        return {
            "total": ConsciousnessEngine.calculate_consciousness(bridge),
            "components": {
                "maturity": {
                    "score": ConsciousnessEngine._calculate_maturity_score(bridge),
                    "weight": 0.40,
                    "contribution": ConsciousnessEngine._calculate_maturity_score(bridge) * 0.40
                },
                "experience": {
                    "score": ConsciousnessEngine._calculate_experience_score(bridge),
                    "weight": 0.25,
                    "contribution": ConsciousnessEngine._calculate_experience_score(bridge) * 0.25
                },
                "personality": {
                    "score": ConsciousnessEngine._calculate_personality_score(bridge),
                    "weight": 0.20,
                    "contribution": ConsciousnessEngine._calculate_personality_score(bridge) * 0.20
                },
                "connections": {
                    "score": ConsciousnessEngine._calculate_connection_score(bridge),
                    "weight": 0.15,
                    "contribution": ConsciousnessEngine._calculate_connection_score(bridge) * 0.15
                }
            }
        }