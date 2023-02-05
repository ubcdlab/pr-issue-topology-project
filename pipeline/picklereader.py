import sys
import pickle
import os
from pathlib import Path


class PickleReader(object):
    def __init__(self, target_repo_list):
        self.target_repo_list = target_repo_list

    def read_repo_local_file(self, repo, target_repo):
        target_repo_no_slash = target_repo.replace("/", "-")  # slashes breaks file path
        # PATH_FROM_PARENT_DIR = f'raw_data/nodes_{target_repo_no_slash}'
        # PATH = os.path.abspath(os.path.join(os.path.abspath('..'), PATH_FROM_PARENT_DIR))
        PATH = Path(__file__).resolve().parents[1].joinpath(f"raw_data/nodes_{target_repo_no_slash}")
        nodes, node_list, comment_list, timeline_list, review_comment_list = ([] for i in range(5))
        try:
            nodes = pickle.load(open(f"{PATH}.pk", "rb"))
            node_list = pickle.load(open(f"{PATH}_progress.pk", "rb"))
            comment_list = pickle.load(open(f"{PATH}_comments.pk", "rb"))
            timeline_list = pickle.load(open(f"{PATH}_event.pk", "rb"))
            review_comment_list = pickle.load(open(f"{PATH}_review_comments.pk", "rb"))
        except FileNotFoundError:
            print("One or more binary files missing. Redownloading repo files.")
            nodes = list(repo.get_issues(state="all", sort="created", direction="desc"))
            node_list = nodes.copy()
            review_comment_list = list(repo.get_pulls_review_comments(sort="created", direction="desc"))
            pickle.dump(review_comment_list, open(f"{PATH}_review_comments.pk", "wb"))
        except Exception as e:
            print(e)
            print(
                "To the new RA, an exception (that is not FileNotFoundError) has happened, and it's not supposed to ever happen."
            )
            sys.exit(1)
        return nodes, node_list, comment_list, timeline_list, review_comment_list

    def write_variables_to_file(self, nodes, node_list, comment_list, timeline_list, review_comment_list, target_repo):
        target_repo_no_slash = target_repo.replace("/", "-")  # slashes breaks file path
        PATH = Path(__file__).resolve().parents[1].joinpath(f"raw_data/nodes_{target_repo_no_slash}")
        print("Writing raw nodes and comment data to disk...\nDO NOT INTERRUPT OR TURN OFF YOUR COMPUTER.")
        pickle.dump(nodes, open(f"{PATH}.pk", "wb"))
        pickle.dump(node_list, open(f"{PATH}_progress.pk", "wb"))
        pickle.dump(comment_list, open(f"{PATH}_comments.pk", "wb"))
        pickle.dump(timeline_list, open(f"{PATH}_event.pk", "wb"))
        pickle.dump(review_comment_list, open(f"{PATH}_review_comments.pk", "wb"))
