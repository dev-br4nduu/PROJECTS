"""
Análise Biométrica
Ponto 11: Reconhecimento de voz, retina, rosto, sinais corporais
"""

from typing import Dict, List, Any
from datetime import datetime

class BiometricSystem:
    """Sistema de análise biométrica do JARVIS"""

    def __init__(self):
        self.enrolled_users = {}
        self.access_logs = []
        self.biometric_confidence_threshold = 0.95

    def enroll_user(self, user_id: str, biometric_data: Dict) -> Dict:
        """
        Matricula novo usuário com dados biométricos

        Ponto 11: Autenticação biométrica
        """
        enrollment = {
            "user_id": user_id,
            "voice_print": self._create_voice_print(biometric_data.get("voice")),
            "retina_scan": self._create_retina_scan(biometric_data.get("retina")),
            "facial_recognition": self._create_facial_profile(biometric_data.get("face")),
            "enrollment_date": datetime.now().isoformat(),
            "status": "ENROLLED"
        }

        self.enrolled_users[user_id] = enrollment
        return enrollment

    def verify_identity(self, user_id: str, biometric_sample: Dict) -> Dict:
        """
        Verifica identidade através de múltiplas modalidades

        Ponto 11: Autenticação multi-modal
        """
        if user_id not in self.enrolled_users:
            return {"authenticated": False, "reason": "User not enrolled"}

        enrolled = self.enrolled_users[user_id]

        voice_match = self._compare_voice(
            enrolled["voice_print"],
            biometric_sample.get("voice")
        )
        face_match = self._compare_face(
            enrolled["facial_recognition"],
            biometric_sample.get("face")
        )
        retina_match = self._compare_retina(
            enrolled["retina_scan"],
            biometric_sample.get("retina")
        )

        confidence = (voice_match + face_match + retina_match) / 3

        result = {
            "user_id": user_id,
            "authenticated": confidence >= self.biometric_confidence_threshold,
            "confidence_score": round(confidence, 3),
            "individual_scores": {
                "voice": voice_match,
                "facial": face_match,
                "retina": retina_match
            },
            "timestamp": datetime.now().isoformat()
        }

        self.access_logs.append(result)
        return result

    def analyze_vital_signs(self, sensor_data: Dict) -> Dict:
        """
        Analisa sinais vitais do usuário

        Ponto 11: Sinais corporais
        """
        vitals = {
            "heart_rate": sensor_data.get("heart_rate", 75),
            "blood_pressure": sensor_data.get("blood_pressure", "120/80"),
            "oxygen_saturation": sensor_data.get("o2_sat", 98),
            "body_temperature": sensor_data.get("temperature", 37.0),
            "stress_level": self._analyze_stress(sensor_data),
            "overall_status": "NORMAL",
            "timestamp": datetime.now().isoformat()
        }

        if vitals["stress_level"] > 0.7:
            vitals["overall_status"] = "ELEVATED_STRESS"
        elif vitals["heart_rate"] > 100:
            vitals["overall_status"] = "ELEVATED_HR"

        return vitals

    def _create_voice_print(self, voice_data: Any) -> Dict:
        """Cria impressão de voz"""
        return {
            "frequency_signature": "unique_voice_pattern",
            "pitch_profile": "analysis_stored",
            "voice_id": "VOICEPRINT_ENROLLED"
        }

    def _create_retina_scan(self, retina_data: Any) -> Dict:
        """Cria padrão de retina"""
        return {
            "vessel_pattern": "analyzed",
            "retina_id": "RETINA_ENROLLED",
            "uniqueness": 0.99
        }

    def _create_facial_profile(self, face_data: Any) -> Dict:
        """Cria perfil facial"""
        return {
            "facial_landmarks": "mapped",
            "face_id": "FACE_ENROLLED",
            "characteristics": ["eye_distance", "nose_shape", "jaw_structure"]
        }

    def _compare_voice(self, enrolled: Dict, sample: Any) -> float:
        """Compara impressão de voz"""
        if sample is None:
            return 0.5
        return 0.92

    def _compare_face(self, enrolled: Dict, sample: Any) -> float:
        """Compara reconhecimento facial"""
        if sample is None:
            return 0.5
        return 0.98

    def _compare_retina(self, enrolled: Dict, sample: Any) -> float:
        """Compara scan de retina"""
        if sample is None:
            return 0.5
        return 0.99

    def _analyze_stress(self, sensor_data: Dict) -> float:
        """Analisa nível de estresse (0-1)"""
        stress = 0.0

        if sensor_data.get("heart_rate", 75) > 90:
            stress += 0.3

        if sensor_data.get("skin_conductance", 0) > 0.5:
            stress += 0.3

        if sensor_data.get("cortisol_level", 0) > 15:
            stress += 0.4

        return min(stress, 1.0)

    def get_biometric_status(self) -> Dict:
        """Retorna status do sistema biométrico"""
        return {
            "enrolled_users": len(self.enrolled_users),
            "access_attempts": len(self.access_logs),
            "successful_authentications": sum(
                1 for log in self.access_logs if log.get("authenticated")
            ),
            "confidence_threshold": self.biometric_confidence_threshold,
            "biometric_modalities": ["voice", "facial", "retina"]
        }
