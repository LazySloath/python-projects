# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 00:22:26 2018

@author: User

This is a chordsheet generator. It scrapes ultimateguitar for chords, puts it
into a word document.

bold chords or not?
UI to be implemented
Transposing to be implemented?
[A, A#, B, C, C#, D, D#, E, F, F#, G, G#, A]
"""

import requests, bs4, docx

def soupify(link):
    """Create BeautifulSoup object from a link"""
    
    res = requests.get(link)
    res.raise_for_status
    return bs4.BeautifulSoup(res.text, 'lxml')

def song_search(title):
    """Search for song on ultimateguitar and return chords from top hit"""
    
    ugsearch = ('https://www.ultimate-guitar.com/search.php?'
    'search_type=title&order=&value=' + title)
    ugsoup = soupify(ugsearch)
    # Get list 'hits' of search results
    hits = ugsoup.select('.search-version--link > a')
    for hit in hits:
        href = hit.get('href')
        soup = soupify(href)
        content = soup.select('.js-tab-content')
        if len(content) == 1:
            return content[0].getText()
    # If no chords found
    print('No chords found!')

def add_chords():
    """Add chords to the docx"""
    
    title = input('Please enter the song title: ')
    chords = song_search(title)
    if chords != None:
        # Add title on docx
        p = chordsheet.add_paragraph('')
        # Title bold and underline
        p.add_run(title.upper()).bold = True
        p.runs[0].underline = True
        # Add chords
        chordsheet.add_paragraph(chords)
        # Add newline after chords
        print('Chords added!')
    
# Initialise the chordsheet
chordsheet = docx.Document()
# Set 2 columns
section = chordsheet.sections[0]
cols = section._sectPr.xpath('./w:cols')[0]
cols.set(docx.oxml.ns.qn('w:num'),'2')
# Create document style
style = chordsheet.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = docx.shared.Pt(11)
# Let user get chords as required
while True:
    reply = input('Enter "y" to search for chords or "n" to exit: ')
    if reply.lower() == 'y':
        add_chords()
    elif reply.lower() == 'n':
        break
# Save the chordsheet
chordsheet.save('chordsheet.docx')
print('Chords saved!')
