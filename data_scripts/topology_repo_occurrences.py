from typing import Dict, List
from click import command, option
from tqdm import tqdm
from neo4j import GraphDatabase
from sys import path
from prettytable import PrettyTable
from dataclasses import dataclass
from statistics import fmean, pstdev


path.append("..")


@dataclass(repr=True)
class RepoResult:
    repository: str
    matches: int
    proportions: List[float]
    num_issues: int
    num_prs: int


ISSUE_QUERY = """
match (n:issue {repository: $repository}) return count(distinct n) as issue_count
"""

PR_QUERY = """
match (n:pull_request {repository: $repository}) return count(distinct n) as pr_count
"""


@command()
@option("--cypher", "cypher_path")
def main(cypher_path: str):
    command = open(cypher_path, "r").read()
    param_repository = None

    def run_command(tx):
        if param_repository:
            result = tx.run(command, {"repository": param_repository})
        else:
            result = tx.run(command)
        records = list(result)
        summary = result.consume()
        return records, summary

    with open("generate_neo4j_images/password", "r") as x:
        password = x.readline().strip()
    db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", password))
    session = db.session(database="neo4j")
    records, _ = session.execute_read(run_command)

    repo_map: Dict[str, RepoResult] = {}
    for record in tqdm(records, total=len(records), leave=False):
        repository = ""
        is_issue = False
        for key in record.keys():
            if key != "proportion":
                if key == "i" and key not in ["nodes", "relationships"]:
                    is_issue = True
                repository = record.get(key)._properties["repository"]
                break
        if not repository:
            continue
        if repository in repo_map:
            repo_map[repository].proportions.append(record.get("proportion"))
            repo_map[repository].matches += 1
        else:
            param_repository = repository
            command = ISSUE_QUERY
            issue_records, _ = session.execute_read(run_command)
            issue_count = issue_records[0].get("issue_count")
            command = PR_QUERY
            pr_records, _ = session.execute_read(run_command)
            pr_count = pr_records[0].get("pr_count")
            repo_map[repository] = RepoResult(repository, 1, [record.get("proportion")], issue_count, pr_count)
            param_repository = None

    table = PrettyTable()
    table.field_names = [
        "Repository",
        "Average MTCO",
        "Low MTCO",
        "High MTCO",
        "STDev MTCO",
        "# PRs",
        "# Issues",
        "# Matches",
    ]
    for k, v in sorted(
        repo_map.items(), key=lambda i: i[1].matches / (i[1].num_issues if is_issue else i[1].num_prs), reverse=True
    ):
        table.add_row(
            [
                k,
                f"{fmean(v.proportions):.3f}",
                f"{min(v.proportions):.3f}",
                f"{max(v.proportions):.3f}",
                f"{pstdev(v.proportions):.3f}",
                v.num_prs,
                v.num_issues,
                v.matches,
            ]
        )
    print(table)

    session.close()
    db.close()


if __name__ == "__main__":
    main()
