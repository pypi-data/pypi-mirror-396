# -*- coding: utf-8 -*-
"""Filter an entry of the RSS feeds"""

# standard library imports
import sys


class FilterEntry:
    """FilterEntry class"""

    def __init__(self, elements, entry, options, byrsspatterns, rssobject, feedname):
        """Constructor of the FilterEntry class"""
        self.matching = {}
        self.entry = entry
        self.elements = elements
        self.options = options
        self.byrsspatterns = byrsspatterns
        self.rssobject = rssobject
        self.feedname = feedname
        self.main()

    def main(self):
        """Main of the FilterEntry class"""
        authorized_elements = [
            "feedname",
        ]
        authorized_elements.extend(self.entry.keys())
        for i in self.elements:
            if i not in authorized_elements:
                sys.exit(
                    "The element {} is not available in the RSS feed. The available ones are: {}".format(
                        i, [j for j in self.entry]
                    )
                )
            # for the case if no pattern at all is defined
            if i == "feedname":
                self.matching[i] = self.feedname
            elif (
                not self.options["patterns"]
                and not self.byrsspatterns
                and not self.rssobject
            ):
                self.matching[i] = self.entry[i]
            # global filter only
            elif (
                self.options["patterns"]
                and not self.byrsspatterns
                and not self.rssobject
            ):
                if not self.options["nopatternurinoglobalpattern"]:
                    self.applyglobalfilter(i)
                else:
                    self.matching[i] = self.entry[i]
            # global filter and then by rss filter
            elif self.options["patterns"] and self.byrsspatterns and self.rssobject:
                # patterns by rss
                self.applyglobalfilter(i)
                self.applyspecificfilter(i)
            elif not self.options["patterns"] and self.byrsspatterns and self.rssobject:
                self.applyspecificfilter(i)
            else:
                self.matching[i] = self.entry[i]

    def applyglobalfilter(self, i):
        """Apply the global filter"""
        for patternlist in self.options["patterns"]:
            if not self.options["patternscasesensitive"][
                "{}_case_sensitive".format(patternlist)
            ]:
                # not case sensitive, so we compare the lower case
                for pattern in self.options["patterns"][patternlist]:
                    finalpattern = pattern.lower()
                    finaltitle = self.entry[patternlist.split("_")[0]].lower()
                    if finalpattern in finaltitle:
                        self.matching[i] = self.entry[i]
            else:
                # case sensitive, so we use the user-defined pattern
                for pattern in self.options["patterns"][patternlist]:
                    if pattern in self.entry["title"]:
                        self.matching[i] = self.entry[i]

    def applyspecificfilter(self, i):
        """Apply specific filters for by-rss pattern matching"""
        for byrsspattern in self.byrsspatterns:
            byrssfinalpattern = byrsspattern.lower()
            if byrssfinalpattern in self.entry[self.rssobject].lower():
                self.matching[i] = self.entry[i]

    @property
    def finalentry(self):
        """Return the processed entry"""
        return self.matching
