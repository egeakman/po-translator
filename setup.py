from setuptools import find_packages, setup

version = "0.1.0"

# with open("README.md", "r", encoding="utf-8") as f:
#     long_description = f.read()
long_description = "to-be-added"


setup(
    name="po-translator",
    author="egeakman",
    author_email="me@egeakman.dev",
    url="to-be-added",
    description="to-be-added",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=version,
    license="MIT",
    download_url="to-be-added",
    packages=find_packages(where="."),
    install_requires=["httpx"],
    python_requires=">=3.10",
    entry_points={"console_scripts": ["po-translator=po_translator.cli:main"]},
    classifiers=[
        "Topic :: Utilities",
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
    keywords=["to-be-added"],
    project_urls={
        "Homepage": "to-be-added",
        "Issues": "to-be-added",
    },
)
