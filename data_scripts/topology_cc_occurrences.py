from os import makedirs
from typing import Dict, List
from click import command, option
from tqdm import tqdm
from neo4j import GraphDatabase
from sys import path
from prettytable import PrettyTable
from dataclasses import dataclass
from statistics import fmean, pstdev
from csv import writer


path.append("..")


@dataclass(repr=True)
class CCResult:
    matches: int
    proportions: List[float]


@command()
@option("--cypher", "cypher_path")
@option("--to-csv", "to_csv", is_flag=True, default=False)
@option("--name", "name", default="")
def main(cypher_path: str, to_csv: bool, name: str):
    command = open(cypher_path, "r").read()

    def run_command(tx):
        result = tx.run(command)
        records = list(result)
        summary = result.consume()
        return records, summary

    with open("generate_neo4j_images/password", "r") as x:
        password = x.readline().strip()
    db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", password))
    session = db.session(database="neo4j")
    records, _ = session.execute_read(run_command)

    size_map: Dict[int, CCResult] = {}
    for record in tqdm(records, total=len(records), leave=False):
        cypher_cc = record.get("nodes")
        if len(cypher_cc) in size_map:
            size_map[len(cypher_cc)].proportions.append(record.get("proportion"))
            size_map[len(cypher_cc)].matches += 1
        else:
            size_map[len(cypher_cc)] = CCResult(1, [record.get("proportion")])

    total = sum(map(lambda i: i.matches, size_map.values()))
    table = PrettyTable()
    table.field_names = [
        "Size",
        "# Matches",
        "% Total Matches",
        "Average MTCO",
        "Low MTCO",
        "High MTCO",
        "STDev MTCO",
    ]
    for k, v in sorted(size_map.items(), key=lambda i: i[1].matches, reverse=True):
        table.add_row(
            [
                k,
                v.matches,
                f"{v.matches / total:.2f}%",
                f"{fmean(v.proportions):.3f}",
                f"{min(v.proportions):.3f}",
                f"{max(v.proportions):.3f}",
                f"{pstdev(v.proportions):.3f}",
            ]
        )
    if to_csv:
        if not name:
            print("--name required with --to-csv.")
            exit(1)
        try:
            makedirs(f"neo4j_statistics/")
        except:
            pass
        with open(f"neo4j_statistics/{name}_statistics.csv", "w") as x:
            x.write(table.get_csv_string())
    else:
        print(table)

    session.close()
    db.close()


if __name__ == "__main__":
    main()
