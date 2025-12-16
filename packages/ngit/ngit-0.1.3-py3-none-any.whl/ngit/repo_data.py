# from pydantic import BaseModel
from git import Repo, InvalidGitRepositoryError
from console import console

class RepoData():
    repo: Repo | None
    current_branch = None
    unstaged = None
    untracked = None
    deleted_files = None
    def __init__(self):
        try:
            repo = Repo(".", search_parent_directories=True)
            current_branch = repo.active_branch
            unstaged = repo.index.diff(None)
            untracked = repo.untracked_files
            deleted_files = [
                d.a_path for d in repo.index.diff(None) 
                if d.change_type == "D"
            ]
        except InvalidGitRepositoryError:
            console.print("[bold red]Error: Not inside a git repository.")
