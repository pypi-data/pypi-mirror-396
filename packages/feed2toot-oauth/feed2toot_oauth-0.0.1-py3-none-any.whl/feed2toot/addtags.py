#!/usr/bin/env python3
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Add as many tags as possible depending on the tweet length"""

# standard library imports
from operator import itemgetter


class AddTags:
    """Add as many tags as possible depending on the tweet length"""

    def __init__(self, tweet, tags):
        """Constructor of AddTags class"""
        self.tags = tags
        self.tweet = tweet
        self.main()

    def main(self):
        """Main of the AddTags class class"""
        maxlength = 500
        tweetlength = len(self.tweet)

        # sort list of tags, the ones with the greater length first
        tagswithindices = ({"text": i, "length": len(i)} for i in self.tags)
        sortedtagswithindices = sorted(
            tagswithindices, key=itemgetter("length"), reverse=True
        )
        self.tags = (i["text"] for i in sortedtagswithindices)

        # add tags is space is available
        for tag in self.tags:
            taglength = len(tag)
            if (tweetlength + (taglength + 1)) <= maxlength:
                self.tweet = " ".join([self.tweet, tag])
                tweetlength += taglength + 1

    @property
    def finaltweet(self):
        """return the final tweet with as many tags as possible"""
        return self.tweet
