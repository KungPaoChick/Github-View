import requests
import argparse
import colorama
import os
import csv
import pandas as pd
from bs4 import BeautifulSoup as soup


def repos(username, links):
    with open(os.path.join(name, f'{username}.csv'), 'w', encoding='utf-8') as f:
        headers = ['Link', 'Repository', 'Commits',
                   'Stars', 'Forks', 'Contributors']
        writer = csv.writer(f, dialect='excel')

        writer.writerow(headers)
        print(colorama.Fore.YELLOW,
              f'[!] {name} has {len(links)} Public Repositor{plural_ies(len(links))}\n',
              colorama.Style.RESET_ALL)
        for link in links:
            try:
                with requests.get(link) as rep_response:
                    rep_response.raise_for_status()
                    rep_soup = soup(rep_response.text, 'html.parser')

                my_data = [link]
                # gets repo name
                for repo_name in rep_soup.findAll('a', {'data-pjax': '#js-repo-pjax-container'}):
                    print(colorama.Fore.GREEN,
                          f'[*] {repo_name.text}', colorama.Style.RESET_ALL)
                    my_data.append(repo_name.text)
                    if args.clone:
                        os.system(f'git clone {link}.git ~/Documents/{repo_name.text}')

                # gets number of commits to the repository
                my_data.append([x.text.split() for x in rep_soup.findAll(
                    'ul', {'class': 'list-style-none d-flex'})][0].pop(0))

                # gets description of the repository
                with open(os.path.join(name, f'{repo_name.text}.txt'), 'w') as repo_des:
                    abouts = {'None': [x.text for x in rep_soup.findAll('div', {'class': 'f4 mt-3 color-text-secondary text-italic'})],
                              'About': [x.text for x in rep_soup.findAll('p', {'class': 'f4 mt-3'})]}
                    if abouts['About'] == []:
                        os.remove(os.path.join(name, f'{repo_name.text}.txt'))
                    else:
                        for info in abouts['About']:
                            repo_des.write(info)

                # gets star count
                my_data.append([star.text.split() for star in rep_soup.findAll(
                    'a', {'href': f'{link.split(url)[1]}/stargazers'})].pop(0)[0])

                # gets fork count
                my_data.append([fork.text.split() for fork in rep_soup.findAll(
                    'a', {'href': f'{link.split(url)[1]}/network/members'})].pop(0)[0])

                con = []
                for contributor in [x['title'] for x in rep_soup.findAll('span', {'class': 'Counter'})]:
                    con.append(contributor)

                if int(con[-1]) == 0:
                    my_data.append(1)
                else:
                    my_data.append(con[-1])
                writer.writerows([my_data])
            except requests.HTTPError as err:
                print(colorama.Fore.RED,
                    f'[!!] Something went wrong! {err}',
                    colorama.Style.RESET_ALL)

    return read_data(os.path.join(os.getcwd(), name), f'{username}.csv')


def read_data(path, filename):
    df = pd.read_csv(os.path.join(path, filename))
    pd.set_option('display.max_rows', None)
    df.drop(['Link'], axis=1, inplace=True)
    print(f'"{filename}" Data Frame:\n\n{df}')


def plural_ies(v):
    return 'ies' if not abs(v) == 1 else 'y'


def conn(uname, main_url):
    try:
        with requests.get(f'{main_url}/{uname}?tab=repositories') as response:
            response.raise_for_status()
            page_soup = soup(response.text, 'html.parser')

            links = []
            for repo in page_soup.findAll('a', {'itemprop': 'name codeRepository'}):
                links.append(f"{main_url}{repo['href']}")

            for name in page_soup.findAll('span', {'itemprop': 'name'}):
                return repos(''.join(name.text.split()), links)
    except requests.HTTPError as err:
        print(colorama.Fore.RED,
            f'[!!] Something went wrong! {err}',
            colorama.Style.RESET_ALL)


if __name__ == '__main__':
    colorama.init()
    url = 'https://github.com'
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description="Views Public Repositories of Users")

    parser.add_argument('-c', '--clone', nargs='+',
                        metavar='CLONE', action='store',
                        help="Clones and Views Public Repositories from the user/s. (e.g -c KungPaoChick uname2 uname3)")

    parser.add_argument('-u', '--username',
                        nargs='+', metavar='USERNAMES',
                        action='store',
                        help="Views Public Repositories from the user/s. (e.g -u KungPaoChick uname2 uname3)")

    args = parser.parse_args()
    if args.clone or args.username:
        for name in args.username or args.clone:
            if not os.path.exists(name):
                os.mkdir(name)
            conn(name, url)

