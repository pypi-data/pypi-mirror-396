from setuptools import setup, find_packages

class postinstall:
    def run(self):
        print("i'm ready")

setup(
    name="byteripper",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "byteripper=byteripper.cli:main",
        ],
    },
)

print("i'm ready")
