from asyncio import gather, run
from collections import Counter, defaultdict
from dataclasses import dataclass
from os.path import isdir
from statistics import mean, pstdev
from time import sleep
from datetime import datetime
from typing import List, Set
from click import command, option
import networkx as nx
from prettytable import PrettyTable
from tqdm import tqdm
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
from random import sample
from sys import path
from os import scandir, remove
from requests import get
from json import loads
from pause import until


path.append("..")

from data_scripts.helpers import generate_image, fetch_path, to_json
from archive.pipeline.picklereader import PickleReader

pr = PickleReader([])
headers = {
    "Authorization": "token " + open("scripts/token.txt", "r").readline().strip()
}


@command()
@option("--cypher", "cypher_path")
@option("--name", "name")
def main(cypher_path: str, name: str):
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

    users = defaultdict(int)
    for record in tqdm(records, total=len(records), leave=False):
        cypher_nodes = record.get("nodes")
        cypher_mr = record.get("match_relationships")
        for n in cypher_nodes:
            users[n._properties["user"]] += 1
        for mr in cypher_mr:
            users[mr._properties["user"]] += 1
    users = dict(sorted(users.items(), key=lambda x: x[1], reverse=True))

    emails = {}
    res = get(f"https://api.github.com/rate_limit", headers=headers)
    res = loads(res.text)
    print(
        f"{res['resources']['core']['remaining']} left, resets at {res['resources']['core']['reset']}"
    )
    if res["resources"]["core"]["remaining"] == 0:
        until(res["resources"]["core"]["reset"] + 5)

    for user in tqdm(users, total=len(users), leave=False):
        res = get(f"https://api.github.com/rate_limit", headers=headers)
        res = loads(res.text)
        print(
            f"{res['resources']['core']['remaining']} left, resets at {res['resources']['core']['reset']}"
        )
        if res["resources"]["core"]["remaining"] == 0:
            until(res["resources"]["core"]["reset"] + 5)
        req = get(f"https://api.github.com/users/{user}/repos", headers=headers)
        res = loads(req.text)
        while "message" in res:
            if res["message"] == "Not Found":
                break
            print(res)
            sleep(70)
            req = get(f"https://api.github.com/users/{user}/repos", headers=headers)
            res = loads(req.text)
            print("NEW:", res)
        if "message" in res and res["message"] == "Not Found":
            continue
        if len(res) == 0:
            continue
        res = get(
            f"https://api.github.com/repos/{res[0]['full_name']}/commits?author={user}",
            headers=headers,
        )
        res = loads(res.text)
        if len(res) == 0:
            continue
        if "message" in res:
            print(res["message"])
            continue
        res = res[0]
        if (
            "commit" in res
            and not res["commit"]["author"]["email"].endswith(
                "users.noreply.github.com"
            )
            and "author" in res
            and res["author"]
            and res["author"]["login"] == user
        ):
            emails[user] = res["commit"]["author"]["email"]
        elif (
            "commit" in res
            and not res["commit"]["committer"]["email"].endswith(
                "users.noreply.github.com"
            )
            and "committer" in res
            and res["committer"]
            and res["committer"]["login"] == user
        ):
            emails[user] = res["commit"]["committer"]["email"]
    with open(f"emails/{name}_query.txt", "w") as x:
        contents = ""
        for user, email in emails.items():
            contents += (
                f"""call {{MATCH (n {{user: "{user}"}}) SET n.email = "{email}"}}\n"""
            )
        x.write(contents)

    session.close()
    db.close()


if __name__ == "__main__":
    run(main())
