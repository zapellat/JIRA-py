import os
import json
import logging
from atlassian import Jira
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# JIRA API Configuration
JIRA_URL = os.getenv('JIRA_URL')
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_TOKEN = os.getenv('JIRA_TOKEN')

jira_api = Jira(
    url=JIRA_URL,
    username=JIRA_USERNAME,
    token=JIRA_TOKEN
)

# Replace with your issue key
issue_key = "GRIDSBCRBR-315"

# Fetch all field metadata (field ID and field name)
fields_metadata = jira_api.get("/rest/api/2/field")

# Create a dictionary to map field IDs to field names
field_map = {field["id"]: field["name"] for field in fields_metadata}

# Fetch the issue object (returns a dictionary)
issue = jira_api.issue(issue_key)

# Extract the fields data
fields = issue.get('fields', {})

# Print all fields with both their ID and display name
print(f"Fields for issue {issue_key}:\n")

# Loop through the fields and display both ID and name with values
for field_id, value in fields.items():
    # Get the field name from the field map or use the field ID if not found
    field_name = field_map.get(field_id, field_id)

    # Skip null or empty values
    if value is not None:
        print(f"Field ID: {field_id}")
        print(f"Field Name: {field_name}")
        print(f"Value: {json.dumps(value, indent=4, ensure_ascii=False)}\n")
