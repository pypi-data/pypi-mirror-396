import typer
from repo_data import RepoData
from rich import print as rprint
from console import console
from git import Repo


# repo_data = RepoData()
repo = Repo(".", search_parent_directories=True)
app = typer.Typer()
# repo = repo_data.repo
current_branch = repo.active_branch
unstaged = repo.index.diff(None)
untracked = repo.untracked_files
deleted_files = [
    d.a_path for d in repo.index.diff(None) 
    if d.change_type == "D"
]




@app.command()
def ngit():
    rprint(f'''
Current branch: {current_branch}

Your branch is up to date with 'origin/[branch]'

Changes not stashed for commit:

''')
    for diff in unstaged:
        rprint(diff.a_path, diff.change_type)
    rprint(f'''
Added files:

''')
        
    for f in untracked:
        rprint(f)



@app.command()
def status():
    console.print(f"Current branch: [bold purple]{current_branch}[/bold purple]")
    console.rule("[bold red] Changed & Untracked Files", style="rule.line", align="center")
    with console.status("Pushing...."):
        pass

@app.command()
def checkout(branch: str, create: bool = typer.Option(False, "-b", "--branch")):
    if create:
        try:
            repo.create_head(branch).checkout()
        except:
            console.print_exception()
    else:
        try:
            repo.git.checkout(branch)
        except:
            console.print("[red][bold]Error:[/bold] Branch does not exist")
            console.print("[green][bold]Do you want to create branch and checkout")
            ask_create = typer.confirm("")
            if ask_create:
                repo.create_head(branch).checkout()

    

if __name__ == "__main__":
    app()