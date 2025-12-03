Jira-Py - Python Scripts for Jira Issue Extraction and Label Automation.

I do work in IT but I'm NOT a full Developer and I made this only to make my life easier while managing Jira at work.

This repository contains some scripts designed to:

Perform large-scale Jira issue extraction

Inspect field metadata (including customfields)

Automate label updates across multiple issues

Generate Excel reports with organized tabs



Repository Contents:
1. Issue_Extraction.py
    Jira API authentication;
   
    Dynamic JQL construction;
   
    Paginated issue retrieval;
   
    Mapping and normalization of dozens of fields;
   
    Categorization of issues by type and status;
   
    Automatic generation of a structured Excel file;
   


3. getFieldsJIRA.py
    A helper tool used to inspect all fields of a given issue
   
    Lists every field (Field ID + Name + Value)
   
    Displays complete JSON values
   
    Helps identify new or unknown customfields
   
    Ideal for debugging or mapping complex Jira schemas
   

5. Update_Labels.py
    This script updates labels in bulk without overwriting existing ones.
   
    Executes a JQL for a list of issues
   
    Reads current labels
   
    Appends only missing labels
   
    Prevents duplicates
   
    Logs updates clearly
   

Install dependencies:
pip install atlassian-python-api openpyxl python-dotenv requests


.env Configuration
Create a .env file in the project root containing your Jira Credentials (do not upload env files online):

JIRA_URL=https://your_jira_url

JIRA_USERNAME=your.username

JIRA_TOKEN=your_api_token


