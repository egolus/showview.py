"""
tests for showview
"""

import sys
import shutil
import tempfile
from unittest import TestCase
from unittest.mock import patch, call
import xml.etree.ElementTree as ET

from showview import ShowView, main

TESTXML = './test.xml'


class SimpleTestCase(TestCase):
    """
    this test case opens the xml file directly. Don't write with this test
    case!
    """
    def setUp(self):
        """ open the xmlfile directly """
        self.showview = ShowView(TESTXML)


class TestCaseWithTempDir(TestCase):
    """
    this test case copies the xml file to a tempfolder and cleans up after the
    tests. So changes to the xml file are fine.
    """

    def setUp(self):
        """ copy xml to a tempfolder so we can change it """
        self.tempfolder = tempfile.mkdtemp()
        self.tmpxml = shutil.copy(TESTXML, self.tempfolder)

        self.showview = ShowView(self.tmpxml)

    def tearDown(self):
        """clean up the tempfolder """
        shutil.rmtree(self.tempfolder)


class TestSingleShow(SimpleTestCase):
    """ tests the basic behaviors """

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


class TestAllShows(SimpleTestCase):
    """ tests the basic behaviors """

    def test_return_all_shows(self):
        """ get all shows from the xml file """

        self.assertEqual(list(self.showview.get_shows()),
                         [{"name": "test1", "season": 1, "episode": 1},
                          {"name": "test2", "season": 10, "episode": 10}])

    def test_return_all_shows_with_partial_name(self):
        """
        get a partial list of shows (containing 1 show) from the xml file
        """

        self.assertEqual(list(self.showview.get_shows('test1')),
                         [{"name": "test1", "season": 1, "episode": 1}])

    def test_return_empty_list(self):
        """ get an empty list because we entered a non-existing name """

        self.assertEqual(list(self.showview.get_shows('test_not_present')), [])


class TestChangeShow(SimpleTestCase):
    """ test the basic behavior to change a show """

    def test_change_episode(self):
        """ get one show and change the episode """

        self.showchange = self.showview.get_show('test1')
        self.showchange['episode'] = 2
        self.showview.set_show(self.showchange)
        self.assertEqual(self.showview.get_show('test1'),
                         {"name": "test1", "season": 1, "episode": 2})

    def test_change_episode_0(self):
        """ set the episode to zero """

        self.showchange = self.showview.get_show('test1')
        self.showchange['episode'] = 0
        self.showview.set_show(self.showchange)
        self.assertEqual(self.showview.get_show('test1'),
                         {"name": "test1", "season": 1, "episode": 0})

    def test_change_season(self):
        """ get one show and change the season """

        self.showchange = self.showview.get_show('test1')
        self.showchange['season'] = 5
        self.showview.set_show(self.showchange)
        self.assertEqual(self.showview.get_show('test1'),
                         {"name": "test1", "season": 5, "episode": 1})

    def test_change_season_0(self):
        """ set the season to zero """

        self.showchange = self.showview.get_show('test1')
        self.showchange['season'] = 0
        self.showview.set_show(self.showchange)
        self.assertEqual(self.showview.get_show('test1'),
                         {"name": "test1", "season": 0, "episode": 1})

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


class TestInsertShow(SimpleTestCase):
    """ test the insert function """

    def test_insert_show(self):
        """ insert a new show """

        shows = list(self.showview.get_shows())
        show = self.showview.add_show(name='test0')
        shows.append(show)
        shows.sort(key=lambda x: x["name"])
        print(shows)
        shows_new = list(self.showview.get_shows())
        print(shows_new)
        print(ET.tostring(self.showview.root))
        self.assertEqual(shows, shows_new)


class TestWrite(TestCaseWithTempDir):
    """ test the writing to a file """

    def test_write_xml_file(self):
        """ do a change and write the xmlfile """

        with open(self.tmpxml, 'r') as file:
            xml_before = file.readlines()

        show = self.showview.get_show('test1')
        show['episode'] += 1
        self.showview.set_show(show)
        self.showview.write_shows()
        xml_expected = ET.tostring(self.showview.root).decode()
        with open(self.tmpxml, 'r') as file:
            xml_after = ''.join(file.readlines())

        self.assertNotEqual(xml_before, xml_after)

        self.assertEqual(xml_expected, xml_after)


class TestMain(SimpleTestCase):
    """ test the main function print statements """

    def setUp(self):
        super().setUp()
        sys.argv = ['showview.py', '--showfile', TESTXML]

    @patch('builtins.print')
    def test_main_without_show(self, mock_print):
        """ should return every show from the xml file """
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test2                                    10 - 10')]

        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_with_show(self, mock_print):
        """ should return one show from the xml file """
        sys.argv.append('test1')
        main()
        mock_print.assert_called_with(
            'test1                                     1 -  1')

    @patch('builtins.print')
    def test_main_with_missing_show(self, mock_print):
        """ should return an error string about the missing show """
        sys.argv.append('test_missing')
        main()
        self.assertIsInstance(mock_print.mock_calls[-1][1][0], KeyError)

        self.assertEqual(str(mock_print.mock_calls[-1][1][0]),
            str(KeyError("No show found for name 'test_missing'")))


class TestMainWrite(TestCaseWithTempDir):
    """ test the main functions that change the xml file """

    def setUp(self):
        super().setUp()
        sys.argv = ['showview.py', '--showfile', self.tmpxml]

    @patch('builtins.print')
    def test_main_incEpisode(self, mock_print):
        """ should increase the episode by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('--incepisode')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                     1 -  2')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_incEpisodeShort(self, mock_print):
        """ should increase the episode by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('-ie')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                     1 -  2')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_decEpisode(self, mock_print):
        """ should increase the episode by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('--decepisode')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                     1 -  0')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_decEpisodeShort(self, mock_print):
        """ should increase the episode by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('-de')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                     1 -  0')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_incSeason(self, mock_print):
        """ should increase the season by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('--incseason')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                     2 -  1')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_incSeasonShort(self, mock_print):
        """ should increase the season by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('-is')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                     2 -  1')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_decSeason(self, mock_print):
        """ should increase the season by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('--decseason')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                     0 -  1')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_decSeasonShort(self, mock_print):
        """ should increase the season by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('-ds')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                     0 -  1')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_setEpisode(self, mock_print):
        """ should increase the episode by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('--setepisode')
        sys.argv.append('10')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                     1 - 10')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_setEpisodeShort(self, mock_print):
        """ should increase the episode by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('-se')
        sys.argv.append('10')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                     1 - 10')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_setSeason(self, mock_print):
        """ should increase the season by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('--setseason')
        sys.argv.append('10')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                    10 -  1')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_setSeasonShort(self, mock_print):
        """ should increase the season by 1 """
        sys.argv.append('test1')
        main()
        sys.argv.append('-ss')
        sys.argv.append('10')
        main()
        expected = [call('test1                                     1 -  1'),
                    call('test1                                    10 -  1')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_names(self, mock_print):
        """ should print all names """
        sys.argv.append('-n')
        main()
        expected = [call('test1'),
                    call('test2')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_one_name(self, mock_print):
        """ should print the one name we're looking for """
        sys.argv.append('-n')
        sys.argv.append('test2')
        main()
        expected = [call('test2')]
        self.assertEqual(mock_print.mock_calls, expected)

    @patch('builtins.print')
    def test_main_no_name(self, mock_print):
        """ should not print anything """
        sys.argv.append('-n')
        sys.argv.append('test_not_present')
        main()
        mock_print.assert_not_called()
