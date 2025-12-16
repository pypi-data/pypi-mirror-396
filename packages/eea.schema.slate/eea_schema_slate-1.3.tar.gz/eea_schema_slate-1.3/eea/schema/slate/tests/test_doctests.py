"""Tests"""

import re
import unittest
import doctest
import six


class Py23DocChecker(doctest.OutputChecker):
    """Python2 / Python3 checker"""

    def check_output(self, want, got, optionflags):
        """Check output"""
        if six.PY2:
            got = re.sub(' encoding="utf-8"', "", got)
            want = re.sub("b'(.*?)'", "'\\1'", want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    """Test Suite"""
    return unittest.TestSuite(
        (doctest.DocTestSuite("eea.schema.slate.field", checker=Py23DocChecker()),)
    )
