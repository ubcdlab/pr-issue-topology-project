from scripts.helpers import all_graphs, fetch_repo, num_graphs
from pickle import load
from json import dumps
from tqdm import tqdm
from time import mktime

for path in tqdm(all_graphs(), total=num_graphs(), leave=True):
    repo_name = fetch_repo(str(path), from_graph=True)
    objects = []
    with open(f"raw_data/nodes_{repo_name}_comments.pk", "rb") as x:
        comment_list = load(x)
        for thread in comment_list:
            for comment in thread:
                objects.append(
                    {
                        "contents": comment.body,
                        "created_at": mktime(comment.created_at.timetuple()),
                        "id": comment.id,
                        "url": comment.url,
                    }
                )
    with open(f"comments_dump/{repo_name}_comments.json", "w") as x:
        x.write(dumps(objects))
