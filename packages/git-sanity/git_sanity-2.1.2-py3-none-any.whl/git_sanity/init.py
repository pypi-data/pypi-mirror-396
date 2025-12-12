import json
import logging
import os
from git_sanity import __prog_name__
from git_sanity import __config_root_dir__
from git_sanity import __config_file_name__
from git_sanity.utils import run

default_config = {
    "this_is_a_comment_example": "<!--JSON-style comment markers (similar to HTML comments)-->",
    "working_branch": f"<!--change via the `{__prog_name__} switch` command, default=None-->",
    "projects": [
        {
            "code_hosting_platform": "<!--code hosting platform, eg:gitcode-->",
            "name": "<!--project's name-->",
            "owner": "<!--organization or individual to which the project belongs.-->",
            "path": "project's path on the code hosting platform",
            "branch": "<!--branch's name-->",
            "url": "<!--project's repo url>",
            "local_path": "<!--local path to clone repo, default=.>",
            "additional_remotes": [
                {"<!--remote's name-->": "<!--remote's url-->"}
            ],
            "forward_to_git": {
                "clone": ["<!--command args of git clone, eg:--depth=1-->"]
            }
        }
    ],
    "groups": [
        {
            "group_name": "all",
            "projects": [
                "<!--project_name, default=[]-->"
            ]
        }
    ],
    "commands" : [
        {"<!--command_name-->": ["<!--command and command args-->"]},
        {"<!--test-->": ["<!-- ls -->", "<!-- -l -->"]}
    ]
}

def init_impl(args):
    """
    Initialize a git-sanity repository with optional URL or local configuration
    
    Parameters:
    - args: Command-line arguments object containing:
        * directory: Target directory for repository
        * URL: Optional remote repository URL for cloning
        
    Returns:
    - None (exits with status code 0 on success, 1 on failure)
    """
    if not os.path.isdir(args.directory):
        logging.error(f"the value of -d/--directory is not a valid path: {args.directory}")
        exit(1)

    repo_path = os.path.join(args.directory, __config_root_dir__)
    if os.path.isdir(repo_path):
        logging.error(f"reinitialized existing {__prog_name__} repository in {args.directory}")
        exit(0)

    clone_cmd = ["git", "clone", args.url, __config_root_dir__]
    if args.url and args.branch:
        clone_cmd.extend(["-b", args.branch])
    elif args.branch:
        logging.error("when -b/--branch is specified, -u/--url must exist")
        exit(1)
    if args.url and run(clone_cmd, workspace=args.directory).returncode == 0:
        exit(0)
    elif args.url:
        logging.error(f"failed to initialize {__prog_name__} with {args.url}")
        exit(1)
    else:
        os.mkdir(repo_path)
        config_file_path = os.path.join(repo_path, __config_file_name__)
        with open(config_file_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        logging.warning(f"default config file created at {config_file_path}. Customize as needed.")
        exit(0)
