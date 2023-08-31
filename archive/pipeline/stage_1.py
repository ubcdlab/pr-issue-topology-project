import sys
import dataminer
from pathlib import Path

def get_token():
    # get personal access token from a file named token.txt
    token = None
    PATH = Path(__file__).resolve().parents[1].joinpath('.token')
    try:
        with open(PATH, 'r') as f:
            token = f.read()
            print('Github token read OK')
    except IOError:
        print('Failed to read Github token. Did you create a .token file in the project root directory?')
        print('Exiting.')
        sys.exit(1)
    return token

def main():
    try:
        TARGET_REPO_ARRAY = sys.argv[1:]
        if len(TARGET_REPO_ARRAY) < 1:
            raise IndexError
    except IndexError:
        print(f'Expected at least 1 argument, found {len(sys.argv) - 1}')
        print(f'You need to specify the names of Github repo to download as arguments.')
        print('Exiting.')
        sys.exit(1)
    dm = dataminer.Dataminer(get_token(), TARGET_REPO_ARRAY)
    dm.download_all_repo_data()

if __name__ == '__main__':
    main()