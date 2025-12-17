from setuptools_scm.version import ScmVersion, guess_next_version
from setuptools import setup


def custom_local_scheme(version: ScmVersion):
    if version.exact:
        return ""
    else:
        return "+git." + version.node[1:8] if version.node else ""


def custom_version_scheme(version: ScmVersion):
    if version.exact:
        return version.format_with("{tag}")
    else:
        return guess_next_version(version)


setup(use_scm_version={"version_scheme": custom_version_scheme, "local_scheme": custom_local_scheme})
