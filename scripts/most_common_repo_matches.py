from collections import defaultdict

from scripts.helpers import all_graphs, fetch_repo

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
for p in all_graphs():
    repo = fetch_repo(str(p), from_graph=True)
    if repo not in repo_to_matches_map:
        print(repo)
