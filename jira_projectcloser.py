from dotenv import load_dotenv
from typing import Dict, List
from datetime import date
from typing import Any
from jira_auth import session, BASE_URL
from jira_profields import ProjectField, Profields
from jira_roles import JiraRoles
import time

load_dotenv()

KEEP_GROUPS = [
    "GG-springlab-jira-admins",
    "ictgovernanceandcompliancebrazil",
    "jira-administrators",
    "ato"
]

FIELDS = {
    ProjectField.PROJECT_STATUS: "Closed",
    ProjectField.GDS_LINE: "ICT Brazil",
    ProjectField.APM_CODE_DEV: [],
    ProjectField.APM_CODE_RELEASE: [],
    ProjectField.APM_CODE_CORRECTIVE: [],
    ProjectField.OWNER_ORG_UNIT: "Global Digital Solutions (30024927)",
    ProjectField.DIGITAL_HUB: "Y",
    ProjectField.ANNOUNCER: "",
    ProjectField.COMPLAINCE_BADGE: "",
    ProjectField.SPONSOR: "",
    ProjectField.ILD: "",
    ProjectField.DEVELOPERS: "",
    ProjectField.APP_RESPONDENT: "",
    ProjectField.PO: "",
    ProjectField.SCRUM: "",
    ProjectField.SNOW_CODES: [],
    ProjectField.END_DATE: date.today().isoformat(),
}


class ProjectCloser:

    def __init__(self, session=session, base_url=BASE_URL):
        self.roles = JiraRoles(session, base_url)
        self.profields = Profields(session, base_url)

    def close_project(
            self,
            project: str,
            keep_groups: List[str],
            fields: Dict[ProjectField, Any]
    ):
        print("\n############################# CLOSING PROJECT STARTED #############################")
        print(f"\nClosing Project: {project}...")
        print(f"Updating project fields...")
        updated = self.profields.update_multifields(project, fields)
        if not updated:
            print("\n##################################### SUMMARY #####################################")
            print(f"Project {project} was not closed.")
            print("###################################################################################")
            return None
        return self.roles.clean_project(
            project,
            keep_groups
        )

    def close_projects(
            self,
            projects: List[str],
            keep_groups: List[str],
            fields: Dict[ProjectField, Any]
    ):
        results = {}
        failed = []

        for i, project in enumerate(projects):
            result = self.close_project(
                project=project,
                keep_groups=keep_groups,
                fields=fields
            )
            results[project] = result

            if result is None:
                failed.append(project)

            if i < len(projects) - 1:
                print("\nWaiting 60 seconds before the next project...")
                time.sleep(60)

        return results, failed


def main():
    projects = ["PTI"]

    closer = ProjectCloser()

    results, failed = closer.close_projects(
        projects=projects,
        keep_groups=KEEP_GROUPS,
        fields=FIELDS
    )

    print("\n##################################### SUMMARY #####################################")

    total_users = set()
    total_groups = set()

    for project, result in results.items():
        if result is None:
            continue
        for data in result.values():
            total_users.update(data["users"])
            total_groups.update(data["groups"])

        print(f"Project {project} closed in ProjectData")

    print(f"Unique users removed: {len(total_users)}")
    print(f"Unique groups removed: {len(total_groups)}")

    if failed:
        print("\nProjects that failed:")
        for project in failed:
            print(f"  - {project}")
    print("###################################################################################")


if __name__ == "__main__":
    main()
