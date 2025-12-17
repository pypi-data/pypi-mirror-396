from setuptools import setup, find_packages

setup(
    name="mypackage",  # the package name for pip
    version="0.1.0",
    packages=find_packages(),  # automatically find packages
    install_requires=[ 'primer3-py>=2.0.0',
        'biopython>=1.79',
        'pandas>=1.3.0',
        'matplotlib>=3.4.0',
        'numpy>=1.21.0',
        'jinja2>=3.0.0',
        'openpyxl>=3.0.0',
        'pyyaml>=6.0',
    ],
    url="https://github.com/xiaoguanghuan123/fine_mapping_indelPrimerDesign",
    author="Guangchao Sun & Changchuang Liu",
    author_email="guangchaosun@sicau.edu.cn",
    description="Automated indel primer design for fine mapping within a F2:3 recombinant population",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
