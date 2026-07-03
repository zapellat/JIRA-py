import os
import logging
from atlassian import Jira
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import builtins

print("lower on int exists?", hasattr(1, "lower"))

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
new_label_here = ['XXXXXX', 'XXXXXXX']
READY_TO_INSTALL_TRANSITION_ID = 121

# JIRA ISSUES KEYS #
issue_keys = ["XXXX-643", "XXXX-641", "XXXX-635", "XXXX-634", "XXX-632",
              ]

# SERACHING ISSUES
jql_query = 'key in ({})'.format(','.join(f'"{k}"' for k in issue_keys))
logging.info(f"Searching Query: {jql_query}")


# JIRA TRANSITION
def transition_issue_by_id(jira, issue_key, transition_id):
    try:
        transitions = jira.get_issue_transitions(issue_key)
        available_ids = {int(t['id']) for t in transitions}
        if int(transition_id) not in available_ids:
            logging.info(
                f"Issue {issue_key} already in 'Ready To Install' or transition ID={transition_id} not available."
            )
            return False

        base_url = jira.url.rstrip("/")
        url = f"{base_url}/rest/api/2/issue/{issue_key}/transitions"
        payload = {
            "transition": {
                "id": str(transition_id)
            }
        }
        response = jira._session.post(url, json=payload)
        response.raise_for_status()

        logging.info(f"Issue {issue_key} transitioned using ID={transition_id}")
        return True
    except Exception as e:
        logging.error(
            f"Transition failed for {issue_key} | ID={transition_id} | {e}"
        )
        return False


# SEARCH ALL ISSUES AND QUERY LIMITS
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

logging.info(f"Total Issues loaded: {len(all_issues)}")

# UPDATING LABELS
if not all_issues:
    logging.info("No Issues founded.")
else:
    for issue in all_issues:
        issue_key = issue['key']

        try:
            existing_labels = issue['fields'].get('labels', [])
            existing_labels = [str(lbl) for lbl in existing_labels]
            labels_to_add = [
                lbl for lbl in new_label_here
                if lbl not in existing_labels
            ]
            if labels_to_add:
                updated_labels = existing_labels + labels_to_add
                jira_api.update_issue_field(
                    issue_key,
                    fields={"labels": updated_labels}
                )
                logging.info(f"Labels added to the Issue {issue_key}: {labels_to_add}")
            else:
                logging.info(f"Issue {issue_key} already have the labels.")
        except HTTPError as err:
            logging.error(
                f"Issue {issue_key} | HTTP Error Updating Labels: "
                f"{err.response.status_code} - {err.response.text}"
            )
        except Exception as e:
            logging.error(
                f"Issue {issue_key} | Unexpected Error Updating Labels: {e}"
            )
        try:
            transition_issue_by_id(
                jira_api,
                issue_key,
                READY_TO_INSTALL_TRANSITION_ID
            )
        except Exception as e:
            logging.error(
                f"Issue {issue_key} | Transition failed: {e}"
            )

logging.info(f"Issues Updated: {len(all_issues)}.")
