import os


def get_dirs(root, sort=True):
    return (sorted if sort else list)(
        (name for name in os.listdir(root) if os.path.isdir(os.path.join(root, name)))
    )
