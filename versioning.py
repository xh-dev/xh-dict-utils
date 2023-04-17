import argparse
import re
import sys

import toml

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="py-project-versioner",
        description="snippet update version of python `pyproject.toml`"
    )

    parser.add_argument("--version-mod", type=str, choices=["major", "minor", "patch"], default="", help="the mode of modification")
    parser.add_argument("-d", "--direct", action="store_true", help="upgrade")
    parser.add_argument("--patch", dest="version_mod", action="store_const", const="patch", help="update the patch level[default option]")
    parser.add_argument("--minor", dest="version_mod", action="store_const", const="minor", help="update the minor level")
    parser.add_argument("--major", dest="version_mod", action="store_const", const="major", help="update the mjaro level")
    parser.add_argument("-r", "--release", action="store_true", default=False, help="release with any build meta removed")

    argv = parser.parse_args(sys.argv[1:])
    version_mod = argv.version_mod


    toml_data = toml.load("pyproject.toml")

    version_str = toml_data["project"]["version"]

    pattern = re.compile("^(\\d+)\\.(\\d+)\\.(\\d+)(-dev)?(\\+[^ ]+)?$")
    matcher = pattern.match(version_str)
    if matcher:
        major = int(matcher.group(1))
        minor = int(matcher.group(2))
        patch = int(matcher.group(3))
        pre_release = matcher.group(4)[1:] if matcher.group(4) else None
        build = int(matcher.group(5)[1:]) if matcher.group(5) else 0

        if argv.release:
            toml_data["project"]["version"] = f"{major}.{minor}.{patch}"
        else:
            if pre_release != "dev":
                if version_mod == "major":
                    major=major+1
                elif version_mod == "minor":
                    minor=minor+1
                elif version_mod == "patch":
                    patch=patch+1
                else:
                    print("Current version: ", version_str)
                    exit()

                pre_release = "dev"
                build = 0

            else:
                build+=1

            pre_release_str = '' if argv.direct else f"-{pre_release}"
            build_str = '' if argv.direct else f"+{+build:03d}"
            toml_data["project"]["version"] = f"{major}.{minor}.{patch}{pre_release_str}{build_str}"
        print("Existing version: ", version_str)
        print("New version: ", toml_data["project"]["version"])
        with open("pyproject.toml", "w") as f:
            toml.dump(toml_data, f)
    else:
        raise Exception("not match version")
