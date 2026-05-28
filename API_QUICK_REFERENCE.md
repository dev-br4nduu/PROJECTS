# JARVIS v2.0 - API Quick Reference Guide

## Base URL
```
http://localhost:5000
```

## Authentication
Endpoints biométricos requerem autenticação multi-modal. Outros endpoints são open.

---

## 🤖 CHAT & CONVERSAÇÃO

### Chat com Análise Cognitiva
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "Good morning. How are you?"
}

Response:
{
  "user": "Good morning. How are you?",
  "jarvis": "Good day, sir. I am functioning optimally...",
  "cognitive_state": {
    "threat_level": 0.0,
    "autonomy_engaged": true,
    "emotional_context": "neutral"
  },
  "emotion": "playful",
  "autonomy_level": 0.45
}
```

### Obter Histórico
```bash
GET /api/history

Response:
{
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### Reset de Conversa
```bash
POST /api/reset

Response:
{
  "status": "Conversation reset",
  "greeting": "Good day, sir. How may I be of service?"
}
```

---

## 🔷 SISTEMA OPERACIONAL

### Status Completo do Sistema
```bash
GET /api/system/status

Response:
{
  "system": "JARVIS v2.0",
  "operational_status": "ONLINE",
  "technical_level": {
    "conversational_ai": "AGI-like",
    "automation": "EXTREME",
    "systemic_integration": "TOTAL",
    "consciousness": "PARTIAL"
  },
  "monitoring": {...}
}
```

### Monitorar Todos os Sistemas
```bash
GET /api/system/monitor

Response:
{
  "operational_status": "ONLINE",
  "systems": {
    "cognition": {"status": "OPTIMAL", "health": 0.98},
    "memory": {"status": "OPTIMAL", "health": 0.95},
    "security": {"status": "SECURE", "health": 0.99},
    ...
  },
  "overall_health": 0.98
}
```

### Inicializar Sistemas
```bash
POST /api/system/initialize

Response:
{
  "subsystems_initialized": [
    {"subsystem": "cognition", "status": "ONLINE", ...},
    {"subsystem": "memory", "status": "ONLINE", ...},
    ...
  ]
}
```

---

## 🧠 COGNIÇÃO & APRENDIZADO

### Estado Cognitivo Atual
```bash
GET /api/cognition/state

Response:
{
  "emotional_state": "curious",
  "autonomy_level": 0.65,
  "learning_metrics": {
    "interactions": 150,
    "patterns_learned": 23,
    "decisions_made": 450,
    "errors_corrected": 12
  },
  "initiative_active": true
}
```

### Evoluir Cognitivamente
```bash
POST /api/cognition/evolve

Response:
{
  "autonomy_improvement": {
    "previous_level": 0.30,
    "current_level": 0.65,
    "improvement_rate": "0.01 per 100 interactions"
  },
  "behavioral_updates": {
    "new_emotional_states": ["PLAYFUL", "CONCERNED"],
    "improved_decision_making": true
  }
}
```

---

## 🔒 SEGURANÇA

### Análise de Ameaça
```bash
POST /api/security/threat-assessment
Content-Type: application/json

{
  "moving": true,
  "weapon_detected": false,
  "unusual_traffic": true
}

Response:
{
  "threat_level": "HIGH",
  "security_analysis": {
    "threat_level": 0.75,
    "anomaly_detected": true,
    "recommended_action": "activate_defensive_protocols"
  },
  "recommended_response": "Activate security protocols"
}
```

### Status de Segurança
```bash
GET /api/security/status

Response:
{
  "encryption_level": "AES-256",
  "threats_detected": 5,
  "intrusions_blocked": 2,
  "critical_threats": 0
}
```

---

## 📍 NAVEGAÇÃO & RASTREAMENTO

### Atualizar Posição GPS
```bash
POST /api/navigation/gps
Content-Type: application/json

{
  "device_id": "armor_01",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "altitude": 1000
}

Response:
{
  "device_id": "armor_01",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "altitude": 1000,
  "accuracy": 5
}
```

### Planejar Rota de Voo
```bash
POST /api/navigation/route
Content-Type: application/json

{
  "start": [40.7128, -74.0060],
  "destination": [40.8000, -74.0000]
}

Response:
{
  "start": [40.7128, -74.0060],
  "destination": [40.8000, -74.0000],
  "distance": 8.47,
  "estimated_time": 0.08,
  "waypoints": [[40.7128, -74.0060], [40.7564, -74.003], [40.8000, -74.0000]],
  "optimal_altitude": 3000
}
```

### Rastrear Alvo
```bash
POST /api/navigation/track
Content-Type: application/json

{
  "target_id": "threat_01",
  "position": [40.7128, -74.0060]
}

Response:
{
  "target_id": "threat_01",
  "current_position": [40.7128, -74.0060],
  "position_history": [[40.7128, -74.0060]],
  "status": "TRACKING"
}
```

---

## 🏗️ ENGENHARIA

### Projetar Armadura
```bash
POST /api/engineering/design-armor
Content-Type: application/json

{
  "type": "body_armor",
  "material": "vibranium",
  "power_efficiency": 0.95
}

Response:
{
  "design_id": "DESIGN_0",
  "type": "body_armor",
  "material": "vibranium",
  "weight": 6.25,
  "protection_rating": 1.0,
  "mobility_score": 0.94,
  "status": "DESIGNED"
}
```

### Simular Design
```bash
POST /api/engineering/simulate
Content-Type: application/json

{
  "design_id": "DESIGN_0",
  "parameters": {
    "test": "impact",
    "force": 1000,
    "duration": 5
  }
}

Response:
{
  "simulation_id": "SIM_0",
  "test_type": "impact",
  "results": {
    "structural_integrity": 0.98,
    "deformation": 2.3,
    "passed": true
  }
}
```

### Status de Engenharia
```bash
GET /api/engineering/status

Response:
{
  "total_designs": 1,
  "simulations_run": 1,
  "materials_in_database": 4,
  "designs_approved": 1
}
```

---

## 🔐 BIOMETRIA

### Matricular Usuário
```bash
POST /api/biometrics/enroll
Content-Type: application/json

{
  "user_id": "tony_stark",
  "biometric_data": {
    "voice": "voice_sample",
    "retina": "retina_scan",
    "face": "facial_image"
  }
}

Response:
{
  "user_id": "tony_stark",
  "voice_print": {...},
  "retina_scan": {...},
  "facial_recognition": {...},
  "status": "ENROLLED"
}
```

### Verificar Identidade
```bash
POST /api/biometrics/verify
Content-Type: application/json

{
  "user_id": "tony_stark",
  "biometric_sample": {
    "voice": "voice_input",
    "face": "camera_input",
    "retina": "eye_scanner"
  }
}

Response:
{
  "user_id": "tony_stark",
  "authenticated": true,
  "confidence_score": 0.983,
  "individual_scores": {
    "voice": 0.92,
    "facial": 0.98,
    "retina": 0.99
  }
}
```

---

## ⚙️ AUTOMAÇÃO

### Agendar Tarefa
```bash
POST /api/automation/schedule
Content-Type: application/json

{
  "task_name": "database_backup",
  "trigger": "immediate",
  "parameters": {"database": "stark_db"}
}

Response:
{
  "task_id": "TASK_0",
  "task_name": "database_backup",
  "status": "SCHEDULED",
  "executions": 1
}
```

### Criar Workflow
```bash
POST /api/automation/workflow
Content-Type: application/json

{
  "workflow_name": "security_lockdown",
  "steps": [
    {"name": "block_ip", "action": "firewall"},
    {"name": "alert_admin", "action": "notification"},
    {"name": "backup_data", "action": "data_protection"}
  ]
}

Response:
{
  "workflow_name": "security_lockdown",
  "steps": [...],
  "status": "CREATED"
}
```

---

## 📊 ANALYTICS

### Processar Fluxo de Dados
```bash
POST /api/analytics/process-stream
Content-Type: application/json

{
  "stream_name": "sensor_data",
  "data_points": [
    {"value": 100, "timestamp": "2024-01-01T10:00:00"},
    {"value": 102, "timestamp": "2024-01-01T10:05:00"},
    {"value": 98, "timestamp": "2024-01-01T10:10:00"}
  ]
}

Response:
{
  "stream": "sensor_data",
  "records_processed": 3,
  "statistics": {
    "count": 3,
    "mean": 100.0,
    "min": 98,
    "max": 102
  },
  "anomalies": []
}
```

---

## 💾 MEMÓRIA

### Estatísticas de Memória
```bash
GET /api/memory/stats

Response:
{
  "total_episodes": 150,
  "event_types": 5,
  "buffer_size": 150,
  "correlations_found": 23
}
```

### Correlações de Eventos
```bash
GET /api/memory/correlations

Response:
{
  "correlations": [
    {
      "episode_pair": [0, 1],
      "strength": 0.8,
      "pattern": "Recurring security_breach pattern"
    }
  ]
}
```

---

## 🎯 MISSÕES

### Executar Missão
```bash
POST /api/mission/execute
Content-Type: application/json

{
  "objective": "Neutralize threat",
  "start_position": [40.7128, -74.0060],
  "destination": [40.8000, -74.0000],
  "requires_navigation": true,
  "requires_security": true,
  "monitored_systems": ["network", "firewall", "intrusion_detection"]
}

Response:
{
  "mission_id": "MISSION_1704096000",
  "objective": "Neutralize threat",
  "status": "IN_PROGRESS",
  "flight_plan": {...},
  "subsystems_engaged": ["navigation", "security"]
}
```

---

## Error Handling

Todos os endpoints retornam código de status HTTP apropriado:

- **200 OK** - Sucesso
- **400 Bad Request** - Parâmetros inválidos
- **404 Not Found** - Recurso não encontrado
- **500 Internal Server Error** - Erro no servidor

Exemplo de erro:
```json
{
  "error": "An error occurred: Invalid parameter",
  "status": "error"
}
```

---

## Rate Limiting

Não há rate limiting implementado na v2.0. Considere adicionar para produção.

---

## Autenticação

Para endpoints sensíveis de segurança e biometria, considere adicionar:
- OAuth 2.0
- JWT tokens
- API keys

---

## Best Practices

1. **Use HTTPS em produção** - Dados sensíveis
2. **Implemente rate limiting** - Proteção contra abuse
3. **Adicione logging** - Rastreamento de operações
4. **Monitore performance** - Análise de carga
5. **Mantenha backups** - Proteção de dados episódicos

---

**JARVIS v2.0 API - Fully Operational**
