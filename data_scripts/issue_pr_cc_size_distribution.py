from collections import Counter, defaultdict
from os.path import isfile
from pickle import dump, load
from statistics import mean, median, pstdev, fmean, correlation
from os import makedirs
from sys import path
from pathlib import Path
from click import command, option
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import use
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from powerlaw import Fit, pdf
from scipy.optimize import curve_fit
from numpy import array, polyfit

path.append("..")

from data_scripts.helpers import all_graphs, num_graphs, to_json
from archive.pipeline.picklereader import PickleReader
from archive.pipeline.NetworkVisCreator import NetworkVisCreator

pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])


def parallelize_graph_processing(path: Path):
    path_str = str(path)
    target_repo = to_json(path_str)["repo_url"].replace("https://github.com/", "")

    nodes, _, comment_list, timeline_list, _ = pr.read_repo_local_file(
        None, target_repo
    )

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
                    "type": (
                        "pull_request" if node.pull_request is not None else "issue"
                    ),
                    "status": node_status,
                    "repository": target_repo,
                    "number": node.number,
                    "creation_date": node.created_at.timestamp(),
                    "closed_at": (
                        node.closed_at.timestamp() if node.closed_at is not None else 0
                    ),
                    "updated_at": node.updated_at.timestamp(),
                },
            )
        )
        node_timeline = timeline_list[-index - 1]
        node_timeline = list(
            filter(
                lambda x: x.event == "cross-referenced"
                and x.source.issue.repository.full_name == target_repo,
                node_timeline,
            )
        )
        for mention in node_timeline:
            mentioning_issue_comments = nwvc.find_comment(
                mention.source.issue.url, comment_list
            )
            edges_to_add.append(
                (
                    f"{target_repo}#{mention.source.issue.number}",
                    f"{target_repo}#{node.number}",
                    {
                        "link_type": nwvc.find_automatic_links(
                            node.number,
                            mention.source.issue.body,
                            mentioning_issue_comments,
                        )
                    },
                )
            )

    local_graph.add_nodes_from(to_add)
    local_graph.add_edges_from(edges_to_add)
    return local_graph


def main():
    # use("agg")
    font = {"fontname": "IBM Plex Sans"}
    plt.rcParams["font.sans-serif"] = "IBM Plex Sans"
    plt.rcParams["font.family"] = "sans-serif"
    plt.figure(figsize=(6.4, 3.2))
    plt.xlabel("Connected Component Size", **font)
    plt.ylabel("% of Total", **font)
    ax = plt.gca()
    ax.set_xscale("log")
    ax.spines[["right", "top"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, zorder=-1, which="major", color="#ddd")
    ax.xaxis.grid(True, zorder=-1, which="minor", color="#ddd")
    cc_size_distribution_issues_map = defaultdict(int)
    cc_size_distribution_prs_map = defaultdict(int)
    if not isfile("cc_size_node_distribution.pickle"):
        with Pool(cpu_count() // 2) as p:
            with tqdm(total=num_graphs(), leave=False) as pbar:
                for res in p.imap_unordered(parallelize_graph_processing, all_graphs()):
                    for component in nx.connected_components(res):
                        cc_size_distribution_prs_map[len(component)] += len(
                            list(
                                filter(
                                    lambda x: x[1]["type"] == "pull_request",
                                    res.subgraph(component).nodes(data=True),
                                )
                            )
                        )
                        cc_size_distribution_issues_map[len(component)] += len(
                            list(
                                filter(
                                    lambda x: x[1]["type"] == "issue",
                                    res.subgraph(component).nodes(data=True),
                                )
                            )
                        )
                    pbar.update()
        with open("cc_size_node_distribution.pickle", "wb") as x:
            dump([cc_size_distribution_issues_map, cc_size_distribution_prs_map], x)
    else:
        with open("cc_size_node_distribution.pickle", "rb") as x:
            # cc_size_distribution_issues_map, cc_size_distribution_prs_map = load(x) # use this line, using below to avoid recomputing local results
            cc_size_distribution_prs_map, cc_size_distribution_issues_map = load(x)

    all_total = sum(cc_size_distribution_issues_map.values()) + sum(
        cc_size_distribution_prs_map.values()
    )
    y = list(
        map(
            lambda x: x[1] / (x[1] + cc_size_distribution_prs_map[x[0]]),
            cc_size_distribution_issues_map.items(),
        )
    )
    plt.bar(
        cc_size_distribution_issues_map.keys(),
        y,
        color="#1894C9",
        label="Issues",
        width=0.1 * array(list(cc_size_distribution_issues_map.keys())),
    )
    old_y = y
    y = list(map(lambda x: 1 - x, y))
    plt.bar(
        cc_size_distribution_issues_map.keys(),
        y,
        bottom=old_y,
        color="#EA9649",
        label="Pull Requests",
        width=0.1 * array(list(cc_size_distribution_issues_map.keys())),
    )
    plt.legend()

    try:
        makedirs("misc_images/")
    except:
        pass
    plt.savefig(f"misc_images/issue_pr_ratio_cc_size.png", bbox_inches="tight", dpi=150)

    print(correlation(list(cc_size_distribution_issues_map.keys()), old_y))
    print(correlation(list(cc_size_distribution_prs_map.keys()), y))
    print(
        cc_size_distribution_issues_map[1]
        / (cc_size_distribution_issues_map[1] + cc_size_distribution_prs_map[1])
    )


if __name__ == "__main__":
    main()
