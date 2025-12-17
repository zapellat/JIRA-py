import os
import logging
from atlassian import Jira
from requests.exceptions import HTTPError
from dotenv import load_dotenv

# LOAD ENV #
load_dotenv()

# LOGGING #
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# JIRA API #
JIRA_URL = os.getenv('JIRA_URL')
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_TOKEN = os.getenv('JIRA_TOKEN')

jira_api = Jira(
    url=JIRA_URL,
    username=JIRA_USERNAME,
    token=JIRA_TOKEN
)
logging.info("JIRA API Authenticated.")

# LABELS - THIS IS A LIST #
new_label_here = ['2025_CAB', '2025_DEZ_S2']

# ISSUES
issue_keys = [
    "JIRAISSUE-527", "JIRAISSUE-468"
]

# JQL
jql_query = 'key in ({})'.format(','.join(f'"{k}"' for k in issue_keys))
logging.info(f"Searching: {jql_query}")

# SERACHING ISSUES
all_issues = []
start_at = 0
max_results = 100

while True:
    page = jira_api.jql(jql_query, start=start_at, limit=max_results)
    issues_page = page.get('issues', [])

    if not issues_page:
        break

    all_issues.extend(issues_page)
    start_at += max_results

    if len(issues_page) < max_results:
        break

logging.info(f"Issues loaded: {len(all_issues)}")

# UPDATING LABELS
try:
    if not all_issues:
        logging.info("Zero issues found.")
    else:
        for issue in all_issues:
            issue_key = issue['key']
            existing_labels = issue['fields'].get('labels', [])

            existing_labels = [str(lbl) for lbl in existing_labels]

            labels_to_add = [lbl for lbl in new_label_here if lbl not in existing_labels]

            if labels_to_add:
                updated_labels = existing_labels + labels_to_add

                jira_api.update_issue_field(issue_key, fields={'labels': updated_labels})
                logging.info(f"Labels add to issue {issue_key}: {labels_to_add}")
            else:
                logging.info(f"Issue {issue_key} already have the label.")

    logging.info(f"{len(all_issues)} labels updated.")

except HTTPError as err:
    logging.error(f"Erro HTTP: {err.response.status_code} - {err.response.text}")
except Exception as e:
    logging.error(f"Error: {str(e)}")
