from github.File import File
from langgraph.constants import Send
import logging
import operator
from typing import Annotated, TypedDict, List
from github.Commit import Commit

from service.github_service import GithubService
from workflow.comment_node import comment_reviewer
from models.comment_model import CommentModel

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class ReviewState(TypedDict):
    file: File
    github_service: GithubService

class OverallState(TypedDict):
    github_service: GithubService
    pull_number: int
    commit: Commit
    files: List[File]
    comments: Annotated[List[CommentModel], operator.add]

def list_files(state: OverallState):
    """
    This node retrieves all files that are part of the PR
    """
    gh_service: GithubService = state["github_service"]
    pull_number = state["pull_number"]
    
    files = gh_service.get_pull_request_files(pull_number)
    commit = gh_service.get_last_commit_for_pr(pull_number)

    return {"files": files, "commit": commit}

def generate_review_comments(state: ReviewState):
    """
    This node generates review comments for a particular file patch
    """
    gh_service: GithubService = state["github_service"]
    file: File = state["file"]
    file_contents = gh_service.get_file_contents(file.sha)

    # Generate review comments
    numbered_file_contents = ""
    for line_number, line in enumerate(file_contents.split('\n'), start=1):
        numbered_file_contents += f"{line_number}: {line}\n"
    review_comments = comment_reviewer.invoke({"file_contents": numbered_file_contents, "file_patch": file.patch})
    for comment in review_comments:
        comment.update({"file": file})

    return {"comments": review_comments}


def update_review_comments(state: OverallState):
    """
    This node combines all review comments and updates them to the PR
    """
    gh_service: GithubService = state["github_service"]
    review_comments: List[CommentModel] = state["comments"]
    commit: Commit = state["commit"]
    pull_number = state["pull_number"]

    # Update review comments
    for comment in review_comments:
        gh_service.add_pull_request_comment(pull_number=pull_number, comment=comment, commit=commit)
    
    return {"comments": review_comments}

def continue_to_review_comments(state):
    """
    We will return a list of `Send` objects
    Each `Send` object consists of the name of a node in the graph
    as well as the state to send to that node
    """
    return [Send("generate_review_comments", {"file": file, "github_service": state["github_service"]}) for file in state["files"]]