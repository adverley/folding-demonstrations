import fnmatch
import os


def all_directories_in(path):
    return sorted([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])


def walk_files(data_path, extension):
    fragment_files = []
    for root, dirnames, filenames in os.walk(data_path):
        for filename in fnmatch.filter(filenames, '*.{}'.format(extension)):
            fragment_files.append(os.path.join(root, filename))

    return sorted(fragment_files)
