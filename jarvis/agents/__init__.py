"""
Multi-Agent System Framework
Fase 3.0: Autonomia Plena

Capacidades:
- Autonomous agents (agentes autônomos)
- Task delegation (delegação de tarefas)
- Coordination protocols (protocolos de coordenação)
- Swarm intelligence (inteligência de enxame)
- Agent communication (comunicação entre agentes)
- Collective problem-solving (resolução coletiva de problemas)
"""

from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
from enum import Enum
import uuid
import json

class AgentRole(Enum):
    """Papéis dos agentes autônomos"""
    SPECIALIST = "specialist"          # Especialista em domínio
    COORDINATOR = "coordinator"        # Coordena outros agentes
    SCOUT = "scout"                    # Explora e coleta informações
    EXECUTOR = "executor"              # Executa tarefas
    MONITOR = "monitor"                # Monitora sistemas
    LEARNER = "learner"                # Aprende novos padrões
    STRATEGIST = "strategist"          # Planeja estratégias
    MESSENGER = "messenger"            # Comunica entre agentes

class AgentState(Enum):
    """Estados possíveis de um agente"""
    IDLE = "idle"
    ACTIVE = "active"
    WORKING = "working"
    WAITING = "waiting"
    THINKING = "thinking"
    DELEGATING = "delegating"
    SUSPENDED = "suspended"

class Agent:
    """Agente autônomo individual"""

    def __init__(self, agent_id: str, name: str, role: AgentRole,
                 capabilities: List[str], priority: float = 0.5):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.priority = priority
        self.state = AgentState.IDLE
        self.tasks = []
        self.completed_tasks = []
        self.knowledge_base = {}
        self.communication_queue = []
        self.created_at = datetime.now().isoformat()
        self.performance_metrics = {
            "tasks_completed": 0,
            "success_rate": 0.0,
            "avg_response_time": 0.0,
            "reliability": 0.95
        }

    def assign_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Atribui tarefa ao agente"""
        task_id = f"TASK_{uuid.uuid4().hex[:8]}"

        task_entry = {
            "task_id": task_id,
            "task": task,
            "assigned_at": datetime.now().isoformat(),
            "status": "ASSIGNED",
            "progress": 0,
            "expected_completion": None
        }

        self.tasks.append(task_entry)
        self.state = AgentState.ACTIVE

        return task_entry

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Executa tarefa atribuída"""
        task_entry = next((t for t in self.tasks if t["task_id"] == task_id), None)

        if not task_entry:
            return {"error": "Task not found"}

        self.state = AgentState.WORKING

        result = {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "status": "COMPLETED",
            "result": task_entry["task"],
            "execution_time": 0.5,  # seconds
            "completed_at": datetime.now().isoformat(),
            "success": True
        }

        task_entry["status"] = "COMPLETED"
        task_entry["progress"] = 100
        self.completed_tasks.append(task_entry)
        self.tasks.remove(task_entry)
        self.performance_metrics["tasks_completed"] += 1

        self.state = AgentState.IDLE

        return result

    def communicate(self, recipient_id: str, message: Dict) -> Dict[str, Any]:
        """Comunica com outro agente"""
        communication = {
            "from": self.agent_id,
            "to": recipient_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "type": message.get("type", "general")
        }

        self.communication_queue.append(communication)

        return communication

    def learn(self, knowledge_item: str, value: Any) -> None:
        """Aprende nova informação"""
        self.knowledge_base[knowledge_item] = {
            "value": value,
            "learned_at": datetime.now().isoformat(),
            "confidence": 0.8
        }

    def request_assistance(self, task_type: str) -> Dict[str, Any]:
        """Solicita assistência de outros agentes"""
        return {
            "requester": self.agent_id,
            "request_type": task_type,
            "requested_at": datetime.now().isoformat(),
            "status": "PENDING"
        }

    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual do agente"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "state": self.state.value,
            "tasks_active": len(self.tasks),
            "tasks_completed": self.performance_metrics["tasks_completed"],
            "performance_metrics": self.performance_metrics,
            "capabilities": self.capabilities,
            "knowledge_items": len(self.knowledge_base)
        }

class MultiAgentSystem:
    """Sistema de múltiplos agentes coordenados"""

    def __init__(self):
        self.agents = {}
        self.active_agents = 0
        self.task_queue = []
        self.completed_tasks = []
        self.agent_communications = []
        self.coordination_protocol = "CONSENSUS"
        self.system_state = "INITIALIZING"
        self.created_at = datetime.now().isoformat()

    def create_agent(self, name: str, role: AgentRole,
                    capabilities: List[str], priority: float = 0.5) -> Agent:
        """Cria novo agente autônomo"""
        agent_id = f"AGENT_{uuid.uuid4().hex[:8]}"
        agent = Agent(agent_id, name, role, capabilities, priority)

        self.agents[agent_id] = agent
        self.active_agents = len([a for a in self.agents.values()
                                  if a.state != AgentState.SUSPENDED])

        return agent

    def delegate_task(self, task: Dict[str, Any], preferred_role: Optional[AgentRole] = None) -> Dict[str, Any]:
        """Delega tarefa para agente apropriado"""
        # Seleciona agente baseado em papel e prioridade
        suitable_agents = [
            a for a in self.agents.values()
            if (preferred_role is None or a.role == preferred_role) and
            a.state in [AgentState.IDLE, AgentState.WAITING]
        ]

        if not suitable_agents:
            return {"error": "No suitable agent available"}

        # Seleciona agente com menor workload
        selected_agent = min(suitable_agents, key=lambda a: len(a.tasks))

        task_entry = selected_agent.assign_task(task)
        self.task_queue.append(task_entry)

        return {
            "task_id": task_entry["task_id"],
            "assigned_to": selected_agent.agent_id,
            "agent_name": selected_agent.name,
            "status": "DELEGATED"
        }

    def coordinate_agents(self, goal: str, agents_involved: List[str]) -> Dict[str, Any]:
        """Coordena múltiplos agentes para objetivo comum"""
        coordination = {
            "coordination_id": f"COORD_{uuid.uuid4().hex[:8]}",
            "goal": goal,
            "agents_involved": agents_involved,
            "protocol": self.coordination_protocol,
            "started_at": datetime.now().isoformat(),
            "status": "COORDINATING",
            "sub_tasks": []
        }

        # Quebra objetivo em subtarefas
        for i, agent_id in enumerate(agents_involved):
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                subtask = {
                    "sequence": i + 1,
                    "agent_id": agent_id,
                    "objective": f"Part {i+1} of {goal}",
                    "status": "PENDING"
                }
                coordination["sub_tasks"].append(subtask)

        return coordination

    def enable_swarm_intelligence(self) -> Dict[str, Any]:
        """Ativa inteligência de enxame entre agentes"""
        swarm_config = {
            "swarm_mode": "ACTIVE",
            "agents_in_swarm": len(self.agents),
            "collective_intelligence": True,
            "information_sharing": "ENABLED",
            "consensus_mechanism": "MAJORITY_VOTE",
            "behavior_rules": [
                "Share discoveries immediately",
                "Learn from collective experience",
                "Adapt to collective strategy",
                "Maintain individual autonomy within guidelines"
            ],
            "activated_at": datetime.now().isoformat()
        }

        return swarm_config

    def broadcast_message(self, source_agent_id: str, message: Dict,
                         recipients: Optional[List[str]] = None) -> Dict[str, Any]:
        """Transmite mensagem para múltiplos agentes"""
        if recipients is None:
            recipients = [a for a in self.agents.keys() if a != source_agent_id]

        broadcast = {
            "broadcast_id": f"BCAST_{uuid.uuid4().hex[:8]}",
            "from": source_agent_id,
            "to": recipients,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "status": "SENT",
            "acknowledged": 0
        }

        self.agent_communications.append(broadcast)

        return broadcast

    def consensus_decision(self, decision_topic: str, options: List[str]) -> Dict[str, Any]:
        """Toma decisão por consenso entre agentes"""
        votes = {}
        for agent in self.agents.values():
            # Simula voto de cada agente
            vote = options[hash(agent.agent_id) % len(options)]
            votes[agent.agent_id] = vote

        winner = max(set(votes.values()), key=list(votes.values()).count)
        consensus_percentage = (list(votes.values()).count(winner) / len(votes)) * 100

        decision = {
            "decision_topic": decision_topic,
            "options": options,
            "votes": votes,
            "consensus_decision": winner,
            "consensus_strength": round(consensus_percentage, 1),
            "decided_at": datetime.now().isoformat()
        }

        return decision

    def execute_all_tasks(self) -> Dict[str, Any]:
        """Executa todas as tarefas na fila"""
        execution_report = {
            "total_tasks": len(self.task_queue),
            "executed": 0,
            "failed": 0,
            "results": [],
            "execution_time": datetime.now().isoformat()
        }

        for task_entry in self.task_queue[:]:
            # Encontra agente responsável e executa
            for agent in self.agents.values():
                for agent_task in agent.tasks:
                    if agent_task["task_id"] == task_entry["task_id"]:
                        result = agent.execute_task(task_entry["task_id"])
                        execution_report["executed"] += 1
                        execution_report["results"].append(result)
                        self.completed_tasks.append(result)
                        self.task_queue.remove(task_entry)
                        break

        return execution_report

    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema multi-agente"""
        agent_statuses = {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }

        return {
            "system_state": self.system_state,
            "total_agents": len(self.agents),
            "active_agents": self.active_agents,
            "agents": agent_statuses,
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "communications": len(self.agent_communications),
            "coordination_protocol": self.coordination_protocol,
            "swarm_intelligence": "ENABLED",
            "created_at": self.created_at
        }

    def get_agent_network_graph(self) -> Dict[str, Any]:
        """Retorna grafo de rede de comunicação dos agentes"""
        network = {
            "nodes": [
                {"id": agent_id, "name": agent.name, "role": agent.role.value}
                for agent_id, agent in self.agents.items()
            ],
            "edges": [
                {"from": comm["from"], "to": comm["to"], "type": comm.get("type", "communication")}
                for comm in self.agent_communications
            ],
            "total_connections": len(self.agent_communications)
        }

        return network
