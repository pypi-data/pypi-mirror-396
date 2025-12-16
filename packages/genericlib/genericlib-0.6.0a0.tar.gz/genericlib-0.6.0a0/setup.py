from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="genericlib",
    version="0.6.0a0",  # alpha versioning
    license="BSD-3-Clause",
    license_files=["LICENSE"],
    description="The Generic Python Library accelerates development with "
                "reusable utilities, supporting regexgenerator and "
                "textfsmgenerator while streamlining workflows, "
                "reducing redundancy, and enabling efficient, adaptable, "
                "maintainable applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tuyen Mathew Duong",
    author_email="tuyen@geekstrident.com",
    maintainer="Tuyen Mathew Duong",
    maintainer_email="tuyen@geekstrident.com",
    install_requires=[
        "pyyaml",
    ],
    url="https://github.com/Geeks-Trident-LLC/genericlib",
    packages=find_packages(
        exclude=(
            "tests*", "testing*", "examples*",
            "build*", "dist*", "docs*", "venv*"
        )
    ),
    project_urls={
        "Documentation": "https://github.com/Geeks-Trident-LLC/genericlib/wiki",
        "Source": "https://github.com/Geeks-Trident-LLC/genericlib",
        "Tracker": "https://github.com/Geeks-Trident-LLC/genericlib/issues",
    },
    include_package_data=True,
    classifiers=[
        # development status
        "Development Status :: 3 - Alpha",
        # natural language
        "Natural Language :: English",
        # intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",
        # operating system
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        # programming language
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        # topic
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Processing",
    ],
)
