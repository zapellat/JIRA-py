from enum import IntEnum
from typing import Any
from requests.exceptions import (HTTPError, SSLError, ConnectionError, Timeout)
from jira_auth import JiraClient


class ProjectField(IntEnum):
    PROJECT_STATUS = 38
    GDS_LINE = 111
    APM_CODE_CORRECTIVE = 105
    APM_CODE_DEV = 60
    APM_CODE_RELEASE = 107
    OWNER_ORG_UNIT = 33
    DIGITAL_HUB = 15
    VALUE_CHAIN_PARENT = 36
    VALUE_CHAIN_CHILD = 37
    END_DATE = 24
    ANNOUNCER = 177
    COMPLAINCE_BADGE = 155
    APP_RESPONDENT = 152
    ILD = 150
    DEVELOPERS = 147
    SPONSOR = 151
    SNOW_CODES = 80
    PO = 148
    SCRUM = 149


class Profields(JiraClient):

    def __init__(self, session, base_url):
        super().__init__(session, base_url)

    # ------------------------------------------------------------------
    # UPDATE A SINGLE FIELD
    # ------------------------------------------------------------------

    def update_onefield(self, project: str, field: ProjectField, value: Any):
        payload = {
            "id": int(field),
            "value": value,
            "action": {
                "isVisibleValue": True,
                "isEditableValue": True
            }
        }
        url = (
            f"{self.base_url}"
            f"/rest/profields/api/2.0/values/projects/"
            f"{project}/fields/{int(field)}"
        )
        try:
            response = self.request("POST", url, json=payload)
            return response.json() if response.text else None

        except (SSLError, ConnectionError, Timeout):
            print("Network Error: Unable to connect to Jira. Check your company network or VPN connection.")
            raise SystemExit(1)

    # ------------------------------------------------------------------
    # UPDATE MULTIPLE FIELDS
    # ------------------------------------------------------------------

    def update_multifields(self, project: str, fields: dict[ProjectField, Any]) -> bool:
        for field, value in fields.items():
            print(f"Updating {field.name} -> {value}")
            try:
                self.update_onefield(project, field, value)
            except HTTPError as e:
                response = e.response
                if response is None:
                    print("HTTPError without response object")
                    print(e)
                    return False
                status_code = response.status_code
                if status_code in (400, 401, 403, 405):
                    print(
                        f"API Returned {status_code} - Cannot update project '{project}'."
                    )
                    return False
                print(
                    f"Unexpected error updating project '{project}'."
                )
                print(f"HTTP Status: {status_code}")
                print(response.text)
                return False
        return True
