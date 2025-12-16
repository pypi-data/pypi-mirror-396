"""Doc tests"""

import doctest
import re
import unittest

import six
from plone.testing import layered

from eea.stringinterp.tests.base import FUNCTIONAL_TESTING

OPTIONFLAGS = (
    doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
)


class Py23DocChecker(doctest.OutputChecker):
    """Cross-Python checker"""

    def check_output(self, want, got, optionflags):
        if six.PY2:
            got = re.sub("u'(.*?)'", "'\\1'", got)
            got = re.sub(' encoding="utf-8"', "", got)
            # want = re.sub("b'(.*?)'", "'\\1'", want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    """Suite"""
    suite = unittest.TestSuite()
    suite.addTests(
        [
            layered(
                doctest.DocFileSuite(
                    "adapters/__init__.py",
                    optionflags=OPTIONFLAGS,
                    checker=Py23DocChecker(),
                    package="eea.stringinterp",
                ),
                layer=FUNCTIONAL_TESTING,
            ),
        ]
    )

    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
