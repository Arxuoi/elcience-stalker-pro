#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
El Cienco Stalker Pro - Backend Server
Instagram & TikTok OSINT API
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ig_osint import InstagramOSINT
from tt_osint import TikTokOSINT
from database import Database
from utils import print_banner, Colors

# Initialize Flask
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize modules
ig_osint = InstagramOSINT()
tt_osint = TikTokOSINT()
db = Database()

# ==================== STATIC FILES ====================
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# ==================== API ENDPOINTS ====================

# ---------- STATUS ----------
@app.route('/api/status', methods=['GET'])
def get_status():
    """Cek status API"""
    return jsonify({
        "success": True,
        "status": "online",
        "version": "2.0.0",
        "name": "El Cienco Stalker Pro",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "instagram": "/api/ig/profile/<username>",
            "tiktok": "/api/tt/profile/<username>",
            "history": "/api/history",
            "favorites": "/api/favorites",
            "stats": "/api/stats"
        }
    })

# ---------- INSTAGRAM ----------
@app.route('/api/ig/profile/<username>', methods=['GET'])
def ig_profile(username):
    """Get Instagram profile"""
    result = ig_osint.get_profile(username)
    
    # Add to history if success
    if result["success"]:
        db.add_history({
            "id": result["data"]["id"],
            "platform": "instagram",
            "username": username,
            "full_name": result["data"]["full_name"],
            "followers": result["data"]["followers"],
            "is_verified": result["data"]["is_verified"],
            "profile_pic": result["data"]["profile_pic_url"]
        })
    
    return jsonify(result)

@app.route('/api/ig/posts/<username>', methods=['GET'])
def ig_posts(username):
    """Get Instagram posts"""
    count = request.args.get('count', 12, type=int)
    result = ig_osint.get_posts(username, count)
    return jsonify(result)

@app.route('/api/ig/stories/<username>', methods=['GET'])
def ig_stories(username):
    """Get Instagram stories"""
    result = ig_osint.get_stories(username)
    return jsonify(result)

@app.route('/api/ig/compare', methods=['POST'])
def ig_compare():
    """Compare two Instagram profiles"""
    data = request.json
    username1 = data.get('username1', '')
    username2 = data.get('username2', '')
    
    if not username1 or not username2:
        return jsonify({"success": False, "error": "Both usernames required"}), 400
    
    result = ig_osint.compare_profiles(username1, username2)
    return jsonify(result)

# ---------- TIKTOK ----------
@app.route('/api/tt/profile/<username>', methods=['GET'])
def tt_profile(username):
    """Get TikTok profile"""
    result = tt_osint.get_profile(username)
    
    # Add to history if success
    if result["success"]:
        db.add_history({
            "id": result["data"]["id"],
            "platform": "tiktok",
            "username": username,
            "full_name": result["data"].get("nickname", username),
            "followers": result["data"].get("followers", 0),
            "is_verified": result["data"].get("verified", False),
            "profile_pic": result["data"].get("profile_pic", "")
        })
    
    return jsonify(result)

@app.route('/api/tt/videos/<username>', methods=['GET'])
def tt_videos(username):
    """Get TikTok videos"""
    count = request.args.get('count', 10, type=int)
    result = tt_osint.get_videos(username, count)
    return jsonify(result)

@app.route('/api/tt/compare', methods=['POST'])
def tt_compare():
    """Compare two TikTok profiles"""
    data = request.json
    username1 = data.get('username1', '')
    username2 = data.get('username2', '')
    
    if not username1 or not username2:
        return jsonify({"success": False, "error": "Both usernames required"}), 400
    
    result = tt_osint.compare_profiles(username1, username2)
    return jsonify(result)

# ---------- BATCH PROCESSING ----------
@app.route('/api/batch', methods=['POST'])
def batch_process():
    """Process multiple usernames at once"""
    data = request.json
    platform = data.get('platform', 'instagram')
    usernames = data.get('usernames', [])
    
    if not usernames:
        return jsonify({"success": False, "error": "No usernames provided"}), 400
    
    results = []
    for username in usernames:
        if platform == 'instagram':
            result = ig_osint.get_profile(username.strip())
        else:
            result = tt_osint.get_profile(username.strip())
        results.append(result)
    
    return jsonify({
        "success": True,
        "platform": platform,
        "total": len(usernames),
        "successful": len([r for r in results if r.get("success")]),
        "results": results
    })

# ---------- HISTORY ----------
@app.route('/api/history', methods=['GET'])
def get_history():
    """Get search history"""
    limit = request.args.get('limit', 50, type=int)
    platform = request.args.get('platform', None)
    history = db.get_history(limit, platform)
    return jsonify({"success": True, "data": history})

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Clear all history"""
    result = db.clear_history()
    return jsonify(result)

@app.route('/api/history/<item_id>', methods=['DELETE'])
def delete_history_item(item_id):
    """Delete single history item"""
    result = db.delete_history_item(item_id)
    return jsonify(result)

# ---------- FAVORITES ----------
@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """Get all favorites"""
    platform = request.args.get('platform', None)
    favorites = db.get_favorites(platform)
    return jsonify({"success": True, "data": favorites})

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """Add profile to favorites"""
    data = request.json
    result = db.add_favorite(data)
    return jsonify(result)

@app.route('/api/favorites/<platform>/<username>', methods=['DELETE'])
def remove_favorite(platform, username):
    """Remove from favorites"""
    result = db.remove_favorite(username, platform)
    return jsonify(result)

@app.route('/api/favorites/check/<platform>/<username>', methods=['GET'])
def check_favorite(platform, username):
    """Check if profile is favorited"""
    is_fav = db.is_favorited(username, platform)
    return jsonify({"success": True, "is_favorited": is_fav})

# ---------- STATS ----------
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get usage statistics"""
    stats = db.get_stats()
    return jsonify({"success": True, "data": stats})

@app.route('/api/stats/reset', methods=['POST'])
def reset_stats():
    """Reset statistics"""
    result = db.reset_stats()
    return jsonify(result)

# ---------- SEARCH ----------
@app.route('/api/search', methods=['GET'])
def search_history():
    """Search within history"""
    query = request.args.get('q', '').lower()
    platform = request.args.get('platform', None)
    
    history = db.get_history(100, platform)
    
    if query:
        history = [h for h in history if 
                   query in h.get('username', '').lower() or 
                   query in h.get('full_name', '').lower()]
    
    return jsonify({"success": True, "query": query, "data": history})

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    print_banner()
    print(f"{Colors
