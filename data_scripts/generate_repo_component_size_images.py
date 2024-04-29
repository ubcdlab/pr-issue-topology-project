from collections import defaultdict
from os import makedirs
from statistics import median, pstdev, fmean, stdev
from sys import path
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import rc
from prettytable import PrettyTable
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from click import command, option
from dataclasses import dataclass

path.append("..")

from data_scripts.helpers import all_graphs, num_graphs, to_json
from archive.pipeline.picklereader import PickleReader
from archive.pipeline.NetworkVisCreator import NetworkVisCreator

pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])


def parallelize_graph_processing(path_str: str):
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
                            repo=target_repo,
                        )
                    },
                )
            )

    local_graph.add_nodes_from(to_add)
    local_graph.add_edges_from(edges_to_add)
    return local_graph


@command()
@option("--repo", "target_repo")
@option("--all", "all_repos", is_flag=True, default=False)
def main(target_repo: str, all_repos: bool):
    size_frequency_map = defaultdict(int)
    repo_to_size_freq_map = defaultdict(dict)
    font = {"fontname": "IBM Plex Sans"}
    with Pool(cpu_count() // 2) as p:
        with tqdm(total=1 if not all_repos else num_graphs(), leave=False) as pbar:
            for res in p.imap_unordered(
                parallelize_graph_processing,
                (
                    [f"data/graph_{target_repo.replace('/','-')}.json"]
                    if not all_repos
                    else list(map(lambda x: str(x), all_graphs()))
                ),
            ):
                if all_repos:
                    repo_to_size_freq_map[res.graph["repository"]] = defaultdict(int)
                for component in nx.connected_components(res):
                    if not all_repos:
                        size_frequency_map[len(component)] += 1
                    else:
                        repo_to_size_freq_map[res.graph["repository"]][
                            len(component)
                        ] += 1
                pbar.update()

    plt.rcParams["font.sans-serif"] = "IBM Plex Sans"
    plt.rcParams["font.family"] = "sans-serif"
    plt.xlabel("Component Sizes", **font)
    plt.ylabel("Frequency of Components of Size", **font)
    ax = plt.gca()
    ax.set_yscale("log")
    legend = None
    if not all_repos:
        plt.title(f"Component sizes by frequency for {target_repo}", **font)
        plt.scatter(size_frequency_map.keys(), size_frequency_map.values())
    else:
        plt.title(f"Component sizes by frequency for all projects", **font)
        cmap = plt.cm.get_cmap(plt.cm.viridis, 143)
        for i, data_dict in enumerate(repo_to_size_freq_map.values()):
            x = data_dict.keys()
            y = data_dict.values()
            plt.scatter(x, y, color=cmap(2 * i))
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        legend = plt.legend(
            list(repo_to_size_freq_map.keys())[-10:],
            loc="center left",
            bbox_to_anchor=(1, 0.5),
        )
    try:
        makedirs("repo_component_size_freq_img/")
    except:
        pass
    if not all_repos:
        plt.savefig(f"repo_component_size_freq_img/{target_repo.replace('/','')}.png")
    else:
        plt.tight_layout()
        plt.savefig(f"repo_component_size_freq_img/all_repos.png")


if __name__ == "__main__":
    main()
