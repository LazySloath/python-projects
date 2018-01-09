# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 13:11:27 2018

@author: User

Improved version of chordsheet generator with a GUI
"""

import tkinter, requests, bs4, docx
import tkinter.filedialog

class ChordSearch(tkinter.Tk):
    # Parent is its container
    def __init__(self, parent):
        tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initialise()
        
    def initialise(self):
        self.state = 0
        self.grid()
        # Set window size
        self.geometry("410x85")
        # Set window icon
        self.wm_iconbitmap('chordsearch.ico')
        self.entryVariable = tkinter.StringVar()
        # Entry field for song titles
        self.entry = tkinter.Entry(self, textvariable = self.entryVariable)
        self.entry.grid(column = 0, row = 2, columnspan = 2, sticky = 'EW')
        self.entryVariable.set('Song title here')
        # Hook enter so that OnPressEnter occurs when enter is pressed
        self.entry.bind('<Return>', self.OnPressEnter)
        
        # Save button
        button = tkinter.Button(self, text = 'Save', 
                                command = self.OnButtonClick)
        button.grid(column = 1, row = 3)
        
        # Label for instructions
        instruction = tkinter.Label(self, anchor = 'w', fg = 'white',
                                    bg = 'black', text = 'Enter a song title '
                                    + 'to search for chords or press the '
                                    + '"Save" button when done.')
        instruction.grid(column = 0, row = 0, columnspan = 2, sticky = 'EW')
        # Label for status
        self.labelVariable = tkinter.StringVar()
        label = tkinter.Label(self, textvariable = self.labelVariable,
                              anchor = 'w', fg = 'white', bg = 'grey')
        label.grid(column = 0, row = 1, columnspan = 2, sticky = 'EW')
        # Don't allow grid to resize
        self.grid_columnconfigure(0, weight = 1)
        self.resizable(False, False)
        # Don't allow auto grow and shrink for window
        self.update()
        self.geometry(self.geometry())
            
    def OnPressEnter(self, event):
        # Get song title from entry field
        title = self.entryVariable.get()
        chords = song_search(title)
        # No chords found
        if chords == None:
            self.labelVariable.set('No chords found for ' + title + '!')
        # Chords found
        else:
            add_chords(title, chords)
            self.labelVariable.set('Chords added for ' + title + '!')
        # Auto keyboard focus on entry field
        self.entry.focus_set()
        self.entry.selection_range(0, tkinter.END)
        
    def OnButtonClick(self):
        # Get user input for doc name then exit
        self.filepath = tkinter.filedialog.asksaveasfilename()
        app.destroy()


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
        # If chords found
        if len(content) == 1:
            return content[0].getText()

def add_chords(title, chords):
    """Add chords to the docx"""
    
    # Add title on docx
    p = chordsheet.add_paragraph('')
    # Title bold and underline
    p.add_run(title.upper()).bold = True
    p.runs[0].underline = True
    # Add chords
    chordsheet.add_paragraph(chords)


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
# Run GUI to let user get chords as required    
app = ChordSearch(None)
app.title('chordsearch')
app.mainloop()
# Save the chordsheet
try:
    if len(app.filepath) > 0:
        chordsheet.save(app.filepath + '.docx')
        print('Chords saved!')
except AttributeError:
    pass