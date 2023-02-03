from typing import List
from .helpers import fetch_path, all_graphs, num_graphs, to_json
from sys import argv
from dataclasses import dataclass
from prettytable import PrettyTable
from datetime import timedelta, date
from human_readable import time_delta
from human_readable import date as hr_date
from tqdm import tqdm


@dataclass(repr=True)
class ConnectedComponentsStatistics:
    nodes: List[int]
    size: int
    min_time: float
    max_time: float
    average_comment_span_duration: int  # diff between creation and last comment
    component_id: int
    repo: str


output_csv = None
for arg in argv:
    if "output_csv" in arg:
        output_csv = open(arg.split("=")[-1], "w")
        output_csv.writelines(
            [
                "Repo,Component ID,Component Size,Nodes,First Node Creation,Last Node Update,Delta,Average Conversation Span Duration\n"
            ]
        )

is_small = False
if "small" in argv:
    is_small = True

to_print = False
if "print" in argv:
    to_print = True

repo_str = None
for arg in argv:
    if "repo" in arg:
        repo_str = arg.split("=")[-1].replace("/", "-")
        print(f"Using repository {repo_str}...")

specific_size = None
for arg in argv:
    if "specific_size" in arg:
        specific_size = int(arg.split("=")[-1])
        print(f"Searching for size {specific_size}...")

pathlist = all_graphs()
for path in tqdm(pathlist, total=num_graphs()):
    path_str = str(path)
    graph_json = to_json(path_str)
    seen = set()

    for node in graph_json["nodes"]:
        if node["id"] in seen:
            continue
        seen.add(node["id"])
        if not specific_size and (
            (
                not is_small
                and (
                    (type(node["connected_component_size"]) is list and node["connected_component_size"][0] < 20)
                    or (type(node["connected_component_size"]) is int and node["connected_component_size"] < 20)
                )
            )
            or (
                is_small
                and (
                    (type(node["connected_component_size"]) is list and node["connected_component_size"][0] >= 10)
                    or (type(node["connected_component_size"]) is int and node["connected_component_size"] >= 10)
                )
            )
        ):
            continue
        if specific_size and (
            (type(node["connected_component_size"]) is list and node["connected_component_size"][0] != specific_size)
            or (type(node["connected_component_size"]) is int and node["connected_component_size"] != specific_size)
        ):
            continue
        node_cc_stats = ConnectedComponentsStatistics(
            [node["id"]],
            1,
            node["creation_date"],
            node["closed_at"] if node["closed_at"] else node["creation_date"],
            node["event_list"][-1]["created_at"] - node["creation_date"] if len(node["event_list"]) else 0,
            node["component_id"],
            graph_json["repo_url"].replace("https://github.com/", ""),
        )
        for cc_node_id in node["connected_component"]:
            if cc_node_id in seen:
                continue
            seen.add(cc_node_id)
            cc_node = next(filter(lambda n: n["id"] == cc_node_id, graph_json["nodes"]))
            node_cc_stats.min_time = min(node_cc_stats.min_time, cc_node["creation_date"])
            node_cc_stats.max_time = max(
                node_cc_stats.min_time,
                cc_node["event_list"][-1]["created_at"] if len(cc_node["event_list"]) else 0,
            )
            if len(cc_node["event_list"]):
                node_cc_stats.average_comment_span_duration = (
                    node_cc_stats.average_comment_span_duration * node_cc_stats.size
                    + cc_node["event_list"][-1]["created_at"]
                    - cc_node["creation_date"]
                ) / (node_cc_stats.size + 1)
            node_cc_stats.size += 1
            node_cc_stats.nodes += [cc_node_id]
        if to_print or not output_csv:
            table = PrettyTable()
            table.field_names = [
                "Repository",
                "Component ID",
                # "Nodes",
                "Size",
                "Creation",
                "Last Update",
                "Δ",
                "Average comment span",
            ]
            table.add_row(
                [
                    node_cc_stats.repo,
                    node_cc_stats.component_id,
                    # node_cc_stats.nodes,
                    node_cc_stats.size,
                    hr_date(date.fromtimestamp(int(node_cc_stats.min_time))),
                    hr_date(date.fromtimestamp(int(node_cc_stats.max_time))),
                    time_delta(timedelta(seconds=int(node_cc_stats.max_time) - int(node_cc_stats.min_time))),
                    time_delta(timedelta(seconds=int(node_cc_stats.average_comment_span_duration))),
                ]
            )
            print(table)
        if output_csv:
            output_csv.writelines(
                [
                    ",".join(
                        [
                            str(e)
                            for e in [
                                node_cc_stats.repo,
                                node_cc_stats.component_id,
                                node_cc_stats.size,
                                node_cc_stats.nodes,
                                int(node_cc_stats.min_time),
                                int(node_cc_stats.max_time),
                                int(node_cc_stats.max_time) - int(node_cc_stats.min_time),
                                int(node_cc_stats.average_comment_span_duration),
                            ]
                        ]
                    )
                    + "\n"
                ]
            )
