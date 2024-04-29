from collections import Counter, defaultdict
from os.path import isfile
from pickle import dump, load
from statistics import median, pstdev, fmean
from os import makedirs
from sys import path
from pathlib import Path
from click import command, option
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import use
from numpy import quantile, array
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from powerlaw import Fit, pdf
from scipy.optimize import curve_fit

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
    use("agg")
    plt.figure(figsize=(8, 2))
    font = {"fontname": "IBM Plex Sans"}
    plt.rcParams["font.sans-serif"] = "IBM Plex Sans"
    plt.rcParams["font.family"] = "sans-serif"
    plt.xlabel("Power Law Exponent ", **font, fontsize=12)
    # plt.ylabel("Frequency", **font)
    ax = plt.gca()
    ax.set_axisbelow(True)
    ax.yaxis.set_visible(False)
    plt.rc("xtick", labelsize=12)
    ax.spines[["right", "top", "left"]].set_visible(False)
    if not isfile("dd_blot.pickle"):
        fits = []
        repo_to_fit_map = {}
        with Pool(cpu_count() // 2) as p:
            with tqdm(total=num_graphs(), leave=False) as pbar:
                for res in p.imap_unordered(parallelize_graph_processing, all_graphs()):
                    deg_to_freq_map = defaultdict(int)
                    for i, val in enumerate(nx.degree_histogram(res)):
                        deg_to_freq_map[i] += val
                    num_nodes = []
                    for i in range(1, max(deg_to_freq_map.keys()) + 1):
                        num_nodes.append(deg_to_freq_map.get(i, 0))

                    fit = Fit(num_nodes, discrete=True)
                    fits.append(fit.power_law.alpha)
                    repo_to_fit_map[res.graph["repository"]] = fit.power_law.alpha
                    pbar.update()
        with open("dd_blot.pickle", "wb") as x:
            dump(fits, x)
        with open("dd_blot_map.pickle", "wb") as x:
            dump(repo_to_fit_map, x)
    else:
        with open("dd_blot.pickle", "rb") as x:
            fits = load(x)
        with open("dd_blot_map.pickle", "rb") as x:
            repo_to_fit_map = load(x)
    fits = list(map(lambda x: x + 1, fits))
    quantiles = quantile(fits, array([0.00, 0.25, 0.50, 0.75, 1.00]))
    ax.vlines(
        quantiles,
        [1] * quantiles.size,
        [1.2] * quantiles.size,
        color="black",
        ls=":",
        lw=0.5,
        zorder=0,
    )
    ax.set_ylim(1, 1.3)
    for i in range(len(quantiles)):
        ax.text(
            quantiles[i], 1.22, f"{quantiles[i]:.2f}", **font, fontsize=12, ha="center"
        )
    ax.set_ylim(0.5, 1.5)
    plt.boxplot(fits, vert=False)

    try:
        makedirs("misc_images/")
    except:
        pass
    plt.tight_layout()
    plt.savefig(
        f"misc_images/degree_distribution_bplot.png", bbox_inches="tight", dpi=150
    )
    print(
        dict(
            filter(
                lambda x: x[1] > quantiles[3] + 3 * (quantiles[3] - quantiles[1]) / 2,
                repo_to_fit_map.items(),
            )
        )
    )


if __name__ == "__main__":
    main()
