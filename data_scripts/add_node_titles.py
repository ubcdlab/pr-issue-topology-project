from sys import path
from os.path import isdir, dirname, abspath
from tqdm import tqdm

path.append(dirname(dirname(abspath(__file__))))

from archive.pipeline.picklereader import PickleReader
from helpers import all_graphs

pr = PickleReader([])
new_lines = []
for repo in tqdm(all_graphs(), total=len(list(all_graphs())), leave=False):
    repo = str(repo).replace("data/graph_", "").replace(".json", "")
    if repo.lower() not in [
        "rapptz-discord.py",
        "metafizzy-flickity",
        "kubernetes-sigs-kustomize",
        "typestrong-ts-node",
        "mithriljs-mithril.js",
        "jupyterhub-jupyterhub",
        "apache-dubbo",
        "app-vnext-polly",
        "mlflow-mlflow",
        "rematch-rematch",
        "grpc-grpc-web",
        "chaijs-chai",
        "iron-iron",
        "ptomasroos-react-native-scrollable-tab-view",
        "project-osrm-osrm-backend",
        "tensorpack-tensorpack",
        "burntsushi-toml",
        "summernote-summernote",
        "magicstack-uvloop",
        "deployphp-deployer",
        "varvet-pundit",
    ]:
        continue
    pickle_nodes, _, _, _, _ = pr.read_repo_local_file(None, repo)
    for n in pickle_nodes:
        title = n._title.value.replace("\\", "\\").replace('"', '\\"')
        new_lines.append(
            f'call {{MATCH (n {{number: {n._number.value}, repository: "{"/".join(n.url.split("/")[4:6])}"}}) SET n.title = "{title}"}}'
        )
with open("./node_titles_query.txt", "w") as x:
    x.write("\n".join(new_lines))
