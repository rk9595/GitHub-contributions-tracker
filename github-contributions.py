import requests
import pandas as pd
import os
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import csv


def setup_argparse():
    """Set up argparse for command line arguments."""
    parser = argparse.ArgumentParser(description='Fetch GitHub contributions over a specified duration in months.')
    parser.add_argument('--duration-months', type=int, default=4,
                        help='Duration in months for which to fetch the contributions (default: 12 months)')
    return parser.parse_args()

def create_session(token):
    """Create a requests session for API calls."""
    session = requests.Session()
    session.headers.update({'Authorization': f'token {token}'})
    return session

def fetch_all_pages(url, session):
    """Fetch all pages for a given API request using a session."""
    all_data = []
    while url:
        response = session.get(url)
        if response.status_code == 200:
            all_data.extend(response.json())
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                break
        else:
            print(f"Failed to fetch data: {response.status_code}")
            break
    return all_data

def get_repositories(username, session):
    """Fetch all repositories the user has access to."""
    url = f"https://api.github.com/users/{username}/repos?type=all&per_page=100"
    return fetch_all_pages(url, session)

def get_pull_requests_for_repo(username, repo_name, session, start_date):
    """Fetch closed pull requests made by the user in a specific repository after a start date."""
    prs_url = f"https://api.github.com/repos/{username}/{repo_name}/pulls?state=closed&per_page=100&sort=updated&direction=desc"
    prs = fetch_all_pages(prs_url, session)
    return [pr for pr in prs if pr['merged_at'] and datetime.strptime(pr['merged_at'], '%Y-%m-%dT%H:%M:%SZ') >= start_date]

def generate_intervals(duration_months):
    """Generate interval from 'duration_months' ago to today."""
    end_date = datetime.now()
    start_date = end_date - relativedelta(months=duration_months)
    return [(start_date, end_date)]


def main():
    """Main function to fetch and save GitHub contributions for a specified duration."""
    args = setup_argparse()
    load_dotenv()
    username = os.getenv('GITHUB_USERNAME')
    token = os.getenv('GITHUB_TOKEN')
    
    if not username or not token:
        print("Error: GitHub username and token must be set in environment variables.")
        return  # Early exit if environment variables are not set
    
    session = create_session(token)
    intervals = generate_intervals(args.duration_months)
    repositories = get_repositories(username, session)
    all_pr_data = []

    # Assuming there is only one interval for simplification
    start_date, end_date = intervals[0]
    interval_description = f"# Interval: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    for repo in repositories:
        repo_name = repo['name']
        pull_requests = get_pull_requests_for_repo(username, repo_name, session, start_date)
        for pr in pull_requests:
            pr_merged_at = datetime.strptime(pr['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
            if start_date <= pr_merged_at <= end_date:
                all_pr_data.append({
                    'Repository': repo_name,
                    'Pull Request Title': pr['title'],
                    'Date Merged': pr['merged_at'],
                    'Description': pr.get('body', '')  # Get description, default to empty string if not present
                })

    csv_filename = 'github_contributions.csv'
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        file.write(f"{interval_description}\n")  # Write the interval description as a comment
        # Write headers
        headers = ['Repository', 'Pull Request Title', 'Date Merged', 'Description']
        writer.writerow(headers)
        # Write data rows
        for item in all_pr_data:
            writer.writerow([item['Repository'], item['Pull Request Title'], item['Date Merged'], item['Description']])

    print(f"Contributions saved to {csv_filename}")

if __name__ == "__main__":
    main()

