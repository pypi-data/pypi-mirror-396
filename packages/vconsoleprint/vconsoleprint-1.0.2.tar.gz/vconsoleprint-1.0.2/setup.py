from setuptools import setup, find_packages

setup(
    name="vconsoleprint",          # PyPI package name
    version="1.0.2",              # Increment version for updates
    packages=find_packages(),     # Automatically finds 'vconsoleprint'
    install_requires=[
        "termcolor"
    ],
    author="Vansh Sharma",
    author_email="vanshsharma7832@gmail.com",
    description="Auto-colored Python console print replacement",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/vconsoleprint/",
    license="MIT",
    python_requires=">=3.6",
)
