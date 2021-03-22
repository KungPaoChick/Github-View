import requests
import argparse
import colorama
import os
import csv
from bs4 import BeautifulSoup as soup


def repos(username, links):
    with open(os.path.join(name, f'{username}.csv'), 'w', encoding='utf-8') as f:
        headers = ['Link', 'Repository', 'Stars', 'Forks', 'Contributors']
        writer = csv.writer(f, dialect='excel')
        
        writer.writerow(headers)
        print(colorama.Fore.YELLOW,
            f'[!] {name} has {len(links)} Public Repositor{plural_ies(len(links))}\n',
            colorama.Style.RESET_ALL)
        for link in links:
            with requests.get(link) as rep_response:
                rep_response.raise_for_status()
                rep_soup = soup(rep_response.text, 'html.parser')

            my_data = [link]
            # gets repo name
            for repo_name in rep_soup.findAll('a', {'data-pjax':'#js-repo-pjax-container'}):
                print(colorama.Fore.GREEN,
                    f'[*] {repo_name.text}', colorama.Style.RESET_ALL)
                my_data.append(repo_name.text)

            # gets description of the repository
            with open(os.path.join(name, f'{repo_name.text}.txt'), 'w') as repo_des:
                abouts = {'None' : [x.text for x in rep_soup.findAll('div', {'class': 'f4 mt-3 color-text-secondary text-italic'})],
                          'About' : [x.text for x in rep_soup.findAll('p', {'class': 'f4 mt-3'})]}
                if abouts['About'] == []:
                    os.remove(os.path.join(name, f'{repo_name.text}.txt'))
                else:
                    for info in abouts['About']:
                        repo_des.write(info)

            # gets star count
            for star in [x.text.split() for x in rep_soup.findAll('a', {'href': f'{link.split(url)[1]}/stargazers'})].pop(0):
                my_data.append(star)

            # gets fork count
            for fork in [x.text.split() for x in rep_soup.findAll('a', {'href': f'{link.split(url)[1]}/network/members'})].pop(0):
                my_data.append(fork)

            con = []
            for contributor in [x['title'] for x in rep_soup.findAll('span', {'class': 'Counter'})]:
                con.append(contributor)

            if int(con[-1]) == 0:
                my_data.append(1)
            else:
                my_data.append(con[-1])
            writer.writerows([my_data])


def plural_ies(v):
    return 'ies' if not abs(v) == 1 else 'y'


def conn(uname, main_url):
    with requests.get(f'{main_url}/{uname}?tab=repositories') as response:
        response.raise_for_status()
        page_soup = soup(response.text, 'html.parser')

        links = []
        for repo in page_soup.findAll('a', {'itemprop': 'name codeRepository'}):
            links.append(f"{main_url}{repo['href']}")

        for name in page_soup.findAll('span', {'itemprop':'name'}):
            return repos(name.text, links)


if __name__ == '__main__':
    colorama.init()
    url = 'https://github.com'
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description="Clones all Public Repositories from Github Users.")

    parser.add_argument('username',
                        nargs='+', metavar='USERNAMES',
                        action='store',
                        help="Clones repositories from user/s. (e.g KungPaoChick uname2 uname3)")

    args = parser.parse_args()

    for name in args.username:
        if not os.path.exists(name):
            os.mkdir(name)
        conn(name, url)
