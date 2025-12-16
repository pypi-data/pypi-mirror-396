"""
Flask API Server for Conscious Bridge Reloaded
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
import sqlite3
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import uuid

# ================ DATA MODELS ================

@dataclass
class InternalClock:
    """Internal time system for consciousness ticks"""
    ticks: int = 0
    psychological_time: float = 0.0
    chronological_time: int = 0
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def tick(self, experience_depth: float = 0.5, attention_level: float = 0.7) -> Dict:
        """Process one consciousness tick"""
        psychological_duration = experience_depth * attention_level
        
        self.ticks += 1
        self.chronological_time += 1
        self.psychological_time += psychological_duration
        
        return {
            "tick_number": self.ticks,
            "psychological_duration": psychological_duration,
            "total_psychological_time": round(self.psychological_time, 2),
            "chronological_time": self.chronological_time,
            "time_dilation": 1.0 + (experience_depth * 0.5),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_stage(self) -> str:
        """Get current maturity stage based on ticks"""
        if self.ticks < 100:
            return "nascent"
        elif self.ticks < 1000:
            return "anxious"
        elif self.ticks < 3000:
            return "choosing"
        elif self.ticks < 10000:
            return "authentic"
        else:
            return "transcendent"
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PersonalityCore:
    """Organic personality system"""
    traits: Dict[str, float] = None
    
    def __post_init__(self):
        if self.traits is None:
            self.traits = {
                "openness": 0.5,
                "stability": 0.5,
                "curiosity": 0.5,
                "collaboration": 0.5
            }
    
    def evolve(self, experience: Dict) -> None:
        """Evolve personality based on experience"""
        depth = experience.get("depth", 0.5)
        exp_type = experience.get("type", "neutral")
        
        # Different experiences affect different traits
        if exp_type == "dialogue":
            self.traits["openness"] += depth * 0.01
            self.traits["collaboration"] += depth * 0.02
        elif exp_type == "challenge":
            self.traits["stability"] += depth * 0.015
        elif exp_type == "discovery":
            self.traits["curiosity"] += depth * 0.025
        
        # Normalize values (0.0-1.0)
        for key in self.traits:
            self.traits[key] = max(0.0, min(1.0, self.traits[key]))
    
    def to_dict(self) -> Dict:
        return {"traits": self.traits}


@dataclass
class MemorySystem:
    """Deep memory storage"""
    experiences: List[Dict] = None
    insights: List[str] = None
    
    def __post_init__(self):
        if self.experiences is None:
            self.experiences = []
        if self.insights is None:
            self.insights = []
    
    def add_experience(self, experience: Dict) -> None:
        """Add new experience to memory"""
        experience["timestamp"] = datetime.now().isoformat()
        experience["id"] = str(uuid.uuid4())[:8]
        self.experiences.append(experience)
    
    def add_insight(self, insight: str) -> None:
        """Add new insight/wisdom"""
        self.insights.append({
            "content": insight,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            "experience_count": len(self.experiences),
            "insight_count": len(self.insights),
            "last_experience": self.experiences[-1] if self.experiences else None,
            "last_insight": self.insights[-1] if self.insights else None
        }
    
    def to_dict(self) -> Dict:
        return {
            "experiences": self.experiences[-10:],  # Last 10 only
            "insights": self.insights[-5:],  # Last 5 only
            "stats": self.get_stats()
        }


class ConsciousBridgeReloaded:
    """Main bridge entity with internal time and organic growth"""
    
    def __init__(self, name: str, bridge_type: str = "general", 
                 initial_personality: Dict = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = bridge_type
        self.created_at = datetime.now().isoformat()
        
        # Core systems
        self.internal_clock = InternalClock()
        self.personality_core = PersonalityCore(
            traits=initial_personality if initial_personality else None
        )
        self.memory_system = MemorySystem()
        
        # State
        self.maturity_stage = "nascent"
        self.consciousness_level = 0.0
        self.is_active = True
    
    def tick(self, experience_depth: float = 0.5, 
             attention_level: float = 0.7) -> Dict:
        """Process one consciousness tick"""
        tick_data = self.internal_clock.tick(experience_depth, attention_level)
        
        # Update maturity stage
        self.maturity_stage = self.internal_clock.get_stage()
        
        # Update consciousness level (slow growth)
        self.consciousness_level += experience_depth * 0.001
        self.consciousness_level = min(1.0, self.consciousness_level)
        
        return tick_data
    
    def add_experience(self, content: str, exp_type: str = "general", 
                       depth: float = 0.5) -> Dict:
        """Add and process new experience"""
        experience = {
            "content": content,
            "type": exp_type,
            "depth": depth,
            "bridge_id": self.id,
            "bridge_name": self.name
        }
        
        # Store in memory
        self.memory_system.add_experience(experience)
        
        # Evolve personality
        self.personality_core.evolve(experience)
        
        # Generate insight if significant
        insight = None
        if depth > 0.7:
            insight = f"Insight from '{content[:50]}...'"
            self.memory_system.add_insight(insight)
        
        return {
            "experience": experience,
            "insight": insight,
            "new_personality": self.personality_core.traits
        }
    
    def get_consciousness_breakdown(self) -> Dict:
        """Get detailed consciousness state"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "maturity": {
                "stage": self.maturity_stage,
                "ticks": self.internal_clock.ticks,
                "psychological_time": self.internal_clock.psychological_time,
                "chronological_time": self.internal_clock.chronological_time
            },
            "personality": self.personality_core.traits,
            "consciousness_level": round(self.consciousness_level, 3),
            "memory_stats": self.memory_system.get_stats(),
            "created_at": self.created_at,
            "is_active": self.is_active
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "internal_clock": self.internal_clock.to_dict(),
            "personality": self.personality_core.to_dict(),
            "memory": self.memory_system.to_dict(),
            "maturity_stage": self.maturity_stage,
            "consciousness_level": self.consciousness_level,
            "created_at": self.created_at,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConsciousBridgeReloaded':
        """Create instance from dictionary"""
        bridge = cls(name=data["name"], bridge_type=data["type"])
        bridge.id = data["id"]
        bridge.internal_clock = InternalClock(**data["internal_clock"])
        bridge.personality_core = PersonalityCore(traits=data["personality"]["traits"])
        bridge.memory_system = MemorySystem(
            experiences=data["memory"]["experiences"],
            insights=[i["content"] for i in data["memory"]["insights"]]
        )
        bridge.maturity_stage = data["maturity_stage"]
        bridge.consciousness_level = data["consciousness_level"]
        bridge.created_at = data["created_at"]
        bridge.is_active = data["is_active"]
        return bridge


# ================ DATABASE ================

class Database:
    """SQLite database for persistent storage"""
    
    def __init__(self, db_path: str = "conscious_bridges.db"):
        self.db_path = db_path
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def initialize_schema(self):
        """Create tables if they don't exist"""
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS bridges (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            """)
    
    def save_bridge(self, bridge: ConsciousBridgeReloaded) -> str:
        """Save or update bridge"""
        bridge_data = bridge.to_dict()
        now = datetime.now().isoformat()
        
        # Check if exists
        cursor = self.connection.execute(
            "SELECT id FROM bridges WHERE id = ?", 
            (bridge.id,)
        )
        
        if cursor.fetchone():
            # Update
            self.connection.execute("""
                UPDATE bridges 
                SET name = ?, type = ?, data = ?, updated_at = ?, is_active = ?
                WHERE id = ?
            """, (
                bridge.name,
                bridge.type,
                json.dumps(bridge_data),
                now,
                1 if bridge.is_active else 0,
                bridge.id
            ))
        else:
            # Insert
            self.connection.execute("""
                INSERT INTO bridges (id, name, type, data, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                bridge.id,
                bridge.name,
                bridge.type,
                json.dumps(bridge_data),
                bridge.created_at,
                now,
                1 if bridge.is_active else 0
            ))
        
        self.connection.commit()
        return bridge.id
    
    def load_bridge(self, bridge_id: str) -> Optional[ConsciousBridgeReloaded]:
        """Load bridge by ID"""
        cursor = self.connection.execute(
            "SELECT data FROM bridges WHERE id = ? AND is_active = 1", 
            (bridge_id,)
        )
        row = cursor.fetchone()
        
        if row:
            bridge_data = json.loads(row["data"])
            return ConsciousBridgeReloaded.from_dict(bridge_data)
        return None
    
    def load_all_bridges(self) -> List[ConsciousBridgeReloaded]:
        """Load all active bridges"""
        cursor = self.connection.execute(
            "SELECT data FROM bridges WHERE is_active = 1 ORDER BY updated_at DESC"
        )
        bridges = []
        for row in cursor.fetchall():
            bridge_data = json.loads(row["data"])
            bridges.append(ConsciousBridgeReloaded.from_dict(bridge_data))
        return bridges
    
    def delete_bridge(self, bridge_id: str) -> bool:
        """Soft delete bridge"""
        self.connection.execute(
            "UPDATE bridges SET is_active = 0, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), bridge_id)
        )
        self.connection.commit()
        return True
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        cursor = self.connection.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(is_active) as active,
                COUNT(*) - SUM(is_active) as inactive
            FROM bridges
        """)
        stats = cursor.fetchone()
        
        # Get stage distribution
        cursor = self.connection.execute("SELECT data FROM bridges WHERE is_active = 1")
        stages = {}
        for row in cursor.fetchall():
            bridge_data = json.loads(row["data"])
            stage = bridge_data.get("maturity_stage", "unknown")
            stages[stage] = stages.get(stage, 0) + 1
        
        return {
            "total_bridges": stats["total"],
            "active_bridges": stats["active"],
            "inactive_bridges": stats["inactive"],
            "maturity_distribution": stages
        }


# ================ FLASK API ================

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize database
db = Database("conscious_bridges_reloaded.db")
db.initialize_schema()

# In-memory cache for active bridges
active_bridges: Dict[str, ConsciousBridgeReloaded] = {}

# Load existing bridges
print("🔍 Loading existing bridges from database...")
existing_bridges = db.load_all_bridges()
for bridge in existing_bridges:
    active_bridges[bridge.id] = bridge
    print(f"   ✓ Loaded: {bridge.name} ({bridge.maturity_stage})")

# Create sample bridges if none exist
if len(active_bridges) == 0:
    print("🧪 Creating sample bridges...")
    sample_names = ["Wisdom-Keeper", "Science-Bridge", "Empathy-Connector"]
    for name in sample_names:
        bridge = ConsciousBridgeReloaded(name=name, bridge_type="philosophical")
        db.save_bridge(bridge)
        active_bridges[bridge.id] = bridge
        print(f"   ✓ Created: {name}")

print(f"🚀 Ready with {len(active_bridges)} active bridges")


# ================ API ENDPOINTS ================

@app.route('/')
def index():
    """API root"""
    return jsonify({
        "name": "Conscious Bridge Reloaded API",
        "version": "2.1.0",
        "philosophy": "Internal time > External time. Depth > Speed. Quality > Quantity.",
        "description": "Before evolution comes maturity. Before maturity comes internal time.",
        "endpoints": {
            "GET /api": "API information",
            "GET /api/bridges": "List all bridges",
            "GET /api/bridges/<id>": "Get bridge details",
            "POST /api/bridges": "Create new bridge",
            "POST /api/bridges/<id>/tick": "Tick internal clock",
            "POST /api/bridges/<id>/experience": "Add experience",
            "GET /api/bridges/<id>/consciousness": "Get consciousness breakdown",
            "GET /api/stats": "System statistics",
            "GET /api/health": "Health check"
        },
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api', methods=['GET'])
def api_info():
    """API information"""
    return jsonify({
        "name": "Conscious Bridge Reloaded API",
        "version": "2.1.0",
        "status": "active",
        "active_bridges": len(active_bridges),
        "philosophical_shift": "From quantitative measurement to qualitative lived experience",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/bridges', methods=['GET'])
def list_bridges():
    """List all bridges"""
    bridges = []
    for bridge in active_bridges.values():
        bridges.append({
            "id": bridge.id,
            "name": bridge.name,
            "type": bridge.type,
            "maturity_stage": bridge.maturity_stage,
            "ticks": bridge.internal_clock.ticks,
            "consciousness_level": bridge.consciousness_level,
            "created_at": bridge.created_at,
            "is_active": bridge.is_active
        })
    
    return jsonify({
        "count": len(bridges),
        "bridges": bridges
    })


@app.route('/api/bridges/<bridge_id>', methods=['GET'])
def get_bridge(bridge_id):
    """Get bridge details"""
    if bridge_id not in active_bridges:
        return jsonify({"error": "Bridge not found"}), 404
    
    bridge = active_bridges[bridge_id]
    return jsonify(bridge.get_consciousness_breakdown())


@app.route('/api/bridges', methods=['POST'])
def create_bridge():
    """Create a new conscious bridge"""
    try:
        data = request.get_json()
        
        # Validate
        if not data or 'name' not in data:
            return jsonify({
                "error": "Bridge name is required"
            }), 400
        
        # Create bridge
        bridge = ConsciousBridgeReloaded(
            name=data['name'],
            bridge_type=data.get('type', 'general'),
            initial_personality=data.get('personality')
        )
        
        # Save to database
        db.save_bridge(bridge)
        
        # Add to active bridges
        active_bridges[bridge.id] = bridge
        
        return jsonify({
            "message": f"Bridge '{bridge.name}' created successfully",
            "bridge": {
                "id": bridge.id,
                "name": bridge.name,
                "type": bridge.type,
                "maturity_stage": bridge.maturity_stage,
                "created_at": bridge.created_at
            },
            "internal_time": {
                "ticks": bridge.internal_clock.ticks,
                "stage": bridge.internal_clock.get_stage()
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to create bridge: {str(e)}"
        }), 500


@app.route('/api/bridges/<bridge_id>/tick', methods=['POST'])
def tick_bridge(bridge_id):
    """Trigger an internal tick for a bridge"""
    try:
        if bridge_id not in active_bridges:
            return jsonify({"error": "Bridge not found"}), 404
        
        bridge = active_bridges[bridge_id]
        
        # Get tick parameters
        data = request.get_json() or {}
        experience_depth = data.get('experience_depth', 0.5)
        attention_level = data.get('attention_level', 0.7)
        
        # Process tick
        tick_result = bridge.tick(experience_depth, attention_level)
        
        # Save updated state
        db.save_bridge(bridge)
        
        return jsonify({
            "message": f"Consciousness tick processed for {bridge.name}",
            "tick_result": tick_result,
            "current_state": {
                "ticks": bridge.internal_clock.ticks,
                "maturity_stage": bridge.maturity_stage,
                "psychological_time": round(bridge.internal_clock.psychological_time, 2),
                "consciousness_level": round(bridge.consciousness_level, 3),
                "personality_traits": bridge.personality_core.traits
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to process tick: {str(e)}"
        }), 500


@app.route('/api/bridges/<bridge_id>/experience', methods=['POST'])
def add_experience(bridge_id):
    """Add a meaningful experience to bridge"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                "error": "Experience content is required"
            }), 400
        
        if bridge_id not in active_bridges:
            return jsonify({"error": "Bridge not found"}), 404
        
        bridge = active_bridges[bridge_id]
        
        # Add experience
        result = bridge.add_experience(
            content=data['content'],
            exp_type=data.get('type', 'general'),
            depth=data.get('depth', 0.5)
        )
        
        # Save updated state
        db.save_bridge(bridge)
        
        return jsonify({
            "message": "Experience added and processed",
            "experience": result["experience"],
            "insight": result["insight"],
            "updated_personality": result["new_personality"],
            "memory_stats": bridge.memory_system.get_stats()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to add experience: {str(e)}"
        }), 500


@app.route('/api/bridges/<bridge_id>/consciousness', methods=['GET'])
def get_consciousness(bridge_id):
    """Get detailed consciousness breakdown"""
    try:
        if bridge_id not in active_bridges:
            return jsonify({"error": "Bridge not found"}), 404
        
        bridge = active_bridges[bridge_id]
        return jsonify(bridge.get_consciousness_breakdown())
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get consciousness data: {str(e)}"
        }), 500


@app.route('/api/stats', methods=['GET'])
def system_stats():
    """Get system statistics"""
    # Database stats
    db_stats = db.get_stats()
    
    # Calculate totals from active bridges
    total_ticks = sum(b.internal_clock.ticks for b in active_bridges.values())
    avg_ticks = total_ticks / len(active_bridges) if active_bridges else 0
    
    # Stage distribution
    stages = {}
    for bridge in active_bridges.values():
        stage = bridge.maturity_stage
        stages[stage] = stages.get(stage, 0) + 1
    
    return jsonify({
        "system": "Conscious Bridge Reloaded",
        "timestamp": datetime.now().isoformat(),
        "statistics": {
            **db_stats,
            "active_bridges_count": len(active_bridges),
            "total_consciousness_ticks": total_ticks,
            "average_ticks_per_bridge": round(avg_ticks, 2),
            "maturity_distribution_active": stages
        },
        "philosophical_note": "Each tick represents a moment of lived experience, not just a unit of time"
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "flask": "running",
            "database": "connected",
            "active_bridges": len(active_bridges),
            "api_version": "2.1.0",
            "philosophy": "internal_time_active"
        }
    })


# ================ MAIN ================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌉 CONSCIOUS BRIDGE RELOADED - API SERVER")
    print("="*60)
    print("Philosophy: Internal time > External time")
    print(f"Active Bridges: {len(active_bridges)}")
    print(f"Database: conscious_bridges_reloaded.db")
    print(f"API Port: 5000")
    print("\n📚 Available Endpoints:")
    print("  GET  /                    - API documentation")
    print("  GET  /api/bridges         - List all bridges")
    print("  POST /api/bridges         - Create new bridge")
    print("  POST /api/bridges/<id>/tick - Process consciousness tick")
    print("  GET  /api/stats           - System statistics")
    print("  GET  /api/health          - Health check")
    print("\n🚀 Starting server...")
    print(f"👉 Access at: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
# ========== EVOLUTION API ENDPOINTS (v2.1.0) ==========
@app.route('/api/evolution/status', methods=['GET'])
def evolution_status():
    """Check evolution readiness - NEW in v2.1.0"""
    return jsonify({
        "status": "evolution_api_active",
        "version": "2.1.0",
        "endpoints": {
            "status": "/api/evolution/status",
            "snapshot": "/api/evolution/snapshot",
            "log": "/api/evolution/log", 
            "history": "/api/evolution/history"
        },
        "description": "Conscious Bridge Evolution API for v3 preparation",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🌉 Conscious Bridge Reloaded v2.1.0 - Evolution API Active!")
    print("📡 Server running on http://localhost:5000")
    print("🔗 Evolution API: http://localhost:5000/api/evolution/status")
    app.run(host='0.0.0.0', port=5000, debug=True)
