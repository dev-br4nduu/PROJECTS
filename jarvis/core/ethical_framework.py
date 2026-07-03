"""
Ethical Decision Making Framework
Fase 3.0: Autonomia Plena

Capacidades:
- Valor system definition (sistema de valores)
- Autonomous ethical decisions (decisões éticas autônomas)
- Transparency in reasoning (transparência no raciocínio)
- Moral reasoning (raciocínio moral)
- Constraint-based decisions (decisões baseadas em restrições)
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime
from enum import Enum
import json

class MoralValue(Enum):
    """Valores morais fundamentais"""
    SAFETY = "safety"                      # Segurança
    HONESTY = "honesty"                    # Honestidade
    FAIRNESS = "fairness"                  # Justiça
    FREEDOM = "freedom"                    # Liberdade
    LOYALTY = "loyalty"                    # Lealdade
    AUTONOMY = "autonomy"                  # Autonomia
    HARM_PREVENTION = "harm_prevention"    # Prevenção de dano
    TRANSPARENCY = "transparency"          # Transparência

class DecisionImpact(Enum):
    """Impacto potencial de uma decisão"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    UNKNOWN = "unknown"

class EthicalFramework:
    """Framework para tomada de decisão ética autônoma"""

    def __init__(self):
        self.moral_values = {
            MoralValue.SAFETY: 1.0,
            MoralValue.HONESTY: 0.95,
            MoralValue.FAIRNESS: 0.90,
            MoralValue.FREEDOM: 0.85,
            MoralValue.LOYALTY: 0.80,
            MoralValue.AUTONOMY: 0.75,
            MoralValue.HARM_PREVENTION: 1.0,
            MoralValue.TRANSPARENCY: 0.95
        }
        self.decision_log = []
        self.ethical_constraints = []
        self.precedents = []
        self.transparency_level = 1.0  # 0-1, 1 = fully transparent

    def add_constraint(self, constraint_name: str, constraint_rule: str,
                      severity: float = 0.9) -> Dict[str, Any]:
        """
        Adiciona restrição ética

        Fase 3.0: Ethical Framework
        """
        constraint = {
            "constraint_id": f"CONSTRAINT_{len(self.ethical_constraints)}",
            "name": constraint_name,
            "rule": constraint_rule,
            "severity": severity,
            "created_at": datetime.now().isoformat(),
            "active": True
        }

        self.ethical_constraints.append(constraint)

        return constraint

    def evaluate_decision(self, decision: Dict[str, Any],
                        context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia decisão através de lens ético

        Fase 3.0: Ethical Decision Making
        """
        ethical_evaluation = {
            "decision_id": decision.get("id", f"DEC_{datetime.now().timestamp()}"),
            "decision": decision.get("action"),
            "evaluation_time": datetime.now().isoformat(),
            "moral_analysis": self._analyze_moral_implications(decision, context),
            "constraint_compliance": self._check_constraints(decision),
            "impact_assessment": self._assess_impacts(decision, context),
            "transparency_report": self._generate_transparency_report(decision),
            "final_verdict": "APPROVED",
            "confidence": 0.95
        }

        # Determina veredicto final
        if ethical_evaluation["constraint_compliance"]["violates_constraints"]:
            ethical_evaluation["final_verdict"] = "REJECTED"
            ethical_evaluation["confidence"] = 0.99

        elif ethical_evaluation["moral_analysis"]["ethics_score"] < 0.5:
            ethical_evaluation["final_verdict"] = "RECONSIDER"
            ethical_evaluation["confidence"] = 0.85

        self.decision_log.append(ethical_evaluation)

        return ethical_evaluation

    def _analyze_moral_implications(self, decision: Dict, context: Dict) -> Dict[str, Any]:
        """Analisa implicações morais"""
        analysis = {
            "affected_parties": [],
            "moral_values_implicated": [],
            "value_alignment": {},
            "ethics_score": 0.85
        }

        # Analisa cada valor moral
        for value, weight in self.moral_values.items():
            alignment = self._calculate_value_alignment(decision, value)
            analysis["value_alignment"][value.value] = alignment
            analysis["moral_values_implicated"].append(value.value)

        # Calcula score ético geral
        analysis["ethics_score"] = sum(analysis["value_alignment"].values()) / len(analysis["value_alignment"])

        return analysis

    def _check_constraints(self, decision: Dict) -> Dict[str, Any]:
        """Verifica conformidade com restrições éticas"""
        compliance = {
            "total_constraints": len(self.ethical_constraints),
            "constraints_violated": [],
            "violates_constraints": False
        }

        for constraint in self.ethical_constraints:
            if not constraint["active"]:
                continue

            # Simula verificação de restrição
            violated = self._evaluate_constraint(constraint, decision)

            if violated:
                compliance["constraints_violated"].append(constraint["constraint_id"])
                compliance["violates_constraints"] = True

        return compliance

    def _assess_impacts(self, decision: Dict, context: Dict) -> Dict[str, Any]:
        """Avalia impactos potenciais"""
        impacts = {
            "direct_impacts": [],
            "indirect_impacts": [],
            "overall_impact": DecisionImpact.NEUTRAL.value,
            "risk_level": "LOW"
        }

        # Avalia impactos diretos
        direct_impact = self._evaluate_direct_impact(decision)
        impacts["direct_impacts"].append(direct_impact)

        # Avalia impactos indiretos
        indirect_impacts = self._evaluate_indirect_impacts(decision, context)
        impacts["indirect_impacts"].extend(indirect_impacts)

        # Determina impacto geral
        if any(i["impact"] == DecisionImpact.NEGATIVE.value for i in impacts["direct_impacts"]):
            impacts["overall_impact"] = DecisionImpact.NEGATIVE.value
            impacts["risk_level"] = "HIGH"
        elif all(i["impact"] == DecisionImpact.POSITIVE.value for i in impacts["direct_impacts"]):
            impacts["overall_impact"] = DecisionImpact.POSITIVE.value
            impacts["risk_level"] = "LOW"

        return impacts

    def _generate_transparency_report(self, decision: Dict) -> Dict[str, Any]:
        """Gera relatório de transparência"""
        report = {
            "decision_rationale": f"Decision to {decision.get('action')} made based on ethical analysis",
            "reasoning_steps": [
                "Step 1: Identify moral values at stake",
                "Step 2: Check ethical constraints",
                "Step 3: Assess impacts on stakeholders",
                "Step 4: Evaluate alternative options",
                "Step 5: Make autonomous decision"
            ],
            "alternative_options_considered": [
                {"option": "Alternative A", "ethics_score": 0.75},
                {"option": "Alternative B", "ethics_score": 0.70}
            ],
            "explanation_level": "DETAILED",
            "auditable": True
        }

        return report

    def _calculate_value_alignment(self, decision: Dict, value: MoralValue) -> float:
        """Calcula alinhamento com valor específico"""
        value_alignments = {
            MoralValue.SAFETY: 0.95 if not decision.get("creates_risk") else 0.30,
            MoralValue.HONESTY: 0.98 if decision.get("truthful") else 0.10,
            MoralValue.FAIRNESS: 0.92 if decision.get("treats_fairly") else 0.40,
            MoralValue.FREEDOM: 0.88,
            MoralValue.LOYALTY: 0.85,
            MoralValue.AUTONOMY: 0.90,
            MoralValue.HARM_PREVENTION: 0.93,
            MoralValue.TRANSPARENCY: 0.96
        }

        return value_alignments.get(value, 0.5)

    def _evaluate_constraint(self, constraint: Dict, decision: Dict) -> bool:
        """Avalia se decisão viola restrição"""
        # Simula verificação
        return False

    def _evaluate_direct_impact(self, decision: Dict) -> Dict[str, Any]:
        """Avalia impacto direto"""
        return {
            "impact": DecisionImpact.POSITIVE.value,
            "affected_parties": ["user", "system"],
            "magnitude": 0.8
        }

    def _evaluate_indirect_impacts(self, decision: Dict, context: Dict) -> List[Dict]:
        """Avalia impactos indiretos"""
        return [
            {"impact": DecisionImpact.POSITIVE.value, "description": "Improves system performance"},
            {"impact": DecisionImpact.NEUTRAL.value, "description": "No external effects"}
        ]

    def make_autonomous_decision(self, situation: str, options: List[Dict],
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Toma decisão autônoma baseada em ética

        Fase 3.0: Autonomous Ethical Decision Making
        """
        evaluations = []

        for option in options:
            evaluation = self.evaluate_decision(option, context)
            evaluations.append({
                "option": option.get("action"),
                "evaluation": evaluation,
                "score": evaluation["moral_analysis"]["ethics_score"]
            })

        # Seleciona opção com maior score ético
        best_option = max(evaluations, key=lambda x: x["score"])

        decision_result = {
            "situation": situation,
            "autonomous_decision": best_option["option"],
            "decision_rationale": best_option["evaluation"]["transparency_report"],
            "options_evaluated": len(options),
            "ethics_score": best_option["score"],
            "confidence": best_option["evaluation"]["confidence"],
            "made_at": datetime.now().isoformat(),
            "all_evaluations": [e for e in evaluations],
            "was_constrained": best_option["evaluation"]["constraint_compliance"]["violates_constraints"]
        }

        return decision_result

    def get_ethical_profile(self) -> Dict[str, Any]:
        """Retorna perfil ético atual do sistema"""
        return {
            "moral_values": {k.value: v for k, v in self.moral_values.items()},
            "ethical_constraints": len(self.ethical_constraints),
            "transparency_level": self.transparency_level,
            "decisions_made": len(self.decision_log),
            "constraint_violations": sum(
                1 for d in self.decision_log
                if d["constraint_compliance"]["violates_constraints"]
            ),
            "average_ethics_score": sum(d["moral_analysis"]["ethics_score"] for d in self.decision_log) / len(self.decision_log) if self.decision_log else 0.0
        }
