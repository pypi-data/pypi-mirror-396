#!/usr/bin/env python
# encoding: utf-8
"""Extended dollarReplace.py"""

from AccessControl import Unauthorized
from plone.stringinterp.dollarReplace import Interpolator as PloneInterpolator
from plone.stringinterp.dollarReplace import LazyDict as PloneLazyDict
from plone.stringinterp.interfaces import IStringSubstitution
from zope.component import ComponentLookupError, getAdapter

_marker = "_bad_"


class LazyDict(PloneLazyDict):
    """Lazy dict"""

    def __getitem__(self, key):
        if key and key[0] not in ["_", "."]:
            try:
                res = super(LazyDict, self).__getitem__(key)
            except KeyError:
                try:
                    # Use generic, IStringSubstitution adapter
                    res = getAdapter(self.context, IStringSubstitution)(key=key)
                except ComponentLookupError:
                    res = _marker
                except Unauthorized:
                    res = "Unauthorized"

                self._cache[key] = res

            if res != _marker:
                return res

        raise KeyError(key)


class Interpolator(PloneInterpolator):
    """Custom Interpolator"""

    def __init__(self, context):
        self._ldict = LazyDict(context)
