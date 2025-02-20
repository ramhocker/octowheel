#!/bin/env python3

import requests
import bs4

PLACE          = 'Place'
PERSON         = 'Person'
THING          = 'Thing'
LANDMARK       = 'Landmark'
PHRASE         = 'Phrase'
THINGS         = 'Things'
TITLE          = 'Title'
PEOPLE         = 'People'
EVENT          = 'Event'
FICTION_PERSON = 'Fiction Person'
SAME_NAME      = 'Same Name'

# FIXME: We should get rid of this dict. Provide a script to scrape the puzzles
#        and at the same time replace the categories.
CLEAN_CATS = {
    u'Star & Role': PERSON,
    u'Proper Name': PERSON,
    u'On the Map': LANDMARK,
    u'Title': TITLE,
    u'Things': THING,
    u'TV Quote': PHRASE,
    u'Character': PERSON,
    u'Family': PERSON,
    u'Song Lyrics': TITLE,
    u'Food & Drink': THING,
    u'\xa0Phrase': PHRASE,
    u'Proper Names': PERSON,
    u'Husband & Wife': PERSON,
    u'Movie Title': TITLE,
    u'Fun & Games': THING,
    u'Living Things': THING,
    u'Events': EVENT,
    u'Same Letter': THING,
    u'Same Name': SAME_NAME,
    u'Movie Quote': PHRASE,
    u'Fictional Place': PLACE,
    u'Person': PERSON,
    u'Next Line Please': PHRASE,
    u'Rhyme Time': PHRASE,
    u'Clue': PHRASE,
    u'Who Is It?': PERSON,
    u'\xa0Thing': THING,
    u'Fictional Character': FICTION_PERSON,
    u'Headline': TITLE,
    u'College Life': THING,
    u'On the Menu': THING,
    u'Living Thing': THING,
    u'Slogan': PHRASE,
    u'Places': PLACE,
    u'Title/Author': TITLE,
    u'Thing': THING,
    u'Before & After': PHRASE,
    u'Place': PLACE,
    u'Around the House': THING,
    u'Phrase': PHRASE,
    u'Phrases': PHRASE,
    u'Who Said It?': PHRASE,
    u'Landmark': LANDMARK,
    u'Landmarks': LANDMARK,
    u'Best Seller': TITLE,
    u'Fictional Character': FICTION_PERSON,
    u'Fictional Characters': FICTION_PERSON,
    u'Characters': PERSON,
    u'In the Kitchen': THING,
    u'Song Title': TITLE,
    u'People': PERSON,
    u'Song/Artist': TITLE,
    u'Fictional Family': FICTION_PERSON,
    u'Classic TV': TITLE,
    u'Slang': PHRASE,
    u'Show Biz': THING,
    u'Quotation': PHRASE,
    u'TV Title': TITLE,
    u'Event': EVENT,
    u'Occupation': PERSON
}

url='https://buyavowel.boards.net/page/compendium%i'

results = {}
unknown_categories = {}

for i in range(1, 42):
    print('Scraping URL', url % i)
    html = requests.get(url % i).text
    soup = bs4.BeautifulSoup(html, features="lxml")
    table = soup.find_all('table')[4]
    for row in table.find_all('tr'):
        cols = row.find_all('td')[:2]
        puzzle = cols[0].text
        category = cols[1].text
        if category not in CLEAN_CATS:
            if category not in unknown_categories:
                unknown_categories[category] = []
            unknown_categories[category].append(puzzle)
            continue
        category = CLEAN_CATS[category]
        if category not in results:
            results[category] = []
        results[category].append(puzzle)

with open('puzzlelist-scraped', 'a') as out:
    for category, puzzles in results.items():
        out.write('\n[' + category + ']\n')
        for puzzle in puzzles:
            out.write(puzzle + '\n')

if unknown_categories:
    with open('puzzlefails', 'w') as fails:
        for category, puzzles in unknown_categories.items():
            print('Unknown category:', category, '('+ str(len(puzzles))+ ' occurrences)')
            fails.write('\n[' + category + ']\n')
            for puzzle in puzzles:
                fails.write(puzzle + '\n')

successful_puzzles = sum([len(puzzles) for puzzles in results.values()])
failed_puzzles = sum([len(puzzles) for puzzles in unknown_categories.values()])
print(successful_puzzles, 'puzzles successfully parsed and written to: puzzlelist-scraped')
print(failed_puzzles, 'puzzles in', len(unknown_categories), 'categories that could not be parsed were written to: puzzlefails')


