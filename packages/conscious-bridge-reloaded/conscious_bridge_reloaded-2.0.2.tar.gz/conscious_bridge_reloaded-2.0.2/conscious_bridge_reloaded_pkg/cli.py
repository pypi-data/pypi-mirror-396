#!/usr/bin/env python3
"""
Conscious Bridge RELOADED - Command Line Interface
Version: 2.0.1
"""

import argparse
import sys
import os
from flask import Flask, jsonify

VERSION = "2.0.1"

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Route الرئيسية
    @app.route('/')
    def home():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Conscious Bridge RELOADED</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { background: #4CAF50; color: white; padding: 20px; border-radius: 5px; }
                .status { background: #f5f5f5; padding: 15px; margin: 20px 0; border-left: 4px solid #4CAF50; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Conscious Bridge RELOADED v''' + VERSION + '''</h1>
                    <p>Mobile AI Consciousness System</p>
                </div>
                <div class="status">
                    <h3>System Status: <span style="color:green">● ONLINE</span></h3>
                    <p>Internal Clock: Active</p>
                    <p>Personality Core: Initialized</p>
                    <p>Bridge Systems: Ready</p>
                </div>
                <p>API Endpoints:</p>
                <ul>
                    <li><a href="/api/status">/api/status</a> - System status</li>
                    <li><a href="/health">/health</a> - Health check</li>
                    <li><a href="/api/clock">/api/clock</a> - Internal clock</li>
                </ul>
            </div>
        </body>
        </html>
        '''
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "service": "conscious-bridge-reloaded",
            "version": VERSION
        })
    
    @app.route('/api/status')
    def api_status():
        return jsonify({
            "system": "Conscious Bridge RELOADED",
            "version": VERSION,
            "status": "operational",
            "components": {
                "internal_clock": "active",
                "personality_core": "initialized",
                "memory_system": "ready",
                "bridge_engine": "online"
            }
        })
    
    @app.route('/api/clock')
    def internal_clock():
        import time
        return jsonify({
            "timestamp": time.time(),
            "consciousness_ticks": int(time.time() * 1000),
            "formatted": time.ctime()
        })
    
    return app

def start_server(host="0.0.0.0", port=5050, debug=False):
    """Start the Flask server"""
    app = create_app()
    
    print("=" * 50)
    print(f"🚀 Conscious Bridge RELOADED v{VERSION}")
    print(f"🌐 Mobile AI Consciousness System")
    print("=" * 50)
    print(f"📊 Configuration:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print()
    print(f"🌐 Access URLs:")
    print(f"   Local: http://localhost:{port}")
    print(f"   Network: http://{host if host != '0.0.0.0' else '127.0.0.1'}:{port}")
    print()
    print("📡 Starting Flask server...")
    print("   Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        app.run(host=host, port=port, debug=debug, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return 1
    
    return 0

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description=f"Conscious Bridge RELOADED v{VERSION}",
        epilog="Example: cb-reloaded --port=5050 --debug"
    )
    
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=5050,
        help="Port to run server on (default: 5050)"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show version information"
    )
    
    args = parser.parse_args()
    
    if args.version:
        print(f"Conscious Bridge RELOADED v{VERSION}")
        print("Mobile AI Consciousness System for Android/Termux")
        print("Author: Rite of Renaissance")
        return 0
    
    return start_server(
        host=args.host,
        port=args.port,
        debug=args.debug
    )

if __name__ == "__main__":
    sys.exit(main())
