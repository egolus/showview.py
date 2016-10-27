#!/usr/bin/python
"""
showview.py

a tool to keep track of the shows you're watching
"""

import argparse
import xml.etree.ElementTree as ET
# import pygtk

SOURCE = '/mnt/sda4/_Daten/showview/show.xml'


class ShowView():
    """
    the shows you're watching
    """

    def __init__(self, sourcefile=SOURCE):
        """ reads the xml file """

        self.sourcefile = sourcefile
        self.tree = ET.parse(sourcefile)
        self.root = self.tree.getroot()

    def get_shows(self):
        """ returns all shows """

        for show in self.root.findall('Show'):
            yield {"name": show.find('Name').text,
                   "season": int(show.find('Season').text),
                   "episode": int(show.find('Episode').text)}

    def get_show(self, name):
        """ returns one show found by its name """

        show = None
        for _show in self.root.findall('Show'):
            if _show.find('Name').text == name:
                show = _show
                break
        else:
            raise KeyError("No show found for name '{}'".format(name))

        return {"name": show.find('Name').text,
                "season": int(show.find('Season').text),
                "episode": int(show.find('Episode').text)}

    def set_show(self,
                 show=None,
                 name=None,
                 season=None,
                 episode=None,
                 new_name=None):
        """ update a show with new values """

        if not (show or name):
            raise LookupError("Name or show must be set")

        if not show:
            show = dict()

        if name:
            show['name'] = name
        if season:
            show['season'] = season
        if episode:
            show['episode'] = episode
        if new_name:
            show['new_name'] = new_name

        for _show in self.root.findall('Show'):
            if _show.find('Name').text == show['name']:
                if 'new_name' in show:
                    _show.find('Name').text = str(show['new_name'])
                if 'season' in show:
                    _show.find('Season').text = str(show['season'])
                if 'episode' in show:
                    _show.find('Episode').text = str(show['episode'])

    def write_shows(self):
        """ write the xml back to the file """

        self.tree.write(self.sourcefile)


def main():
    """ this function gets called from the commandline """

    ap = argparse.ArgumentParser()
    ap.add_argument('-ie', '--incepisode',
                    action='store_true',
                    help='increase the episode by one')
    ap.add_argument('-is', '--incseason',
                    action='store_true',
                    help='increase the season by one')
    ap.add_argument('-de', '--decepisode',
                    action='store_true',
                    help='increase the episode by one')
    ap.add_argument('-ds', '--decseason',
                    action='store_true',
                    help='increase the season by one')
    ap.add_argument('--showfile',
                    nargs='?',
                    default=SOURCE,
                    help='the xmlfile with the shows')
    ap.add_argument('show',
                    nargs='?',
                    help='select a single show')
    args = ap.parse_args()

    showview = ShowView(args.showfile)

    try:
        if args.show:
            show = showview.get_show(args.show)
            if args.incepisode:
                show['episode'] += 1
                showview.set_show(show)
                showview.write_shows()
            if args.incseason:
                show['season'] += 1
                showview.set_show(show)
                showview.write_shows()
            if args.decepisode:
                show['episode'] -= 1
                showview.set_show(show)
                showview.write_shows()
            if args.decseason:
                show['season'] -= 1
                showview.set_show(show)
                showview.write_shows()
            print("{:40} {:2} - {:2}".format(show["name"],
                                             show["season"],
                                             show["episode"]))
        else:
            for show in showview.get_shows():
                print("{:40} {:2} - {:2}".format(show["name"],
                                                 show["season"],
                                                 show["episode"]))
    except KeyError as e:
        print(e)


if __name__ == '__main__':
    main()
