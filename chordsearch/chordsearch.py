# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 13:11:27 2018

@author: User

Improved version of chordsheet generator with a GUI
Added transpose function
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
        self.entry.grid(column = 0, row = 2, columnspan = 5, sticky = 'EW')
        self.entryVariable.set('Song title here')
        # Hook enter so that OnPressEnter occurs when enter is pressed
        self.entry.bind('<Return>', self.OnPressEnter)
        # Enter button
        enter = tkinter.Button(self, text = 'Enter', 
                                command = self.OnEnterClick)
        enter.grid(column = 3, row = 3)
        # Save button
        save = tkinter.Button(self, text = 'Save', 
                                command = self.OnSaveClick)
        save.grid(column = 4, row = 3)
        # Up button
        up = tkinter.Button(self, text = '/\\', command = self.OnUpClick)
        up.grid(column = 1, row = 3)
        # Down button
        down = tkinter.Button(self, text = '\\/', command = self.OnDownClick)
        down.grid(column = 2, row = 3)
        # Label for instructions
        self.instructionVariable = tkinter.StringVar()
        instruction = tkinter.Label(self, anchor = 'w', 
                                    fg = 'white', bg = 'black', 
                                    textvariable = self.instructionVariable)
        self.instructionVariable.set('Enter a song title '
                                    + 'to search for chords or press the '
                                    + '"Save" button when done.')
        instruction.grid(column = 0, row = 0, columnspan = 5, sticky = 'EW')
        # Label for status
        self.labelVariable = tkinter.StringVar()
        label = tkinter.Label(self, textvariable = self.labelVariable,
                              anchor = 'w', fg = 'white', bg = 'grey')
        label.grid(column = 0, row = 1, columnspan = 5, sticky = 'EW')
        # Don't allow grid to resize
        self.grid_columnconfigure(0, weight = 1)
        self.resizable(False, False)
        # Don't allow auto grow and shrink for window
        self.update()
        self.geometry(self.geometry())
    
    def OnEnterClick(self):
        if self.state == 0:
            # Get song title from entry field
            self.title = self.entryVariable.get()
            self.title = capitalise(self.title)
            self.chords = song_search(self.title)
            # No chords found
            if self.chords == None:
                self.labelVariable.set('No chords found for ' + self.title + '!')
            # Chords found
            else:
                self.key = get_key(self.chords)
                self.instructionVariable.set('Toggle the arrows to transpose or '
                                             + 'press "Enter" to continue.')
                self.labelVariable.set('Song: {0} / Key: {1}'.format(self.title, self.key))
                self.state = 1
                
        elif self.state == 1:
            add_chords(self.title, self.chords)
            self.state = 0
            self.labelVariable.set('Chords added for ' + self.title + '!')
            self.instructionVariable.set('Enter a song title '
                                         + 'to search for chords or press the '
                                         + '"Save" button when done.')
        # Auto keyboard focus on entry field
        self.entry.focus_set()
        self.entry.selection_range(0, tkinter.END)
        
    def OnPressEnter(self, event):
        self.OnEnterClick()
        
    def OnSaveClick(self):
        # Get user input for doc name then exit
        self.filepath = tkinter.filedialog.asksaveasfilename()
        app.destroy()
    
    def OnUpClick(self):
        if self.state == 0:
            pass
        elif self.state == 1:
            # Transpose up
            transpose(self.chords)
            if self.key != 'unknown':
                allkeys = ('A', 'A#', 'B', 'C', 'C#', 'D', 
                           'D#', 'E', 'F', 'F#', 'G', 'G#', 'A')
                self.key = allkeys[allkeys.index(self.key) + 1]
            self.labelVariable.set('Song: {0} / Key: {1}'.format(self.title, self.key))
            
    def OnDownClick(self):
        if self.state == 0:
            pass
        elif self.state == 1:
            # Transpose down
            for i in range(11):
                transpose(self.chords)
            if self.key != 'unknown':
                allkeys = ('A', 'G#', 'G', 'F#', 'F', 'E', 
                             'D#', 'D', 'C#', 'C', 'B', 'A#', 'A')
                self.key = allkeys[allkeys.index(self.key) + 1]
            self.labelVariable.set('Song: {0} / Key: {1}'.format(self.title, self.key))
    
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
            return(content[0])

def capitalise(title):
    """Capitalise each word in the title"""
    
    titlelist = []
    for word in title.split():
        try:
            titlelist.append(word[0].upper() + word[1:].lower())
        except IndexError:
            titlelist.append(word.upper())
    return ' '.join(titlelist)

def add_chords(title, chords):
    """Add chords to the docx"""
    chords = chords.getText()
    # Add title on docx
    p = chordsheet.add_paragraph('')
    # Title bold and underline
    p.add_run(title.upper()).bold = True
    p.runs[0].underline = True
    # See if lines have \r appended to the back
    has_return = '\r' in chords
    # Clean up chords
    if has_return:
        chords = chords.split('\n')
    # Add chords
    p1 = chordsheet.add_paragraph()
    for line in chords:
        p1.add_run(line)

def in_letters(letters, note1, note2):
    """Helper function for get_key. Determine if chosen notes are in chords"""
    
    if note1 in letters and note2 in letters:
        return True
    return False

def get_key(chords):
    """Get the key of chords"""
    
    letters = chords.select('span')
    for i in range(len(letters)):
        letters[i] = letters[i].getText()
    simplechords = ['F', 'C', 'G', 'D', 'A', 'E', 'B']
    for i in range(6):
        if in_letters(letters, simplechords[i], simplechords[i+1]):
            return simplechords[i+1]
    complexchords = ['A#', 'D#', 'G#', 'C#', 'F#', 'B']
    for i in range(5):
        if in_letters(letters, complexchords[i], complexchords[i+1]):
            return complexchords[i]
    return 'unknown'

def transpose(chords):
    """Transpose chords one semitone up"""
    
    letterssoup = chords.select('span')
    letterstext = letterssoup.copy()
    for i in range(len(letterstext)):
        letterstext[i] = letterstext[i].getText()
    allchords = ('A', 'A#', 'B', 'C', 'C#', 'D', 
                 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A') 
    sharps = ('A#', 'C#', 'D#', 'F#', 'G#')
    # Messy transpose function (try to optimise next time)
    for i in range(len(letterstext)):
        normals = ['A', 'C', 'B', 'D', 'F', 'E', 'G']
        for chord in sharps:
            if chord in letterstext[i]:
                j = letterstext[i].index(chord)
                chordportion = allchords[allchords.index(chord) + 1]
                newchord = (letterstext[i][:j] 
                            + chordportion
                            + letterstext[i][j+2:])
                letterstext[i] = newchord
                # Prevent changing chord again
                normals.remove(chordportion)
        for chord in normals:
            if chord in letterstext[i]:
                j = letterstext[i].index(chord)
                chordportion = allchords[allchords.index(chord) + 1]
                newchord = (letterstext[i][:j] 
                            + chordportion
                            + letterstext[i][j+1:])
                letterstext[i] = newchord
    # Edit html directly
    for i in range(len(letterssoup)):
        letterssoup[i].string = letterstext[i]

if __name__ == '__main__':
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
    app.title('ChordSearch')
    app.mainloop()
    # Save the chordsheet
    try:
        if len(app.filepath) > 0:
            chordsheet.save(app.filepath + '.docx')
    except AttributeError:
        pass