import sys
import dataminer

def get_token():
    # get personal access token from a file named token.txt
    token = None
    try:
        with open('.token', 'r') as f:
            token = f.read()
            print('Github token read OK')
    except IOError:
        pass
    return token

def main():
    try:
        TARGET_REPO_ARRAY = sys.argv[1:]
    except IndexError:
        print(f'Expected at least 1 argument, found {len(sys.argv) - 1}')
        print('Exiting')
        sys.exit(1)
    dm = dataminer.Dataminer(get_token(), "Frozemint/pr_dev")
    dm.download_repo_data()
    print('hi')

if __name__ == '__main__':
    main()