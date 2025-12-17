import os
import json
import logging
from atlassian import Jira
from dotenv import load_dotenv

# LOAD ENV
load_dotenv()

# LOGGING
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# JIRA API
JIRA_URL = os.getenv('JIRA_URL')
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_TOKEN = os.getenv('JIRA_TOKEN')

jira_api = Jira(
    url=JIRA_URL,
    username=JIRA_USERNAME,
    token=JIRA_TOKEN
)

# REPLACE WITH YOUR ISSUE KEY
issue_key = "JIRAISSUE-315"

# FETCH ALL FIELD METADATA - FIELD ID AND FIELD NAME
fields_metadata = jira_api.get("/rest/api/2/field")

# CREATE A DICTIONARU TO MAP FIELD ID TO FIELD NAME
field_map = {field["id"]: field["name"] for field in fields_metadata}

# FETCH THE ISSUE OBJECT
issue = jira_api.issue(issue_key)

# EXTRACT THE FIELD DATA
fields = issue.get('fields', {})

# PRINT ALL FIELDS WITH BOTH THEIR ID AND DISPLAY NAME
print(f"Fields for issue {issue_key}:\n")

# LOOP THROUGH THE FIELDS AND DISPLAY BOTH ID AND NAME WITH VALUES
for field_id, value in fields.items():
    field_name = field_map.get(field_id, field_id)
    if value is not None:
        print(f"Field ID: {field_id}")
        print(f"Field Name: {field_name}")
        print(f"Value: {json.dumps(value, indent=4, ensure_ascii=False)}\n")

