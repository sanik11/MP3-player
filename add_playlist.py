from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from mutagen.mp3 import EasyMP3


class AddPlaylist(QWidget):

    def __init__(self):
        super(AddPlaylist, self).__init__()

        self.txt = "#EXTM3U	Program “Playlist” v.m 3.0 © 2013 by Isaak Rozenfeld\n"

        self.list_song = []

    def start_add(self):
        self.ui = uic.loadUi('create_playlist.ui')
        self.ui.setWindowTitle('Create a playlist')
        self.playlistWindow = self.ui.listView  # вікно для списку пісень
        self.playlistModel = QStandardItemModel(self.playlistWindow)
        self.playlistWindow.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.show()
        self.ui.commandLinkButton.clicked.connect(self.add_playlist)
        self.ui.commandLinkButton_2.clicked.connect(self.add_song_playlist)
        self.ui.commandLinkButton_3.clicked.connect(self.del_song_playlist)

    def add_playlist(self):
        try:
            for i in self.list_song:
                self.txt = self.txt + '#EXTINF:0, ' + i[0].split("/", -1)[-1].split(".mp3")[0] + '.mp3\n' + i[0] + '\n'

            self.sv = QFileDialog.getSaveFileName(self, "Save File", '/', '.m3u')
            with open(self.sv[0] + self.sv[1], "w") as file:
                file.write(self.txt)
            file.close()
            self.ui.close()
        except:
            pass

    def add_song_playlist(self):
        try:
            op = QFileDialog.getOpenFileName(self, "Open File", '/', 'Songs (*.mp3)')
            if op not in self.list_song:
                self.list_song.append(op)
                self.addM3USongsToPlaylistWindow(self.list_song)
        except:
            pass

    def addM3USongsToPlaylistWindow(self, list_song):
        self.playlistModel.removeRows(0, self.playlistModel.rowCount())
        i = 1
        for track in list_song:

            self.songFile = EasyMP3(track[0])
            if "title" in self.songFile:
                self.songFileTitle = self.songFile["title"][0]
            else:
                self.songFileTitle = track[0].split("/", -1)[-1].split(".mp3")[0]
            self.item = QStandardItem(str(i) + ": " + self.songFileTitle)
            self.playlistModel.appendRow(self.item)
            self.playlistWindow.setModel(self.playlistModel)
            i += 1

    def del_song_playlist(self):
        if len(self.list_song) != 0:
            self.selectedIndexes = self.playlistWindow.selectedIndexes()
            for selected in self.selectedIndexes:
                song_index = selected.data().split(": ")[0]
                del (self.list_song[int(song_index) - 1])
                self.addM3USongsToPlaylistWindow(self.list_song)
