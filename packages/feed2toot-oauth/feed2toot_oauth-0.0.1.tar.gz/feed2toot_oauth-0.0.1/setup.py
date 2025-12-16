"""Setup for Feed2toot"""

from setuptools import setup, find_packages

CLASSIFIERS = [
    "Intended Audience :: End Users/Desktop",
    "Environment :: Console",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
]

setup(
    name="feed2toot-oauth",
    version="0.0.1",
    license="MIT",
    description="Parse rss feeds and send new posts to Mastodon-likes",
    long_description="Parse rss feeds and send new posts to the Mastodon-like social networks",
    author="theelous3",
    author_email="thee_grandmaster@hotmail.com",
    url="https://github.com/theelous3/feed2toot-oauth",
    classifiers=CLASSIFIERS,
    download_url="https://github.com/theelous3/feed2toot-oauth",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "feed2toot=feed2toot.cli:main",
            "feed2toot-register-app=feed2toot.register_app:main",
        ]
    },
    install_requires=["beautifulsoup4", "feedparser", "Mastodon.py"],
    extras_require={"influxdb": ["influxdb"]},
)
