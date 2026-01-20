from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# In-memory storage cho player data
player_data = {}

def get_time_ago(timestamp):
    """Tính thời gian từ lần update cuối"""
    now = datetime.now()
    diff = (now - timestamp).total_seconds()
    minutes = int(diff / 60)
    
    if minutes < 1:
        return 'just now'
    elif minutes == 1:
        return '1 minute ago'
    elif minutes < 60:
        return f'{minutes} minutes ago'
    
    hours = int(minutes / 60)
    if hours == 1:
        return '1 hour ago'
    elif hours < 24:
        return f'{hours} hours ago'
    
    days = int(hours / 24)
    if days == 1:
        return '1 day ago'
    return f'{days} days ago'

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        'message': 'Blox Fruits Player Tracking API',
        'endpoints': {
            'POST /api/data': 'Submit player data',
            'GET /api/data/trackstats': 'Get all player stats',
            'GET /api/data/<username>': 'Get specific player stats',
            'DELETE /api/data/<username>': 'Delete player data'
        }
    })

@app.route('/api/data', methods=['POST'])
def post_data():
    """
    POST endpoint để nhận data từ script
    Tự động UPDATE data nếu username đã tồn tại
    """
    try:
        data = request.get_json()
        
        # Validate username
        if not data or 'username' not in data:
            return jsonify({
                'error': 'Username is required'
            }), 400
        
        username = data.pop('username')
        
        # UPDATE hoặc THÊM MỚI player data
        # Nếu username đã tồn tại -> XÓA data cũ và UPDATE data mới
        player_data[username] = {
            'timestamp': datetime.now(),
            'data': data
        }
        
        action = 'updated' if username in player_data else 'created'
        
        return jsonify({
            'success': True,
            'message': f'Data {action} for {username}',
            'username': username,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/data/trackstats', methods=['GET'])
def get_trackstats():
    """GET endpoint để lấy tất cả player stats"""
    try:
        formatted_data = {}
        
        for username, info in player_data.items():
            formatted_data[username] = {
                'last_update': get_time_ago(info['timestamp']),
                'data': info['data']
            }
        
        return jsonify(formatted_data), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/data/<username>', methods=['GET'])
def get_player_data(username):
    """GET endpoint để lấy data của một player cụ thể"""
    try:
        if username not in player_data:
            return jsonify({
                'error': 'Player not found'
            }), 404
        
        info = player_data[username]
        return jsonify({
            username: {
                'last_update': get_time_ago(info['timestamp']),
                'data': info['data']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/data/<username>', methods=['DELETE'])
def delete_player_data(username):
    """DELETE endpoint để xóa data của player"""
    try:
        if username not in player_data:
            return jsonify({
                'error': 'Player not found'
            }), 404
        
        del player_data[username]
        
        return jsonify({
            'success': True,
            'message': f'Data deleted for {username}'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)