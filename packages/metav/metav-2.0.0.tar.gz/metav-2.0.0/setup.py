# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r",encoding="utf-8") as fh:
  long_description = fh.read()

setuptools.setup(
  name="metav",
  version="2.0.0",
  author="Zhi-Jian Zhou",
  description="rapid detection and classification of viruses in metagenomics sequencing.",
  keywords="virus detection, sequencing, metagenomics",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/ZhijianZhou01/metav",
  packages=setuptools.find_packages(),
  install_requires=["colorama>=0.4.5"],

  classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        
    ],
  entry_points={
             'console_scripts': [
                 'metav = metav.main:starts',
             ],
    }
)
