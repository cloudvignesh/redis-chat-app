import json
import os
import bcrypt

from flask import jsonify, session, request

from chat.app import app
from chat import utils


# Return our SPA application.
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return app.send_static_file("index.html")


# This check if the session contains the valid user credentials
@app.route("/me")
def get_me():
    user = session.get("user", None)
    return jsonify(user)


@app.route("/links")
def get_links():
    """Returns JSON with available deploy links"""
    # Return github link to the repo
    try:
        repo = open(os.path.join(app.root_path, "../repo.json"))
        data = json.load(repo)
        return jsonify(data)
    except:
        return jsonify({"github": "https://github.com/redis-developer/basic-redis-chat-app-demo-python"})


@app.route("/login", methods=["POST"])
def login():
    """Simple login for demo purposes"""
    try:
        data = request.get_json()
        username = data["username"]
        password = data["password"]

        username_key = utils.make_username_key(username)
        user_exists = utils.redis_client.exists(username_key)
        
        if not user_exists:
            return jsonify({"error": "User doesn't exist"}), 404

        # Get user ID from username key
        user_id_data = utils.redis_client.hgetall(username_key)
        user_id = user_id_data.get("id")
        
        if not user_id:
            return jsonify({"error": "Invalid user data"}), 404
            
        # Get user data from user key
        user_key = f"user:{user_id}"
        user_data = utils.redis_client.hgetall(user_key)
        stored_password = user_data.get("password", "")
        
        if not stored_password:
            return jsonify({"error": "Invalid user data"}), 404
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            session["user"] = {
                "id": user_id,
                "username": username
            }
            return jsonify({
                "id": user_id,
                "username": username
            })
        else:
            return jsonify({"error": "Invalid password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"status": "logged out"})


@app.route("/users/online")
def get_online_users():
    """Return list of online users (simplified)"""
    # For demo, return the 4 demo users
    demo_users = [
        {"id": "37", "username": "Pablo", "avatar": "2.jpg"},
        {"id": "38", "username": "Joe", "avatar": "1.jpg"}, 
        {"id": "39", "username": "Mary", "avatar": "3.jpg"},
        {"id": "40", "username": "Alex", "avatar": "4.jpg"}
    ]
    return jsonify(demo_users)


@app.route("/rooms")
def get_user_rooms():
    """Get user's chat rooms/conversations"""
    current_user = session.get("user")
    if not current_user:
        return jsonify([]), 401
    
    # Create sample chat rooms for the logged-in user
    current_user_id = current_user.get("id")
    sample_rooms = []
    
    # Create rooms with other demo users
    demo_users = [
        {"id": "37", "username": "Pablo"},
        {"id": "38", "username": "Joe"}, 
        {"id": "39", "username": "Mary"},
        {"id": "40", "username": "Alex"}
    ]
    
    # General chat room
    sample_rooms.append({
        "id": "0",
        "name": "General Chat",
        "type": "general",
        "lastMessage": "Welcome to the chat!",
        "timestamp": "2025-11-20T18:00:00Z",
        "unreadCount": 0
    })
    
    # Create private rooms with other users
    for user in demo_users:
        if user["id"] != current_user_id:
            room_id = f"{min(current_user_id, user['id'])}_{max(current_user_id, user['id'])}"
            sample_rooms.append({
                "id": room_id,
                "name": user["username"], 
                "type": "private",
                "userId": user["id"],
                "avatar": f"{int(user['id']) % 10}.jpg",
                "lastMessage": f"Chat with {user['username']}",
                "timestamp": "2025-11-20T17:00:00Z",
                "unreadCount": 0
            })
    
    return jsonify(sample_rooms)


@app.route("/rooms/<room_id>")
def get_room_messages(room_id):
    """Get messages for a room (simplified)"""
    current_user = session.get("user")
    if not current_user:
        return jsonify([]), 401
    
    # Sample messages based on room type
    if room_id == "0":
        # General chat messages
        sample_messages = [
            {
                "id": "1",
                "from": "Pablo",
                "fromUserId": "37", 
                "message": "Hello everyone! Welcome to the general chat!",
                "timestamp": "2025-11-20T17:00:00Z"
            },
            {
                "id": "2", 
                "from": "Joe",
                "fromUserId": "38",
                "message": "Hi Pablo! This chat app looks great!",
                "timestamp": "2025-11-20T17:05:00Z"
            },
            {
                "id": "3",
                "from": "Mary", 
                "fromUserId": "39",
                "message": "Hello everyone! How's the demo going?",
                "timestamp": "2025-11-20T17:10:00Z"
            }
        ]
    else:
        # Private chat messages
        sample_messages = [
            {
                "id": f"{room_id}_1",
                "from": "Pablo",
                "fromUserId": "37",
                "message": "Hey! How are you doing?",
                "timestamp": "2025-11-20T16:30:00Z"
            },
            {
                "id": f"{room_id}_2", 
                "from": "Joe",
                "fromUserId": "38",
                "message": "I'm doing great! Thanks for asking.",
                "timestamp": "2025-11-20T16:35:00Z"
            }
        ]
    
    return jsonify(sample_messages)


@app.route("/rooms/<room_id>/messages", methods=["POST"])
def send_message(room_id):
    """Send a message to a room"""
    current_user = session.get("user")
    if not current_user:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    message_content = data.get("message", "").strip()
    
    if not message_content:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    # In a real app, you'd save this to Redis
    # For demo, just return the message as if it was sent
    new_message = {
        "id": f"msg_{room_id}_{int(__import__('time').time())}",
        "from": current_user["username"],
        "fromUserId": current_user["id"],
        "message": message_content,
        "timestamp": __import__('datetime').datetime.now().isoformat() + "Z"
    }
    
    return jsonify(new_message), 201


@app.route("/stream")
def get_stream():
    """Get message stream (simplified)"""
    # Return recent messages across all rooms
    current_user = session.get("user")
    if not current_user:
        return jsonify([])
    
    recent_messages = [
        {
            "id": "stream_1",
            "roomId": "0", 
            "from": "Pablo",
            "fromUserId": "37",
            "message": "Welcome to the chat app!",
            "timestamp": "2025-11-20T17:30:00Z"
        },
        {
            "id": "stream_2",
            "roomId": "37_38",
            "from": "Joe", 
            "fromUserId": "38",
            "message": "Hey Pablo, how's the demo?",
            "timestamp": "2025-11-20T17:45:00Z"
        }
    ]
    return jsonify(recent_messages)


@app.route("/users/<user_id>")
def get_user_info(user_id):
    """Get user information"""
    demo_users = {
        "37": {"id": "37", "username": "Pablo", "avatar": "2.jpg", "online": True},
        "38": {"id": "38", "username": "Joe", "avatar": "1.jpg", "online": True},
        "39": {"id": "39", "username": "Mary", "avatar": "3.jpg", "online": True},
        "40": {"id": "40", "username": "Alex", "avatar": "4.jpg", "online": True}
    }
    
    user = demo_users.get(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404


@app.route("/socket.io/")
def socketio_placeholder():
    """Placeholder for SocketIO to prevent 404s"""
    return jsonify({"message": "SocketIO not implemented in this simplified version"})


@app.route("/test")
def test():
    return jsonify({"status": "ok", "message": "Chat app is running!"})


@app.route("/debug-redis")
def debug_redis():
    """Debug endpoint to check Redis data"""
    try:
        # Check what keys exist
        all_keys = utils.redis_client.keys("*")
        
        debug_info = {
            "total_users": utils.redis_client.get("total_users"),
            "all_keys": [k for k in all_keys],
            "user_data": {}
        }
        
        # Get data for Pablo as example
        username_key = "username:Pablo"
        if utils.redis_client.exists(username_key):
            debug_info["pablo_username_data"] = utils.redis_client.hgetall(username_key)
            
            user_id = utils.redis_client.hget(username_key, "id")
            if user_id:
                user_key = f"user:{user_id}"
                debug_info["pablo_user_data"] = utils.redis_client.hgetall(user_key)
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500