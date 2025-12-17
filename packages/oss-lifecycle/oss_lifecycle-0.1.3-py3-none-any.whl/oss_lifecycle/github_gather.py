"""
Collects commit information from a specified GitHub repository and processes it to generate detailed and monthly commit data.
Functions:
    install_gitpython():
        Installs GitPython if it is not already installed.
    clone_github_repo(repo_url, local_path=None):
        Clones a GitHub repository to a local directory.
    collect_commits(repo_path):
        Collects commit information from a local git repository and returns it as a pandas DataFrame.
    get_commits_df(repo_url):
        Main function to clone a repository and collect commits, saving the data to CSV files.
    get_monthly_commits(df):
        Consolidates the commits data by month to give a time series for modeling, saving the data to a CSV file.
Usage:
    To run the script, use the following command:
    python github_gather.py "<owner>/<repo>"
"""

import os
import pandas as pd
from datetime import datetime
import subprocess
import sys
import shutil
import git
import re
import time

def install_gitpython():
    """Install GitPython if not already installed"""
    try:
        import git
        print("Git already installed")
    except ImportError:
        print("Installing Git")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'GitPython'])

# Install GitPython
install_gitpython()

# Functions to collect GitHub commits
def clone_github_repo(repo_url, local_path=None):
    """
    Clone a GitHub repository to a local directory

    Parameters:
    -----------
    repo_url : str
        URL of the GitHub repository
    local_path : str, optional
        Local path to clone the repository.
        If None, uses the repository name in current directory

    Returns:
    --------
    str
        Path to the cloned repository
    """
    # If no local path specified, use repo name
    if local_path is None:
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        local_path = os.path.join(os.getcwd(), repo_name)

    # Ensure directory doesn't exist or is empty
    if os.path.exists(local_path):
        print(f"Directory {local_path} already exists. Skipping clone.")
        # If the directory exists but is empty, remove it and clone again
        if not os.listdir(local_path):
            print(f"Directory {local_path} is empty. Removing and cloning again.")
            shutil.rmtree(local_path)
            git.Repo.clone_from(repo_url, local_path)
            print(f"Repository cloned to {local_path}")
    else:
        # Clone the repository
        git.Repo.clone_from(repo_url, local_path)
        print(f"Repository cloned to {local_path}")

    return local_path

def collect_commits(repo_path):
    """
    Collect commit information from a local git repository using git log

    Parameters:
    -----------
    repo_path : str
        Path to the local git repository

    Returns:
    --------
    pandas.DataFrame
        DataFrame with commit details
    """
    print("Collecting commits...")
    # Use git log with a custom format to get commit details and stats
    # Format: hash, author name, author email, author date (ISO 8601), full message
    log_format = "--pretty=format:%H%x09%an%x09%ae%x09%aI%x09%B" # %B for full message
    command = ["git", "-C", repo_path, "log", "--numstat", log_format]
    result = subprocess.run(command, capture_output=True, text=True, check=True)

    commits_data = []
    current_commit = None
    # Regex to extract commit details from lines starting with --
    commit_regex = re.compile(r"([0-9a-f]{40})\t(.*?)\t(.*?)\t(.*?)\t(.*)", re.DOTALL) # Updated regex and added re.DOTALL for multiline messages

    for line in result.stdout.splitlines():
        commit_match = commit_regex.match(line)
        if commit_match:
            if current_commit:
                commits_data.append(current_commit)
            hash, author, author_email, date, message = commit_match.groups()
            current_commit = {
                'hash': hash,
                'author': author,
                'author_email': author_email,
                'date': date,
                'message': message.strip(),
                'additions': 0,
                'deletions': 0,
                'files_changed': 0
            }
        elif current_commit and line.strip() and not commit_regex.match(line):
             # This line contains file stats from --numstat
            parts = line.strip().split()
            if len(parts) >= 2 and (parts[0].isdigit() or parts[0] == '-') and (parts[1].isdigit() or parts[1] == '-'):
                additions = 0 if parts[0] == '-' else int(parts[0])
                deletions = 0 if parts[1] == '-' else int(parts[1])
                current_commit['additions'] += additions
                current_commit['deletions'] += deletions
                current_commit['files_changed'] += 1
            # Lines with only file name are not stat lines we need to process here
            else: # add other text to the message
                current_commit['message'] += "\n" + line.strip()

    if current_commit:
        commits_data.append(current_commit)

    # Convert to DataFrame
    df_commits = pd.DataFrame(commits_data)

    # Convert date to datetime objects, handling potential errors
    df_commits['date'] = pd.to_datetime(df_commits['date'], utc=True, errors='coerce')

    return df_commits


def get_commits_df(repo_url, repo_name):
    """
    Main function to clone repo and collect commits

    Parameters:
    -----------
    repo_url : str
        URL of the GitHub repository
    """
    # Clone the repository
    start_time = time.time()
    repo_path = clone_github_repo(repo_url)
    end_time = time.time()
    print(f"\nTime to clone repo: {end_time - start_time} seconds")
    package = repo_name.replace('/', '-')

    # Ensure data directory exists
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Collect commits
    start_time = time.time()
    df_commits = collect_commits(repo_path)
    end_time = time.time()
    print(f"\nTime to collect commits: {end_time - start_time} seconds")

    # Save to CSV
    df_commits.to_csv('data/' + package + '-commits_w_desc.csv', index=False)

    # Reformat df to clean up
    df = df_commits[['hash','author','date','additions','deletions', 'message']]
    df.columns = ['commit_id','author','date','lines_added','lines_removed', 'message']

    # Save to CSV
    print(f"\nCommits collected. Total commits: {len(df)}")

    return df

# Create monthly data frame
def get_monthly_commits(df, repo_name):
    """
    Consolidates the commits data by month to give a time series for modeling
    """
    df.loc[:, 'date'] = pd.to_datetime(df['date'], utc=True)

    df1 = df.groupby(pd.Grouper(key='date', freq='ME')).agg({
        'author': 'nunique',          # Count unique authors
        'lines_added': 'sum',           # Total lines added
        'lines_removed': 'sum',           # Total lines removed
    }).reset_index()

    df1['total_changes'] = df1['lines_added'] + df1['lines_removed']
    df1.drop(['lines_added', 'lines_removed'], axis=1, inplace=True)
    df1.columns = ['date', 'contributors', 'total_changes']
    print("Monthly dataframe shape =", df1.shape)

    package = repo_name.replace('/', '-')
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    output_file = os.path.join(data_dir, package + '-monthly.csv')
    df1.to_csv(output_file)
    print(f"Saved monthly data to {output_file}")

    return df1


def collect(repo_name):
    """
    To run:
    python oss_lifecycle/github_gather.py <owner>/<repo> (from root folder)
    """
    if not "/" in repo_name:
        print("Please provide a GitHub repository name in format '<owner>/<repo>'.")
        # EXAMPLES
        # repo_name = 'jupyterlab/jupyter-ai'
        # repo_name = 'jupyter-server/jupyter-scheduler'
        # repo_name = 'pandas-dev/pandas'
        # repo_name = 'jupyterlab/jupyterlab'
        # repo_name = 'langchain-ai/langchain'
        # repo_name = 'langchain-ai/langchain-aws'
    else:
        # repo_name = sys.argv[1]
        owner, repo = repo_name.split('/', 1)
        print(f"Owner: {owner} | Repo: {repo}")
        repo_url = "https://github.com/" + repo_name + ".git"
        df = get_commits_df(repo_url, repo_name)
        df1 = get_monthly_commits(df, repo_name)
        shutil.rmtree(repo)



# Main run
if __name__ == "__main__":
    """
    To run: 
    python oss_lifecycle/github_gather.py <owner>/<repo> (from root folder)
    """
    if len(sys.argv) < 2:
        print("Please provide a GitHub repository name in format '<owner>/<repo>'.")
        # EXAMPLES
        # repo_name = 'jupyterlab/jupyter-ai'
        # repo_name = 'jupyter-server/jupyter-scheduler'
        # repo_name = 'pandas-dev/pandas'
        # repo_name = 'jupyterlab/jupyterlab'
        # repo_name = 'langchain-ai/langchain'
        # repo_name = 'langchain-ai/langchain-aws'        
    else:  
        repo_name = sys.argv[1]
        collect(repo_name)
