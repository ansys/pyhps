import os
import re
import sys


def replace_regex(filename, new_version, patterns, group=1):

    with open(filename, "r") as myfile:
        content = myfile.read()

    header = f"File: {os.path.relpath(filename)}\n   "

    for pattern in patterns:
        re_res = re.search(pattern, content)
        if re_res is not None:
            old_string = re_res.group(0)
            old_version = ".".join(re_res.groups())

            if new_version != old_version:
                new_string = old_string.replace(old_version, new_version)

                print(f"{header}'{old_string}' --> '{new_string}' ")
                content = content.replace(old_string, new_string)

            else:
                print(f"{header}'{old_string}' already up-to-date ")

        else:
            print(f"{header}Couldn't find a match for {pattern}")

    with open(filename, "w") as myfile:
        myfile.write(content)


def main():

    internal_version = sys.argv[1]
    external_version = sys.argv[2]
    internal_version_no_dot = internal_version.replace(".", "")

    cwd = os.getcwd()

    version_file_path = os.path.join(cwd, "ansys", "rep", "client", "__version__.py")
    replace_regex(version_file_path, internal_version, [r"(\d+.\d+).0"])

    replace_regex(version_file_path, internal_version_no_dot, [r'__version_no_dots__ = "(\d+)"'])

    replace_regex(version_file_path, external_version, [r'__external_version__ = "(.*)"'])

    replace_regex(
        os.path.join(cwd, "doc", "source", "conf.py"), internal_version_no_dot, [r"corp/v(\d+)"]
    )


if __name__ == "__main__":
    main()
