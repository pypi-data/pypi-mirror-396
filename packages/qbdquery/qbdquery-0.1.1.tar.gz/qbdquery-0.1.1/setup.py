from setuptools import setup, find_packages

setup(
    name="qbdquery",
    version="0.1.1",
    packages=find_packages(exclude=["tests*", "venv*"]),
    install_requires=[
        "pywin32>=306",
    ],
    python_requires=">=3.7",
)
