from flask import Flask, jsonify, request
from flask_cors import CORS
from jarvis.config import Config
from jarvis.ai_engine import JarvisAI
from jarvis.core.system import JarvisOS

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

jarvis_ai = JarvisAI()
jarvis_os = JarvisOS()

# Inicializa sistema
jarvis_os.initialize_systems()

# ============= ENDPOINTS BÁSICOS =============

@app.route("/", methods=["GET"])
def home():
    """Endpoint inicial"""
    return jsonify({
        "name": Config.JARVIS_NAME,
        "greeting": Config.JARVIS_GREETING,
        "status": "Online and ready to assist",
        "version": "JARVIS v2.0 - Cognitive Operating System"
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
        response = jarvis_ai.process_request(user_message)

        # Processa através do sistema operacional
        os_response = jarvis_os.process_request({
            "type": "CONVERSATION",
            "input": user_message
        })

        return jsonify({
            "user": user_message,
            "jarvis": response,
            "cognitive_state": os_response["cognitive_assessment"],
            "emotion": os_response["emotion"],
            "autonomy_level": os_response["autonomy_level"],
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
        "history": jarvis_ai.get_conversation_history()
    })

@app.route("/api/reset", methods=["POST"])
def reset():
    """Reseta a conversa"""
    jarvis_ai.reset_conversation()
    return jsonify({
        "status": "Conversation reset",
        "greeting": Config.JARVIS_GREETING
    })

# ============= ENDPOINTS SISTEMA OPERACIONAL =============

@app.route("/api/system/status", methods=["GET"])
def system_status():
    """Retorna status completo do sistema"""
    return jsonify(jarvis_os.get_system_status())

@app.route("/api/system/monitor", methods=["GET"])
def monitor_systems():
    """Monitora todos os sistemas"""
    return jsonify(jarvis_os.monitor_all_systems())

@app.route("/api/system/initialize", methods=["POST"])
def initialize():
    """Reinicializa todos os subsistemas"""
    result = jarvis_os.initialize_systems()
    return jsonify(result)

# ============= ENDPOINTS SEGURANÇA =============

@app.route("/api/security/threat-assessment", methods=["POST"])
def threat_assessment():
    """Analisa ameaça"""
    data = request.get_json() or {}
    threat = jarvis_os.threat_assessment(data)
    return jsonify(threat)

@app.route("/api/security/status", methods=["GET"])
def security_status():
    """Retorna status de segurança"""
    return jsonify(jarvis_os.security.get_security_status())

# ============= ENDPOINTS MEMÓRIA =============

@app.route("/api/memory/stats", methods=["GET"])
def memory_stats():
    """Retorna estatísticas de memória"""
    return jsonify(jarvis_os.memory.get_memory_stats())

@app.route("/api/memory/correlations", methods=["GET"])
def memory_correlations():
    """Retorna correlações de eventos"""
    return jsonify({
        "correlations": jarvis_os.memory.correlate_events()
    })

# ============= ENDPOINTS COGNIÇÃO =============

@app.route("/api/cognition/state", methods=["GET"])
def cognitive_state():
    """Retorna estado cognitivo"""
    return jsonify(jarvis_os.cognition.get_cognitive_state())

@app.route("/api/cognition/evolve", methods=["POST"])
def evolve_cognition():
    """Evoluir cognitivamente"""
    evolution = jarvis_os.evolve()
    return jsonify(evolution)

# ============= ENDPOINTS NAVEGAÇÃO =============

@app.route("/api/navigation/gps", methods=["POST"])
def update_gps():
    """Atualiza posição GPS"""
    data = request.get_json()
    position = jarvis_os.navigation.update_gps(
        device_id=data.get("device_id", "device1"),
        latitude=data.get("latitude", 0),
        longitude=data.get("longitude", 0),
        altitude=data.get("altitude", 0)
    )
    return jsonify(position)

@app.route("/api/navigation/route", methods=["POST"])
def plan_route():
    """Planeja rota de voo"""
    data = request.get_json()
    route = jarvis_os.navigation.plan_flight_route(
        start=tuple(data.get("start", [0, 0])),
        destination=tuple(data.get("destination", [0, 0]))
    )
    return jsonify(route)

@app.route("/api/navigation/track", methods=["POST"])
def track_target():
    """Rastreia alvo"""
    data = request.get_json()
    tracker = jarvis_os.navigation.track_target(
        target_id=data.get("target_id", "target1"),
        initial_position=tuple(data.get("position", [0, 0]))
    )
    return jsonify(tracker)

# ============= ENDPOINTS ENGENHARIA =============

@app.route("/api/engineering/design-armor", methods=["POST"])
def design_armor():
    """Projeta armadura"""
    data = request.get_json() or {}
    design = jarvis_os.engineering.design_armor(data)
    return jsonify(design)

@app.route("/api/engineering/simulate", methods=["POST"])
def run_simulation():
    """Executa simulação física"""
    data = request.get_json()
    simulation = jarvis_os.engineering.run_physics_simulation(
        design_id=data.get("design_id"),
        test_parameters=data.get("parameters", {})
    )
    return jsonify(simulation)

@app.route("/api/engineering/status", methods=["GET"])
def engineering_status():
    """Status do departamento de engenharia"""
    return jsonify(jarvis_os.engineering.get_engineering_status())

# ============= ENDPOINTS BIOMETRIA =============

@app.route("/api/biometrics/enroll", methods=["POST"])
def enroll_user():
    """Matricula usuário com biometria"""
    data = request.get_json()
    enrollment = jarvis_os.biometrics.enroll_user(
        user_id=data.get("user_id"),
        biometric_data=data.get("biometric_data", {})
    )
    return jsonify(enrollment)

@app.route("/api/biometrics/verify", methods=["POST"])
def verify_identity():
    """Verifica identidade"""
    data = request.get_json()
    result = jarvis_os.biometrics.verify_identity(
        user_id=data.get("user_id"),
        biometric_sample=data.get("biometric_sample", {})
    )
    return jsonify(result)

# ============= ENDPOINTS AUTOMAÇÃO =============

@app.route("/api/automation/schedule", methods=["POST"])
def schedule_task():
    """Agenda tarefa automática"""
    data = request.get_json()

    # Simula ação
    def dummy_action(params):
        return {"result": "Task executed"}

    task = jarvis_os.automation.schedule_automation(
        task_name=data.get("task_name"),
        action=dummy_action,
        trigger=data.get("trigger", "immediate"),
        parameters=data.get("parameters")
    )
    return jsonify(task)

@app.route("/api/automation/workflow", methods=["POST"])
def create_workflow():
    """Cria workflow de automação"""
    data = request.get_json()
    workflow = jarvis_os.automation.create_workflow(
        workflow_name=data.get("workflow_name"),
        steps=data.get("steps", [])
    )
    return jsonify(workflow)

# ============= ENDPOINTS ANALYTICS =============

@app.route("/api/analytics/process-stream", methods=["POST"])
def process_stream():
    """Processa fluxo de dados"""
    data = request.get_json()
    analysis = jarvis_os.analytics.process_data_stream(
        stream_name=data.get("stream_name"),
        data_points=data.get("data_points", [])
    )
    return jsonify(analysis)

# ============= ENDPOINTS MISSÕES =============

@app.route("/api/mission/execute", methods=["POST"])
def execute_mission():
    """Executa missão"""
    data = request.get_json()
    mission = jarvis_os.execute_mission(data)
    return jsonify(mission)

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist",
        "status": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": str(error),
        "status": 500
    }), 500

if __name__ == "__main__":
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
