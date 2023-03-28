from collections import Counter, defaultdict
from statistics import median, pstdev, fmean
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

path.append("..")

from scripts.helpers import all_graphs, num_graphs, to_json
from pipeline.picklereader import PickleReader
from pipeline.NetworkVisCreator import NetworkVisCreator
from scripts.plplot import plplot

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
@option("--print-plaw", "print_plaw", is_flag=True, default=False)
def main(print_plaw: bool):
    use("agg")
    font = {"fontname": "IBM Plex Sans"}
    plt.rcParams["font.sans-serif"] = "IBM Plex Sans"
    plt.rcParams["font.family"] = "sans-serif"
    plt.xlabel("Degree", **font)
    plt.ylabel("Frequency", **font)
    ax = plt.gca()
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.spines[["right", "top"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, zorder=-1, which="major", color="#ddd")
    ax.xaxis.grid(True, zorder=-1, which="minor", color="#ddd")
    deg_to_freq_map = defaultdict(int)
    with Pool(cpu_count() // 2) as p:
        with tqdm(total=num_graphs(), leave=False) as pbar:
            for res in p.imap_unordered(parallelize_graph_processing, all_graphs()):
                for i, val in enumerate(nx.degree_histogram(res)):
                    deg_to_freq_map[i] += val
                pbar.update()
    num_nodes = []
    for i in range(1, max(deg_to_freq_map.keys()) + 1):
        num_nodes.append(deg_to_freq_map.get(i, 0))

    fit = Fit(num_nodes, discrete=True)
    if print_plaw:
        print("α:", fit.power_law.alpha)
        print("KS:", fit.power_law.KS())
    plplot(num_nodes, fit.power_law.xmin, fit.power_law.alpha, fit.power_law.KS())
    try:
        makedirs("misc_images/")
    except:
        pass
    plt.savefig(f"misc_images/degree_distribution.png", bbox_inches="tight", dpi=150)


if __name__ == "__main__":
    main()
