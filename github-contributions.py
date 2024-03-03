import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('GITHUB_USERNAME')
token = os.getenv('GITHUB_TOKEN')

def fetch_all_pages(url, headers):
    """Fetch all pages for a given API request."""
    all_data = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            all_data.extend(response.json())
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                break
        else:
            print("Failed to fetch data:", response.status_code)
            break
    return all_data

def get_repositories(username, token):
    """Fetch all repositories the user has access to."""
    url = f"https://api.github.com/users/{username}/repos?type=all&per_page=100"
    headers = {'Authorization': f'token {token}'}
    return fetch_all_pages(url, headers)

def get_commits_for_repo(username, token, repo_name):
    """Fetch all commits made by the user in a specific repository."""
    commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits?author={username}&per_page=100"
    headers = {'Authorization': f'token {token}'}
    return fetch_all_pages(commits_url, headers)

def main():
    repositories = get_repositories(username, token)
    all_commits_data = []

    for repo in repositories:
        repo_name = repo['name']
        commits = get_commits_for_repo(username, token, repo_name)
        for commit in commits:
            all_commits_data.append({
                'Repository': repo_name,
                'Commit Message': commit['commit']['message'],
                'Date': commit['commit']['author']['date']
            })

    commits_df = pd.DataFrame(all_commits_data)
    csv_filename = 'github_contributions.csv'
    commits_df.to_csv(csv_filename, index=False)
    print(f"Contributions saved to {csv_filename}")

if __name__ == "__main__":
    main()
