import os
import re
from git import Repo
from packaging.version import Version

repo = Repo(".")
valid_version_re = r"[0-9]+\.[0-9]+\.[0-9]"


def valid_version(v: str):
    return re.search(valid_version_re, v)


def strip_version(v: str):
    return re.search(valid_version_re, v).group(0)


MASTER_VERSION = strip_version((repo.commit("origin/master").tree / "src/lhcb_ftcalib/_version.py").data_stream.read().decode())
CURRENT_VERSION = strip_version(open("src/lhcb_ftcalib/_version.py", "r").read())
merge_branch_name = os.environ["CURRENT_BRANCH"]
print("MASTER:",         MASTER_VERSION)
print("FEATURE BRANCH:", merge_branch_name)
print("__version__:",    CURRENT_VERSION)

on_master = merge_branch_name == "master"

def test_branch_name():
    assert on_master or valid_version(merge_branch_name), f"{merge_branch_name} is not a valid X.Y.Z release branch name"

def test_release_name():
    assert on_master or valid_version(CURRENT_VERSION), "Version specified in _version.py is not of the form X.Y.Z"

def test_branch_matches_release():
    assert on_master or Version(strip_version(merge_branch_name)) == Version(CURRENT_VERSION), f"_version.py needs version update to {merge_branch_name}!"

def test_release_is_newer():
    assert on_master or Version(strip_version(merge_branch_name)) > Version(MASTER_VERSION), f"New release must have strictly newer version than master (>{MASTER_VERSION})"
