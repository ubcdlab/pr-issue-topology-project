from pathlib import Path
from json import loads
from dataclasses import dataclass
from re import match
from prettytable import PrettyTable
from .helpers import all_structures, to_json, fetch_path


@dataclass
class OverallStatistics:
    issue_issue: int
    issue_pr: int
    pr_issue: int
    pr_pr: int
    total_diad: int


overall_statistics = OverallStatistics(0, 0, 0, 0, 0)
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
