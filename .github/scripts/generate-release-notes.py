import os
from github import Github
import re


def increment_version(latest_tag_name):

    closed_pr = repo.get_pulls(state='closed')
    closed_pull_request = closed_pr[0]
    
    labels = closed_pull_request.get_labels()
    branch_name = [label.name for label in labels][0].strip()
    branch_name = [label.name for label in labels][0].strip()
    print("branch_name",branch_name)
    if branch_name=="feature":
        change_type = "major"
    elif branch_name=="bugfix" or branch_name == "bug_fix":
       change_type = "minor"
    elif branch_name=="hotfix" or branch_name=="hot_fix":
       change_type = "patch"
    else:
        change_type = 'misc'    
    version_numbers = latest_tag_name[1:].split('.')

    # Increment the version numbers based on the change type
    major_increment = 1 if change_type == 'major' else 0
    minor_increment = 1 if change_type == 'minor' else 0
    patch_increment = 1 if change_type == 'patch' else 0

    # Increment the version numbers accordingly
    major_number = int(version_numbers[0]) + major_increment
    minor_number = int(version_numbers[1]) + minor_increment
    patch_number = int(version_numbers[2]) + patch_increment

    # Construct the new tag name
    new_tag_name = f"v{major_number}.{minor_number}.{patch_number}"
    

    return new_tag_name

def fetch_closed_pull_requests(repo):
    # Fetch closed pull requests
    closed_pr = repo.get_pulls(state='closed')
    closed_pull_request = closed_pr[0]

    labels = closed_pull_request.get_labels()
    branch_name = [label.name for label in labels][0]


    # Organize pull requests under different headings
    feature_notes = []
    bug_fix_notes = []
    hot_fix_notes = []
    misc_notes = []

    pull_request_url = closed_pull_request.html_url

    commits = closed_pull_request.get_commits()
    
    if branch_name=="feature":
        feature_notes.append(f"@{closed_pull_request.user.login} {closed_pull_request.title}")

        # Append the link to the pull request to your feature_notes
        feature_notes.append(f"Pull Request: {pull_request_url}")

        # Add commit messages
        for commit in commits:
            feature_notes.append(f"Commit: {commit.sha[:7]} - {commit.commit.message}")

# Now feature_notes contains the pull request URL, pull request title, body, and commit messages

    elif branch_name=="bugfix" or branch_name=="bug_fix":
        bug_fix_notes.append(f"@{closed_pull_request.user.login} {closed_pull_request.title}")

        # Append the link to the pull request to your feature_notes
        bug_fix_notes.append(f"Pull Request: {pull_request_url}")

        # Add commit messages
        for commit in commits:
            bug_fix_notes.append(f"Commit: {commit.sha[:7]} - {commit.commit.message}")


    elif branch_name=="hotfix" or branch_name=="hot_fix":

        hot_fix_notes.append(f"@{closed_pull_request.user.login} {closed_pull_request.title}")

        # Append the link to the pull request to your feature_notes
        hot_fix_notes.append(f"Pull Request: {pull_request_url}")

        # Add commit messages
        for commit in commits:
            hot_fix_notes.append(f"Commit: {commit.sha[:7]} - {commit.commit.message}")

    else:
        misc_notes.append(f"@{closed_pull_request.user.login} {closed_pull_request.title}")

        # Append the link to the pull request to your feature_notes
        misc_notes.append(f"Pull Request: {pull_request_url}")

        # Add commit messages
        for commit in commits:
            misc_notes.append(f"Commit: {commit.sha[:7]} - {commit.commit.message}")

# Construct release notes
    release_notes = ""
    if feature_notes:
        release_notes += "### 🚀 Features\n"
        release_notes += "\n".join(feature_notes) + "\n\n"

    if bug_fix_notes:
        release_notes += "### 🐛 Bug Fixes\n"
        release_notes += "\n".join(bug_fix_notes) + "\n\n"

    if hot_fix_notes:
        release_notes += "### 🧰 Hot Fixes\n"
        release_notes += "\n".join(hot_fix_notes) + "\n\n"

    if misc_notes:
        release_notes += "### 🧺 Miscellaneous\n"
        release_notes += "\n".join(misc_notes) + "\n\n"
    return release_notes

def group_release_info(release_notes):
    # Split the release notes into sections based on section titles
    sections = re.split(r'(?:^|\n)#{2,3}\s+', release_notes.strip())

    # Initialize a dictionary to store sections
    grouped_info = {}
    
    # Process each section
    for section in sections:
        if section.strip():
            # Split each section into title and content
            lines = section.strip().split('\n')
            section_title = lines[0].strip()
           
            section_content = '\n'.join(lines[1:]).strip()
            
            # Add section content to the corresponding title in the dictionary
            if section_title in grouped_info:
                grouped_info[section_title].append(section_content)
            else:
                grouped_info[section_title] = [section_content]

    return grouped_info





def create_draft_release(repo, release_notes, version):
    # Get the latest release
    try:
        latest_release = repo.get_releases()[0]
    except:
        latest_release = ""

    # Get the body of the latest release
    if latest_release == "" :
        release_body = ""
    else:
        if latest_release.draft:
            release_body = latest_release.body
        else:
            release_body = ""

    # Merge the old body with the new release notes
    merged_message = release_body + '\n\n' + release_notes

    # Format the merged message using group_release_info()
    formatted_message = ""
    grouped_info = group_release_info(merged_message)
    # Format the merged message using group_release_info()
    formatted_message = ""
    for section, notes in grouped_info.items():
        formatted_message += f"## {section}\n"
        for note in notes:
            formatted_message += f"{note}\n"
        formatted_message += "\n"


    # Update the release with the formatted message and keep it as a draft
    if latest_release.draft :
        latest_release.update_release(
            name=version,
            message=formatted_message,
            draft=True
        )   
    else:
        repo.create_git_release(
        tag=new_version,
        name=version,
        message=formatted_message,
        draft=True)

    return formatted_message





if __name__ == "__main__":
    # Get GitHub token from environment variable
    github_token = os.environ.get('GITHUB_TOKEN')

    # Create a GitHub instance
    g = Github(github_token)
    # Get the repository
    repo = g.get_repo(os.environ.get('GITHUB_REPOSITORY'))


    # Fetch the latest tags and their versions
    tags = repo.get_tags()

    latest_draft_tag = os.environ.get('DRAFT_RELEASE_TAG_NUMBER')
    latest_tag = os.environ.get('LATEST_TAG')

    print()
    
    # Increment the version based on the type of change
    if latest_draft_tag is not None and latest_draft_tag != "":
        new_version = increment_version(latest_draft_tag)  # Example: Incrementing minor version
    elif latest_tag is not None and latest_tag != "" and latest_tag != "null":
        new_version = increment_version(latest_tag)
    else:
        new_version = "v0.0.0"

    print("new_version",new_version)

    # Fetch closed pull requests and generate release notes
    release_notes = fetch_closed_pull_requests(repo)

    print("release_notes", release_notes)

    # Create a new tag with the updated version
    release_notes_final = create_draft_release(repo, release_notes, new_version)

    print(f"Draft release {new_version} created successfully.")

  
