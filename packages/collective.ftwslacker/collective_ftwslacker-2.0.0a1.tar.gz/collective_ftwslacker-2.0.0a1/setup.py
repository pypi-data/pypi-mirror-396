from pathlib import Path
from setuptools import setup


version = "2.0.0a1"


long_description = (
    f"{Path('README.md').read_text()}\n" f"{Path('CHANGES.md').read_text()}\n"
)

setup(
    name="collective.ftwslacker",
    version=version,
    description="Uses webhooks to post messages into a slack channel.",
    long_description_content_type="text/markdown",
    long_description=long_description,
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Addon",
        "Framework :: Plone",
        "Framework :: Zope :: 2",
        "Framework :: Zope :: 4",
        "Framework :: Zope",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="ftw slacker slack webhook api",
    author="4teamwork AG",
    author_email="mailto:info@4teamwork.ch",
    url="https://github.com/collective/collective.ftwslacker",
    license="GPL2",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "zope.component",
        "zope.interface",
        "requests",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "zope.configuration",
            "transaction",
        ]
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
