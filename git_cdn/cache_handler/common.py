import os
from datetime import datetime
from shutil import rmtree

NOW = datetime.now()


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


# using scandir recursively is faster than using os.walk()
def dir_size(directory):
    size = 0
    for entry in os.scandir(directory):
        if entry.is_symlink():
            continue
        elif entry.is_dir():
            size += dir_size(entry.path)
        elif entry.is_file():
            size += entry.stat().st_size
    return size


class BasePrune:
    def __str__(self):
        return f"{self.path:100}\t{self.age} days\t{self.size_fmt}"

    def __repr__(self):
        return self.__str__()

    @property
    def age(self):
        return (NOW - self.mtime).days

    @property
    def size_fmt(self):
        return sizeof_fmt(self.size)


class GitRepo(BasePrune):
    def __init__(self, directory):
        self.lockfile = directory.path + ".lock"
        self.path = directory.path
        self._mtime = None
        self._size = None

    @property
    def mtime(self):
        mtime = os.stat(self.lockfile).st_mtime
        return datetime.fromtimestamp(mtime)

    @property
    def size(self):
        if self._size is None:
            self._size = dir_size(self.path)
        return self._size

    def delete(self):
        print(f"Delete {self.path}", end="")
        rmtree(self.path, ignore_errors=True)
        try:
            os.unlink(self.lockfile)
        except FileNotFoundError:
            pass
        print("\t\t[OK]")


def find_git_repo(s):
    dir_entries = [e for e in os.scandir(s) if e.is_dir()]
    subgroups = [d for d in dir_entries if not d.name.endswith(".git")]
    repos = [d for d in dir_entries if d.name.endswith(".git")]
    git_repos = [GitRepo(d) for d in repos]
    for subgroup in subgroups:
        yield from find_git_repo(subgroup)
    for g in git_repos:
        yield g


class LfsFile(BasePrune):
    def __init__(self, file):
        self.file = file
        self.path = file.path
        self.lock = file.path + ".lock"
        self._mtime = None

    @property
    def mtime(self):
        if self._mtime is None:
            self._mtime = datetime.fromtimestamp(self.file.stat().st_mtime)
        return self._mtime

    @property
    def size(self):
        return self.file.stat().st_size

    def delete(self):
        print(f"Removing {self.path}")
        os.unlink(self.path)
        try:
            os.unlink(self.lock)
        except FileNotFoundError:
            pass
        tree = os.path.dirname(self.path)
        while tree != "lfs":
            try:
                os.rmdir(tree)
            except OSError:
                break
            print(f"Cleaned empty dir {tree}")
            tree = os.path.dirname(tree)


def find_lfs(s):
    dir_entries = [e for e in os.scandir(s) if e.is_dir()]
    lfs = [
        LfsFile(f)
        for f in os.scandir(s)
        if f.is_file() and not f.name.endswith(".lock")
    ]

    for directory in dir_entries:
        for g in find_lfs(directory):
            yield g
    for f in lfs:
        yield f


class BundleFile(BasePrune):
    def __init__(self, file):
        self.file = file
        self.path = file.path
        # remove "_clone.bundle" and add ".lock"
        self.lock = file.path[:-13] + ".lock"
        self._mtime = None

    @property
    def mtime(self):
        if self._mtime is None:
            self._mtime = datetime.fromtimestamp(self.file.stat().st_mtime)
        return self._mtime

    @property
    def size(self):
        return self.file.stat().st_size

    def delete(self):
        print(f"Removing {self.path}")
        os.unlink(self.path)
        try:
            os.unlink(self.lock)
        except FileNotFoundError:
            pass


def find_bundle():
    for f in os.scandir("bundles"):
        if f.is_file() and f.path.endswith(".bundle"):
            yield BundleFile(f)
