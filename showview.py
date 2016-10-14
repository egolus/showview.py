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
            raise(Exception("No show found for name '" + name + "'"))

        return {"name": show.find('Name').text,
                "season": int(show.find('Season').text),
                "episode": int(show.find('Episode').text)}


def main():
    """ this function gets called from the commandline """

    ap = argparse.ArgumentParser()
    ap.add_argument('--showfile', nargs='?', help='the xmlfile with the shows')
    ap.add_argument('show', nargs='?', help='select a single show')
    args = ap.parse_args()

    if args.show:
        show = ShowView(args.showfile).get_show(args.show)
        print("{:40} {:2} - {:2}".format(show["name"],
                                         show["season"],
                                         show["episode"]))

    else:
        for show in ShowView(args.showfile).get_shows():
            print("{:40} {:2} - {:2}".format(show["name"],
                                             show["season"],
                                             show["episode"]))


if __name__ == '__main__':
    main()
