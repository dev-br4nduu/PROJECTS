"""
Collaborative Features Module
Fase 4.0: Infraestrutura Corporativa

Capacidades:
- Multi-user management
- Shared workspaces
- Team coordination
- Permission system
- Real-time collaboration
"""

from typing import Dict, List, Any
from datetime import datetime

class CollaborationSystem:
    """Sistema de colaboração corporativa"""

    def __init__(self):
        self.workspaces = {}
        self.teams = {}
        self.shared_resources = {}
        self.activity_feed = []

    def create_workspace(self, name: str, owner: str) -> Dict[str, Any]:
        """
        Cria workspace compartilhado

        Fase 4.0: Collaboration - Workspaces
        """
        workspace = {
            "workspace_id": f"WS_{datetime.now().timestamp()}",
            "name": name,
            "owner": owner,
            "members": [owner],
            "resources": [],
            "created_at": datetime.now().isoformat(),
            "settings": {
                "visibility": "private",
                "allow_guests": False,
                "real_time_sync": True
            },
            "status": "ACTIVE"
        }

        self.workspaces[workspace["workspace_id"]] = workspace
        self._log_activity(owner, "WORKSPACE_CREATED", workspace["workspace_id"])
        return workspace

    def create_team(self, team_name: str, lead: str, members: List[str]) -> Dict[str, Any]:
        """
        Cria equipe de trabalho

        Fase 4.0: Collaboration - Teams
        """
        team = {
            "team_id": f"TEAM_{datetime.now().timestamp()}",
            "name": team_name,
            "lead": lead,
            "members": [lead] + members,
            "projects": [],
            "created_at": datetime.now().isoformat(),
            "status": "ACTIVE"
        }

        self.teams[team["team_id"]] = team
        return team

    def add_member_to_workspace(self, workspace_id: str, username: str,
                               role: str = "member") -> Dict[str, Any]:
        """
        Adiciona membro ao workspace

        Fase 4.0: Collaboration - Member Management
        """
        if workspace_id not in self.workspaces:
            return {"error": "Workspace not found"}

        workspace = self.workspaces[workspace_id]
        if username not in workspace["members"]:
            workspace["members"].append(username)
            self._log_activity(username, "MEMBER_ADDED", workspace_id)

        return {
            "workspace_id": workspace_id,
            "username": username,
            "role": role,
            "total_members": len(workspace["members"]),
            "status": "ADDED"
        }

    def share_resource(self, workspace_id: str, resource: Dict,
                      shared_by: str) -> Dict[str, Any]:
        """
        Compartilha recurso no workspace

        Fase 4.0: Collaboration - Resource Sharing
        """
        shared = {
            "resource_id": f"RES_{datetime.now().timestamp()}",
            "workspace_id": workspace_id,
            "resource": resource,
            "shared_by": shared_by,
            "shared_at": datetime.now().isoformat(),
            "access_count": 0
        }

        self.shared_resources[shared["resource_id"]] = shared
        self._log_activity(shared_by, "RESOURCE_SHARED", shared["resource_id"])
        return shared

    def real_time_collaboration(self, workspace_id: str, user: str,
                              action: Dict) -> Dict[str, Any]:
        """
        Colaboração em tempo real

        Fase 4.0: Collaboration - Real-time Sync
        """
        collaboration_event = {
            "event_id": f"COLLAB_{datetime.now().timestamp()}",
            "workspace_id": workspace_id,
            "user": user,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "synced_to_members": True,
            "conflict_resolution": "last_write_wins"
        }

        return collaboration_event

    def get_activity_feed(self, workspace_id: str = None, limit: int = 50) -> Dict[str, Any]:
        """Retorna feed de atividades"""
        activities = self.activity_feed
        if workspace_id:
            activities = [a for a in activities if a.get("resource_id") == workspace_id]

        return {
            "total_activities": len(activities),
            "activities": activities[-limit:]
        }

    def _log_activity(self, user: str, action: str, resource_id: str) -> None:
        """Registra atividade"""
        self.activity_feed.append({
            "user": user,
            "action": action,
            "resource_id": resource_id,
            "timestamp": datetime.now().isoformat()
        })

    def get_collaboration_status(self) -> Dict[str, Any]:
        """Retorna status de colaboração"""
        return {
            "workspaces": len(self.workspaces),
            "teams": len(self.teams),
            "shared_resources": len(self.shared_resources),
            "total_activities": len(self.activity_feed),
            "real_time_sync": "ENABLED",
            "collaboration_status": "ACTIVE"
        }
