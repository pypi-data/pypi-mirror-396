import logging
import os
from git_sanity.utils import run
from git_sanity.utils import get_config_dir
from git_sanity.utils import load_user_config
from git_sanity.utils import get_user_config
from git_sanity.utils import get_projects_by_group

def branch_impl(args):
    """
    Implementation for managing Git branches across multiple projects.
    
    Args:
        args: Command-line arguments containing:
            - group (str): Group name to filter projects
            - delete (str): Branch name to delete (non-force)
            - force_delete (str): Branch name to force delete
    
    Returns:
        None
    """
    user_config = load_user_config()
    for project in get_projects_by_group(user_config, args.group):
        project_name = get_user_config(project, "name")
        logging.info(f"Processing branches for {project_name}...")
        logging.debug(f"Processing project={project}")

        repo_path = os.path.join(get_config_dir(), get_user_config(project, "local_path", "."), project_name)
        if not os.path.isdir(repo_path):
            logging.error(f"the remote {project_name} project branch hasn't been pulled locally yet.")
            exit(1)

        branch_cmd = ["git", "branch"]
        if args.delete is not None:
            branch_cmd.extend(["-d", args.delete])
        elif args.force_delete is not None:
            branch_cmd.extend(["-D", args.force_delete])
        run(branch_cmd, workspace=repo_path)
