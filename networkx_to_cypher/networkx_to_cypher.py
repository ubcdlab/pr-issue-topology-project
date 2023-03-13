from sys import path

import networkx as nx

path.append("..")

from scripts.helpers import all_graphs, to_json
from pipeline.picklereader import PickleReader
from pipeline.NetworkVisCreator import NetworkVisCreator
from json import loads

graph_list = all_graphs()
graph_path = str(next(graph_list))
graph_json = to_json(graph_path)
target_repo = graph_json["repo_url"].replace("https://github.com/", "")

given_input = """{
            "id": 3992,
            "type": "pull_request",
            "status": "closed",
            "label": [
                "dependencies",
                "github_actions"
            ],
            "creation_date": 1657540205.0,
            "closed_at": 1657626697.0,
            "updated_at": 1657626702.0,
            "comments": 1,
            "node_creator": "https://github.com/apps/dependabot",
            "event_list": [
                {
                    "event": "committed",
                    "created_at": 1657515005.0,
                    "author": "49699333+dependabot[bot]@users.noreply.github.com",
                    "email": "49699333+dependabot[bot]@users.noreply.github.com"
                },
                {
                    "event": "labeled",
                    "created_at": 1657540207.0,
                    "author": "https://github.com/apps/dependabot",
                    "email": ""
                },
                {
                    "event": "labeled",
                    "created_at": 1657540207.0,
                    "author": "https://github.com/apps/dependabot",
                    "email": ""
                },
                {
                    "event": "commented",
                    "created_at": 1657626696.0,
                    "author": "https://github.com/apps/dependabot",
                    "email": ""
                },
                {
                    "event": "closed",
                    "created_at": 1657626697.0,
                    "author": "None",
                    "email": ""
                },
                {
                    "event": "head_ref_deleted",
                    "created_at": 1657626702.0,
                    "author": "https://github.com/apps/dependabot",
                    "email": ""
                }
            ],
            "connected_component": [
                3992,
                3986,
                3996
            ],
            "connected_component_size": [
                3
            ],
            "component_id": 17,
            "node_degree": 1
        }
"""

pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])

nodes, _, comment_list, timeline_list, _ = pr.read_repo_local_file(None, "Activiti/Activiti")
selected = loads(given_input)
graph = nx.Graph()
to_add = []
edges_to_add = []
for index, node in enumerate(list(filter(lambda x: x.number in selected["connected_component"], nodes))):
    node_status = node.state
    if node.pull_request is not None:
        if node.pull_request.raw_data["merged_at"] is not None:
            node_status = "merged"
    to_add.append(
        (
            f"{target_repo}#{node.number}",
            {
                "type": "pull_request" if node.pull_request is not None else "issue",
                "status": node_status,
                "repository": target_repo,
                "number": node.number,
                "creation_date": node.created_at.timestamp(),
                "closed_at": node.closed_at.timestamp() if node.closed_at is not None else 0,
                "updated_at": node.updated_at.timestamp(),
            },
        )
    )
    node_timeline = timeline_list[-index - 1]
    node_timeline = list(
        filter(
            lambda x: x.event == "cross-referenced" and x.source.issue.repository.full_name == target_repo,
            node_timeline,
        )
    )
    for mention in node_timeline:
        mentioning_issue_comments = nwvc.find_comment(mention.source.issue.url, comment_list)
        edges_to_add.append(
            (
                f"{target_repo}#{mention.source.issue.number}",
                f"{target_repo}#{node.number}",
                {
                    "link_type": nwvc.find_automatic_links(
                        node.number, mention.source.issue.body, mentioning_issue_comments
                    )
                },
            )
        )

graph.add_nodes_from(to_add)
graph.add_edges_from(edges_to_add)

query = "match "
for node in graph.nodes(data=True):
    query += f"({'i' if node[1]['type'] =='issue' else 'pr'}_{node[1]['number']}:{node[1]['type']}), "
for edge in graph.edges(data=True):
    query += f"({'i' if nx.get_node_attributes(edge[0],'type')[1]=='issue' else 'pr'}_{edge[0]})--({'i' if nx.get_node_attributes(edge[1],'type')[1]=='issue' else 'pr'}_{edge[1]}), "
query += "\nreturn "
for node in graph.nodes(data=True):
    query += f"{'i' if node[1]['type'] =='issue' else 'pr'}_{node[1]['number']}, "

print(query)
