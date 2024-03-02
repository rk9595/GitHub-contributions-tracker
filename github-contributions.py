import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('GITHUB_USERNAME')
token = os.getenv('GITHUB_TOKEN')


# Fetch events
def fetch_events(username, token):
    url = f"https://api.github.com/users/{username}/events"
    response = requests.get(url, headers={'Authorization': f'token {token}'})
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data:", response.status_code)
        return []

# Extract commit data
def extract_commit_data(events):
    commits_data = []
    for event in events:
        if event['type'] == 'PushEvent':
            repo_name = event['repo']['name']
            for commit in event['payload']['commits']:
                commits_data.append({
                    'Repository': repo_name,
                    'Commit Message': commit['message'],
                    'Date': event['created_at']
                })
    return pd.DataFrame(commits_data)


# Main function
def main():
    events = fetch_events(username, token)
    commits_df = extract_commit_data(events)
    

if __name__ == "__main__":
    main()
