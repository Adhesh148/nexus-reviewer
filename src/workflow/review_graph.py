from langgraph.graph import END, StateGraph, START
from workflow.review_nodes import OverallState, list_files, generate_review_comments, update_review_comments, continue_to_review_comments
from service.github_service import GithubService

from pprint import pprint

# Construct the review graph
graph = StateGraph(OverallState)
graph.add_node("list_files", list_files)
graph.add_node("generate_review_comments", generate_review_comments)
graph.add_node("update_review_comments", update_review_comments)

graph.add_edge(START, "list_files")
graph.add_conditional_edges("list_files", continue_to_review_comments, ["generate_review_comments"])
graph.add_edge("generate_review_comments", "update_review_comments")
graph.add_edge("update_review_comments", END)

review_graph = graph.compile()

if __name__ == "__main__":
    github_service = GithubService("101")
    inputs = {"pull_number": 2, "github_service": github_service}

    for output in review_graph.stream(inputs):
        for key, value in output.items():
            # Node
            pprint(f"Node '{key}':")
            # Optional: print full state at each node
            # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
        pprint("\n---\n")

    comments = value["comments"]
    for item in comments:
        pprint(f"{item}")
