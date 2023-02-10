from sys import path
from os import makedirs
import networkx as nx
from tqdm import tqdm

path.append("..")

from scripts.helpers import all_graphs, to_json
from pipeline.picklereader import PickleReader
from pipeline.NetworkVisCreator import NetworkVisCreator

pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])
cypher_command = []


path_list_len = len(list(all_graphs()))
for path in tqdm(all_graphs(), total=path_list_len):
    path_str = str(path)
    target_repo = to_json(path_str)["repo_url"].replace("https://github.com/", "")

    nodes, _, comment_list, timeline_list, _ = pr.read_repo_local_file(None, target_repo)

    local_graph = nx.Graph()
    for index, node in enumerate(nodes):
        node_status = node.state
        if node.pull_request is not None:
            if node.pull_request.raw_data["merged_at"] is not None:
                node_status = "merged"
        local_graph.add_node(
            f"{target_repo}#{node.number}",
            type="pull_request" if node.pull_request is not None else "issue",
            status=node_status,
            repository=target_repo,
            creation_date=int(node.created_at.timestamp()),
            closed_at=int(node.closed_at.timestamp()) if node.closed_at is not None else 0,
            updated_at=int(node.updated_at.timestamp()),
            labels="pull_request" if node.pull_request is not None else "issue",
            number=node.number,
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
            local_graph.add_edge(
                f"{target_repo}#{mention.source.issue.number}",
                f"{target_repo}#{node.number}",
                link_type=nwvc.find_automatic_links(node.number, mention.source.issue.body, mentioning_issue_comments),
                labels=nwvc.find_automatic_links(node.number, mention.source.issue.body, mentioning_issue_comments),
            )
    try:
        makedirs(f"graphml_dump/")
    except:
        pass
    nx.write_graphml(local_graph, f"graphml_dump/{target_repo.replace('/','-')}.graphml", named_key_ids=True)
    cypher_command += [
        f"CALL apoc.import.graphml('file://graphml_dump/{target_repo.replace('/','-')}.graphml', {{ readLabels:true }}) ; \n"
    ]

with open("graphml_dump/cypher_command.txt", "w") as x:
    x.writelines(cypher_command)
