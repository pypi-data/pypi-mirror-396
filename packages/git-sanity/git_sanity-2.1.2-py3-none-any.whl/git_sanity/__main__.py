import argparse
import logging
from git_sanity import __prog_name__
from git_sanity import __version__
from git_sanity.init import init_impl
from git_sanity.clone import clone_impl
from git_sanity.fetch import fetch_impl
from git_sanity.rebase import rebase_impl
from git_sanity.sync import sync_impl
from git_sanity.switch import switch_impl
from git_sanity.branch import branch_impl
from git_sanity.cherry_pick import cherry_pick_impl
from git_sanity.push import push_impl
from git_sanity.command import command_impl

def main():
    prog = argparse.ArgumentParser(prog=__prog_name__, formatter_class=argparse.RawTextHelpFormatter, description=__doc__)
    prog.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    prog.add_argument("-d", "--debug", action='store_true', help=f"run {__prog_name__} in debug mode")

    subparsers = prog.add_subparsers(
        title="sub-commands", help="additional help with sub-command -h"
    )
    prog_init = subparsers.add_parser("init", description="Initialize the projects", help="initialize the projects")
    prog_init.add_argument("-u", "--url", dest="url", help=f"the {__prog_name__} configuration repository")
    prog_init.add_argument("-b", "--branch", dest="branch", help="branch to init")
    prog_init.add_argument("-d", "--directory", dest="directory", default=".", help=f"the path to init {__prog_name__} configuration repository")
    prog_init.set_defaults(func=init_impl)

    prog_clone = subparsers.add_parser("clone", description="Clone repo(s)", help="clone repo(s)")
    prog_clone.add_argument("-g", "--group", dest="group", default="all", help="group to clone, default all")
    prog_clone.set_defaults(func=clone_impl)

    prog_fetch = subparsers.add_parser("fetch", description="Fetch project(s)", help="fetch project(s)")
    prog_fetch.add_argument("-g", "--group", dest="group", default="all", help="projects to fetch, default all")
    prog_fetch.add_argument("-r", "--remote", dest="remote", default="origin", help="remote to fetch from, default origin")
    prog_fetch.set_defaults(func=fetch_impl)

    prog_rebase = subparsers.add_parser("rebase", description="Rebase project(s)", help="rebase project(s)")
    prog_rebase.add_argument("-g", "--group", dest="group", default="all", help="projects to rebase, default all")
    prog_rebase.add_argument("-r", "--remote", dest="remote", default="origin", help="remote to rebase from, default origin")
    prog_rebase.add_argument("-b", "--branch", dest="branch", help="branch to rebase onto, default the branch configured for the project")
    prog_rebase.set_defaults(func=rebase_impl)

    prog_sync = subparsers.add_parser("sync", description="Sync source project(s) ", help="sync source project(s)")
    prog_sync.add_argument("-g", "--group", dest="group", default="all", help="projects to sync, default all")
    prog_sync.set_defaults(func=sync_impl)

    prog_switch = subparsers.add_parser("switch", description="Switch branches", help="switch branches")
    prog_switch.add_argument("-b", "--branch", required=True, dest="branch_name", help="branch to switch to, create the branch from origin/HEAD if it doesn't exist")
    prog_switch.add_argument("-g", "--group", dest="group", default="all", help="group to switch branches, default all")
    prog_switch.set_defaults(func=switch_impl)

    prog_branch = subparsers.add_parser("branch", description="List or delete branches", help="list or delete branches")
    prog_branch.add_argument("list", nargs='?', default="list", help="list branch names")
    prog_branch.add_argument("-g", "--group", dest="group", default="all", help="group to operate, default all")
    prog_branch_meg = prog_branch.add_mutually_exclusive_group()
    prog_branch_meg.add_argument("-d", "--delete", dest="delete", help="delete fully merged branch")
    prog_branch_meg.add_argument("-D", "--DELETE", dest="force_delete", help="delete branch (even if not merged)")
    prog_branch.set_defaults(func=branch_impl)

    prog_cherry_pick = subparsers.add_parser("cherry-pick", description="Apply the changes introduced by some existing PRs", help="apply the changes introduced by some existing PRs")
    prog_cherry_pick.add_argument("-i", "--issue", required=True, dest="issue_id", help="issue ID")
    prog_cherry_pick.add_argument("-p", "--project", required=True, dest="project_name", help="the project to which the issue belongs")
    prog_cherry_pick.set_defaults(func=cherry_pick_impl)

    prog_push = subparsers.add_parser("push", description="Update remote refs along with associated objects", help="update remote refs along with associated objects")
    prog_push.add_argument("remote_name", help="the target remote to push to")
    prog_push.add_argument("-g", "--group", dest="group", default="all", help="group to push, default all")
    prog_push.add_argument("-f", "--force", dest="force", action='store_true', help="force updates")
    prog_push.set_defaults(func=push_impl)

    prog_command = subparsers.add_parser("command", description="Execute user-defined commands", help="execute user-defined commands")
    prog_command_meg = prog_command.add_mutually_exclusive_group()
    prog_command_meg.add_argument("-c", "--command", dest="command_name", help="execute 'command_name'")
    prog_command_meg.add_argument("-l", "--list", dest="list", action='store_true', help="list all user-defined commands")
    prog_command.set_defaults(func=command_impl)

    args = prog.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.debug(f"command args={args}")
    if "func" in args:
        args.func(args)
    else:
        prog.print_help()

if __name__ == "__main__":
    main()