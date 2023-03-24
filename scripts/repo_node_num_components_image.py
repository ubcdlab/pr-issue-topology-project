from collections import defaultdict
from os import makedirs
from pickle import dump, load
from statistics import median, pstdev, fmean, stdev
from sys import path
from os import path as os_path
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import rc
from numpy import corrcoef
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
@option("--print-corr", "print_corr", is_flag=True, default=False)
def main(print_corr: bool):
    repo_to_point_map = defaultdict(dict)
    font = {"fontname": "IBM Plex Sans"}
    if not os_path.exists("repo_to_point_map.pickle"):
        with Pool(cpu_count() // 2) as p:
            with tqdm(total=num_graphs(), leave=False) as pbar:
                for res in p.imap_unordered(
                    parallelize_graph_processing,
                    all_graphs(),
                ):
                    repo_to_point_map[res.graph["repository"]] = {}
                    repo_to_point_map[res.graph["repository"]][res.number_of_nodes()] = nx.number_connected_components(
                        res
                    )

                    pbar.update()
        with open("repo_to_point_map.pickle", "wb") as x:
            dump(repo_to_point_map, x)
    else:
        with open("repo_to_point_map.pickle", "rb") as x:
            repo_to_point_map = load(x)

    plt.rcParams["font.sans-serif"] = "IBM Plex Sans"
    plt.rcParams["font.family"] = "sans-serif"
    plt.xlabel("Number of Nodes (log scale)", **font)
    plt.ylabel("Number of Connected Components (log scale)", **font)
    ax = plt.gca()
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.spines[["right", "top"]].set_visible(False)
    legend = None
    cmap = plt.cm.get_cmap("RdYlGn", num_graphs())
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, zorder=-1, which="minor", color="#ddd")
    ax.xaxis.grid(True, zorder=-1, which="minor", color="#ddd")
    repo_to_point_map = dict(
        sorted(repo_to_point_map.items(), key=lambda item: list(item[1].values())[0], reverse=True)
    )
    xs = []
    ys = []
    for i, data_dict in enumerate(repo_to_point_map.values()):
        x = data_dict.keys()
        y = data_dict.values()
        plt.scatter(x, y, color=cmap(i))
        xs.extend(x)
        ys.extend(y)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    min_top = [
        plt.Line2D([0], [0], color="w", marker="o", markerfacecolor=cmap(i), label=x, markersize=8)
        for i, x in enumerate(list(repo_to_point_map.keys())[:5])
    ]
    max_top = [
        plt.Line2D([0], [0], color="w", marker="o", markerfacecolor=cmap(num_graphs() - 5 + i), label=x, markersize=8)
        for i, x in enumerate(list(repo_to_point_map.keys())[-5:])
    ]
    plt.legend(handles=min_top + max_top, loc="center left", bbox_to_anchor=(1, 0.5))
    try:
        makedirs("misc_images/")
    except:
        pass
    plt.savefig(f"misc_images/nodes_to_num_components.png", bbox_inches="tight", dpi=150)
    if print_corr:
        print(corrcoef(xs, ys))


if __name__ == "__main__":
    main()
