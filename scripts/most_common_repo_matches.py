from collections import defaultdict

from scripts.helpers import all_graphs, fetch_repo, to_json

with open("scripts/tableConvert.csv") as x:
    lines = x.readlines()
    lines = [l for l in lines if l.replace(",", "").strip()]

repo_to_matches_map = defaultdict(int)
for l in lines:
    lsplit = l.split(",")
    repo_to_matches_map[lsplit[0]] += int(lsplit[1])

repo_to_matches_map = dict(
    sorted(map(lambda x: [x[0].replace("/", "-"), x[1]], repo_to_matches_map.items()), key=lambda x: x[1], reverse=True)
)
print(repo_to_matches_map)
print(len(repo_to_matches_map))
sum_t = 0
for p in all_graphs():
    repo = fetch_repo(str(p), from_graph=True)
    if repo not in repo_to_matches_map:
        print(repo, len(to_json(str(p))["nodes"]))
        sum_t += len(to_json(str(p))["nodes"])
print(sum_t)
