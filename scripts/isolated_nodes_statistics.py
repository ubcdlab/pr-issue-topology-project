from dataclasses import dataclass
from pathlib import Path
from json import loads
from re import match
from prettytable import PrettyTable
from .helpers import all_structures, to_json, fetch_path


@dataclass
class OverallStatistics:
    open: int
    merged: int
    closed: int
    total: int


@dataclass
class PRStatistics(OverallStatistics):
    open: int
    merged: int
    closed: int
    total: int


@dataclass
class IssueStatistics(OverallStatistics):
    open: int
    merged: int
    closed: int
    total: int


pr_statistics = PRStatistics(0, 0, 0, 0)
issue_statistics = IssueStatistics(0, 0, 0, 0)

# pull isolated nodes from data/structure_*, then grab node data from data/graph_*
pathlist = all_structures()
for path in pathlist:
    isolated_nodes = []
    path_str = str(path)

    structure_json = to_json(path_str)
    isolated_nodes = structure_json["1"]["isolated"]
    isolated_nodes = [nested[0] for nested in isolated_nodes]

    graph_json = to_json(fetch_path(path_str))
    for isolated_node in isolated_nodes:
        graph_node = next(filter(lambda g_node: g_node["id"] == isolated_node, graph_json["nodes"]))
        to_modify = None
        if graph_node["type"] == "pull_request":
            to_modify = pr_statistics
        else:
            to_modify = issue_statistics
        to_modify.total += 1
        if graph_node["status"] == "open":
            to_modify.open += 1
        elif graph_node["status"] == "merged":
            to_modify.merged += 1
        else:
            to_modify.closed += 1

table = PrettyTable()
table.field_names = ["Node Type", "Open", "Merged", "Closed", "Total"]
table.add_row(
    [
        "PR",
        f"{pr_statistics.open/pr_statistics.total:.2%}",
        f"{pr_statistics.merged/pr_statistics.total:.2%}",
        f"{pr_statistics.closed/pr_statistics.total:.2%}",
        f"{pr_statistics.total/(pr_statistics.total + issue_statistics.total):.2%}",
    ]
)
table.add_row(
    [
        "Issue",
        f"{issue_statistics.open/issue_statistics.total:.2%}",
        "—",
        f"{issue_statistics.closed/issue_statistics.total:.2%}",
        f"{issue_statistics.total/(pr_statistics.total + issue_statistics.total):.2%}",
    ]
)
table.add_row(
    [
        "Total",
        f"{(pr_statistics.open + issue_statistics.open)/(pr_statistics.total + issue_statistics.total):.2%}",
        f"{(pr_statistics.merged)/(pr_statistics.total + issue_statistics.total):.2%}",
        f"{(pr_statistics.closed + issue_statistics.closed)/(pr_statistics.total + issue_statistics.total):.2%}",
        f"{(pr_statistics.total + issue_statistics.total)/(pr_statistics.total + issue_statistics.total):.2%}",
    ],
)
print(table)
