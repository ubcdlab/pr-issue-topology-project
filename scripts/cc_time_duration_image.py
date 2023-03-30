from collections import defaultdict
from os import makedirs
from pickle import dump, load
from statistics import correlation, median, pstdev, fmean, stdev
from sys import path
from os import path as os_path
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import rc
from numpy import array
from prettytable import PrettyTable
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from click import command, option
from dataclasses import dataclass
from statistics import mean
from scipy import interpolate
from math import sqrt

path.append("..")

from scripts.helpers import all_graphs, num_graphs, to_json, fetch_path
from pipeline.picklereader import PickleReader
from pipeline.NetworkVisCreator import NetworkVisCreator
from typing import List

pr = PickleReader([])
nwvc = NetworkVisCreator(None, [])


@dataclass(repr=True)
class ConnectedComponentsStatistics:
    size: int
    min_time: float
    max_time: float


def parallelize_graph_processing(path: Path) -> List[ConnectedComponentsStatistics]:
    path_str = str(path)
    graph_json = to_json(path_str)
    structure_json = to_json(fetch_path(path_str, from_graph=True))
    seen = set()

    repo_ccs = []
    for node in graph_json["nodes"]:
        if node["id"] in seen:
            continue
        seen.add(node["id"])
        last_date = node["creation_date"]
        if node["event_list"] and node["event_list"][-1]["created_at"] > node["creation_date"]:
            last_date = node["event_list"][-1]["created_at"]
        elif node["updated_at"] > node["creation_date"]:
            last_date = node["updated_at"]
        node_cc_stats = ConnectedComponentsStatistics(
            1,
            node["creation_date"],
            last_date,
        )
        for cc_node_id in node["connected_component"]:
            if cc_node_id in seen:
                continue
            seen.add(cc_node_id)
            cc_node = next(filter(lambda n: n["id"] == cc_node_id, graph_json["nodes"]))
            node_cc_stats.min_time = min(node_cc_stats.min_time, cc_node["creation_date"])
            node_cc_stats.max_time = max(
                node_cc_stats.max_time,
                cc_node["event_list"][-1]["created_at"] if len(cc_node["event_list"]) else cc_node["updated_at"],
            )
            node_cc_stats.size += 1
        repo_ccs.append(node_cc_stats)

    return repo_ccs


def main():
    cc_size_to_duration_map = defaultdict(list)
    font = {"fontname": "IBM Plex Sans"}
    if not os_path.exists("cc_size_to_duration.pickle"):
        with Pool(cpu_count() // 2) as p:
            with tqdm(total=num_graphs(), leave=False) as pbar:
                for res in p.imap_unordered(
                    parallelize_graph_processing,
                    all_graphs(),
                ):
                    for cc in res:
                        cc_size_to_duration_map[cc.size].append((cc.max_time - cc.min_time) / 86400)

                    pbar.update()
        with open("cc_size_to_duration.pickle", "wb") as x:
            dump(cc_size_to_duration_map, x)
    else:
        with open("cc_size_to_duration.pickle", "rb") as x:
            cc_size_to_duration_map = load(x)

    plt.rcParams["font.sans-serif"] = "IBM Plex Sans"
    plt.rcParams["font.family"] = "sans-serif"
    plt.xlabel("Component Size", **font)
    plt.ylabel("Component Duration (log scale, days.)", **font)
    ax = plt.gca()
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.spines[["right", "top"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, zorder=-1, which="minor", color="#ddd")
    ax.xaxis.grid(True, zorder=-1, which="minor", color="#ddd")
    cc_size_to_duration_map = dict(sorted(cc_size_to_duration_map.items(), key=lambda x: x[0]))
    plt.bar(
        list(cc_size_to_duration_map.keys()),
        list(map(lambda x: x / 86400, list(map(lambda x: mean(x), cc_size_to_duration_map.values())))),
        width=0.1 * array(list(cc_size_to_duration_map.keys())),
    )
    non_singular = dict(filter(lambda x: len(x[1]) > 1, list(cc_size_to_duration_map.items())[:31]))
    plt.errorbar(
        list(non_singular.keys()),
        list(map(lambda x: x / 86400, list(map(lambda x: mean(x), non_singular.values())))),
        yerr=list(
            map(
                lambda x: x / 86400,
                list(map(lambda x: stdev(x) / sqrt(len(x)) if len(x) > 1 else 0, list(non_singular.values()))),
            )
        ),
        capsize=3,
        linestyle="None",
        fmt="",
        ecolor="black",
        color="black",
        elinewidth=0.75,
        capthick=0.75,
    )
    print(
        correlation(
            list(cc_size_to_duration_map.keys())[15:],
            list(map(lambda x: x / 86400, list(map(lambda x: mean(x), cc_size_to_duration_map.values()))))[15:],
        )
    )

    try:
        makedirs("misc_images/")
    except:
        pass
    plt.savefig(f"misc_images/cc_time_duration.png", bbox_inches="tight", dpi=150)


if __name__ == "__main__":
    main()
