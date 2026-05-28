from flask import Flask, jsonify, request
from flask_cors import CORS
from jarvis.config import Config
from jarvis.ai_engine import JarvisAI

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

jarvis = JarvisAI()

@app.route("/", methods=["GET"])
def home():
    """Endpoint inicial"""
    return jsonify({
        "name": Config.JARVIS_NAME,
        "greeting": Config.JARVIS_GREETING,
        "status": "Online and ready to assist"
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """Processa mensagens do usuário"""
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Message required"}), 400

    user_message = data.get("message").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        response = jarvis.process_request(user_message)
        return jsonify({
            "user": user_message,
            "jarvis": response,
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}",
            "status": "error"
        }), 500

@app.route("/api/history", methods=["GET"])
def get_history():
    """Retorna o histórico da conversa"""
    return jsonify({
        "history": jarvis.get_conversation_history()
    })

@app.route("/api/reset", methods=["POST"])
def reset():
    """Reseta a conversa"""
    jarvis.reset_conversation()
    return jsonify({
        "status": "Conversation reset",
        "greeting": Config.JARVIS_GREETING
    })

if __name__ == "__main__":
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
