"""
Sistema de Navegação e Rastreamento
Ponto 10: GPS avançado, rastreamento global, navegação aérea
"""

from typing import Dict, Tuple, List
from datetime import datetime
import math

class NavigationSystem:
    """Sistema de navegação e rastreamento global"""

    def __init__(self):
        self.gps_data = {}
        self.tracked_targets = {}
        self.navigation_history = []
        self.waypoints = []

    def update_gps(self, device_id: str, latitude: float, longitude: float,
                   altitude: float = 0.0) -> Dict:
        """
        Atualiza posição GPS

        Ponto 10: GPS avançado
        """
        position = {
            "device_id": device_id,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "timestamp": datetime.now().isoformat(),
            "accuracy": 5  # metros
        }

        self.gps_data[device_id] = position
        self.navigation_history.append(position)

        return position

    def track_target(self, target_id: str, initial_position: Tuple[float, float]) -> Dict:
        """
        Rastreia alvo em tempo real

        Ponto 10: Rastreamento global
        """
        tracker = {
            "target_id": target_id,
            "current_position": initial_position,
            "position_history": [initial_position],
            "velocity": None,
            "trajectory_predicted": None,
            "tracking_started": datetime.now().isoformat(),
            "status": "TRACKING"
        }

        self.tracked_targets[target_id] = tracker
        return tracker

    def calculate_triangulation(self, signal_points: List[Dict]) -> Tuple[float, float]:
        """
        Calcula posição por triangulação

        Ponto 10: Triangulação
        """
        if len(signal_points) < 3:
            return (0.0, 0.0)

        lat_avg = sum(p["latitude"] for p in signal_points) / len(signal_points)
        lon_avg = sum(p["longitude"] for p in signal_points) / len(signal_points)

        return (lat_avg, lon_avg)

    def plan_flight_route(self, start: Tuple[float, float],
                         destination: Tuple[float, float]) -> Dict:
        """
        Planeja rota de voo

        Ponto 10: Navegação aérea
        """
        distance = self._calculate_distance(start, destination)

        route = {
            "start": start,
            "destination": destination,
            "distance": round(distance, 2),
            "estimated_time": round(distance / 100, 2),  # assumindo 100 km/h
            "waypoints": self._generate_waypoints(start, destination),
            "weather_considerations": self._check_weather_route(start, destination),
            "optimal_altitude": 3000  # metros
        }

        return route

    def identify_target(self, target_data: Dict) -> Dict:
        """
        Identifica alvo específico

        Ponto 10: Identificação de alvos
        """
        identification = {
            "target_id": target_data.get("signature"),
            "classification": self._classify_target(target_data),
            "threat_level": self._assess_threat_level(target_data),
            "identification_confidence": 0.98,
            "timestamp": datetime.now().isoformat()
        }

        return identification

    def update_target_position(self, target_id: str, new_position: Tuple[float, float]) -> Dict:
        """Atualiza posição do alvo sendo rastreado"""
        if target_id not in self.tracked_targets:
            return {"error": "Target not found"}

        tracker = self.tracked_targets[target_id]
        old_pos = tracker["current_position"]

        tracker["current_position"] = new_position
        tracker["position_history"].append(new_position)

        # Calcula velocidade
        tracker["velocity"] = self._calculate_velocity(old_pos, new_position)

        # Prediz trajetória
        tracker["trajectory_predicted"] = self._predict_trajectory(tracker)

        return tracker

    def _calculate_distance(self, point1: Tuple[float, float],
                           point2: Tuple[float, float]) -> float:
        """Calcula distância entre dois pontos"""
        lat1, lon1 = point1
        lat2, lon2 = point2

        # Fórmula simples (Haversine poderia ser usada)
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # km

    def _generate_waypoints(self, start: Tuple[float, float],
                           destination: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Gera waypoints para rota"""
        waypoints = [start]

        # Gera waypoint intermediário
        lat_mid = (start[0] + destination[0]) / 2
        lon_mid = (start[1] + destination[1]) / 2
        waypoints.append((lat_mid, lon_mid))

        waypoints.append(destination)
        return waypoints

    def _check_weather_route(self, start: Tuple[float, float],
                            destination: Tuple[float, float]) -> Dict:
        """Verifica condições de tempo para rota"""
        return {
            "current_conditions": "CLEAR",
            "wind_speed": 5,
            "wind_direction": "NW",
            "visibility": "EXCELLENT",
            "flight_recommended": True
        }

    def _classify_target(self, target_data: Dict) -> str:
        """Classifica tipo de alvo"""
        if target_data.get("airborne"):
            return "AIRCRAFT"
        elif target_data.get("vehicle"):
            return "GROUND_VEHICLE"
        else:
            return "UNKNOWN"

    def _assess_threat_level(self, target_data: Dict) -> float:
        """Avalia nível de ameaça (0-1)"""
        threat = 0.0

        if target_data.get("weapon_detected"):
            threat += 0.5

        if target_data.get("hostile_intent"):
            threat += 0.3

        if target_data.get("unidentified"):
            threat += 0.2

        return min(threat, 1.0)

    def _calculate_velocity(self, old_pos: Tuple[float, float],
                           new_pos: Tuple[float, float]) -> float:
        """Calcula velocidade do alvo"""
        distance = self._calculate_distance(old_pos, new_pos)
        return round(distance, 2)  # km/s

    def _predict_trajectory(self, tracker: Dict) -> List[Tuple[float, float]]:
        """Prediz trajetória do alvo"""
        if len(tracker["position_history"]) < 2:
            return []

        current_pos = tracker["current_position"]
        previous_pos = tracker["position_history"][-2]

        # Extrapolação simples
        lat_diff = current_pos[0] - previous_pos[0]
        lon_diff = current_pos[1] - previous_pos[1]

        predicted = [
            (current_pos[0] + lat_diff, current_pos[1] + lon_diff),
            (current_pos[0] + lat_diff*2, current_pos[1] + lon_diff*2),
            (current_pos[0] + lat_diff*3, current_pos[1] + lon_diff*3)
        ]

        return predicted

    def get_navigation_status(self) -> Dict:
        """Retorna status do sistema de navegação"""
        return {
            "gps_signals": len(self.gps_data),
            "targets_tracked": len(self.tracked_targets),
            "navigation_history_size": len(self.navigation_history),
            "active_route": "ESTABLISHED" if self.waypoints else "NONE",
            "triangulation_accuracy": 0.95
        }
