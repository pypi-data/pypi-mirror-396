import re
from pathlib import Path
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read() 

' read version '
def get_version():
	content = Path("src/edcapi/__init__.py").read_text()
	return re.search(r'__version__ = "([^"]+)"', content).group(1)

setup(
	name='edcapi',
	version=get_version(),
	author='Christian Schwatke',
	author_email='christian.schwatke@tum.de', 
	license="MIT",
	license_files=[], 
	packages=find_packages(where="src"),
	package_dir={"": "src"},
	#~ url='https://gitlab.lrz.de/edc/python3-edcapi',
	description='Eurolas Data Center API (EDC, https://edc.dgfi.tum.de)',
	long_description=long_description,
	long_description_content_type="text/markdown", 
	include_package_data=True,
	package_data={},
	install_requires=[],
	scripts=[
		"bin/edc-uploader",
		"bin/edc-downloader"
	],
	# Project URLs (shown on the PyPI page)
	project_urls={
		"EDC Homepage": "https://edc.dgfi.tum.de/",
		"Documentation": "https://edc-api.readthedocs.io/",
		"Source Code": "https://gitlab.lrz.de/edc/python3-edcapi/",		
	},

	classifiers=[
		"Programming Language :: Python :: 3",
	#	"License :: MIT License",
		"Operating System :: OS Independent",
	],

	python_requires='>=3.8',
)

