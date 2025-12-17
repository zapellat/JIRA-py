import os
import logging
from atlassian import Jira
from requests.exceptions import HTTPError
from dotenv import load_dotenv

# CARREGAR ARQUIVO ENV #
load_dotenv()

# CONFIGURAR LOGGING #
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CONFIGURAR JIRA API #
JIRA_URL = os.getenv('JIRA_URL')
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_TOKEN = os.getenv('JIRA_TOKEN')

jira_api = Jira(
    url=JIRA_URL,
    username=JIRA_USERNAME,
    token=JIRA_TOKEN
)
logging.info("JIRA API Configurada e Autenticada.")

# LABELS A INSERIR
new_label_here = ['2025_CAB', '2025_DEZ_S2']

# LISTA DE ISSUES
issue_keys = [
    "ICTBRSAPISU-527", "ICTBRSAPCCS-468", "ICTBRDELSGNSP-10", "ICTBRSAPBW-77", "EICTCRBRDGID-81", "ICTBRSFBR-152",
    "ICTBRSFBR-149", "ICTBRSFBR-146", "EICTCRBRIDTC-77", "EICTCRBRINDES-294", "EICTCRBRINDES-298", "EICTCRBRIDWRM-146",
    "ICTBRMLATAM-124", "ICTBRSAPCCS-474", "ICTBRSAPCCS-497", "ICTBRMLATAM-131", "ICTBRMLATAM-128", "ICTBRSAPISU-517",
    "ICTBRSAPISU-515", "ICTBRSAPISU-516", "ICTBRSAPISU-518", "ICTBRSAPCCS-505", "ICTBRSAPISU-526", "ICTDASGESPBR-8",
    "ICTBRPIMRJSP-12", "EICTCRBRIDWRM-148", "EICTCRBRIDWF-330", "EICTCRBRIDWF-321", "EICTCRBRIDWF-320",
    "AROOM25056731-481", "AP0520804IM-225", "AP0520804IM-234", "AP0520804IM-237", "ICTBRSAPISU-511", "ICTBRSAPISU-512",
    "ICTBRSAPCCS-507", "EICTCRBRIDACS-265", "EICTCRBRIDACS-273", "EICTCRBRIDTC-74",
    "EICTCRBRIDACS-274"
]

# MONTAR O JQL
jql_query = 'key in ({})'.format(','.join(f'"{k}"' for k in issue_keys))
logging.info(f"Procurando pela Query: {jql_query}")

# BUSCAR TODAS AS ISSUES COM PAGINAÇÃO
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

logging.info(f"Total de Issues carregados: {len(all_issues)}")

# ATUALIZAR LABELS
try:
    if not all_issues:
        logging.info("Nenhum Issue encontrado.")
    else:
        for issue in all_issues:
            issue_key = issue['key']
            existing_labels = issue['fields'].get('labels', [])

            # Garantir que todos os labels existentes são strings
            existing_labels = [str(lbl) for lbl in existing_labels]

            # Labels faltantes
            labels_to_add = [lbl for lbl in new_label_here if lbl not in existing_labels]

            if labels_to_add:
                updated_labels = existing_labels + labels_to_add

                jira_api.update_issue_field(issue_key, fields={'labels': updated_labels})
                logging.info(f"Labels adicionados ao Issue {issue_key}: {labels_to_add}")
            else:
                logging.info(f"Issue {issue_key} já contém todos os labels necessários.")

    logging.info(f"Foram atualizados {len(all_issues)} itens.")

except HTTPError as err:
    logging.error(f"Erro HTTP: {err.response.status_code} - {err.response.text}")
except Exception as e:
    logging.error(f"Ocorreu um Erro: {str(e)}")
