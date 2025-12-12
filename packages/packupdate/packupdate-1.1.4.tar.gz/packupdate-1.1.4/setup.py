from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent / "../docs"
long_description = (this_directory / "python.md").read_text()

setup(
    name="packupdate",
    version="1.1.4",
    description="A Python utility to update Node.js project dependencies safely with interactive mode and version management.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Manish Shrestha",
    author_email="sth.pratik@gmail.com",
    url="https://github.com/sthpratik/PackUpdate",
    packages=find_packages(),  # Automatically finds the 'packUpdate' package
    install_requires=[
        "inquirer>=2.10.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "packUpdate=packUpdate.updatePackages:main",
            "updatepkgs=packUpdate.updatePackages:main",
            "updatenpmpackages=packUpdate.updatePackages:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
