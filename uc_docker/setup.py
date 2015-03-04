"""Setup for uc_docker XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='uc_docker-xblock',
    version='0.1',
    description='uc_docker XBlock',   # TODO: write a better description.
    packages=[
        'uc_docker',
    ],
    install_requires=[
        'XBlock',
        'paramiko',
        'docker-py',
    ],
    entry_points={
        'xblock.v1': [
            'uc_docker = uc_docker:UcDockerXBlock',
        ]
    },
    package_data=package_data("uc_docker", ["static", "public"]),
)
