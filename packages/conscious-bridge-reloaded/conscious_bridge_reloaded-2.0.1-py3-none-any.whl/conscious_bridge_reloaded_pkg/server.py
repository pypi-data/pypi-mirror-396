from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🌉 Conscious Bridge Test</h1>
    <p>System is loading...</p>
    <p><a href="/api/health">Health Check</a></p>
    '''

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'time': datetime.now().isoformat(),
        'message': 'Core system initializing'
    })

if __name__ == '__main__':
    print("🚀 Starting test server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
