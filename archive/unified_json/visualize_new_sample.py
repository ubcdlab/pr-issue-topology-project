from csv import reader
from math import sqrt
import networkx as nx
from tqdm import tqdm
from click import command, option
from sys import path
from multiprocessing import Pool, cpu_count
from typing import List

path.append("..")

from pipeline.picklereader import PickleReader
from pipeline.NetworkVisCreator import NetworkVisCreator
from scripts.helpers import generate_image


pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])


def parallelize_sample_generation(line: List[str]):
    target_repo = line[1]
    node_list = list(map(lambda l: int(l), line[-1].split("|")))
    nodes, _, comment_list, timeline_list, _ = pr.read_repo_local_file(None, target_repo)
    local_graph = nx.DiGraph()
    to_add = []
    edges_to_add = []
    for index, node in enumerate(nodes):
        if node.number not in node_list:
            continue
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
            if mention.source.issue.number not in node_list:
                continue
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
    local_graph.add_nodes_from(to_add)
    local_graph.add_edges_from(edges_to_add)
    generate_image(
        local_graph,
        int(line[0]),
        f"Component #{int(line[0])} from {target_repo}",
        10 + (sqrt(local_graph.size() - 20) if local_graph.size() > 20 else 0),
        "unified_json/second_sample_images/",
    )


@command()
@option("--file", "file")
def main(file: str):
    with open(file, "r") as x:
        lines = x.readlines()
        lines = lines[1:]
        total_lines = len(lines)

    with Pool(cpu_count() // 2) as p:
        with tqdm(total=total_lines, leave=False) as pbar:
            for _ in p.imap_unordered(parallelize_sample_generation, reader(lines)):
                pbar.update()


if __name__ == "__main__":
    main()
