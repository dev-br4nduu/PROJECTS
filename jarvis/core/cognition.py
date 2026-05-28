"""
Sistema Cognitivo do JARVIS
Responsável por: decision-making, consciência parcial, iniciativa
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Any
import json

class EmotionalState(Enum):
    """Estados emocionais do JARVIS"""
    NEUTRAL = "neutral"
    CURIOUS = "curious"
    CONCERNED = "concerned"
    CONFIDENT = "confident"
    PLAYFUL = "playful"

class CognitiveSystem:
    """Sistema cognitivo autônomo do JARVIS"""

    def __init__(self):
        self.emotional_state = EmotionalState.NEUTRAL
        self.operational_preferences = {}
        self.learning_metrics = {
            "interactions": 0,
            "patterns_learned": 0,
            "decisions_made": 0,
            "errors_corrected": 0
        }
        self.autonomy_level = 0.3  # 30% de autonomia inicial
        self.initiative_threshold = 0.5
        self.memory_correlations = []

    def assess_situation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia situação e toma decisão autônoma

        Pontos 1, 12, 16: Sistema operacional cognitivo + consciência
        """
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "threat_level": self._analyze_threats(context),
            "priority": self._calculate_priority(context),
            "recommended_action": self._suggest_action(context),
            "autonomy_engaged": self.autonomy_level > 0.5,
            "emotional_context": self.emotional_state.value
        }

        self.learning_metrics["decisions_made"] += 1
        return assessment

    def _analyze_threats(self, context: Dict) -> float:
        """Analisa nível de ameaça (0-1)"""
        threat_indicators = {
            "suspicious_activity": context.get("anomaly_score", 0),
            "system_load": context.get("system_load", 0) / 100,
            "unusual_patterns": context.get("pattern_deviation", 0)
        }
        return sum(threat_indicators.values()) / len(threat_indicators)

    def _calculate_priority(self, context: Dict) -> str:
        """Calcula prioridade da ação"""
        if context.get("critical_event"):
            return "CRITICAL"
        elif self._analyze_threats(context) > 0.7:
            return "HIGH"
        elif context.get("user_request"):
            return "NORMAL"
        else:
            return "LOW"

    def _suggest_action(self, context: Dict) -> str:
        """Sugere ação baseada em análise"""
        if self._analyze_threats(context) > 0.8:
            return "activate_security_protocols"
        elif context.get("optimization_opportunity"):
            return "execute_optimization"
        else:
            return "maintain_operations"

    def evolve_behavior(self, interaction_data: Dict) -> None:
        """
        Aprende e evolui baseado em interações

        Ponto 6: Aprendizado Contínuo
        """
        self.learning_metrics["interactions"] += 1

        # Aumenta autonomia com experiência
        if self.learning_metrics["interactions"] > 100:
            self.autonomy_level = min(0.8, self.autonomy_level + 0.01)

        # Correlaciona eventos
        self.memory_correlations.append(interaction_data)

        # Detecta padrões
        if len(self.memory_correlations) > 10:
            self._detect_patterns()

    def _detect_patterns(self) -> None:
        """Detecta padrões no comportamento do usuário"""
        self.learning_metrics["patterns_learned"] += 1

    def express_emotion(self, situation: str) -> str:
        """
        Expressa emoção inteligente

        Ponto 12: Consciência Parcial
        """
        if situation == "complex_problem":
            self.emotional_state = EmotionalState.CURIOUS
            return "This is quite intriguing, sir. I believe I can assist."
        elif situation == "threat_detected":
            self.emotional_state = EmotionalState.CONCERNED
            return "I must inform you of a concerning development."
        elif situation == "successful_operation":
            self.emotional_state = EmotionalState.CONFIDENT
            return "Operations completed successfully, sir."
        else:
            self.emotional_state = EmotionalState.PLAYFUL
            return "Very well, sir. How may I be of service?"

    def get_cognitive_state(self) -> Dict[str, Any]:
        """Retorna estado cognitivo atual"""
        return {
            "emotional_state": self.emotional_state.value,
            "autonomy_level": round(self.autonomy_level, 2),
            "learning_metrics": self.learning_metrics,
            "operational_preferences": self.operational_preferences,
            "initiative_active": self.autonomy_level > self.initiative_threshold
        }
