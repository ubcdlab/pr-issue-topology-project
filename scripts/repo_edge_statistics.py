from collections import defaultdict
from statistics import median, pstdev, fmean, stdev
from sys import path
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from prettytable import PrettyTable
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from click import command, option
from dataclasses import dataclass

path.append("..")

from scripts.helpers import all_graphs, num_graphs, to_json
from pipeline.picklereader import PickleReader
from pipeline.NetworkVisCreator import NetworkVisCreator

pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])


@dataclass(repr=True)
class RepoLinkStatistics:
    fixes: int
    duplicate: int
    count: int


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
                            node.number, mention.source.issue.body, mentioning_issue_comments, repo=target_repo
                        )
                    },
                )
            )

    local_graph.add_nodes_from(to_add)
    local_graph.add_edges_from(edges_to_add)
    return local_graph


@command()
@option("--print-repos", "print_repos", is_flag=True, default=False)
@option("--print-absolute", "print_abs", is_flag=True, default=False)
def main(print_repos: bool, print_abs: bool):
    total = RepoLinkStatistics(0, 0, 0)
    repo_to_rls = {}

    with Pool(cpu_count() // 2) as p:
        with tqdm(total=num_graphs(), leave=False) as pbar:
            for res in p.imap_unordered(parallelize_graph_processing, all_graphs()):
                repo_to_rls[res.graph["repository"]] = RepoLinkStatistics(0, 0, 0)
                for edge in res.edges(data=True):
                    total.count += 1
                    repo_to_rls[res.graph["repository"]].count += 1
                    if edge[2]["link_type"] == "fixes":
                        total.fixes += 1
                        repo_to_rls[res.graph["repository"]].fixes += 1
                    elif edge[2]["link_type"] == "duplicate":
                        total.duplicate += 1
                        repo_to_rls[res.graph["repository"]].duplicate += 1
                pbar.update()

    if print_repos:
        print("Repo to components map:")
        table = PrettyTable()
        table.field_names = ["Repository", "# Components"]
        for row in list(sorted(repo_to_rls.items(), key=lambda x: x[1].count, reverse=True)):
            table.add_row(row)
        print(table)

    table = PrettyTable()
    table.field_names = ["Type", "% of Total", "Min", "Max", "Mean", "Median", "STDEV"]
    print("Total count:", total.count)
    table.add_row(
        [
            "Fixes",
            f"{total.fixes / total.count:.2%}",
            f"{min(map(lambda x: x.fixes / x.count, repo_to_rls.values())):.2%}",
            f"{max(map(lambda x: x.fixes / x.count, repo_to_rls.values())):.2%}",
            f"{fmean(map(lambda x: x.fixes / x.count, repo_to_rls.values())):.2%}",
            f"{median(map(lambda x: x.fixes / x.count, repo_to_rls.values())):.2%}",
            f"{stdev(map(lambda x: x.fixes / x.count, repo_to_rls.values())):.2%}",
        ]
    )
    table.add_row(
        [
            "Duplicate",
            f"{total.duplicate / total.count:.2%}",
            f"{min(map(lambda x: x.duplicate / x.count, repo_to_rls.values())):.2%}",
            f"{max(map(lambda x: x.duplicate / x.count, repo_to_rls.values())):.2%}",
            f"{fmean(map(lambda x: x.duplicate / x.count, repo_to_rls.values())):.2%}",
            f"{median(map(lambda x: x.duplicate / x.count, repo_to_rls.values())):.2%}",
            f"{stdev(map(lambda x: x.duplicate / x.count, repo_to_rls.values())):.2%}",
        ]
    )
    print(table)

    if print_abs:
        table = PrettyTable()
        table.field_names = ["Min", "Max", "Mean", "Median", "STDEV"]
        table.add_row(
            [
                f"{min(map(lambda x: x.count, repo_to_rls.values()))}",
                f"{max(map(lambda x: x.count, repo_to_rls.values()))}",
                f"{fmean(map(lambda x: x.count, repo_to_rls.values()))}",
                f"{median(map(lambda x: x.count, repo_to_rls.values()))}",
                f"{stdev(map(lambda x: x.count, repo_to_rls.values()))}",
            ]
        )
        print(table)


if __name__ == "__main__":
    main()
