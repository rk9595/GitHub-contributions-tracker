import requests
import pandas as pd
import os
import argparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

def setup_argparse():
    """Set up argparse for command line arguments."""
    parser = argparse.ArgumentParser(description='Fetches GitHub contributions by intervals.')
    parser.add_argument('--start-month', type=int, default=((datetime.now().month - 5) % 12) + 1,
                        help='Start month for the interval (default: 4 months before the current month)')
    parser.add_argument('--interval-months', type=int, default=4,
                        help='Length of the interval in months (default: 4)')
    return parser.parse_args()

def create_session(token):
    """Create a requests session for API calls."""
    session = requests.Session()
    session.headers.update({'Authorization': f'token {token}'})
    return session

def fetch_all_pages(url, session):
    """
    Fetch all pages for a given API request using a session.
    
    Args:
        url (str): The initial URL to fetch data from.
        session (requests.Session): The requests session object for making API calls.
    
    Returns:
        list: A list of all items fetched from all pages of the API response.
    """
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
    """
    Fetch all repositories the user has access to.
    
    Args:
        username (str): GitHub username.
        session (requests.Session): The requests session object for making API calls.
    
    Returns:
        list: A list of repositories.
    """
    url = f"https://api.github.com/users/{username}/repos?type=all&per_page=100"
    return fetch_all_pages(url, session)

def get_pull_requests_for_repo(username, repo_name, session):
    """
    Fetch all closed pull requests made by the user in a specific repository.
    
    Args:
        username (str): GitHub username.
        repo_name (str): The name of the repository.
        session (requests.Session): The requests session object for making API calls.
    
    Returns:
        list: A list of merged pull requests.
    """
    prs_url = f"https://api.github.com/repos/{username}/{repo_name}/pulls?state=closed&per_page=100"
    closed_prs = fetch_all_pages(prs_url, session)
    return [pr for pr in closed_prs if pr['merged_at'] is not None]

def generate_intervals(start_month, interval_months):
    """
    Generate a list of interval tuples (start_date, end_date) based on start month and interval length.
    
    Args:
        start_month (int): The month to start the intervals from.
        interval_months (int): The length of each interval in months.
    
    Returns:
        list: A list of tuples each representing the start and end dates of an interval.
    """
    start_date = datetime(datetime.now().year, start_month, 1)
    intervals = []
    while start_date.year == datetime.now().year:
        end_date = start_date + relativedelta(months=interval_months, days=-1)
        intervals.append((start_date, end_date))
        start_date += relativedelta(months=interval_months)
    return intervals

def main():
    """Main function to fetch and save GitHub contributions by specified intervals."""
    args = setup_argparse()
    load_dotenv()
    username = os.getenv('GITHUB_USERNAME')
    token = os.getenv('GITHUB_TOKEN')
    
    if not username or not token:
        raise ValueError("GitHub username and token must be set in environment variables.")

    session = create_session(token)
    intervals = generate_intervals(args.start_month, args.interval_months)
    repositories = get_repositories(username, session)
    all_pr_data = []

    for repo in repositories:
        repo_name = repo['name']
        pull_requests = get_pull_requests_for_repo(username, repo_name, session)
        
        for pr in pull_requests:
            pr_merged_at = datetime.strptime(pr['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
            for start_date, end_date in intervals:
                if start_date <= pr_merged_at <= end_date:
                    all_pr_data.append({
                        'Interval': f"{start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')}",
                        'Repository': repo_name,
                        'Pull Request Title': pr['title'],
                        'Date Merged': pr['merged_at']
                    })
                    break

    pr_df = pd.DataFrame(all_pr_data)
    csv_filename = 'github_contributions_intervals.csv'
    pr_df.to_csv(csv_filename, index=False)
    print(f"Contributions saved to {csv_filename}")

if __name__ == "__main__":
    main()
