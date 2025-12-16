import os
import json
import requests
from jira import JIRA
from jira.exceptions import JIRAError

CONFIG_FILE = os.path.expanduser("~/.jira_config")

# Status transition IDs (replace with your Jira's workflow transition IDs)
APPROVE_TRANSITION_ID = "171"  # Replace with the ID for "approve" transition
CANCEL_TRANSITION_ID = "181"  # Replace with the ID for "cancel" transition

def prompt_with_default(prompt_message, default_value):
    """Prompt the user with a default value."""
    user_input = input(f"{prompt_message} (default: {default_value}): ").strip()
    return user_input if user_input else default_value


def save_config():
    """Prompt the user for Jira configuration and save it to a config file"""
    default_server = "https://hiretual.atlassian.net"
    default_email = ""
    default_token = ""
    default_project = "CMR"

    jira_server = prompt_with_default("Enter Jira server URL", default_server)
    jira_email = prompt_with_default("Enter Jira email", default_email)
    jira_api_token = prompt_with_default("Enter Jira API token", default_token)
    project_key = prompt_with_default("Enter Jira project key", default_project)

    config = {
        "jira_server": jira_server,
        "jira_email": jira_email,
        "jira_api_token": jira_api_token,
        "project_key": project_key
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

    print(f"Configuration saved to {CONFIG_FILE}")

def load_config():
    """Load Jira configuration from the config file"""
    if not os.path.exists(CONFIG_FILE):
        print(f"Configuration file {CONFIG_FILE} not found. Please run the script and set up the configuration.")
        save_config()

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    return config

def validate_config(config):
    """Validate the Jira configuration"""
    try:
        # Use API v3 as v2 has been deprecated and removed by Atlassian
        options = {
            'server': config["jira_server"],
            'rest_api_version': '3'
        }
        jira_client = JIRA(options=options, basic_auth=(config["jira_email"], config["jira_api_token"]))
        jira_client.projects()  # Test the connection
        print("Configuration validated successfully.")
        return jira_client
    except Exception as e:
        print(f"Failed to validate configuration: {e}")
        print("Please reconfigure your Jira settings.")
        save_config()
        return None

def get_my_tickets(jira_client, project_key, config):
    """Fetch all Jira tickets assigned to the current user"""
    query = f'project = {project_key} AND assignee = currentUser() AND status = Open'
    
    try:
        # Try the standard jira library method first (works with jira>=3.8.0)
        tickets = jira_client.search_issues(query, maxResults=100)
        return tickets
    except JIRAError as e:
        if e.status_code == 410:
            # API v2 search removed, use direct API v3 call
            print("Using new Jira API v3 search endpoint...")
            return search_issues_v3(config, query)
        raise


def search_issues_v3(config, jql):
    """Search issues using the new Jira API v3 /search/jql endpoint"""
    url = f"{config['jira_server']}/rest/api/3/search/jql"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    params = {
        "jql": jql,
        "maxResults": 100
    }
    
    response = requests.get(
        url,
        headers=headers,
        params=params,
        auth=(config["jira_email"], config["jira_api_token"])
    )
    
    if response.status_code != 200:
        print(f"Error searching issues: {response.status_code} - {response.text}")
        return []
    
    data = response.json()
    # Convert to simple ticket objects with key and fields
    tickets = []
    for issue in data.get("issues", []):
        ticket = type('Ticket', (), {
            'key': issue['key'],
            'fields': type('Fields', (), {
                'summary': issue['fields'].get('summary', 'No summary')
            })()
        })()
        tickets.append(ticket)
    
    return tickets

def display_tickets(tickets):
    """Display the list of tickets"""
    print("\nTickets assigned to you:")
    for idx, ticket in enumerate(tickets, 1):
        print(f"{idx}. [{ticket.key}] {ticket.fields.summary}")

def change_ticket_status(jira_client, ticket, transition_id):
    """Change the status of a Jira ticket"""
    try:
        jira_client.transition_issue(ticket, transition_id)
        print(f"Successfully changed status for [{ticket.key}] {ticket.fields.summary}")
    except Exception as e:
        print(f"Failed to change status for [{ticket.key}] {ticket.fields.summary}: {e}")

def approve_or_cancel_tickets(jira_client, tickets):
    """Allow the user to approve or cancel tickets"""
    approve = []
    cancel = []

    for idx, ticket in enumerate(tickets, 1):
        while True:
            action = input(f"Action for [{ticket.key}] {ticket.fields.summary} (a=approve, c=cancel, s=skip): ").strip().lower()
            if action == "a":
                change_ticket_status(jira_client, ticket, APPROVE_TRANSITION_ID)
                approve.append(ticket)
                break
            elif action == "c":
                change_ticket_status(jira_client, ticket, CANCEL_TRANSITION_ID)
                cancel.append(ticket)
                break
            elif action == "s":
                break
            else:
                print("Invalid input, please choose a, c, or s.")

    return approve, cancel

def jira_ticket_transaction():
    config = load_config()
    jira_client = validate_config(config)

    if not jira_client:
        return

    # Fetch all tickets assigned to the current user
    # Using currentUser() in JQL query instead of deprecated current_user() method
    tickets = get_my_tickets(jira_client, config["project_key"], config)

    if not tickets:
        print("No tickets assigned to you.")
        return

    # Display the tickets
    display_tickets(tickets)

    # Perform approve or cancel actions
    approve, cancel = approve_or_cancel_tickets(jira_client, tickets)

    # Output results
    print("\nAction results:")
    if approve:
        print("Approved tickets:")
        for ticket in approve:
            print(f"- [{ticket.key}] {ticket.fields.summary}")
    if cancel:
        print("Cancelled tickets:")
        for ticket in cancel:
            print(f"- [{ticket.key}] {ticket.fields.summary}")
    if not approve and not cancel:
        print("No actions were taken.")

if __name__ == "__main__":
    jira_ticket_transaction()

