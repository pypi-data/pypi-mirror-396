import logging
import os
from git_sanity.utils import run
from git_sanity.utils import get_config_dir
from git_sanity.utils import load_user_config
from git_sanity.utils import get_user_config
from git_sanity.utils import get_projects_by_group
from git_sanity.utils import update_user_config

def get_all_branches(local_repo_path: str):
    local_branch_result = run(["git", "branch"], workspace=local_repo_path, capture_output=True)
    if local_branch_result.returncode:
        logging.error(f"Failed to get local branch: {local_branch_result.stderr}")
        return None, None
    local_branches = [
        branch.strip('* ').strip() for branch in local_branch_result.stdout.split('\n') if branch.strip()
    ]

    remote_branch_result = run(["git", "branch", "-r"], workspace=local_repo_path, capture_output=True)
    if remote_branch_result.returncode:
        logging.error(f"Failed to get local branch: {remote_branch_result.stderr}")
        return local_branches, None
    remote_branches = [
        branch.strip().replace('origin/', '') for branch in remote_branch_result.stdout.split('\n') if branch.strip() and '->' not in branch
    ]
    return local_branches, remote_branches


def switch_impl(args):
    """
    Implements the branch switching functionality for multiple projects based on group configuration.

    Parameters:
    - args: Command-line arguments containing:
        - group: Name of the group to switch branches for
        - new_branch_name: Optional name for the new branch to create (if provided)
        - branch_name: Optional name of the existing branch to switch to (if provided)

    Returns:
    - None (exits with error code 1 on failure)
    """
    user_config = load_user_config()
    projects_of_group = get_projects_by_group(user_config, args.group)
    if not projects_of_group:
        return

    for project in projects_of_group:
        project_name = get_user_config(project, "name")
        logging.info(f"Switching branch for {project_name}...")
        logging.debug(f"Switching project={project}")

        repo_path = os.path.join(get_config_dir(), get_user_config(project, "local_path", "."), project_name)
        repo_path = os.path.join(get_config_dir(), get_user_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error(f"the remote {project_name} project branch hasn't been pulled locally yet.")
            continue

        local_branch_result, remote_branch_result = get_all_branches(repo_path)
        logging.debug(f"local branchs of {project_name}: {local_branch_result}")
        logging.debug(f"remote branchs of {project_name}: {remote_branch_result}")
        if args.branch_name in local_branch_result:
            switch_cmd = ["git", "switch", f"{args.branch_name}"]
        else:
            switch_cmd = ["git", "switch", "-c", args.branch_name, f"origin/{get_user_config(project, 'branch')}"]
        result = run(switch_cmd, workspace=repo_path, capture_output=True)
        if result.returncode:
            logging.error(f"Failed to switch {project_name}'s branch to {args.new_branch_name}: {result.stderr}")
            continue
    update_user_config("working_branch", args.branch_name)
