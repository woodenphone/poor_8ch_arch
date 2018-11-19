#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     19-11-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StdLib
import time
import os
import logging
import logging.handlers
import unittest
# Remote libraries
# local
import common
import grab_board_py8ch



class Test_please_utf(unittest.testcase):
    """Tests for grab_board_py8ch.py please_utf()"""
    def test_none(self):
        expected = None
        actual = grab_board_py8ch.please_utf(None)
        self.assertEqual(actual, expected)

    def test_empty_str(self):
        expected = u''
        actual = grab_board_py8ch.please_utf('')
        self.assertEqual(actual, expected)

    def test_empty_unicode(self):
        expected = u''
        actual = grab_board_py8ch.please_utf(u'')
        self.assertEqual(actual, expected)



def main():
    pass

if __name__ == '__main__':
    main()
