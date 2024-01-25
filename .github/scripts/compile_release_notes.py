import requests
from github import Github

# Add your repositories here
repositories = ["owner/repo1", "owner/repo2"]

def get_release_notes(repo):
    g = Github(requests.get(f"https://api.github.com/repos/{repo}").json()["full_name"])
    releases = g.get_repo(repo).get_releases()
    return [f"### {release.title}\n\n{release.body}\n" for release in releases]

def compile_release_notes():
    compiled_notes = []
    for repo in repositories:
        compiled_notes.extend(get_release_notes(repo))

    with open("compiled_release_notes.md", "w") as file:
        file.write("# Compiled Release Notes\n\n")
        file.write("\n\n".join(compiled_notes))

if __name__ == "__main__":
    compile_release_notes()
