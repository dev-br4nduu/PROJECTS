from flask import Flask, jsonify, request
from flask_cors import CORS
from jarvis.config import Config
from jarvis.ai_engine import JarvisAI
from jarvis.core.system import JarvisOS
from jarvis.voice import VoiceInterface
from jarvis.vision import ComputerVision
from jarvis.integrations import ExternalIntegrations
from jarvis.core.learning_persistence import LearningPersistence

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

jarvis_ai = JarvisAI()
jarvis_os = JarvisOS()
jarvis_voice = VoiceInterface()
jarvis_vision = ComputerVision()
jarvis_integrations = ExternalIntegrations()
jarvis_learning = LearningPersistence()

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

# ============= ENDPOINTS VOICE (FASE 2.5) =============

@app.route("/api/voice/speech-to-text", methods=["POST"])
def speech_to_text():
    """Converte fala em texto"""
    if "audio" not in request.files:
        return jsonify({"error": "Audio file required"}), 400

    audio_data = request.files["audio"].read()
    language = request.form.get("language", "en-US")

    transcription = jarvis_voice.speech_to_text(audio_data, language)
    return jsonify(transcription)

@app.route("/api/voice/text-to-speech", methods=["POST"])
def text_to_speech():
    """Sintetiza texto em fala"""
    data = request.get_json()
    text = data.get("text")
    tone = data.get("tone", "sophisticated")

    if not text:
        return jsonify({"error": "Text required"}), 400

    speech = jarvis_voice.text_to_speech(text, tone)
    return jsonify(speech)

@app.route("/api/voice/process-command", methods=["POST"])
def process_voice_command():
    """Processa comando de voz"""
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "Text required"}), 400

    command = jarvis_voice.process_voice_command(text)
    return jsonify(command)

@app.route("/api/voice/detect-sarcasm", methods=["POST"])
def detect_sarcasm():
    """Detecta sarcasmo na fala"""
    data = request.get_json()
    text = data.get("text")
    tone_info = data.get("tone_info", {})

    if not text:
        return jsonify({"error": "Text required"}), 400

    sarcasm = jarvis_voice.detect_sarcasm_in_speech(text, tone_info)
    return jsonify(sarcasm)

@app.route("/api/voice/enroll-voice", methods=["POST"])
def enroll_voice():
    """Matricula perfil de voz do usuário"""
    user_id = request.form.get("user_id")
    voice_samples = request.files.getlist("voice_samples")

    if not user_id:
        return jsonify({"error": "User ID required"}), 400

    audio_data = [f.read() for f in voice_samples]
    profile = jarvis_voice.create_voice_profile(user_id, audio_data)
    return jsonify(profile)

@app.route("/api/voice/verify-identity", methods=["POST"])
def verify_voice_identity():
    """Verifica identidade por voz"""
    user_id = request.form.get("user_id")

    if "audio" not in request.files or not user_id:
        return jsonify({"error": "User ID and audio required"}), 400

    audio_data = request.files["audio"].read()
    verification = jarvis_voice.verify_voice_identity(user_id, audio_data)
    return jsonify(verification)

@app.route("/api/voice/status", methods=["GET"])
def voice_status():
    """Status do sistema de voz"""
    return jsonify(jarvis_voice.get_voice_status())

# ============= ENDPOINTS VISION (FASE 2.5) =============

@app.route("/api/vision/analyze-image", methods=["POST"])
def analyze_image():
    """Analisa imagem com detecção de objetos"""
    if "image" not in request.files:
        return jsonify({"error": "Image file required"}), 400

    image_data = request.files["image"].read()
    analysis_type = request.form.get("type", "full")

    analysis = jarvis_vision.analyze_image(image_data, analysis_type)
    return jsonify(analysis)

@app.route("/api/vision/detect-objects", methods=["POST"])
def detect_objects():
    """Detecta objetos em imagem"""
    if "image" not in request.files:
        return jsonify({"error": "Image file required"}), 400

    image_data = request.files["image"].read()
    detections = jarvis_vision.detect_objects(image_data)
    return jsonify(detections)

@app.route("/api/vision/recognize-faces", methods=["POST"])
def recognize_faces():
    """Reconhece rostos em imagem"""
    if "image" not in request.files:
        return jsonify({"error": "Image file required"}), 400

    image_data = request.files["image"].read()
    faces = jarvis_vision.recognize_faces(image_data)
    return jsonify(faces)

@app.route("/api/vision/understand-scene", methods=["POST"])
def understand_scene():
    """Compreende cena em imagem"""
    if "image" not in request.files:
        return jsonify({"error": "Image file required"}), 400

    image_data = request.files["image"].read()
    scene = jarvis_vision.understand_scene(image_data)
    return jsonify(scene)

@app.route("/api/vision/identify-threats", methods=["POST"])
def identify_threats():
    """Identifica ameaças em imagem"""
    if "image" not in request.files:
        return jsonify({"error": "Image file required"}), 400

    image_data = request.files["image"].read()
    threats = jarvis_vision.identify_threats(image_data)
    return jsonify(threats)

@app.route("/api/vision/process-video", methods=["POST"])
def process_video():
    """Processa fluxo de vídeo"""
    data = request.get_json()
    stream_id = data.get("stream_id")
    duration = data.get("duration", 30)

    if not stream_id:
        return jsonify({"error": "Stream ID required"}), 400

    processing = jarvis_vision.process_video_feed(stream_id, duration)
    return jsonify(processing)

@app.route("/api/vision/status", methods=["GET"])
def vision_status():
    """Status do sistema de visão"""
    return jsonify(jarvis_vision.get_vision_status())

# ============= ENDPOINTS INTEGRAÇÕES (FASE 2.5) =============

@app.route("/api/integrations/connect-weather", methods=["POST"])
def connect_weather():
    """Integra serviço de clima"""
    data = request.get_json()
    api_key = data.get("api_key")

    if not api_key:
        return jsonify({"error": "API key required"}), 400

    service = jarvis_integrations.connect_weather_service(api_key)
    return jsonify(service)

@app.route("/api/integrations/get-weather", methods=["GET"])
def get_weather():
    """Obtém informações de tempo"""
    location = request.args.get("location", "São Paulo")
    weather = jarvis_integrations.get_weather(location)
    return jsonify(weather)

@app.route("/api/integrations/connect-news", methods=["POST"])
def connect_news():
    """Integra serviço de notícias"""
    data = request.get_json()
    api_key = data.get("api_key")

    if not api_key:
        return jsonify({"error": "API key required"}), 400

    service = jarvis_integrations.connect_news_service(api_key)
    return jsonify(service)

@app.route("/api/integrations/get-news", methods=["GET"])
def get_news():
    """Obtém notícias"""
    topic = request.args.get("topic")
    limit = int(request.args.get("limit", 10))
    news = jarvis_integrations.get_news(topic, limit)
    return jsonify(news)

@app.route("/api/integrations/register-iot", methods=["POST"])
def register_iot():
    """Registra dispositivo IoT"""
    data = request.get_json()
    device_id = data.get("device_id")
    device_type = data.get("device_type")
    capabilities = data.get("capabilities", [])

    if not device_id or not device_type:
        return jsonify({"error": "Device ID and type required"}), 400

    device = jarvis_integrations.register_iot_device(device_id, device_type, capabilities)
    return jsonify(device)

@app.route("/api/integrations/send-iot-command", methods=["POST"])
def send_iot_command():
    """Envia comando para dispositivo IoT"""
    data = request.get_json()
    device_id = data.get("device_id")
    command = data.get("command")

    if not device_id or not command:
        return jsonify({"error": "Device ID and command required"}), 400

    execution = jarvis_integrations.send_command_to_iot(
        device_id, command, data.get("parameters")
    )
    return jsonify(execution)

@app.route("/api/integrations/register-webhook", methods=["POST"])
def register_webhook():
    """Registra webhook"""
    data = request.get_json()
    event_type = data.get("event_type")
    webhook_url = data.get("webhook_url")

    if not event_type or not webhook_url:
        return jsonify({"error": "Event type and webhook URL required"}), 400

    webhook = jarvis_integrations.register_webhook(event_type, webhook_url)
    return jsonify(webhook)

@app.route("/api/integrations/status", methods=["GET"])
def integration_status():
    """Status das integrações"""
    return jsonify(jarvis_integrations.get_integration_status())

# ============= ENDPOINTS APRENDIZADO (FASE 2.5) =============

@app.route("/api/learning/create-profile", methods=["POST"])
def create_learning_profile():
    """Cria perfil de aprendizado do usuário"""
    data = request.get_json()
    user_id = data.get("user_id")
    name = data.get("name")

    if not user_id:
        return jsonify({"error": "User ID required"}), 400

    profile = jarvis_learning.create_user_profile(user_id, name)
    return jsonify(profile)

@app.route("/api/learning/save-preference", methods=["POST"])
def save_preference():
    """Salva preferência do usuário"""
    data = request.get_json()
    user_id = data.get("user_id")
    key = data.get("key")
    value = data.get("value")

    if not user_id or not key:
        return jsonify({"error": "User ID and key required"}), 400

    preference = jarvis_learning.save_user_preference(user_id, key, value)
    return jsonify(preference)

@app.route("/api/learning/get-preferences/<user_id>", methods=["GET"])
def get_preferences(user_id):
    """Obtém preferências do usuário"""
    preferences = jarvis_learning.retrieve_user_preferences(user_id)
    return jsonify(preferences)

@app.route("/api/learning/learn-behavior", methods=["POST"])
def learn_behavior():
    """Aprende padrão de comportamento"""
    data = request.get_json()
    user_id = data.get("user_id")
    pattern_name = data.get("pattern_name")
    pattern_data = data.get("pattern_data")
    confidence = data.get("confidence", 0.8)

    if not user_id or not pattern_name:
        return jsonify({"error": "User ID and pattern name required"}), 400

    pattern = jarvis_learning.learn_behavior_pattern(
        user_id, pattern_name, pattern_data, confidence
    )
    return jsonify(pattern)

@app.route("/api/learning/get-patterns/<user_id>", methods=["GET"])
def get_patterns(user_id):
    """Obtém padrões de comportamento aprendidos"""
    patterns = jarvis_learning.get_behavior_patterns(user_id)
    return jsonify(patterns)

@app.route("/api/learning/log-evolution", methods=["POST"])
def log_evolution():
    """Registra evolução do aprendizado"""
    data = request.get_json()
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    autonomy_level = data.get("autonomy_level")
    learning_metrics = data.get("learning_metrics", {})
    improvements = data.get("improvements", {})

    if not user_id or not session_id:
        return jsonify({"error": "User ID and session ID required"}), 400

    evolution = jarvis_learning.log_evolution(
        user_id, session_id, autonomy_level, learning_metrics, improvements
    )
    return jsonify(evolution)

@app.route("/api/learning/evolution-history/<user_id>", methods=["GET"])
def evolution_history(user_id):
    """Obtém histórico de evolução"""
    days = int(request.args.get("days", 30))
    history = jarvis_learning.get_evolution_history(user_id, days)
    return jsonify(history)

@app.route("/api/learning/predict-preference/<user_id>", methods=["GET"])
def predict_preference(user_id):
    """Prediz próxima preferência do usuário"""
    prediction = jarvis_learning.predict_next_preference(user_id)
    return jsonify(prediction)

@app.route("/api/learning/status", methods=["GET"])
def learning_status():
    """Status do sistema de aprendizado"""
    return jsonify(jarvis_learning.get_learning_status())

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
