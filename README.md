# GitHub Contributions Tracker

## Overview

GitHub Contributions Tracker is a Python script designed for developers to fetch and analyze their contributions on GitHub over specific intervals. This tool is especially useful for generating reports for performance reviews, showcasing your work, or simply keeping track of your contributions.

## Features

- Fetch all pull requests made by a user across all repositories.
- Filter contributions by custom intervals (e.g., every 4 months).
- Export contributions data to a CSV file for easy analysis.

## Prerequisites

- Python 3.6 or newer
- `requests` and `pandas` libraries
- A GitHub Personal Access Token
- Docker (for Docker usage)

## Installation

### Standard Installation

Clone this repository to your local machine.

```bash
git clone https://github.com/yourusername/github-contributions-tracker.git
```

Install required Python packages:

```bash
pip install requests pandas python-dotenv
```

### Docker Installation

Ensure Docker is installed and running on your machine. Build the Docker image with:

```bash
docker-compose build
```

## Configuration

Set up your GitHub Personal Access Token (PAT) as environment variables:

- **Without Docker:**

  - On Linux/macOS:

    ```bash
    export GITHUB_USERNAME='your_github_username'
    export GITHUB_TOKEN='your_pat_token'
    ```

  - On Windows:

    ```cmd
    set GITHUB_USERNAME=your_github_username
    set GITHUB_TOKEN=your_pat_token
    ```

- **With Docker:**

  Create a `.env` file in the same directory as your `docker-compose.yml` with the following contents:

  ```env
  GITHUB_USERNAME=your_username
  GITHUB_TOKEN=your_token
  ```

## Usage

### Standard Usage

To run the script with default settings (analyzing the contributions last 4 months):

```bash
python3 github_contributions.py
```

### Customizing Intervals

You can specify the duration in months using command-line arguments:

```bash
python3 github_contributions.py --duration-months 6
```

### Docker Usage

To run the script using Docker, after configuring your `.env` file:

```bash
docker-compose up
```

### Output

The script outputs a CSV file (`github_contributions_intervals.csv`) with the pull requests fetched according to the specified intervals.

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, and suggest features via the issue tracker.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## GitHub API Rate Limiting

Be aware of [GitHub's API rate limits](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting). Ensure not to exceed these limits to avoid disruptions.

## Troubleshooting

- **Environment Variables Not Recognized**: Ensure you restart your terminal or IDE after setting up environment variables.
- **Rate Limit Exceeded**: If you encounter rate limiting errors, consider reducing the frequency of requests or checking your GitHub PAT permissions.
