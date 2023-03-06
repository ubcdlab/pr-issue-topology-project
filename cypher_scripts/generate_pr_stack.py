from click import command, option


def gen_cypher(size: int, subgraph=False):
    query = "match (pr:pull_request)"
    for i in range(1, size):
        query += f"-[r{i}]->(pr_{i+1}:pull_request)"
    query += "\n"
    query += "optional match (optional_issue:issue)-[optional_r]-(pr)\n"
    query += "unwind [pr.number, " + ", ".join([f"pr_{i}.number" for i in range(2, size + 1)]) + "] as number_list\n"
    query += "unwind [pr.status, " + ", ".join([f"pr_{i}.status" for i in range(2, size + 1)]) + "] as status_list\n"
    query += "unwind [pr.user, " + ", ".join([f"pr_{i}.user" for i in range(2, size + 1)]) + "] as user_list\n"
    query += (
        "with pr, "
        + ", ".join([f"pr_{i}" for i in range(2, size + 1)])
        + ", collect(distinct number_list) as number_list, ["
        + ", ".join([f"r{i}" for i in range(1, size)])
        + "] as match_relationships, status_list, optional_issue, optional_r, user_list, count(user_list) as user_counts\n"
    )
    query += (
        "with pr, "
        + ", ".join([f"pr_{i}" for i in range(2, size + 1)])
        + ", number_list, match_relationships, status_list, optional_issue, optional_r, apoc.agg.maxItems(user_list, user_counts) as max_users\n"
    )
    query += (
        f"where size(number_list) = {size} and "
        + " < ".join(["pr.creation_date"] + [f"pr_{i}.creation_date" for i in range(2, size + 1)])
        + f' and not (:pull_request)-->(pr) and not (pr_{size})-->(:pull_request) and size([i in status_list where i = "merged"]) >= {size}/2 and max_users.value >= {size}/2\n'
    )
    if subgraph:
        query += "call apoc.path.subgraphAll(pr, {limit: 50, bfs: true})\n"
        query += "yield nodes, relationships\n"
    query += (
        "return pr, "
        + ("nodes, relationships, match_relationships, " if subgraph else "")
        + ", ".join([f"pr_{i}" for i in range(2, size + 1)])
        + ", [id(pr), "
        + ", ".join([f"id(pr_{i})" for i in range(2, size + 1)])
        + "] as all_ids, optional_issue, optional_r"
    )
    return query


@command()
@option("--size", "size", type=int)
@option("--nodes", "nodes", is_flag=True, default=True)
def main(size: int, nodes: bool):
    query = gen_cypher(size, nodes)
    with open("cypher_scripts/PR_Stack_Gen.cypher", "w") as x:
        x.write(query)


if __name__ == "__main__":
    main()
