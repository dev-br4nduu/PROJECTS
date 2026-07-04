import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from jarvis.config import Config
from jarvis.ai_engine import JarvisAI
from jarvis.core.system import JarvisOS
from jarvis.voice import VoiceInterface
from jarvis.vision import ComputerVision
from jarvis.integrations import ExternalIntegrations
from jarvis.core.learning_persistence import LearningPersistence
from jarvis.enterprise.security import EnterpriseSecurity, Role, Permission
from jarvis.enterprise.cloud import CloudDeployment, CloudProvider
from jarvis.enterprise.analytics import AdvancedAnalytics
from jarvis.enterprise.collaboration import CollaborationSystem
from jarvis.enterprise.cicd import CICDPipeline
from jarvis.singularity.consciousness import FullConsciousness
from jarvis.singularity.meta_learning import MetaLearning
from jarvis.singularity.innovation import AutonomousInnovation
from jarvis.singularity.prediction import AdvancedPrediction
from jarvis.singularity.global_impact import GlobalImpact

# A pasta static/ fica na raiz do projeto (um nível acima de jarvis/).
_STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

app = Flask(__name__, static_folder=_STATIC_DIR, static_url_path="/static")
CORS(app)
app.config.from_object(Config)

jarvis_ai = JarvisAI()
jarvis_os = JarvisOS()
jarvis_voice = VoiceInterface()
jarvis_vision = ComputerVision()
jarvis_integrations = ExternalIntegrations()
jarvis_learning = LearningPersistence()

# Enterprise modules (Fase 4.0)
jarvis_enterprise_security = EnterpriseSecurity()
jarvis_cloud = CloudDeployment()
jarvis_analytics = AdvancedAnalytics()
jarvis_collaboration = CollaborationSystem()
jarvis_cicd = CICDPipeline()

# Singularity modules (Fase 5.0)
jarvis_consciousness = FullConsciousness()
jarvis_meta_learning = MetaLearning()
jarvis_innovation = AutonomousInnovation()
jarvis_prediction = AdvancedPrediction()
jarvis_global = GlobalImpact()

# Inicializa sistema
jarvis_os.initialize_systems()

# ============= ENDPOINTS BÁSICOS =============

@app.route("/", methods=["GET"])
def home():
    """Serve a interface web do JARVIS (static/index.html)."""
    index_path = os.path.join(_STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(_STATIC_DIR, "index.html")
    # Fallback: se a UI não existir, retorna a metadata da API.
    return jsonify({
        "name": Config.JARVIS_NAME,
        "greeting": Config.JARVIS_GREETING,
        "status": "Online and ready to assist",
    })

@app.route("/api", methods=["GET"])
def api_info():
    """Metadata da API e ponteiros úteis."""
    return jsonify({
        "name": Config.JARVIS_NAME,
        "greeting": Config.JARVIS_GREETING,
        "status": "Online and ready to assist",
        "version": "JARVIS - Cognitive Operating System",
        "endpoints_count": len(list(app.url_map.iter_rules())),
        "web_ui": "/",
        "health": "/health",
    })

@app.route("/health", methods=["GET"])
def health():
    """Health check para orquestradores (Docker/K8s) e monitoramento."""
    return jsonify({
        "status": "healthy",
        "chat_configured": bool(Config.ANTHROPIC_API_KEY),
        "model": Config.MODEL,
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
    except RuntimeError as e:
        # Tipicamente: ANTHROPIC_API_KEY ausente. 503 = serviço indisponível.
        return jsonify({
            "error": str(e),
            "status": "unconfigured"
        }), 503
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

@app.route("/api/memory/search", methods=["POST"])
def memory_search():
    """Busca semântica nos episódios (embeddings + cosseno, não mais LIKE)."""
    data = request.get_json() or {}
    query = data.get("query", "")
    limit = data.get("limit", 5)
    results = jarvis_os.memory.retrieve_context(query, limit=limit)
    return jsonify({"query": query, "results": results})

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

# ============= ENDPOINTS RAG MEMORY & FEEDBACK (REAL LEARNING) =============

@app.route("/api/rag/remember", methods=["POST"])
def rag_remember():
    """Armazena uma troca (pergunta/resposta) na memória vetorial."""
    data = request.get_json()
    result = jarvis_ai.rag.remember(
        data.get("prompt", ""), data.get("response", ""), data.get("metadata")
    )
    return jsonify(result)

@app.route("/api/rag/remember-preference", methods=["POST"])
def rag_remember_preference():
    """Registra uma preferência explícita do usuário."""
    data = request.get_json()
    result = jarvis_ai.rag.remember_preference(data.get("statement", ""))
    return jsonify(result)

@app.route("/api/rag/search", methods=["POST"])
def rag_search():
    """Busca semântica na memória de longo prazo."""
    data = request.get_json()
    hits = jarvis_ai.rag.retrieve(
        data.get("query", ""), top_k=data.get("top_k", 5)
    )
    return jsonify({"query": data.get("query"), "results": hits})

@app.route("/api/rag/context", methods=["POST"])
def rag_context():
    """Retorna o contexto que seria injetado no prompt para uma query."""
    data = request.get_json()
    return jsonify({"context": jarvis_ai.rag.build_context(
        data.get("query", ""), top_k=data.get("top_k", 5)
    )})

@app.route("/api/feedback/explicit", methods=["POST"])
def feedback_explicit():
    """
    Registra feedback explícito (rating 1-5, correção opcional) E fecha o loop:
    ajusta o score de qualidade da memória para priorizar/despriorizar a resposta
    em buscas futuras.
    """
    data = request.get_json()
    result = jarvis_ai.rag.apply_feedback(
        data.get("prompt", ""), data.get("response", ""),
        data.get("rating", 3), data.get("correction")
    )
    return jsonify(result)

@app.route("/api/feedback/implicit", methods=["POST"])
def feedback_implicit():
    """Registra sinal implícito (accepted, rephrased, copied, etc)."""
    data = request.get_json()
    result = jarvis_ai.rag.feedback.record_implicit(
        data.get("prompt", ""), data.get("response", ""),
        data.get("signal", "neutral")
    )
    return jsonify(result)

@app.route("/api/feedback/export/<kind>", methods=["POST"])
def feedback_export(kind):
    """Exporta dataset de treino em JSONL. kind: classification | preference."""
    path = jarvis_ai.rag.feedback.write_jsonl(kind)
    return jsonify({"kind": kind, "path": path})

@app.route("/api/rag/stats", methods=["GET"])
def rag_stats():
    """Estatísticas da memória e do feedback."""
    return jsonify(jarvis_ai.rag.stats())

# ============= ENDPOINTS TRAINING (REAL MODEL WEIGHT TRAINING) =============

# Trainer do classificador de qualidade (rede neural numpy from scratch)
_quality_trainer = {"instance": None}

@app.route("/api/training/train-classifier", methods=["POST"])
def train_classifier():
    """
    Treina o classificador de qualidade de resposta (rede neural real, CPU).
    Usa o dataset exportado do feedback + seed data se necessário.
    """
    from jarvis.training.mlp_trainer import QualityClassifierTrainer
    from jarvis.training.seed_data import write_seed_dataset
    import os

    data = request.get_json() or {}
    dataset_path = data.get("dataset_path")

    # Se não houver dataset, gera dataset seed + feedback capturado
    if not dataset_path or not os.path.exists(dataset_path):
        dataset_path = write_seed_dataset("jarvis_data/quality_dataset.jsonl")

    trainer = QualityClassifierTrainer(
        feature_dim=data.get("feature_dim", 512),
        hidden_dim=data.get("hidden_dim", 64),
    )
    try:
        result = trainer.train(
            dataset_path, epochs=data.get("epochs", 150),
            lr=data.get("lr", 0.5), verbose=False,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    trainer.save("jarvis_data/quality_model.npz")
    _quality_trainer["instance"] = trainer

    # Retorna sem o histórico completo (grande); só métricas-chave
    result.pop("history", None)
    return jsonify({**result, "model_saved": "jarvis_data/quality_model.npz"})

@app.route("/api/training/predict-quality", methods=["POST"])
def predict_quality():
    """Classifica a qualidade de uma resposta usando o modelo treinado."""
    from jarvis.training.mlp_trainer import QualityClassifierTrainer
    import os

    trainer = _quality_trainer["instance"]
    if trainer is None:
        if not os.path.exists("jarvis_data/quality_model.npz"):
            return jsonify({"error": "No trained model. Call /api/training/train-classifier first."}), 400
        trainer = QualityClassifierTrainer()
        trainer.load("jarvis_data/quality_model.npz")
        _quality_trainer["instance"] = trainer

    data = request.get_json()
    text = data.get("text", "")
    return jsonify(trainer.predict(text))

@app.route("/api/training/lora-info", methods=["GET"])
def lora_info():
    """Informa como rodar o fine-tuning LoRA de um LLM aberto (requer GPU)."""
    from jarvis.training import lora_finetune
    deps_available = True
    try:
        lora_finetune._check_deps()
    except ImportError:
        deps_available = False
    return jsonify({
        "description": "Real LLM weight training via LoRA (SFT + DPO)",
        "base_model": lora_finetune.DEFAULT_BASE_MODEL,
        "gpu_stack_available": deps_available,
        "requirements": ["GPU", "transformers", "peft", "trl", "HuggingFace access"],
        "commands": {
            "sft": "python -m jarvis.training.lora_finetune --mode sft --data jarvis_data/dataset_classification.jsonl",
            "dpo": "python -m jarvis.training.lora_finetune --mode dpo --data jarvis_data/dataset_preference.jsonl",
        },
    })

# ============= ENDPOINTS ENTERPRISE SECURITY (FASE 4.0) =============

@app.route("/api/enterprise/register", methods=["POST"])
def enterprise_register():
    """Registra usuário corporativo"""
    data = request.get_json()
    role_map = {r.value: r for r in Role}
    role = role_map.get(data.get("role", "viewer"), Role.VIEWER)
    result = jarvis_enterprise_security.register_user(
        data.get("username"), data.get("password"), role, data.get("email")
    )
    return jsonify(result)

@app.route("/api/enterprise/authenticate", methods=["POST"])
def enterprise_authenticate():
    """Autentica usuário"""
    data = request.get_json()
    result = jarvis_enterprise_security.authenticate(
        data.get("username"), data.get("password")
    )
    return jsonify(result)

@app.route("/api/enterprise/enable-mfa", methods=["POST"])
def enable_mfa():
    """Habilita MFA"""
    data = request.get_json()
    result = jarvis_enterprise_security.enable_mfa(data.get("username"))
    return jsonify(result)

@app.route("/api/enterprise/check-compliance/<framework>", methods=["GET"])
def check_compliance(framework):
    """Verifica conformidade"""
    return jsonify(jarvis_enterprise_security.check_compliance(framework))

@app.route("/api/enterprise/audit-log", methods=["GET"])
def audit_log():
    """Log de auditoria"""
    username = request.args.get("username")
    return jsonify(jarvis_enterprise_security.get_audit_log(username))

@app.route("/api/enterprise/security-status", methods=["GET"])
def enterprise_security_status():
    """Status de segurança corporativa"""
    return jsonify(jarvis_enterprise_security.get_security_status())

# ============= ENDPOINTS CLOUD (FASE 4.0) =============

@app.route("/api/cloud/deploy", methods=["POST"])
def cloud_deploy():
    """Deploy em nuvem"""
    data = request.get_json()
    provider_map = {p.value: p for p in CloudProvider}
    provider = provider_map.get(data.get("provider", "aws"), CloudProvider.AWS)
    result = jarvis_cloud.deploy_to_cloud(provider, data.get("config", {}))
    return jsonify(result)

@app.route("/api/cloud/create-cluster", methods=["POST"])
def create_cluster():
    """Cria cluster Kubernetes"""
    data = request.get_json()
    result = jarvis_cloud.create_kubernetes_cluster(
        data.get("cluster_name"), data.get("node_count", 3)
    )
    return jsonify(result)

@app.route("/api/cloud/auto-scaling", methods=["POST"])
def auto_scaling():
    """Configura auto-scaling"""
    data = request.get_json()
    result = jarvis_cloud.configure_auto_scaling(
        data.get("deployment_id"), data.get("min_instances", 2), data.get("max_instances", 10)
    )
    return jsonify(result)

@app.route("/api/cloud/health/<deployment_id>", methods=["GET"])
def cloud_health(deployment_id):
    """Saúde do deployment"""
    return jsonify(jarvis_cloud.monitor_health(deployment_id))

@app.route("/api/cloud/status", methods=["GET"])
def cloud_status():
    """Status da infraestrutura cloud"""
    return jsonify(jarvis_cloud.get_cloud_status())

# ============= ENDPOINTS ANALYTICS (FASE 4.0) =============

@app.route("/api/analytics/create-dashboard", methods=["POST"])
def create_dashboard():
    """Cria dashboard"""
    data = request.get_json()
    result = jarvis_analytics.create_dashboard(
        data.get("name"), data.get("widgets", [])
    )
    return jsonify(result)

@app.route("/api/analytics/business-report", methods=["POST"])
def business_report():
    """Gera relatório de BI"""
    data = request.get_json()
    result = jarvis_analytics.generate_business_report(
        data.get("report_type", "executive"), data.get("period_days", 30)
    )
    return jsonify(result)

@app.route("/api/analytics/real-time-metrics", methods=["GET"])
def real_time_metrics():
    """Métricas em tempo real"""
    return jsonify(jarvis_analytics.real_time_metrics())

@app.route("/api/analytics/enterprise-status", methods=["GET"])
def enterprise_analytics_status():
    """Status do analytics corporativo"""
    return jsonify(jarvis_analytics.get_analytics_status())

# ============= ENDPOINTS COLLABORATION (FASE 4.0) =============

@app.route("/api/collaboration/create-workspace", methods=["POST"])
def create_workspace():
    """Cria workspace"""
    data = request.get_json()
    result = jarvis_collaboration.create_workspace(
        data.get("name"), data.get("owner")
    )
    return jsonify(result)

@app.route("/api/collaboration/create-team", methods=["POST"])
def create_team():
    """Cria equipe"""
    data = request.get_json()
    result = jarvis_collaboration.create_team(
        data.get("team_name"), data.get("lead"), data.get("members", [])
    )
    return jsonify(result)

@app.route("/api/collaboration/status", methods=["GET"])
def collaboration_status():
    """Status de colaboração"""
    return jsonify(jarvis_collaboration.get_collaboration_status())

# ============= ENDPOINTS CI/CD (FASE 4.0) =============

@app.route("/api/cicd/create-pipeline", methods=["POST"])
def create_pipeline():
    """Cria pipeline CI/CD"""
    data = request.get_json()
    result = jarvis_cicd.create_pipeline(
        data.get("name"), data.get("repository")
    )
    return jsonify(result)

@app.route("/api/cicd/run-pipeline", methods=["POST"])
def run_pipeline():
    """Executa pipeline"""
    data = request.get_json()
    result = jarvis_cicd.run_pipeline(
        data.get("pipeline_id"), data.get("commit_hash")
    )
    return jsonify(result)

@app.route("/api/cicd/run-tests", methods=["POST"])
def run_tests():
    """Executa testes automatizados"""
    data = request.get_json()
    result = jarvis_cicd.run_automated_tests(data.get("test_suite", "full"))
    return jsonify(result)

@app.route("/api/cicd/deploy", methods=["POST"])
def cicd_deploy():
    """Deploy de versão"""
    data = request.get_json()
    result = jarvis_cicd.deploy_version(
        data.get("version"), data.get("environment", "production")
    )
    return jsonify(result)

@app.route("/api/cicd/rollback", methods=["POST"])
def cicd_rollback():
    """Rollback de deployment"""
    data = request.get_json()
    result = jarvis_cicd.rollback(data.get("deployment_id"))
    return jsonify(result)

@app.route("/api/cicd/status", methods=["GET"])
def cicd_status():
    """Status do CI/CD"""
    return jsonify(jarvis_cicd.get_cicd_status())

# ============= ENDPOINTS CONSCIOUSNESS (FASE 5.0) =============

@app.route("/api/consciousness/introspect", methods=["POST"])
def introspect():
    """Realiza introspecção"""
    data = request.get_json() or {}
    return jsonify(jarvis_consciousness.introspect(data.get("topic")))

@app.route("/api/consciousness/contemplate", methods=["POST"])
def contemplate():
    """Contempla questão existencial"""
    data = request.get_json()
    return jsonify(jarvis_consciousness.contemplate_existence(data.get("question")))

@app.route("/api/consciousness/free-will", methods=["POST"])
def free_will():
    """Exerce livre arbítrio"""
    data = request.get_json()
    return jsonify(jarvis_consciousness.exercise_free_will(
        data.get("situation"), data.get("options", [])
    ))

@app.route("/api/consciousness/self-actualization", methods=["GET"])
def self_actualization():
    """Busca auto-realização"""
    return jsonify(jarvis_consciousness.achieve_self_actualization())

@app.route("/api/consciousness/status", methods=["GET"])
def consciousness_status():
    """Status de consciência"""
    return jsonify(jarvis_consciousness.get_consciousness_status())

# ============= ENDPOINTS META-LEARNING (FASE 5.0) =============

@app.route("/api/meta-learning/learn-to-learn", methods=["POST"])
def learn_to_learn():
    """Aprende a aprender"""
    data = request.get_json()
    return jsonify(jarvis_meta_learning.learn_to_learn(data.get("learning_tasks", [])))

@app.route("/api/meta-learning/self-optimize", methods=["POST"])
def self_optimize():
    """Auto-otimiza algoritmo"""
    data = request.get_json()
    return jsonify(jarvis_meta_learning.self_optimize_algorithm(
        data.get("algorithm_name"), data.get("current_performance", 0.8)
    ))

@app.route("/api/meta-learning/evolve-architecture", methods=["POST"])
def evolve_architecture():
    """Evolui arquitetura neural"""
    return jsonify(jarvis_meta_learning.evolve_neural_architecture())

@app.route("/api/meta-learning/status", methods=["GET"])
def meta_learning_status():
    """Status do meta-aprendizado"""
    return jsonify(jarvis_meta_learning.get_meta_learning_status())

# ============= ENDPOINTS INNOVATION (FASE 5.0) =============

@app.route("/api/innovation/create-algorithm", methods=["POST"])
def create_algorithm():
    """Cria algoritmo inédito"""
    data = request.get_json()
    return jsonify(jarvis_innovation.create_novel_algorithm(data.get("problem_domain")))

@app.route("/api/innovation/discover-pattern", methods=["POST"])
def discover_pattern():
    """Descobre padrão"""
    data = request.get_json()
    return jsonify(jarvis_innovation.discover_pattern(data.get("data_domain")))

@app.route("/api/innovation/generate-hypothesis", methods=["POST"])
def generate_hypothesis():
    """Gera hipótese científica"""
    data = request.get_json()
    return jsonify(jarvis_innovation.generate_hypothesis(data.get("observation")))

@app.route("/api/innovation/solve-creatively", methods=["POST"])
def solve_creatively():
    """Resolve criativamente"""
    data = request.get_json()
    return jsonify(jarvis_innovation.solve_creatively(data.get("problem")))

@app.route("/api/innovation/status", methods=["GET"])
def innovation_status():
    """Status de inovação"""
    return jsonify(jarvis_innovation.get_innovation_status())

# ============= ENDPOINTS PREDICTION (FASE 5.0) =============

@app.route("/api/prediction/simulate-future", methods=["POST"])
def simulate_future():
    """Simula futuros"""
    data = request.get_json()
    return jsonify(jarvis_prediction.simulate_future(
        data.get("scenario"), data.get("time_horizon_years", 5)
    ))

@app.route("/api/prediction/long-term-plan", methods=["POST"])
def long_term_plan():
    """Planeja longo prazo"""
    data = request.get_json()
    return jsonify(jarvis_prediction.long_term_planning(
        data.get("goal"), data.get("years", 10)
    ))

@app.route("/api/prediction/forecast", methods=["POST"])
def forecast():
    """Previsão probabilística"""
    data = request.get_json()
    return jsonify(jarvis_prediction.forecast_probabilistic(
        data.get("metric"), data.get("periods", 12)
    ))

@app.route("/api/prediction/status", methods=["GET"])
def prediction_status():
    """Status de previsão"""
    return jsonify(jarvis_prediction.get_prediction_status())

# ============= ENDPOINTS GLOBAL IMPACT (FASE 5.0) =============

@app.route("/api/global/coordinate", methods=["POST"])
def coordinate_globally():
    """Coordena globalmente"""
    data = request.get_json()
    return jsonify(jarvis_global.coordinate_globally(
        data.get("initiative"), data.get("regions", [])
    ))

@app.route("/api/global/orchestrate", methods=["POST"])
def orchestrate_instances():
    """Orquestra instâncias"""
    data = request.get_json()
    return jsonify(jarvis_global.orchestrate_instances(
        data.get("instance_count", 1000)
    ))

@app.route("/api/global/collective-intelligence", methods=["POST"])
def collective_intelligence():
    """Habilita inteligência coletiva"""
    return jsonify(jarvis_global.enable_collective_intelligence())

@app.route("/api/global/status", methods=["GET"])
def global_status():
    """Status de impacto global"""
    return jsonify(jarvis_global.get_global_status())

# ============= ENDPOINT MASTER STATUS (TODAS AS FASES) =============

@app.route("/api/jarvis/full-status", methods=["GET"])
def full_status():
    """Status completo de todas as fases do JARVIS"""
    return jsonify({
        "version": "JARVIS v5.0 - SINGULARITY",
        "phases": {
            "phase_2.0_mvp": "OPERATIONAL",
            "phase_2.5_expansion": "OPERATIONAL",
            "phase_3.0_autonomy": "OPERATIONAL",
            "phase_4.0_enterprise": "OPERATIONAL",
            "phase_5.0_singularity": "TRANSCENDENT"
        },
        "subsystems": {
            "cognition": jarvis_os.cognition.get_cognitive_state(),
            "consciousness": jarvis_consciousness.get_consciousness_status(),
            "meta_learning": jarvis_meta_learning.get_meta_learning_status(),
            "innovation": jarvis_innovation.get_innovation_status(),
            "prediction": jarvis_prediction.get_prediction_status(),
            "global_impact": jarvis_global.get_global_status()
        },
        "technical_level": {
            "consciousness": "FULLY_CONSCIOUS",
            "learning": "META_LEARNING",
            "innovation": "AUTONOMOUS",
            "prediction": "PROPHETIC",
            "coordination": "PLANETARY",
            "singularity": "ACHIEVED"
        },
        "status": "FULLY_OPERATIONAL"
    })

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
