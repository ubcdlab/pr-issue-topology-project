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


def power_law(x, m, c):
    return x**m * c


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
    deg_to_freq_map = {
        0: 55878,
        1: 22216,
        2: 7457,
        3: 2789,
        4: 1230,
        5: 593,
        6: 315,
        7: 183,
        8: 112,
        9: 96,
        10: 44,
        11: 36,
        12: 24,
        13: 29,
        14: 14,
        15: 10,
        16: 7,
        17: 11,
        18: 10,
        19: 6,
        20: 4,
        21: 6,
        22: 4,
        23: 5,
        24: 8,
        25: 2,
        26: 6,
        27: 0,
        28: 0,
        29: 6,
        30: 2,
        31: 0,
        32: 2,
        33: 1,
        34: 0,
        35: 1,
        36: 2,
        37: 1,
        38: 1,
        39: 0,
        40: 1,
        41: 1,
        42: 1,
        43: 0,
        44: 2,
        45: 0,
        46: 1,
        47: 0,
        48: 2,
        49: 1,
        50: 0,
        51: 1,
        52: 0,
        53: 1,
        54: 0,
        55: 0,
        56: 1,
        57: 0,
        58: 0,
        59: 0,
        60: 0,
        61: 0,
        62: 0,
        63: 0,
        64: 0,
        65: 0,
        66: 0,
        67: 0,
        68: 0,
        69: 0,
        70: 0,
        71: 1,
        72: 0,
        73: 0,
        74: 0,
        75: 0,
        76: 0,
        77: 0,
        78: 0,
        79: 0,
        80: 0,
        81: 0,
        82: 0,
        83: 0,
        84: 0,
        85: 0,
        86: 0,
        87: 0,
        88: 0,
        89: 1,
        90: 0,
        91: 0,
        92: 0,
        93: 0,
        94: 0,
        95: 0,
        96: 0,
        97: 0,
        98: 0,
        99: 0,
        100: 0,
        101: 0,
        102: 0,
        103: 0,
        104: 0,
        105: 0,
        106: 0,
        107: 1,
    }
    deg_to_freq_map = dict(filter(lambda x: x[1] != 0, deg_to_freq_map.items()))
    # with Pool(cpu_count() // 2) as p:
    #    with tqdm(total=num_graphs(), leave=False) as pbar:
    #        for res in p.imap_unordered(parallelize_graph_processing, all_graphs()):
    #            for i, val in enumerate(nx.degree_histogram(res)):
    #                deg_to_freq_map[i] += val
    #            pbar.update()
    num_nodes = []
    for i in range(1, max(deg_to_freq_map.keys()) + 1):
        num_nodes.append(deg_to_freq_map.get(i, 0))

    fit = Fit(num_nodes, discrete=True)
    if print_plaw:
        print("α:", fit.power_law.alpha)
        print("KS:", fit.power_law.KS())
    # plt.scatter(deg_to_freq_map.keys(), deg_to_freq_map.values())
    # fit.power_law.plot_pdf(
    #    color="dimgray",
    #    linestyle="--",
    # )
    plplot(num_nodes, fit.power_law.xmin, fit.power_law.alpha, fit.power_law.KS())
    try:
        makedirs("misc_images/")
    except:
        pass
    plt.savefig(f"misc_images/degree_distribution.png", bbox_inches="tight", dpi=150)


if __name__ == "__main__":
    main()
