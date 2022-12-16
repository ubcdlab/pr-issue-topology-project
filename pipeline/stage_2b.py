import sys
import ComponentSampler
from pathlib import Path

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
    cs = ComponentSampler.ComponentSampler(None, TARGET_REPO_ARRAY)
    cs.load_all_repo_component()

if __name__ == '__main__':
    main()