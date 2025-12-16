# Copyright (c) 2021-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary

import glob
import os
import shutil
import site
import subprocess
import sys

from setuptools import setup

from cuda_autodetect import infer_best_package, bdist_wheel


# Update this for every release
package_ver = '25.11.1'
package_name = "cuquantum"


# get project long description
with open("README.rst") as f:
    long_description = f.read()


# This setup.py handles 2 cases:
#   1. At the release time, we use it to generate sdist (which contains this script)
#   2. At the install time, users install the sdist from PyPI
# and the two cases have different requirements. We distinguish them by
# setting CUQUANTUM_META_WHEEL_BUILD=1 for Case 1.
if os.environ.get('CUQUANTUM_META_WHEEL_BUILD', '0') == '1':
    # Case 1: generate sdist
    install_requires = []
    data_files = [('', ['cuda_autodetect.py',])]  # extra files to be copied into sdist
    cmdclass = {}
else:
    # Case 2: install sdist
    install_requires = [f"{infer_best_package(package_name)}=={package_ver}",]
    data_files = []
    cmdclass = {'bdist_wheel': bdist_wheel} if bdist_wheel is not None else {}


setup(
    name=package_name,
    version=package_ver,
    description="NVIDIA cuQuantum SDK",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://developer.nvidia.com/cuquantum-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/NVIDIA/cuQuantum/issues",
        "User Forum": "https://github.com/NVIDIA/cuQuantum/discussions",
        "Documentation": "https://docs.nvidia.com/cuda/cuquantum/",
    },
    author="NVIDIA Corporation",
    author_email="cuda_installer@nvidia.com",
    license="NVIDIA Proprietary Software",
    license_files = ('LICENSE',),
    keywords=["cuda", "nvidia", "state vector", "tensor network", "high-performance computing", "quantum computing"],
    # Install files indicated by MANIFEST.in
    # See https://github.com/pypa/sampleproject/issues/30#issuecomment-143947944
    include_package_data=True,
    zip_safe=False,
    data_files=data_files,
    setup_requires=[
        "setuptools",
        "wheel",
    ],
    install_requires=install_requires,
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Environment :: GPU :: NVIDIA CUDA",
        "Environment :: GPU :: NVIDIA CUDA :: 12",
        "Environment :: GPU :: NVIDIA CUDA :: 13",
    ],
    cmdclass=cmdclass,
)
