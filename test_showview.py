"""
tests for showview
"""

import sys
from unittest import TestCase
from unittest.mock import patch, call

from showview import ShowView, main

TESTXML = './test.xml'


def side_effect(arg):
    """ helper for mock """
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

    def test_missing_show(self):
        """ try to get a show that doesn't exist """

        with self.assertRaises(KeyError):
            self.showview.get_show('NotExisting')


class TestAllShows(TestCase):
    """ tests the basic behaviors """

    def setUp(self):
        self.showview = ShowView(TESTXML)

    def test_return_all_shows(self):
        """ get one show from the xml file """

        self.assertEqual(list(self.showview.get_shows()),
                         [{"name": "test1", "season": 1, "episode": 1},
                          {"name": "test2", "season": 10, "episode": 10}])


class TestChangeShow(TestCase):
    """ test the basic behavior to change a show and write to the file """

    def setUp(self):
        self.showview = ShowView(TESTXML)

    def test_change_episode(self):
        """ get one show and change the episode """

        self.showchange = self.showview.get_show('test1')
        self.showchange['episode'] = 2
        self.showview.set_show(self.showchange)
        self.assertEqual(self.showview.get_show('test1'),
                         {"name": "test1", "season": 1, "episode": 2})

    def test_change_season(self):
        """ get one show and change the season """

        self.showchange = self.showview.get_show('test1')
        self.showchange['season'] = 5
        self.showview.set_show(self.showchange)
        self.assertEqual(self.showview.get_show('test1'),
                         {"name": "test1", "season": 5, "episode": 1})

    def test_change_name(self):
        """ get one show and change the name """

        self.showchange = self.showview.get_show('test1')
        self.showchange['new_name'] = 'test_new'
        self.showview.set_show(self.showchange)
        with self.assertRaises(KeyError):
            self.showview.get_show('test1')
        self.showafter = self.showview.get_show('test_new')
        self.assertEqual(self.showview.get_show('test_new'),
                         {"name": "test_new", "season": 1, "episode": 1})


class TestMain(TestCase):
    """ test the main function print statements """

    def setUp(self):
        self.showview = ShowView(TESTXML)
        sys.argv = ['showview.py', '--showfile', TESTXML]

    @patch('builtins.print')
    def test_main_without_show(self, mock_print):
        """ should return every show from the xml file """
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test2                                    10 - 10')]

        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print', side_effect=side_effect)
    def test_main_with_show(self, mock_print):
        """ should return one show from the xml file """
        sys.argv.append('test1')
        main()
        mock_print.assert_called_with(
            'test1                                     1 -  1')

    # @patch('builtins.print', side_effect=side_effect)
    # def test_main_with_missing_show(self, mock_print):
        # """ should return an error string about the missing show """
        # main()
        # sys.argv.append('test_missing')
        # main()

        # mock_print.assert_called_with(
            # KeyError("No show found for name 'test_missing'"))
