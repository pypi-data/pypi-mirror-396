import os
import re
from pathlib import Path

from setuptools import setup

long_description = (Path(__file__).parent / "README.md").read_text()
requirements = (Path(__file__).parent / "requirements.txt").read_text().split("\n")

version = re.sub(r"^v", "", os.getenv("VERSION", "v0.1.0-dev"))

print(f"Publishing version {version}")

setup(
    name="ecs-shell",
    python_requires=">=3.10",
    version=version,
    description="Interactive shell for AWS ECS tasks with service and task selection.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    py_modules=["ecs_shell"],
    entry_points={
        "console_scripts": ["ecs-shell = ecs_shell:main"],
    },
    license="MIT",
    url="https://github.com/yourusername/ecs-shell",
    keywords="aws, ecs, shell, docker, container, devops",
    author="Francisco",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        "Topic :: System :: Systems Administration",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
