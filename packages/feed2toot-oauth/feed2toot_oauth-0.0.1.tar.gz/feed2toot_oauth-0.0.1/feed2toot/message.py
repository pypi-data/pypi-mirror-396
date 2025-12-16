# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Build the message"""

# standard libraires imports
import logging

# external liraries imports
from bs4 import BeautifulSoup

# app libraries imports
from feed2toot.addtags import AddTags
from feed2toot.removeduplicates import RemoveDuplicates
from feed2toot.tootpost import TootPost


def build_message(entrytosend, tweetformat, rss, tootmaxlen, notagsintoot):
    """populate the rss dict with the new entry"""
    tweetwithnotag = tweetformat.format(**entrytosend)
    # replace line breaks
    tootwithlinebreaks = tweetwithnotag.replace("\\n", "\n")
    # remove duplicates from the final tweet
    dedup = RemoveDuplicates(tootwithlinebreaks)
    # only add tags if user wants to
    if not notagsintoot:
        # only append hashtags if they exist
        # remove last tags if tweet too long
        if "hashtags" in rss:
            addtag = AddTags(dedup.finaltweet, rss["hashtags"])
            finaltweet = addtag.finaltweet
        else:
            finaltweet = dedup.finaltweet
    else:
        finaltweet = dedup.finaltweet
    # strip html tags
    finaltweet = BeautifulSoup(finaltweet, "html.parser").get_text()
    # truncate toot to user-defined value whatever the content is
    if len(finaltweet) > tootmaxlen:
        finaltweet = finaltweet[0 : tootmaxlen - 1]
        return "".join([finaltweet[0:-3], "..."])
    else:
        return finaltweet


def send_message_dry_run(config, entrytosend, finaltweet):
    """simulate sending message using dry run mode"""
    if entrytosend:
        logging.warning(
            'Would toot with visibility "{visibility}": {toot}'.format(
                toot=finaltweet,
                visibility=config.get("mastodon", "toot_visibility", fallback="public"),
            )
        )
    else:
        logging.debug(
            "This rss entry did not meet pattern criteria. Should have not been sent"
        )


def send_message(config, clioptions, options, entrytosend, finaltweet, cache, rss):
    """send message"""
    storeit = True
    if entrytosend and not clioptions.populate:
        logging.debug(
            'Tooting with visibility "{visibility}": {toot}'.format(
                toot=finaltweet,
                visibility=config.get("mastodon", "toot_visibility", fallback="public"),
            )
        )
        twp = TootPost(config, options, finaltweet)
        storeit = twp.storeit()
    else:
        logging.debug("populating RSS entry {}".format(rss["id"]))
    # in both cas we store the id of the sent tweet
    if storeit:
        cache.append(rss["id"])
