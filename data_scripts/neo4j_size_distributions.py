from collections import defaultdict
from statistics import mean, pstdev, median
from click import command, option
from tqdm import tqdm
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
from sys import path
from prettytable import PrettyTable
from os import makedirs


path.append("..")

from data_scripts.helpers import generate_image


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

    size_counts_map = defaultdict(int)
    sizes = []
    for record in tqdm(records, total=len(records), leave=False):
        to_highlight = []
        for key in record.keys():
            if key not in [
                "nodes",
                "relationships",
                "match_relationships",
                "all_ids",
                "optional_issue",
                "optional_r",
                "proportion",
            ] or (key == "optional_issue" and record.get(key) is not None):
                if type(record.get(key)) != list:
                    n = record.get(key)
                    to_highlight += [n._properties["number"]]
                else:
                    to_highlight += [
                        list_item._properties["number"] for list_item in record.get(key)
                    ]
        size_counts_map[len(to_highlight)] += 1
        sizes.append(len(to_highlight))
        continue

    total = sum(size_counts_map.values())
    table = PrettyTable()
    table.field_names = ["Size", "Count", "Percentage of Total"]
    for k, v in sorted(size_counts_map.items(), key=lambda i: i[1], reverse=True):
        table.add_row([k, v, f"{v/total:.2%}"])

    if to_csv:
        if not name:
            print("--name required with --to-csv.")
            exit(1)
        try:
            makedirs(f"neo4j_statistics/size_distribution")
        except:
            pass
        with open(
            f"neo4j_statistics/size_distribution/{name}_statistics.csv", "w"
        ) as x:
            x.write(table.get_csv_string())
    else:
        print(table)
        print(f"Total matches: {total}")

    table = PrettyTable()
    table.field_names = ["Average Size", "Min", "Max", "Median", "STDEV"]
    table.add_row(
        [
            f"{mean(sizes):.2f}",
            f"{min(sizes):.2f}",
            f"{max(sizes):.2f}",
            f"{median(sizes):.2f}",
            f"{pstdev(sizes):.2f}",
        ]
    )
    print(table)

    session.close()
    db.close()


if __name__ == "__main__":
    main()
