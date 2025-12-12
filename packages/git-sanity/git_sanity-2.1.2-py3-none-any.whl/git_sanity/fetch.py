import logging
import os
from git_sanity.utils import run
from git_sanity.utils import get_config_dir
from git_sanity.utils import load_user_config
from git_sanity.utils import get_user_config
from git_sanity.utils import get_projects_by_group

def fetch_impl(args):
    user_config = load_user_config()
    for project in get_projects_by_group(user_config, args.group):
        project_name = get_user_config(project, "name")
        logging.info(f"Fetching source for {project_name}...")
        logging.debug(f"Fetching project={project}")

        repo_path = os.path.join(get_config_dir(), get_user_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error(f"the remote {project_name} project branch hasn't been pulled locally yet.")
            continue

        fetch_cmd = ["git", "fetch", args.remote]
        fetch_cmd.extend(get_user_config(project, "forward_to_git.fetch", []))
        if run(fetch_cmd, workspace=repo_path).returncode:
            logging.error(f"Failed to fetch {project_name}")
            continue
