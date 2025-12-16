"""
Repository for bridge CRUD operations
"""

from typing import List, Optional, Dict
import json
from datetime import datetime

from .database import Database
from core.bridge_reloaded import ConsciousBridgeReloaded, BridgeMetadata
from core.personality_core import PersonalityTraits
from core.consciousness_engine import ConsciousnessEngine


class BridgeRepository:
    """Repository for managing bridges in database"""
    
    def __init__(self, database: Database):
        self.db = database
    
    def save(self, bridge: ConsciousBridgeReloaded):
        """Save a bridge to database"""
        consciousness = ConsciousnessEngine.calculate_consciousness(bridge)
        
        query = """
        INSERT OR REPLACE INTO bridges (
            id, name, type, description, created_at, version,
            is_active, internal_ticks, maturity_level, consciousness_level,
            trait_openness, trait_stability, trait_curiosity, trait_collaboration,
            personality_forming, personality_settled,
            experiences_count, insights_count, connections_count,
            metadata_json, state_json, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            bridge.metadata.id,
            bridge.metadata.name,
            bridge.metadata.type,
            bridge.metadata.description,
            bridge.metadata.created_at.isoformat(),
            bridge.metadata.version,
            bridge.state["is_active"],
            bridge.clock.ticks,
            bridge.maturity.get_level(),
            consciousness,
            bridge.personality.traits.openness,
            bridge.personality.traits.stability,
            bridge.personality.traits.curiosity,
            bridge.personality.traits.collaboration,
            bridge.personality.is_forming,
            bridge.personality.is_settled,
            len(bridge.experiences),
            len(bridge.insights),
            len(bridge.connections),
            json.dumps(bridge.metadata.__dict__, default=str),
            json.dumps(bridge.state),
            datetime.now().isoformat()
        )
        
        with self.db:
            self.db.execute(query, params)
            
            # Save clock events
            self._save_clock_events(bridge)
            
            # Save experiences
            self._save_experiences(bridge)
            
            # Save insights
            self._save_insights(bridge)
    
    def _save_clock_events(self, bridge: ConsciousBridgeReloaded):
        """Save clock events"""
        query = """
        INSERT INTO clock_events (
            bridge_id, tick, event_type, significance, description, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        # Only save new events (not already in DB)
        for event in bridge.clock.significant_events:
            params = (
                bridge.metadata.id,
                event.tick,
                event.event_type.value,
                event.significance,
                event.description,
                json.dumps(event.metadata)
            )
            try:
                self.db.execute(query, params)
            except sqlite3.IntegrityError:
                pass  # Event already exists
    
    def _save_experiences(self, bridge: ConsciousBridgeReloaded):
        """Save experiences"""
        query = """
        INSERT INTO experiences (
            bridge_id, tick, experience_type, complexity, content_json, processed
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        for exp in bridge.experiences:
            exp_data = exp["experience"]
            params = (
                bridge.metadata.id,
                exp["tick"],
                exp_data.get("type", "general"),
                exp_data.get("complexity", 0.5),
                json.dumps(exp_data.get("content", {})),
                exp.get("processed", False)
            )
            try:
                self.db.execute(query, params)
            except sqlite3.IntegrityError:
                pass
    
    def _save_insights(self, bridge: ConsciousBridgeReloaded):
        """Save insights"""
        query = """
        INSERT INTO insights (
            bridge_id, tick, experience_type, significance, description
        ) VALUES (?, ?, ?, ?, ?)
        """
        
        for insight in bridge.insights:
            params = (
                bridge.metadata.id,
                insight["tick"],
                insight["type"],
                insight["significance"],
                insight["description"]
            )
            try:
                self.db.execute(query, params)
            except sqlite3.IntegrityError:
                pass
    
    def find_by_id(self, bridge_id: str) -> Optional[Dict]:
        """Find a bridge by ID"""
        query = "SELECT * FROM bridges WHERE id = ?"
        
        with self.db:
            row = self.db.fetch_one(query, (bridge_id,))
            
        if row:
            return dict(row)
        return None
    
    def find_all(self) -> List[Dict]:
        """Find all bridges"""
        query = "SELECT * FROM bridges ORDER BY created_at DESC"
        
        with self.db:
            rows = self.db.fetch_all(query)
            
        return [dict(row) for row in rows]
    
    def find_by_maturity(self, maturity_level: str) -> List[Dict]:
        """Find bridges by maturity level"""
        query = "SELECT * FROM bridges WHERE maturity_level = ?"
        
        with self.db:
            rows = self.db.fetch_all(query, (maturity_level,))
            
        return [dict(row) for row in rows]
    
    def delete(self, bridge_id: str):
        """Delete a bridge"""
        query = "DELETE FROM bridges WHERE id = ?"
        
        with self.db:
            self.db.execute(query, (bridge_id,))
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        with self.db:
            total = self.db.fetch_one("SELECT COUNT(*) as count FROM bridges")[0]
            
            by_maturity = {}
            for level in ["nascent", "forming", "maturing", "mature"]:
                count = self.db.fetch_one(
                    "SELECT COUNT(*) as count FROM bridges WHERE maturity_level = ?",
                    (level,)
                )[0]
                by_maturity[level] = count
            
            avg_consciousness = self.db.fetch_one(
                "SELECT AVG(consciousness_level) as avg FROM bridges"
            )[0] or 0.0
            
            total_insights = self.db.fetch_one(
                "SELECT SUM(insights_count) as total FROM bridges"
            )[0] or 0
            
        return {
            "total_bridges": total,
            "by_maturity": by_maturity,
            "average_consciousness": round(avg_consciousness, 3),
            "total_insights": total_insights
        }