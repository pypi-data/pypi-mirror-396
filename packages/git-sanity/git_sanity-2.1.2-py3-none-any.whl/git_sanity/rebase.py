import logging
import os
from git_sanity.utils import run
from git_sanity.utils import get_config_dir
from git_sanity.utils import load_user_config
from git_sanity.utils import get_user_config
from git_sanity.utils import get_projects_by_group

def rebase_impl(args):
    user_config = load_user_config()
    for project in get_projects_by_group(user_config, args.group):
        project_name = get_user_config(project, "name")
        logging.info(f"Rebaseing source for {project_name}...")
        logging.debug(f"Rebaseing project={project}")

        repo_path = os.path.join(get_config_dir(), get_user_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error(f"the remote {project_name} project branch hasn't been pulled locally yet.")
            continue

        if args.branch:
            branch_to_rebase = args.branch
        else:
            branch_to_rebase = get_user_config(project, "branch")
        rebase_cmd = ["git", "rebase", f"{args.remote}/{branch_to_rebase}"]
        rebase_cmd.extend(get_user_config(project, "forward_to_git.rebase", []))
        if run(rebase_cmd, workspace=repo_path).returncode:
            logging.error(f"Failed to rebase {project_name}")
            continue
