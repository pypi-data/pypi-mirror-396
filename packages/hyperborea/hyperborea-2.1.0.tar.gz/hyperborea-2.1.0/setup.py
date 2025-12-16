from setuptools import setup
from setuptools_scm.version import ScmVersion, get_local_node_and_date


def no_local_develop_scheme(version: ScmVersion) -> str:
    if getattr(version, "branch", None) == "develop" and not version.dirty:
        return ""
    else:
        return get_local_node_and_date(version)


setup(use_scm_version={'local_scheme': no_local_develop_scheme})
