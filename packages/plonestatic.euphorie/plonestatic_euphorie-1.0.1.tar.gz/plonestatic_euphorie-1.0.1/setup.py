from pathlib import Path
from setuptools import find_packages
from setuptools import setup


setup(
    name="plonestatic.euphorie",
    version="1.0.1",
    description="Euphorie Risk Assessment tool static resources",
    long_description="\n".join(
        [
            Path("README.md").read_text(),
            Path("CHANGES.md").read_text(),
            "",
        ]
    ),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="euphorie OiRA Interactive Risk Assessment static resources",
    author="Syslab.com",
    author_email="info@syslab.com",
    url="https://github.com/euphorie/plonestatic.euphorie",
    project_urls={
        "Homepage": "https://github.com/euphorie",
        "Source": "https://github.com/euphorie/plonestatic.euphorie",
        "Issues": "https://github.com/euphorie/plonestatic.euphorie/issues",
    },
    license="GPL",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["plonestatic"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">= 3.9",
    install_requires=[
        "Plone >=6.0",
        "plone.patternslib",
    ],
    tests_require=[
        "plone.app.testing",
    ],
    extras_require={
        "tests": [
            "plone.app.testing",
        ],
    },
    entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
