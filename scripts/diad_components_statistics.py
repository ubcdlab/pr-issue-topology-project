from pathlib import Path
from json import loads
from dataclasses import dataclass
from re import match
from prettytable import PrettyTable
from .helpers import all_structures, to_json, fetch_path
from sys import argv


@dataclass
class OverallStatistics:
    issue_issue: int
    issue_pr: int
    pr_issue: int
    pr_pr: int
    closed_issue_merged_pr: int
    merged_pr_closed_issue: int
    total_diad: int


closed_links = False
if len(argv) == 2 and argv[1] == "include_closed":
    closed_links = True
    print("Including closed Issues → merged PRs and Merged PRs → closed Issues...")

overall_statistics = OverallStatistics(0, 0, 0, 0, 0, 0, 0)
total_component_count = 0

# pull diads from data/structure_* and total node lengths from data/graph_*
pathlist = all_structures()
for path in pathlist:
    path_str = str(path)

    structure_json = to_json(path_str)
    # add duo counts
    overall_statistics.total_diad += len(structure_json["2"]["duo_issue_issue"]) * 2
    overall_statistics.issue_issue += len(structure_json["2"]["duo_issue_issue"]) * 2
    overall_statistics.total_diad += len(structure_json["2"]["duo_issue_pr"]) * 2
    overall_statistics.issue_pr += len(structure_json["2"]["duo_issue_pr"]) * 2
    overall_statistics.total_diad += len(structure_json["2"]["duo_pr_issue"]) * 2
    overall_statistics.pr_issue += len(structure_json["2"]["duo_pr_issue"]) * 2
    overall_statistics.total_diad += len(structure_json["2"]["duo_pr_pr"]) * 2
    overall_statistics.pr_pr += len(structure_json["2"]["duo_pr_pr"]) * 2

    match_obj = match(r".*structure_([\w\-.]+).json", path_str)
    if not match_obj:
        print("Could not find repository name from file path.", path_str)
        exit(1)
    repo_name = match_obj.groups()[0]

    graph_json = to_json(fetch_path(path_str))
    total_component_count += len(graph_json["nodes"])

    if closed_links:
        for issue in structure_json["2"]["duo_issue_pr"]:
            issue_node = next(filter(lambda n: n["id"] == issue[0], graph_json["nodes"]))
            pr_node = next(filter(lambda n: n["id"] == issue[1], graph_json["nodes"]))
            if issue_node["status"] == "closed" and pr_node["status"] == "merged":
                overall_statistics.closed_issue_merged_pr += 1
        for pr in structure_json["2"]["duo_pr_issue"]:
            pr_node = next(filter(lambda n: n["id"] == pr[0], graph_json["nodes"]))
            issue_node = next(filter(lambda n: n["id"] == pr[1], graph_json["nodes"]))
            if pr_node["status"] == "merged" and issue_node["status"] == "closed":
                overall_statistics.merged_pr_closed_issue += 1


table = PrettyTable()
table.field_names = ["Issue → Issue", "Issue → PR", "PR → Issue", "PR → PR"]
table.add_row(
    [
        f"{overall_statistics.issue_issue/overall_statistics.total_diad:.2%}",
        f"{overall_statistics.issue_pr/overall_statistics.total_diad:.2%}",
        f"{overall_statistics.pr_issue/overall_statistics.total_diad:.2%}",
        f"{overall_statistics.pr_pr/overall_statistics.total_diad:.2%}",
    ]
)
print(table)
print(f"(Percentage of components that are diads: {overall_statistics.total_diad/total_component_count:.2%})")

if closed_links:
    table = PrettyTable()
    table.field_names = ["Type", "Closed Issue → Merged PR", "Merged PR → Closed Issue"]
    table.add_row(["Raw Counts", overall_statistics.closed_issue_merged_pr, overall_statistics.merged_pr_closed_issue])
    table.add_row(
        [
            "Percentages of Size 2 Components",
            f"{overall_statistics.closed_issue_merged_pr/overall_statistics.total_diad:.2%}",
            f"{overall_statistics.merged_pr_closed_issue/overall_statistics.total_diad:.2%}",
        ]
    )
    print(table)
