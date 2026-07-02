import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Optional

session = requests.Session()
session.auth = HTTPBasicAuth("XXXXXXXXX", "XXXXXXXX")

BASE_URL = "https://jira.XXXXXXX.XXXXXX.com"


class JiraRoles:

    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url.rstrip("/")
        self._role_cache: Dict[str, Dict[str, dict]] = {}

    # ------------------------------------------------------------------
    # CACHE
    # ------------------------------------------------------------------

    def clear_cache(self, project: Optional[str] = None):
        if project is None:
            self._role_cache.clear()
        else:
            self._role_cache.pop(project, None)

    # ------------------------------------------------------------------
    # PRIVATE METHODS
    # ------------------------------------------------------------------

    def _load_project_roles(self, project: str):
        if project in self._role_cache:
            return
        response = self.session.get(
            f"{self.base_url}/rest/api/2/project/{project}/role"
        )
        response.raise_for_status()
        roles = {}
        for role_name, role_url in response.json().items():
            roles[role_name] = {
                "id": role_url.rstrip("/").split("/")[-1],
                "url": role_url,
            }
        self._role_cache[project] = roles

    def _get_role(self, project: str, role_name: str):
        self._load_project_roles(project)
        if role_name not in self._role_cache[project]:
            raise Exception(
                f"Role '{role_name}' not found in project '{project}'"
            )
        return self._role_cache[project][role_name]

    def get_role_names(self, project: str) -> List[str]:
        self._load_project_roles(project)
        return list(self._role_cache[project].keys())

    def _get_role_data(self, project: str, role_name: str):
        role = self._get_role(project, role_name)
        response = self.session.get(role["url"])
        response.raise_for_status()
        return response.json()

    def _remove_actors(
            self,
            project: str,
            role_name: str,
            parameter: str,
            values: List[str]
    ):
        if not values:
            return
        role = self._get_role(project, role_name)

        for value in values:
            response = self.session.delete(
                role["url"],
                params={parameter: value}
            )
            response.raise_for_status()

    # ------------------------------------------------------------------
    # USERS MANAGEMENT
    # ------------------------------------------------------------------

    def get_users(self, project: str, role_name: str) -> List[str]:
        role = self._get_role_data(project, role_name)
        return [
            actor["name"]
            for actor in role["actors"]
            if actor["type"] == "atlassian-user-role-actor"
        ]

    def add_users(self, project: str, role_name: str, users: List[str]):
        if not users:
            return
        role = self._get_role(project, role_name)
        response = self.session.post(
            role["url"],
            json={"user": users}
        )
        response.raise_for_status()
        return response.json()

    def remove_users(self, project: str, role_name: str, users: List[str]):
        return self._remove_actors(
            project,
            role_name,
            "user",
            users
        )

    def clear_role(self, project: str, role_name: str):
        users = self.get_users(project, role_name)
        if users:
            self.remove_users(project, role_name, users)
        return users

    # ------------------------------------------------------------------
    # GROUP MANAGEMENT
    # ------------------------------------------------------------------

    def get_groups(self, project: str, role_name: str) -> List[str]:
        role = self._get_role_data(project, role_name)
        return [
            actor["name"]
            for actor in role["actors"]
            if actor["type"] == "atlassian-group-role-actor"
        ]

    def add_groups(self, project: str, role_name: str, groups: List[str]):
        if not groups:
            return
        role = self._get_role(project, role_name)
        response = self.session.post(
            role["url"],
            json={"group": groups}
        )
        response.raise_for_status()
        return response.json()

    def remove_groups(self, project: str, role_name: str, groups: List[str]):

        return self._remove_actors(
            project,
            role_name,
            "group",
            groups
        )

    def clear_groups(
        self,
        project: str,
        role_name: str,
        groups: Optional[List[str]] = None
    ):
        if groups is None:
            groups = self.get_groups(project, role_name)
        if groups:
            self.remove_groups(project, role_name, groups)
        return groups

    # ------------------------------------------------------------------
    # REMOVE ALL
    # ------------------------------------------------------------------

    def clean_project(
            self,
            project: str,
            keep_groups: List[str]
    ):
        summary = {}
        role_names = self.get_role_names(project)
        for role_name in role_names:
            # USERS: always remove everything
            users = self.get_users(project, role_name)
            if users:
                self.remove_users(project, role_name, users)
            # GROUPS: selective removal
            groups = self.get_groups(project, role_name)
            groups_to_remove = [
                g for g in groups
                if g not in keep_groups
            ]
            if groups_to_remove:
                self.remove_groups(project, role_name, groups_to_remove)
            summary[role_name] = {
                "users_removed": len(users),
                "groups_removed": len(groups_to_remove)
            }
        return summary


KEEP_GROUPS = [
    "XXXXX",
    "XXXXXXXX",
    "XXXXXXXXXX",
    "XXXXXX"
]

jira_roles = JiraRoles(session, BASE_URL)

result = jira_roles.clean_project(
    "MYPROJECT",
    KEEP_GROUPS
)

print(result)
