import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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

def get_pull_requests_for_repo(username, token, repo_name):
    """Fetch all closed pull requests made by the user in a specific repository."""
    prs_url = f"https://api.github.com/repos/{username}/{repo_name}/pulls?state=closed&per_page=100"
    headers = {'Authorization': f'token {token}'}
    closed_prs = fetch_all_pages(prs_url, headers)
    merged_prs = [pr for pr in closed_prs if pr['merged_at'] is not None]
    return merged_prs

def generate_intervals(start_month, interval_months):
    """Generate a list of interval tuples (start_date, end_date) based on start month and interval length."""
    start_date = datetime(datetime.now().year, start_month, 1)
    intervals = []
    while start_date.year == datetime.now().year:
        end_date = start_date + relativedelta(months=interval_months, days=-1)
        intervals.append((start_date.strftime('%Y-%m-%dT%H:%M:%SZ'), end_date.strftime('%Y-%m-%dT%H:%M:%SZ')))
        start_date += relativedelta(months=interval_months)
    return intervals

def main():
    # Example inputs; replace with user input if necessary
    start_month = int(input("Enter the start month (1-12): "))
    interval_months = int(input("Enter the interval length in months: "))
    
    intervals = generate_intervals(start_month, interval_months)
    repositories = get_repositories(username, token)
    all_pr_data = []

    for repo in repositories:
        repo_name = repo['name']
        pull_requests = get_pull_requests_for_repo(username, token, repo_name)
        
        for pr in pull_requests:
            pr_merged_at = pr['merged_at']
            for start_date, end_date in intervals:
                if start_date <= pr_merged_at <= end_date:
                    all_pr_data.append({
                        'Interval': f"{start_date[:7]} to {end_date[:7]}",
                        'Repository': repo_name,
                        'Pull Request Title': pr['title'],
                        'Date Merged': pr_merged_at
                    })
                    break

    pr_df = pd.DataFrame(all_pr_data)
    csv_filename = 'github_contributions_intervals.csv'
    pr_df.to_csv(csv_filename, index=False)
    print(f"Contributions saved to {csv_filename}")

if __name__ == "__main__":
    main()
