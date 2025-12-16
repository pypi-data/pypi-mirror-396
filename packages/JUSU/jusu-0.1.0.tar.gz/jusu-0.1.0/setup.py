from setuptools import setup, find_packages

setup(
	name="JUSU",
	version="0.1.0",
	author="Francis Jusu",
	author_email="jusufrancis08@gmail.com",
	description="Build HTML pages in Python — simple, readable, and beginner-friendly.",
	long_description=open("README.md").read(),
	long_description_content_type="text/markdown",
	url="https://github.com/Francis589-png/earthplus",  # Update if JUSU gets its own repo
	packages=find_packages(),
	python_requires=">=3.10",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)
