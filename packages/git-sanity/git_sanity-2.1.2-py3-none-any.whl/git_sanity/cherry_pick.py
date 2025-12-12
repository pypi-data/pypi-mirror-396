import json
import logging
import os
import requests
from git_sanity import __config_root_dir__
from git_sanity import __config_file_name__
from git_sanity import __prog_log_file_name__
from git_sanity.utils import run
from git_sanity.utils import get_config_dir
from git_sanity.utils import load_user_config
from git_sanity.utils import get_user_config

# chp: Code Hosting Platform
chp_url = "https://gitcode.com"
chp_api_url = "https://api.gitcode.com/api/v5"

def get_git_password():
    try:
        credential_input = f"protocol=https\nhost=gitcode.com\n\n"
        result = run(['git', 'credential', 'fill'], input=credential_input, capture_output=True)
        if result.returncode:
            logging.error(f"Git credential retrieval failed: {result.stderr}. Use credential.helper to save credentials")
            exit(1)
        for line in result.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1]
    except Exception as e:
        logging.error(f"Git credential retrieval failed: {e}. Use credential.helper to save credentials")
        exit(1)


def get_prs_by_issue_id(owner: str, repo_name: str, issue_id: int):
    url = f'{chp_api_url}/repos/{owner}/{repo_name}/issues/{issue_id}/pull_requests'
    headers = {
        'Authorization': f'Bearer {get_git_password()}',
        'Accept': 'application/json'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            prs_of_issue = response.json()
            if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                log_file_path = os.path.join(get_config_dir(), __config_root_dir__, __prog_log_file_name__)
                with open(log_file_path, "a+", encoding="utf-8") as f:
                    f.write(f"issue #{issue_id} 关联的 PRs:\n")
                    json.dump(prs_of_issue, f, indent=4, ensure_ascii=False)
            return prs_of_issue
        else:
            logging.error(f"Failed to fetch PRs list for issue #{issue_id}: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network request error: {e}")
        return None


def get_pr_commits(owner: str, repo_name: str, pr_id: int):
    url = f"{chp_api_url}/repos/{owner}/{repo_name}/pulls/{pr_id}/commits"
    headers = {
        "Authorization": f"Bearer {get_git_password()}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            commits_of_pr = response.json()
            if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                log_file_path = os.path.join(get_config_dir(), __config_root_dir__, __prog_log_file_name__)
                with open(log_file_path, "a+", encoding="utf-8") as f:
                    f.write(f"All commits related to PR #{pr_id}:\n")
                    json.dump(commits_of_pr, f, indent=4, ensure_ascii=False)
            return commits_of_pr
        else:
            logging.error(f"Failed to get commits list for PR #{pr_id}: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Network request error: {e}")
        return []


def cherry_pick_commit(repo_path: str, commit_sha: str) -> bool:
    try:
        result = run(["git", "cherry-pick", commit_sha], workspace=repo_path, capture_output=True)
        if result.returncode == 0:
            logging.info(f"Successfully cherry-picked #{commit_sha[:8]}")
            return True
        else:
            logging.error(f"Failed to cherry-pick #{commit_sha[:8]}: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Failed to cherry-pick #{commit_sha[:8]}: {e}")
        return False


def fetch_remote_branch(repo_path, remote_url, remote_branch):
    try:
        fetch_cmd = ["git", "fetch", remote_url, remote_branch]
        if run(["git", "rev-parse", "--is-shallow-repository"], workspace=repo_path, capture_output=True).stdout.strip() == "True":
            fetch_cmd.append("--unshallow")
        result = run(fetch_cmd, workspace=repo_path, capture_output=True)
        if result.returncode == 0:
            logging.info(f"Successfully fetched {remote_url}:{remote_branch}")
            return True
        else:
            logging.error(f"Failed to fetch {remote_url}:{remote_branch} : {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Failed to fetch {remote_url}:{remote_branch} : {e}")
        return False


def cherry_pick_impl(args):
    user_config = load_user_config()
    project = get_user_config(user_config, f"projects:name={args.project_name}", [])
    if project:
        for pr in get_prs_by_issue_id(get_user_config(project, "owner"), args.project_name, args.issue_id) or []:
            repo_name = pr["base"]["repo"]["name"]
            if pr["state"] != "open":
                logging.warning(f"PR #{pr['number']} of {repo_name} is not open, skipping.")
                continue

            local_path = get_user_config(user_config, f"projects:name={repo_name}.local_path", ".")
            repo_path = os.path.join(get_config_dir(), local_path, repo_name)
            if not os.path.isdir(repo_path):
                logging.error(f"the repo {repo_name} hasn't been pulled locally yet.")
                continue

            remote_url = f'{chp_url}/{pr["head"]["repo"]["full_name"]}'
            remote_branch = pr["head"]["ref"]
            if not fetch_remote_branch(repo_path, remote_url, remote_branch):
                continue

            commits_of_pr = get_pr_commits("Cangjie", repo_name, pr["number"])
            success = True
            for commit in commits_of_pr:
                success = success and cherry_pick_commit(repo_path, commit["sha"])
    else:
        config_root_dir = os.path.join(get_config_dir(), __config_root_dir__)
        logging.error(f"the project `{args.project_name}` is not listed in {os.path.join(config_root_dir, __config_file_name__)}:projects")