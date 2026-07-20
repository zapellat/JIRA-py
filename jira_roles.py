from jira_auth import JiraClient
from typing import Dict, List, Optional
from jira_auth import session, BASE_URL
from requests.exceptions import HTTPError

#groups to be keep in the group for safety, and adding a group also for safety of not locking the user out
KEEP_GROUPS = [
    "XYZGROUP1",
    "XYZGROUP2",
    "XYZGROUP2",
    "ADM"
]

GOVERNANCE_GROUP = "ITGOV"


class JiraRoles(JiraClient):

    def __init__(self, session, base_url):
        super().__init__(session, base_url)
        self._role_cache = {}

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
        try:
            response = self.request(
                "GET",
                f"{self.base_url}/rest/api/2/project/{project}/role"
            )
        except HTTPError as e:
            response = e.response
            if response is not None and response.status_code in (401, 403):
                print(
                    f"Skipping project '{project}': "
                    f"No permission to access Jira roles."
                )
                self._role_cache[project] = {}
                return

            raise
        roles = {}
        for role_name, role_url in response.json().items():
            roles[role_name] = {
                "id": role_url.rstrip("/").split("/")[-1],
                "url": role_url,
            }
        self._role_cache[project] = roles

    def _get_role(self, project: str, role_name: str):
        self._load_project_roles(project)
        roles = self._role_cache.get(project, {})
        if not roles:
            print(
                f"Cannot access roles for project '{project}'."
            )
            return None
        if role_name not in roles:
            raise Exception(
                f"Role '{role_name}' not found in project '{project}'"
            )
        return roles[role_name]

    def get_role_names(self, project: str) -> List[str]:
        self._load_project_roles(project)
        roles = self._role_cache.get(project)
        if roles is None:
            return []
        return list(roles.keys())

    def _get_role_data(self, project: str, role_name: str):
        role = self._get_role(project, role_name)
        if role is None:
            return None
        response = self.request("GET", role["url"])
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
            self.request("DELETE", role["url"], params={parameter: value})

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
        response = self.request("POST", role["url"], json={"user": users})
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
        current_groups = self.get_groups(project, role_name)
        groups_to_add = [
            group
            for group in groups
            if group not in current_groups
        ]
        if not groups_to_add:
            return
        role = self._get_role(project, role_name)
        response = self.request("POST", role["url"], json={"group": groups_to_add})
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

    def clean_project(self, project: str, keep_groups: List[str]):
        summary = {}
        print(f"\nCleaning roles for project: {project}")
        role_names = self.get_role_names(project)
        if not role_names:
            print(
                f"Skipping role cleanup for '{project}': No Jira role access."
            )
            return summary
        print(f"Adding ICT Governance Brasil to the project: {project}")
        for role_name in [
            "Administrators",
            "Estimate Manager",
            "Initiative Leader Delegate",
            "Technical Leader",
        ]:
            self.add_groups(
                project=project,
                role_name=role_name,
                groups=[GOVERNANCE_GROUP]
            )
        print(f"Removing users and groups from project: {project}")
        for role_name in role_names:
            # ---------------- USERS ----------------
            users = self.get_users(project, role_name)
            if users:
                self.remove_users(project, role_name, users)

            # ---------------- GROUPS ----------------
            groups = self.get_groups(project, role_name)
            groups_to_remove = [
                g for g in groups
                if g not in keep_groups
            ]
            if groups_to_remove:
                self.remove_groups(project, role_name, groups_to_remove)
            summary[role_name] = {
                "users": users,
                "groups": groups_to_remove
            }
        print(f"Finished cleaning roles for project: {project}")
        return summary


def main():
    jira_roles = JiraRoles(session, BASE_URL)
    result = jira_roles.clean_project(
        "XXXXXGROUPCODE",
        KEEP_GROUPS
    )
    print("\n################################ SUMMARY ################################")
    total_users = set()
    total_groups = set()
    for _, data in result.items():
        total_users.update(data["users"])
        total_groups.update(data["groups"])
    print(f"Unique users removed : {len(total_users)}")
    print(f"Unique groups removed: {len(total_groups)}")
    print("#########################################################################")


if __name__ == "__main__":
    main()
