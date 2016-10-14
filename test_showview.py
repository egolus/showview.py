"""
tests for showview
"""

import builtins
import sys
from unittest import TestCase
from unittest.mock import patch, call

from showview import ShowView, main

TESTXML = './test.xml'


def side_effect(arg):
    return arg


class TestSingleShow(TestCase):
    """ tests the basic behaviors """

    def setUp(self):
        self.showview = ShowView(TESTXML)

    def test_return_one_show(self):
        """ get one show from the xml file """

        self.assertEqual(self.showview.get_show('test1'),
                         {"name": "test1", "season": 1, "episode": 1})

    def test_return_one_show2(self):
        """ get another single show from the xml file """

        self.assertEqual(self.showview.get_show('test2'),
                         {"name": "test2", "season": 10, "episode": 10})


class TestAllShows(TestCase):
    """ tests the basic behaviors """

    def setUp(self):
        self.showview = ShowView(TESTXML)

    def test_return_all_shows(self):
        """ get one show from the xml file """

        self.assertEqual(list(self.showview.get_shows()),
                         [{"name": "test1", "season": 1, "episode": 1},
                          {"name": "test2", "season": 10, "episode": 10}])


class TestMain(TestCase):
    """ test the main function print statements """

    def setUp(self):
        self.showview = ShowView(TESTXML)
        sys.argv = ['showview.py', '--showfile', TESTXML]


    @patch('builtins.print')
    def test_main_without_show(self, mock_print):
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test2                                    10 - 10')]

        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print', side_effect=side_effect)
    def test_main_with_show(self, mock_print):
        sys.argv.append('test1')
        main()
        mock_print.assert_called_with('test1                                     1 -  1')
