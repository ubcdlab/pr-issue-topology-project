from collections import defaultdict
from statistics import median, pstdev, fmean
from sys import path
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from prettytable import PrettyTable
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from click import command, option

path.append("..")

from scripts.helpers import all_graphs, num_graphs, to_json
from pipeline.picklereader import PickleReader
from pipeline.NetworkVisCreator import NetworkVisCreator

pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])


def parallelize_graph_processing(path: Path):
    path_str = str(path)
    target_repo = to_json(path_str)["repo_url"].replace("https://github.com/", "")

    nodes, _, comment_list, timeline_list, _ = pr.read_repo_local_file(None, target_repo)

    local_graph = nx.Graph(repository=target_repo)
    to_add = []
    edges_to_add = []
    for index, node in enumerate(nodes):
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

    local_graph.add_nodes_from(to_add)
    local_graph.add_edges_from(edges_to_add)
    return local_graph


@command()
@option("--print-repos", "print_repos", is_flag=True, default=False)
@option("--isolated", "isolated", is_flag=True, default=False)
@option("--diad", "diad", is_flag=True, default=False)
@option("--iandd", "iandd", is_flag=True, default=False)
def main(print_repos: bool, isolated: bool, diad: bool, iandd: bool):
    total_components = 0
    total_isolates = 0
    total_diad = 0
    repo_to_components = defaultdict(float)

    with Pool(cpu_count() // 2) as p:
        with tqdm(total=num_graphs(), leave=False) as pbar:
            for res in p.imap_unordered(parallelize_graph_processing, all_graphs()):
                if isolated:
                    total_isolates += len(list(nx.isolates(res)))
                    repo_to_components[res.graph["repository"]] = len(
                        list(nx.isolates(res))
                    ) / nx.number_connected_components(res)
                elif diad:
                    diads = len(list(filter(lambda x: len(x) == 2, nx.connected_components(res))))
                    total_diad += diads
                    repo_to_components[res.graph["repository"]] = diads / nx.number_connected_components(res)
                elif iandd:
                    diads = len(list(filter(lambda x: len(x) == 2, nx.connected_components(res))))
                    total_components += diads + len(list(nx.isolates(res)))
                    repo_to_components[res.graph["repository"]] = (
                        diads + len(list(nx.isolates(res)))
                    ) / nx.number_connected_components(res)
                else:
                    total_components += nx.number_connected_components(res)
                    repo_to_components[res.graph["repository"]] = nx.number_connected_components(res)
                pbar.update()

    if print_repos:
        print("Repo to components map:")
        table = PrettyTable()
        table.field_names = ["Repository", "# Components"]
        for row in list(sorted(repo_to_components.items(), key=lambda x: x[1], reverse=True)):
            table.add_row(row)
        print(table)

    table = PrettyTable()
    table.field_names = [
        "Total Component Count"
        if not isolated
        else "Total Isolated Node Count"
        if not diad
        else "Total Diad Node Count"
        if not iandd
        else "Total Isolated + Diad Node Count",
        "Min",
        "Max",
        "Mean",
        "Median",
        "STDEV",
    ]
    table.add_row(
        [
            total_components,
            min(repo_to_components.values()),
            max(repo_to_components.values()),
            fmean(repo_to_components.values()),
            median(repo_to_components.values()),
            pstdev(repo_to_components.values()),
        ]
        if not isolated and not diad and not iandd
        else [
            total_isolates if isolated else total_diad if not iandd else total_components,
            f"{min(repo_to_components.values()):.2%}",
            f"{max(repo_to_components.values()):.2%}",
            f"{fmean(repo_to_components.values()):.2%}",
            f"{median(repo_to_components.values()):.2%}",
            f"{pstdev(repo_to_components.values()):.2%}",
        ]
    )
    print(table)


if __name__ == "__main__":
    main()
