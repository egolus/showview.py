#!/usr/bin/python
"""
showview.py

a tool to keep track of the shows you're watching
"""

# TODO: put _ in front of private variables (self.tree, self.root)

import argparse
import xml.etree.ElementTree as ET

SOURCE = '/mnt/sda4/_Daten/showview/show.xml'


def indent(elem, level=0):
    """ pretty print an xml tree """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class ShowView():
    """
    the shows you're watching
    """

    def __init__(self, sourcefile=SOURCE):
        """ reads the xml file """

        self.sourcefile = sourcefile
        self.tree = ET.parse(sourcefile)
        self.root = self.tree.getroot()

    def get_shows(self, name=None):
        """ returns all shows """

        for show in self.root.findall('Show'):
            if (not name) or (show.find('Name').text.startswith(name)):
                yield {"name": show.find('Name').text,
                       "season": int(show.find('Season').text),
                       "episode": int(show.find('Episode').text)}

    def get_show(self, name):
        """ returns one show found by its name """

        show = None
        for _show in self.root.findall('Show'):
            if _show.find('Name').text.startswith(name):
                show = _show
                break
        else:
            raise KeyError("No show found for name '{}'".format(name))

        return {"name": show.find('Name').text,
                "season": int(show.find('Season').text),
                "episode": int(show.find('Episode').text)}

    def add_show(self,
                 show=None,
                 name=None,
                 season=None,
                 episode=None):
        """
        create a show entry and insert it at the right position
        (alphabetically)
        """

        if not (show or name):
            raise LookupError("Name or show must be set")

        if not show:
            show = dict()

        if name:
            show['name'] = name
        if season:
            show['season'] = season
        else:
            show['season'] = 0
        if episode:
            show['episode'] = episode
        else:
            show['episode'] = 0

        show_element = ET.Element('Show')
        name_element = ET.SubElement(show_element, 'Name')
        name_element.text = str(show['name'])
        season_element = ET.SubElement(show_element, 'Season')
        season_element.text = str(show['season'])
        episode_element = ET.SubElement(show_element, 'Episode')
        episode_element.text = str(show['episode'])

        shownames = [show['name'] for show in self.get_shows()]
        shownames.append(show['name'])
        insert_index = sorted(shownames).index(show['name'])
        self.root.insert(insert_index, show_element)

        return show

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

        if name is not None:
            show['name'] = name
        if season is not None:
            show['season'] = season
        if episode is not None:
            show['episode'] = episode
        if new_name is not None:
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

        indent(self.root)
        self.tree = ET.ElementTree(self.root)
        self.tree.write(self.sourcefile)


def main():
    """ this function gets called from the commandline """

    ap = argparse.ArgumentParser()
    ap.add_argument('-n', '--name',
                    action='store_true',
                    help='return the name(s) of the show(s) and exit')
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
    ap.add_argument('-se', '--setepisode',
                    help='set the new episode value',
                    metavar='INTEGER')
    ap.add_argument('-ss', '--setseason',
                    help='set the new season value',
                    metavar='INTEGER')
    ap.add_argument('-as', '--addshow',
                    action='store_true',
                    help='add a new show with '
                    '{name=SHOW, season=0, episode=0}')
    ap.add_argument('--showfile',
                    default=SOURCE,
                    help='the xmlfile with the shows')
    ap.add_argument('show',
                    nargs='?',
                    help='select a single show (or the name for --addshow)',
                    metavar='SHOW')
    args = ap.parse_args()

    showview = ShowView(args.showfile)

    try:
        if args.name:
            for show in showview.get_shows(args.show):
                print(show["name"])
            return

        if args.show:

            if args.addshow:
                show = showview.add_show(name=args.show)
                showview.write_shows()
            else:
                show = showview.get_show(args.show)

            if args.setepisode:
                show['episode'] = args.setepisode
                showview.set_show(show)
                showview.write_shows()
            if args.setseason:
                show['season'] = args.setseason
                showview.set_show(show)
                showview.write_shows()
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
