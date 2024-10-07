from config.config import config
from models.project_model import ProjectPynamoDBModel
from models.comment_model import CommentModel

from github import Github
from github import Auth
from github.Commit import Commit
import base64
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class GithubService():

    GITHUB_API_URL = config.GITHUB_API

    def __init__(self, project_id):
        project_model = ProjectPynamoDBModel.query(project_id).next()
        self._access_token = config.GITHUB_API_TOKEN
        self.repo_name = project_model.configs["github"]["repoName"]
        self.project_url = f"{self.GITHUB_API_URL}/{self.repo_name}"
        
        auth = Auth.Token(self._access_token)
        self.github = Github(base_url=config.GITHUB_API, auth=auth)

    def get_pull_request_files(self, pull_number):
        files = self.github.get_repo(full_name_or_id=self.repo_name).get_pull(pull_number).get_files()
        return files
    
    def get_last_commit_for_pr(self, pull_number):
        commits = self.github.get_repo(full_name_or_id=self.repo_name).get_pull(pull_number).get_commits()
        last_commit = None
        for commit in commits:
            last_commit = commit
        return last_commit
    
    def add_pull_request_comment(self, pull_number, commit: Commit, comment: CommentModel):
        """
        Adds a pull request comment
        """
        try:
            if comment["subject_type"] == "line" and "line" in comment:
                self.github.get_repo(full_name_or_id=self.repo_name).get_pull(pull_number).create_review_comment(
                    body=comment["body"],
                    commit=commit,
                    line=comment["line"],
                    path=comment["file"].filename
                )
            else:
                self.github.get_repo(full_name_or_id=self.repo_name).get_pull(pull_number).create_review_comment(
                    body=comment["body"],
                    commit=commit,
                    subject_type="file",
                    path=comment["file"].filename
                )
            return True
        except Exception as e:
            logging.error(f"Could not create review comment for {comment}")
            return False

    def get_file_contents(self, file_sha):
        repo = self.github.get_repo(full_name_or_id=self.repo_name)
        file_content = repo.get_git_blob(file_sha).content
        decoded_content = base64.b64decode(file_content).decode('utf-8')  # Decoding from base64
        return decoded_content
    
if __name__ == "__main__":
    github_service = GithubService("101")
    files = github_service.get_pull_request_files(2)
    for file in files:
        print(file)
        print(file.filename)
        file_contents = github_service.get_file_contents(file.sha)

        numbered_file_contents = ""
        for line_number, line in enumerate(file_contents.split('\n'), start=1):
            numbered_file_contents += f"{line_number}: {line}\n"
        print(numbered_file_contents)