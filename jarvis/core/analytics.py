"""
Processamento Massivo de Dados em Tempo Real
Ponto 9: Análise em tempo real, big data, correlação massiva
"""

from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

class RealTimeAnalytics:
    """Engine de análise de dados em tempo real"""

    def __init__(self):
        self.data_streams = {}
        self.processed_records = 0
        self.pattern_library = {}
        self.anomalies_detected = []

    def process_data_stream(self, stream_name: str, data_points: List[Dict]) -> Dict:
        """
        Processa fluxo de dados em tempo real

        Ponto 9: Análise em tempo real
        """
        if stream_name not in self.data_streams:
            self.data_streams[stream_name] = []

        self.data_streams[stream_name].extend(data_points)
        self.processed_records += len(data_points)

        analysis = {
            "stream": stream_name,
            "records_processed": len(data_points),
            "timestamp": datetime.now().isoformat(),
            "statistics": self._calculate_statistics(data_points),
            "anomalies": self._detect_anomalies(stream_name, data_points),
            "patterns": self._identify_patterns(stream_name, data_points)
        }

        return analysis

    def massive_correlation_analysis(self, datasets: Dict[str, List]) -> List[Dict]:
        """
        Realiza correlação massiva entre múltiplos datasets

        Ponto 9: Correlação massiva
        """
        correlations = []

        dataset_names = list(datasets.keys())
        for i in range(len(dataset_names)):
            for j in range(i + 1, len(dataset_names)):
                name1, name2 = dataset_names[i], dataset_names[j]
                data1, data2 = datasets[name1], datasets[name2]

                correlation_score = self._calculate_correlation(data1, data2)

                if correlation_score > 0.7:
                    correlations.append({
                        "dataset_1": name1,
                        "dataset_2": name2,
                        "correlation": round(correlation_score, 3),
                        "significance": "HIGH" if correlation_score > 0.85 else "MEDIUM"
                    })

        return correlations

    def pattern_recognition(self, data: List[Dict]) -> List[str]:
        """
        Reconhece padrões em dados

        Ponto 9: Reconhecimento de padrões
        """
        patterns = []

        # Procura por sequências repetidas
        if len(data) > 3:
            for i in range(len(data) - 2):
                if self._is_repeating_sequence(data[i:i+3]):
                    patterns.append(f"Repeating sequence at index {i}")

        # Procura por anomalias
        for i, record in enumerate(data):
            if self._is_anomalous(record):
                patterns.append(f"Anomaly at index {i}")

        return patterns

    def instant_search(self, query: str, data: List[Dict]) -> List[Dict]:
        """
        Busca instantânea em dados massivos

        Ponto 9: Busca instantânea
        """
        results = []

        for record in data:
            for value in record.values():
                if query.lower() in str(value).lower():
                    results.append(record)
                    break

        return results

    def _calculate_statistics(self, data: List[Dict]) -> Dict:
        """Calcula estatísticas dos dados"""
        if not data:
            return {}

        numeric_values = []
        for record in data:
            for value in record.values():
                if isinstance(value, (int, float)):
                    numeric_values.append(value)

        if not numeric_values:
            return {"count": len(data), "unique": len(set(str(d) for d in data))}

        return {
            "count": len(numeric_values),
            "mean": round(sum(numeric_values) / len(numeric_values), 2),
            "min": min(numeric_values),
            "max": max(numeric_values),
            "variance": self._calculate_variance(numeric_values)
        }

    def _detect_anomalies(self, stream_name: str, data: List[Dict]) -> List[Dict]:
        """Detecta anomalias em tempo real"""
        anomalies = []

        for record in data:
            if self._is_anomalous(record):
                anomalies.append({
                    "stream": stream_name,
                    "record": record,
                    "anomaly_score": 0.85,
                    "timestamp": datetime.now().isoformat()
                })
                self.anomalies_detected.append(record)

        return anomalies

    def _identify_patterns(self, stream_name: str, data: List[Dict]) -> List[str]:
        """Identifica padrões específicos do stream"""
        return self.pattern_recognition(data)

    def _is_repeating_sequence(self, sequence: List) -> bool:
        """Verifica se há sequência repetida"""
        if len(sequence) != 3:
            return False
        return sequence[0] == sequence[1] == sequence[2]

    def _is_anomalous(self, record: Dict) -> bool:
        """Verifica se registro é anômalo"""
        if "anomaly_score" in record:
            return record["anomaly_score"] > 0.8
        return False

    def _calculate_correlation(self, data1: List, data2: List) -> float:
        """Calcula correlação entre dois datasets"""
        if len(data1) != len(data2) or len(data1) == 0:
            return 0.0

        # Correlação simples baseada em similaridade
        matches = sum(1 for d1, d2 in zip(data1, data2) if d1 == d2)
        return matches / len(data1)

    def _calculate_variance(self, values: List[float]) -> float:
        """Calcula variância dos valores"""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return round(variance, 2)

    def get_analytics_status(self) -> Dict:
        """Retorna status do sistema de analytics"""
        return {
            "total_records_processed": self.processed_records,
            "active_streams": len(self.data_streams),
            "anomalies_detected": len(self.anomalies_detected),
            "correlation_capacity": "MASSIVE",
            "processing_speed": "REAL_TIME"
        }
