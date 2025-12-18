from importlib.metadata import distribution, packages_distributions


def get_dist_meta(class_: type):
    """
    Retrieve distribution information for the current module.

    Returns:
        tuple: A tuple containing the distribution name, version, and metadata dictionary.
        Returns None if the distribution cannot be determined.
    """
    mod_name = class_.__module__.split(".")[0]

    dist_name = packages_distributions().get(mod_name, [None])[0]
    if dist_name is None:
        return None

    dist = distribution(dist_name)
    return dist.name, dist.version, dist.metadata
