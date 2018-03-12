# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 16:02:00 2018

@author: User
"""

from pytube import YouTube, Playlist
import tkinter, tkinter.filedialog
import requests, bs4

class Ytdl(tkinter.Tk):
    """ Tkinter GUI for downloading YouTube videos """
    def __init__(self, parent):
        tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initialise()
    
    def initialise(self):
        self.state = 0
        self.grid()
        # Set window size
        self.geometry("410x85")
        # Entry field for youtube link
        self.entryVariable = tkinter.StringVar()
        self.entry = tkinter.Entry(self, textvariable = self.entryVariable)
        self.entry.grid(column = 0, row = 2, columnspan = 5, sticky = 'EW')
        self.entryVariable.set('YouTube link/search query here')
        # Audio button
        audio = tkinter.Button(self, text = 'Audio', 
                               command = self.OnAudioClick)
        audio.grid(column = 3, row = 3)
        # Video button
        video = tkinter.Button(self, text = 'Video', 
                              command = self.OnVideoClick)
        video.grid(column = 4, row = 3)
        # Label for instructions
        self.instructionVariable = tkinter.StringVar()
        instruction = tkinter.Label(self, anchor = 'w', 
                                    fg = 'white', bg = 'black', 
                                    textvariable = self.instructionVariable)
        self.instructionVariable.set('Enter YouTube link/search query below. '
                                    + 'Press audio or video to download.')
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
        # Ask for directory to save videos/mp3 in
        self.directory = ''
        while self.directory == '':
            self.directory = tkinter.filedialog.askdirectory()
        # Auto keyboard focus on entry field
        self.entry.focus_set()
        self.entry.selection_range(0, tkinter.END)

    def SearchFor(self):
        """ Simulate youtube search and return link """
        search = 'https://www.youtube.com/results?search_query=' + self.link
        res = requests.get(search)
        soup = bs4.BeautifulSoup(res.text, 'lxml')
        hits = soup.select('div img')
        for hit in hits:
            hit = str(hit)
            if 'https://i.ytimg.com/vi/' in hit:
                index = hit.index('https://i.ytimg.com/vi/')
                hit = hit[index + 23:]
                video_id = hit[:hit.index('/')]
                break
        return 'https://www.youtube.com/watch?v=' + video_id
        
    def IsPlaylist(self):
        """ Perform SearchFor, and check if link is playlist """
        self.link = self.entryVariable.get()
        if 'https:' not in self.link:
            self.link = self.SearchFor()
            return False
        if 'list' in self.link:
            return True
        return False
    
    def OnAudioClick(self):
        """ Download audio """
        if self.IsPlaylist():
            pl = Playlist(self.link)
            pl.populate_video_urls()
            for link in pl.video_urls:
                yt = YouTube(link)
                stream = yt.streams.filter(only_audio = True).all()[0]
                stream.download(output_path = self.directory)
                self.labelVariable.set(stream.default_filename + ' downloaded!')
        else:
            try:
                yt = YouTube(self.link)
                stream = yt.streams.filter(only_audio = True).all()[0]
                stream.download(output_path = self.directory)
                self.labelVariable.set(stream.default_filename + ' downloaded!')
            except:
                self.labelVariable.set('Invalid link!')
                
    def OnVideoClick(self):
        """ Download video """
        if self.IsPlaylist():
            pl = Playlist(self.link)
            pl.populate_video_urls()
            for link in pl.video_urls:
                yt = YouTube(link)
                stream = yt.streams.filter(subtype='mp4', progressive=True).all()[0]
                stream.download(output_path = self.directory)
                self.labelVariable.set(stream.default_filename + ' downloaded!')
        else:
            try:
                yt = YouTube(self.link)
                stream = yt.streams.filter(subtype='mp4', progressive=True).all()[0]
                stream.download(output_path = self.directory)
                self.labelVariable.set(stream.default_filename + ' downloaded!')
            except:
                self.labelVariable.set('Invalid link!')

if __name__ == '__main__':
    app = Ytdl(None)
    app.title('YouTube')
    app.mainloop()