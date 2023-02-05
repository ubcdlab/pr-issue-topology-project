import sys
import NetworkVisCreator as NetworkVisCreator
import BarChartCreator as BarChartCreator
from pathlib import Path


def get_token():
    # get personal access token from a file named token.txt
    token = None
    PATH = Path(__file__).resolve().parents[1].joinpath(".token")
    try:
        with open(PATH, "r") as f:
            token = f.read().strip()
            print("Github token read OK")
    except IOError:
        print("Failed to read Github token. Did you create a .token file in the project root directory?")
        print("Exiting.")
        sys.exit(1)
    return token


def main():
    try:
        TARGET_REPO_ARRAY = sys.argv[1:]
        if len(TARGET_REPO_ARRAY) < 1:
            raise IndexError
    except IndexError:
        print(f"Expected at least 1 argument, found {len(sys.argv) - 1}")
        print(f"You need to specify the names of Github repo to download as arguments.")
        print("Exiting.")
        sys.exit(1)
    network_vis_creator = NetworkVisCreator.NetworkVisCreator(get_token(), TARGET_REPO_ARRAY)
    network_vis_creator.create_vis_for_all_repo()
    # bar_chart_creator = BarChartCreator.BarChartCreator(None, TARGET_REPO_ARRAY)
    # bar_chart_creator.create_vis_for_all_repo()


if __name__ == "__main__":
    main()
