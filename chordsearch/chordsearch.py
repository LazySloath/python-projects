# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 13:11:27 2018

@author: User

Updated to work with new ultimateguitar UI
"""

import tkinter, requests, bs4, docx, json, re
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
            entry = self.entryVariable.get()
            entry = capitalise(entry)
            # LAter add TRY EXCEPT self.songlist = []
            self.songlist = song_search(entry)
            
            # No chords found
            if not self.songlist:
                self.labelVariable.set('No chords found for ' + entry + '!')
            # Chords found
            else:
                self.instructionVariable.set('Use the arrows to search for ' 
                                             + 'the correct version and press ' 
                                             + '"Enter" to continue.')
                self.counter = 0
                self.labelVariable.set(str(self.counter + 1) + ': '
                                       + self.songlist[self.counter][0] + ' / ' 
                                       + self.songlist[self.counter][1])
                self.state = 1
        
        
        elif self.state == 1:
            # Allow for transposing
            self.title = self.songlist[self.counter][1]
            self.chords = self.songlist[self.counter][2]
            self.key = get_key(self.chords)
            self.instructionVariable.set('Use the arrows to transpose and '
                                         + 'press "Enter" to continue.')
            self.labelVariable.set('Song: {0} / Key: {1}'.format(self.title, self.key))
            self.state = 2
            
        elif self.state == 2:
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
            # Scroll through versions
            if self.counter == 0:
                pass
            else:
                self.counter -= 1
                self.labelVariable.set(str(self.counter + 1) + ': '
                                       + self.songlist[self.counter][0] + ' / ' 
                                       + self.songlist[self.counter][1])
                
        elif self.state == 2:
            # Transpose up
            self.chords = transpose(self.chords)
            if self.key != 'unknown':
                allkeys = ('A', 'A#', 'B', 'C', 'C#', 'D', 
                           'D#', 'E', 'F', 'F#', 'G', 'G#', 'A')
                self.key = allkeys[allkeys.index(self.key) + 1]
            self.labelVariable.set('Song: {0} / Key: {1}'.format(self.title, self.key))
            
    def OnDownClick(self):
        if self.state == 0:
            pass
        
        elif self.state == 1:
            # Scroll through versions
            if self.counter == len(self.songlist) - 1:
                pass
            else:
                self.counter += 1
                self.labelVariable.set(str(self.counter + 1) + ': '
                                       + self.songlist[self.counter][0] + ' / ' 
                                       + self.songlist[self.counter][1])
                
        elif self.state == 2:
            # Transpose down
            for i in range(11):
                self.chords = transpose(self.chords)
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
    """Search for song on ug, return list of tuples(singer, title, chords)"""
    
    ugsearch = ('https://www.ultimate-guitar.com/search.php?'
    'search_type=title&value=' + title)
    ugsoup = soupify(ugsearch)
    # Get list 'hits' of search results
    rawhits = ugsoup.select('script')
    n = 0
    for rawhit in rawhits:
        if 'window.UGAPP.store.page' in rawhit.getText():
            break
        n += 1
    datastring = rawhits[n].string
    # This part is messy and might need to be changed occasionally
    cutoff = datastring.index('header_bidding')
    datastring = datastring[31:cutoff - 2] + '}'
    data = json.loads(datastring)
    subset = data['data']['results']
    hits = []
    for i in subset:
        if 'id' in i.keys():
            hits.append(i)
    songlist = []
    singers = []
    for hit in hits:
        singer = hit['artist_name']
        if singer in singers:
            pass
        else:
            href = hit['tab_url']
            title = hit['song_name']
            soup = soupify(href)
            try:
                rawhits = soup.select('script')
                n = 0
                for rawhit in rawhits:
                    if 'window.UGAPP.store.page' in rawhit.getText():
                        break
                    n += 1
                datastring = rawhits[n].string
                # As is this part
                cutoff = datastring.index('revision_id')
                datastring = datastring[31:cutoff - 2] + '}}}}'
                data = json.loads(datastring)
                chords = data['data']['tab_view']['wiki_tab']['content']
                songlist.append((singer, title, chords))
                singers.append(singer)
            except:
                pass
    return songlist
    
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
    #chords = chords.getText()
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
    if type(chords) is str:
        chords = clean_chords(chords)
    else:
        chordstr = ''
        for line in chords:
            chordstr += line
        chords = clean_chords(chordstr)
    p1.add_run(chords)

def clean_chords(chords):
    """Clean chords of [ch], [/ch]"""
    while '[ch]' in chords:
        cleanindex = chords.index('[ch]')
        chords = chords[:cleanindex] + chords[cleanindex + 4:]
    while '[/ch]' in chords:
        cleanindex = chords.index('[/ch]')
        chords = chords[:cleanindex] + chords[cleanindex + 5:]
    return chords

def in_letters(letters, note1, note2):
    """Helper function for get_key. Determine if chosen notes are in chords"""
    
    if note1 in letters and note2 in letters:
        return True
    return False

def get_key(chords):
    """Get the key of chords"""
    
    # Get indexes of [ch]
    openindex = [m.end() for m in re.finditer('\[ch\]', chords)]
    # Get index of [/ch]
    closeindex = [m.start() for m in re.finditer('\[/ch\]', chords)]
    letters = []
    for i in range(len(openindex)):
        letters.append(chords[openindex[i]:closeindex[i]])
    simplechords = ['F', 'C', 'G', 'D', 'A', 'E', 'B']
    # Check for F major
    if in_letters(letters, 'F', 'C') and 'G' not in letters:
        return 'F'
    # Check for C to B major
    for i in range(6):
        if in_letters(letters, simplechords[i], simplechords[i+1]):
            return simplechords[i+1]
    # Check for flat majors
    complexchords = ['A#', 'D#', 'G#', 'C#', 'F#', 'B', 'E']
    for i in range(5):
        if in_letters(letters, complexchords[i], complexchords[i+1]) and \
        complexchords[i+2] not in letters:
            return complexchords[i]
    return 'unknown'

def transpose(chords):
    """Transpose chords one semitone up"""
    # Get index of [ch]
    openindex = [m.end() for m in re.finditer('\[ch\]', chords)]
    # Get index of [/ch]
    closeindex = [m.start() for m in re.finditer('\[/ch\]', chords)]
    letters = []
    for i in range(len(openindex)):
        letters.append(chords[openindex[i]:closeindex[i]])
    originalletters = letters.copy()
    # Change flats to relative sharps
    flats = ('Ab', 'Bb', 'Db', 'Eb', 'Gb')
    relatives = ('G#', 'A#', 'C#', 'D#', 'F#')
    for i in range(len(letters)):
        for chord in flats:
            if chord in letters[i]:
                j = letters[i].index(chord)
                letters[i] = letters[i].replace(letters[i][j:j+2], relatives[flats.index(chord)])
    allchords = ('A', 'A#', 'B', 'C', 'C#', 'D', 
                 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A') 
    sharps = ('A#', 'C#', 'D#', 'F#', 'G#')

    # Messy transpose function 
    for i in range(len(letters)):
        normals = ['A', 'C', 'B', 'D', 'F', 'E', 'G']
        for chord in sharps:
            if chord in letters[i]:
                j = letters[i].index(chord)
                newchord = allchords[allchords.index(chord) + 1]
                letters[i] = letters[i].replace(letters[i][j:j+2], newchord)
                # Prevent changing chord again
                normals.remove(newchord)
        for chord in normals:
            if chord in letters[i]:
                j = letters[i].index(chord)
                letters[i] = letters[i].replace(letters[i][j], allchords[allchords.index(chord) + 1])  

    # Edit chords
    for i in range(len(letters)):
        replaceat = openindex[i]
        chord1 = originalletters[i]
        chord2 = letters[i]
        chords = chords[:replaceat] + chord2 + chords[replaceat + len(chord1):]
        for j in range(len(openindex)):
            openindex[j] += len(chord2) - len(chord1)
    return chords

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