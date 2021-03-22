import formatter
import requests
import argparse
import colorama
import os
import csv
from bs4 import BeautifulSoup as soup


def conn(uname):
    with requests.get(f'https://github.com/{uname}?tab=repositories') as response:
        response.raise_for_status()
        page_soup = soup(response.text, 'html.parser')

    for repo in page_soup.findAll('a', {'itemprop': 'name codeRepository'}):
        print(repo.text)


if __name__ == '__main__':
    colorama.init()

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description="Clones all Public Repositories from Github Users.")

    parser.add_argument('username',
                        nargs='+', metavar='USERNAMES',
                        action='store',
                        help="Clones repositories from user/s. (e.g KungPaoChick uname2 uname3)")

    args = parser.parse_args()

    for name in args.username:
        conn(name)
