from click import command, option
from re import match


@command()
@option("--path", "path")
def main(path: str):
    lines = open(path, "r").readlines()
    new_lines = []
    for l in lines:
        res = match(r'.*user: "(.*)".*email\s=\s"(.*)"', l)
        new_lines.append(f'call {{MATCH ()-[r {{user: "{res.groups()[0]}"}}]-() SET r.email = "{res.groups()[1]}"}}')
    new_path = path.removesuffix("query.txt") + "relationships_query.txt"
    with open(new_path, "w") as x:
        x.write("\n".join(new_lines))


if __name__ == "__main__":
    main()
