import logging

from config.config import config
from service.github_service import GithubService
import json

from workflow.review_graph import review_graph

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    logging.info(f"Starting event with request: {event}")

    try:

        # Get PR url from event
        github_event = event.get("headers", {}).get("X-GitHub-Event", "")

        logging.info(f"Github Event: {github_event}")

        if github_event == "pull_request":
            body = event["body"]
            if isinstance(body, str):
                body = json.loads(body)
            logging.info(f"body: {body}")
            
            query_params = event["queryStringParameters"]
            if isinstance(query_params, str):
                query_params = json.loads(query_params)
            logging.info(f"query_params: {query_params}")

            action = body["action"]
            if action not in ["opened", "reopened"]:
                return
            
            pull_number = body["number"]
            project_id = query_params["project_id"]
            github_service = GithubService(project_id)

            logging.info(f"Starting review processs for pull number: {pull_number}, project: {project_id}")

            # Start comment workflow
            inputs = {
                "github_service": github_service,
                "pull_number": pull_number
            }

            for output in review_graph.stream(inputs):
                for key, value in output.items():
                    pass

            comments = value["comments"]
            logging.info(f"Generated comments: {comments}")
            return True
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return False