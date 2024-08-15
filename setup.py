from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in das_gdrive/__init__.py
from das_gdrive import __version__ as version

setup(
	name="das_gdrive",
	version=version,
	description="DAS Google Drive",
	author="DAS",
	author_email="DAS",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
