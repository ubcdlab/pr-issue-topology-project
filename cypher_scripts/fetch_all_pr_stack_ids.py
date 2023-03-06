from os import makedirs
from subprocess import call
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
from . import generate_pr_stack

all_ids = set()


def main(size: int):
    command = generate_pr_stack.gen_cypher(size)

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

    for record in records:
        all_ids.update(record.get("all_ids"))

    session.close()
    db.close()


if __name__ == "__main__":
    for i in tqdm(range(3, 16), total=(16 - 3)):
        main(i)
    print(all_ids)
    with open("cypher_scripts/all_ids_dump", "w") as x:
        x.write(str(all_ids))
