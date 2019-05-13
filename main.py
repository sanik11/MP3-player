import pygame, os
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import time
from random import randint
from functools import partial

from mutagen.mp3 import MPEGInfo, MP3, EasyMP3
from mutagen import File
from PyLyrics import *

from add_playlist import *
from downloud import DownloudSong


class Track:
    def __init__(self, length, title, path):
        self.length = length
        self.title = title
        self.path = path


class MusicPlayer(QWidget):

    def __init__(self):
        super(MusicPlayer, self).__init__()

        # ------Іконки____________

        self.playIcon = QIcon()
        self.playIconImage = QPixmap("Png/play.png")
        self.playIcon.addPixmap(self.playIconImage)

        self.randIcon = QIcon()
        self.randIconImage = QPixmap("Png/rand.png")
        self.randIcon.addPixmap(self.randIconImage)

        self.randNatIcon = QIcon()
        self.randNatIconImage = QPixmap("Png/randNat.png")
        self.randNatIcon.addPixmap(self.randNatIconImage)

        self.repeatIcon = QIcon()
        self.repeatIconImage = QPixmap("Png/repeat.png")
        self.repeatIcon.addPixmap(self.repeatIconImage)

        self.repeatNatIcon = QIcon()
        self.repeatNatIconImage = QPixmap("Png/repeatNat.png")
        self.repeatNatIcon.addPixmap(self.repeatNatIconImage)

        self.volumeIcon = QIcon()
        self.volumeIconImage = QPixmap("Png/volume.png")
        self.volumeIcon.addPixmap(self.volumeIconImage)

        self.volumeNatIcon = QIcon()
        self.volumeNatIconImage = QPixmap("Png/volumeNat.png")
        self.volumeNatIcon.addPixmap(self.volumeNatIconImage)

        self.pauseIcon = QIcon()
        self.pauseIconImage = QPixmap("Png/pause.png")
        self.pauseIcon.addPixmap(self.pauseIconImage)

        movie = QMovie('Png/gif.gif')

        self.ui = uic.loadUi('main_window.ui')
        self.ui.setWindowTitle('Music player')

        self.playlistWindow = self.ui.listView  # вікно для списку пісень

        self.playlistModel = QStandardItemModel(self.playlistWindow)
        self.playlistWindow.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.playlistWindow.doubleClicked.connect(self.playlistItemDoubleClick)

        self.lyricsWindow = self.ui.textBrowser  # вікно для тексту пісень

        self.albumArt = self.ui.label_2  # Вікно для альбому
        self.albumArt.setMovie(movie)
        movie.start()

        self.songName = self.ui.label_3  # метка для назви пісні

        self.artistName = self.ui.label_4  # метка для виконавця

        self.volLabel = self.ui.label_6  # метка для звуку

        self.openFileButton = self.ui.pushButton_4  # кнопка для відкриття

        self.songCount = self.ui.label_5  # Кількість пісень

        self.songLengh = self.ui.label_7  # Час пісні

        self.ui_2 = DownloudSong()
        self.ui_addPlaylist = AddPlaylist()

        self.ui.pushButton_8.clicked.connect(self.ui_2.start_downl)
        self.ui.pushButton_12.clicked.connect(self.ui_addPlaylist.start_add)

        self.playPauseButton = self.ui.pushButton  # Кнопка грати/пауза

        self.nextSongButton = self.ui.pushButton_2  # Кнопка наступна пісня

        self.prevSongButton = self.ui.pushButton_3  # Кнопка попередня пісня

        self.repeatSongButton = self.ui.pushButton_7  # кнопка для повторення пісні

        self.randSongButton = self.ui.pushButton_6  # Кнопка для рандомної пісні

        self.seekSlider = self.ui.horizontalSlider  # Слайдер для пісні
        self.seekSlider.setValue(0)

        self.volumeButton = self.ui.pushButton_5  # Кнопка для звуку

        self.curSongTimeLabel = self.ui.label  # таймер пісні

        self.volumeSlider = self.ui.horizontalSlider_2  # Слайдер для звуку
        self.volumeSlider.setRange(0, 100)

        self.ui.show()
        self.list_playList = []
        # ---------------------------------Кнопки----------------------------------------
        self.playPauseButton.clicked.connect(self.playPauseAudioButton)

        self.openFileButton.clicked.connect(self.openFileSelectionDialog)

        self.nextSongButton.clicked.connect(self.nextSongAudioButton)
        self.prevSongButton.clicked.connect(self.previousSongAudioButton)

        self.repeatSongButton.clicked.connect(self.repeatSongButton_cl)

        self.randSongButton.clicked.connect(self.randSongButton_cl)

        self.volumeButton.clicked.connect(self.setVolyme_cl)

        self.ui.pushButton_9.clicked.connect(partial(self.setPlayList, self.list_playList, 0))
        self.ui.pushButton_10.clicked.connect(partial(self.setPlayList, self.list_playList, 1))
        self.ui.pushButton_11.clicked.connect(partial(self.setPlayList, self.list_playList, 2))

        # ----------------------------Слайдери-----------------------------
        self.volumeSlider.valueChanged.connect(self.setVolume)

        self.seekSlider.sliderMoved.connect(self.seekMusic)

        self.updateSeekTimer = QTimer()
        self.updateSeekTimer.timeout.connect(self.updateSeekSlider)
        self.updateSeekTimer.start(1000)

        self.nextSongTimer = QTimer()
        self.nextSongTimer.timeout.connect(self.playNextSongInPlaylist)
        self.nextSongTimer.start(1000)

        # ______________________Зміні____________________
        self.timerCounter = 0
        self.pressCounter = 0
        self.playlistCurrentSongIndex = 0
        self.songFileLength = 0
        self.playlistCurrentSongIndex = 0

        self.playmusicValue = False
        self.nextButtonPressed = False
        self.previousButtonPressed = False
        self.playerWentToFirstSongAutomatically = False

        self.randSong = False
        self.repeatSong = False
        self.vol_btn = False

        self.fileDialogFilePath = ""

        pygame.init()
        pygame.mixer.init()

        self.workingDirectory = os.getcwd()

        self.loadSettings()

    def openFileSelectionDialog(self):

        self.fileDialogFilePath = QFileDialog.getOpenFileName(self, "Open File", '/', '*.mp3 *.m3u')[0]

        self.playAudioOnFileSelect(self.fileDialogFilePath, 1)

    # self.fileDialogFilePath = ''

    def saveSettings(self, setting, value):

        if setting == "AudioLevel":
            with open("AudioLevel.config", "w+") as config:
                config.write(str(setting) + " !=! " + str(value))

    def playAudioOnFileSelect(self, path, a):

        self.timerCounter = 0
        self.seekSlider.setValue(0)
        if path.endswith(".m3u"):

            if path not in self.list_playList and len(self.list_playList) < 3:

                self.list_playList.append(path)

            elif path not in self.list_playList and len(self.list_playList) == 3:

                self.list_playList = self.list_playList[1:3]
                self.list_playList.append(path)

            self.setStyle_playList(len(self.list_playList) - 1)

            for i in range(9, 12):
                try:
                    z = self.list_playList[i - 9].split("/", -1)[-1].split(".m3u")[0][:10]
                    if len(z) > 13:
                        z[:10] + '...'
                    eval('self.ui.pushButton_' + str(i) + '.setText("' + z + '")')
                except:
                    pass

            self.playlist = self.parseM3U(path)
            if pygame.mixer.get_init() != None:
                pygame.mixer.music.stop()
            pygame.mixer.quit()
            if a == 0:
                self.playlistCurrentSongIndex = 0

            if os.path.exists(self.playlist[self.playlistCurrentSongIndex].path):

                self.playmusicValue = True
                pygame.mixer.init()

                pygame.mixer.music.load(self.playlist[self.playlistCurrentSongIndex].path.encode("utf8"))
                pygame.mixer.music.play()
                self.loadSettings()

                self.songFileToGetLengthFrom = MP3(self.playlist[self.playlistCurrentSongIndex].path)
                self.songFileLength = self.songFileToGetLengthFrom.info.length
                self.seekSlider.setRange(0, self.songFileLength)

                self.showSongInfo(self.playlist[self.playlistCurrentSongIndex].path)
                self.addM3USongsToPlaylistWindow()
                self.setCurrentSongHighlighted()
            else:
                self.playlistModel.removeRows(0, self.playlistModel.rowCount())
                self.lyricsWindow.setText(
                    "The .m3u playlist file you chose appears to be invalid or broken. Please"
                    " pick another one or play a .mp3 file instead.")
                # self.fileDialogFilePath = ""
                self.loadSettings()

        elif path.endswith(".mp3"):

            if pygame.mixer.get_init() != None:
                pygame.mixer.music.stop()
            pygame.mixer.quit()

            self.info = MPEGInfo(open(path, "rb"))

            self.playmusicValue = True

            pygame.mixer.init()
            pygame.mixer.music.load(path.encode("utf8"))

            pygame.mixer.music.play()
            self.loadSettings()

            self.songFileToGetLengthFrom = MP3(path)
            self.songFileLength = int(self.songFileToGetLengthFrom.info.length)

            self.seekSlider.setRange(0, self.songFileLength)

            self.showSongInfo(path)
            self.playlistModel.removeRows(0, self.playlistModel.rowCount())
            if self.playlistModel.rowCount() == 0:
                self.songFile = EasyMP3(path)
                if "title" in self.songFile:
                    self.songFileTitle = self.songFile["title"][0]
                else:
                    self.songFileTitle = self.fileDialogFilePath.split("/", -1)[-1].split(".mp3")[0]
                self.item = QStandardItem("1: " + self.songFileTitle)
                self.playlistModel.appendRow(self.item)
                self.playlistWindow.setModel(self.playlistModel)
                self.setCurrentSongHighlighted()
        self.playerWentToFirstSongAutomatically = False
        self.isPlaying = True

    def playAudioFromSelectedFile(self, path):
        """Метод для відтворення аудіо з вибраного файлу."""
        self.timerCounter = 0
        self.seekSlider.setValue(0)
        if pygame.mixer.get_init() != None:
            pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.info = MPEGInfo(open(path, "rb"))
        self.loadSettings()
        pygame.mixer.init()
        pygame.mixer.music.load(path.encode("utf8"))
        pygame.mixer.music.play()
        self.songFileToGetLengthFrom = MP3(path)
        self.songFileLength = self.songFileToGetLengthFrom.info.length
        self.seekSlider.setRange(0, self.songFileLength)
        self.showSongInfo(path)
        self.setCurrentSongHighlighted()
        self.playerWentToFirstSongAutomatically = False
        self.isPlaying = True

    def playNextSongInPlaylist(self):
        if self.fileDialogFilePath.endswith(".m3u"):
            if self.isPlaying == True:
                if os.path.exists(self.playlist[self.playlistCurrentSongIndex].path):
                    self.timerCounter += 1

                    self.songFileToGetLengthFrom = MP3(self.playlist[self.playlistCurrentSongIndex].path)
                    self.songFileLength = self.songFileToGetLengthFrom.info.length

                    if int(self.timerCounter) > int(self.songFileLength):

                        if self.repeatSong == True:
                            self.playAudioFromSelectedFile(self.playlist[self.playlistCurrentSongIndex].path)
                        else:

                            if self.randSong == True:
                                self.playlistCurrentSongIndex = randint(0, len(self.playlist))

                                self.playAudioFromSelectedFile(self.playlist[self.playlistCurrentSongIndex].path)
                            else:

                                if self.playlistCurrentSongIndex + 1 <= (
                                        len(self.playlist) - 1) and self.songFileLength:
                                    self.playlistCurrentSongIndex += 1
                                    self.playAudioFromSelectedFile(self.playlist[self.playlistCurrentSongIndex].path)
                                elif self.playlistCurrentSongIndex + 1 > (len(self.playlist) - 1):
                                    self.playlistCurrentSongIndex = 0
                                    self.timerCounter = 0
                                    self.seekSlider.setValue(0)
                                    if pygame.mixer.get_init() != None:
                                        pygame.mixer.music.stop()
                                    pygame.mixer.quit()
                                    pygame.mixer.init()
                                    pygame.mixer.music.load(
                                        self.playlist[self.playlistCurrentSongIndex].path.encode("utf8"))
                                    self.loadSettings()
                                    self.seekSlider.setRange(0, self.songFileLength)
                                    self.showSongInfo(self.playlist[self.playlistCurrentSongIndex].path)
                                    self.setCurrentSongHighlighted()
                                    self.playerWentToFirstSongAutomatically = True
                                    self.isPlaying = False
        elif self.fileDialogFilePath.endswith(".mp3"):
            if self.isPlaying == True:
                self.timerCounter += 1
                self.songFileToGetLengthFrom = MP3(self.fileDialogFilePath)
                self.songFileLength = self.songFileToGetLengthFrom.info.length
                if int(self.timerCounter) > int(self.songFileLength):
                    if self.repeatSong == True:
                        self.playAudioFromSelectedFile(self.fileDialogFilePath)
                    else:
                        self.timerCounter = 0
                        self.seekSlider.setValue(0)
                        if pygame.mixer.get_init() != None:
                            pygame.mixer.music.stop()
                        pygame.mixer.quit()
                        pygame.mixer.init()
                        pygame.mixer.music.load(self.fileDialogFilePath)
                        self.loadSettings()
                        self.seekSlider.setRange(0, self.songFileLength)
                        self.showSongInfo(self.fileDialogFilePath)
                        self.setCurrentSongHighlighted()
                        self.playerWentToFirstSongAutomatically = True
                        self.isPlaying = False

    def nextSongAudioButton(self):
        if self.fileDialogFilePath.endswith(".m3u"):

            if self.randSong == True:
                self.playlistCurrentSongIndex = randint(0, len(self.playlist))

                self.playAudioFromSelectedFile(self.playlist[self.playlistCurrentSongIndex].path)

            else:
                if self.playlistCurrentSongIndex != (len(self.playlist) - 1):
                    self.playlistCurrentSongIndex += 1
                elif self.playlistCurrentSongIndex == (len(self.playlist) - 1):
                    self.playlistCurrentSongIndex = 0
                if os.path.exists(self.playlist[self.playlistCurrentSongIndex].path):
                    self.playAudioFromSelectedFile(self.playlist[self.playlistCurrentSongIndex].path)
            self.nextButtonPressed = True
        elif self.fileDialogFilePath.endswith(".mp3"):
            self.timerCounter = 0
            self.seekSlider.setValue(0)
            self.songFileToGetLengthFrom = MP3(self.fileDialogFilePath)
            self.songFileLength = self.songFileToGetLengthFrom.info.length
            self.seekSlider.setRange(0, self.songFileLength)
            if pygame.mixer.get_init() != None:
                pygame.mixer.music.stop()
            pygame.mixer.music.load(self.fileDialogFilePath.encode("utf8"))
            self.isPlaying = False
            self.nextButtonPressed = True

    def previousSongAudioButton(self):
        if self.fileDialogFilePath.endswith(".m3u") and self.playlistCurrentSongIndex != 0:

            self.playlistCurrentSongIndex -= 1

            if os.path.exists(self.playlist[self.playlistCurrentSongIndex].path):
                self.playAudioFromSelectedFile(self.playlist[self.playlistCurrentSongIndex].path)
                self.previousButtonPressed = True
        elif self.fileDialogFilePath.endswith(".m3u") and self.playlistCurrentSongIndex == 0:
            if os.path.exists(self.playlist[self.playlistCurrentSongIndex].path):
                self.playAudioFromSelectedFile(self.playlist[self.playlistCurrentSongIndex].path)
                self.previousButtonPressed = True
        elif self.fileDialogFilePath.endswith(".mp3"):
            self.timerCounter = 0
            self.seekSlider.setValue(0)
            self.songFileToGetLengthFrom = MP3(self.fileDialogFilePath)
            self.songFileLength = self.songFileToGetLengthFrom.info.length
            self.seekSlider.setRange(0, self.songFileLength)
            if self.isPlaying == True:
                if pygame.mixer.get_init() != None:
                    pygame.mixer.music.stop()
                pygame.mixer.music.play()
                self.previousButtonPressed = True
            elif self.isPlaying == False:
                if pygame.mixer.get_init() != None:
                    pygame.mixer.music.stop()
                pygame.mixer.music.load(self.fileDialogFilePath.encode("utf8"))
                self.previousButtonPressed = True

    def playPauseAudioButton(self):

        if self.fileDialogFilePath.endswith(".m3u") or self.fileDialogFilePath.endswith(".mp3"):
            if self.isPlaying == True:
                if pygame.mixer.get_init() != None:
                    pygame.mixer.music.pause()
                self.previousButtonPressed = False
                self.nextButtonPressed = False
                self.isPlaying = False
                self.playPauseButton.setIcon(self.pauseIcon)
            elif self.isPlaying == False:
                if self.previousButtonPressed == True or self.nextButtonPressed == True or self.playerWentToFirstSongAutomatically == True:
                    if pygame.mixer.get_init() != None:
                        pygame.mixer.music.play()
                    self.previousButtonPressed = False
                    self.nextButtonPressed = False
                    self.playerWentToFirstSongAutomatically = False
                    self.isPlaying = True
                elif self.previousButtonPressed == False or self.nextButtonPressed == False:
                    if pygame.mixer.get_init() != None:
                        pygame.mixer.music.unpause()
                        self.playPauseButton.setIcon(self.playIcon)
                        self.isPlaying = True
        else:
            self.openFileSelectionDialog()

    def resetDoublePressPreviousButtonCounter(self):
        self.pressCounter = 0

    def parseM3U(self, m3u):

        self.locationOfM3UFile = os.path.dirname(m3u)
        m3u = open(m3u, "r")
        line = m3u.readline()
        playlist = []
        song = Track(None, None, None)
        for line in m3u:
            line = line.strip()

            if line.startswith("#EXTINF:"):
                length, title = line.split("#EXTINF:")[1].split(",", 1)
                song = Track(length, title, None)
            elif len(line) != 0:
                self.songFileName = line.split("\\", -1)[-1]
                self.newPath = self.locationOfM3UFile + "/" + self.songFileName
                if os.path.exists(line):
                    song.path = line
                elif os.path.exists(self.newPath):
                    song.path = self.newPath
                else:
                    song.path = ""
                playlist.append(song)
                song = Track(None, None, None)
        m3u.close()

        return playlist

    def randSongButton_cl(self):
        if self.randSong == False:
            self.randSong = True
            self.randSongButton.setIcon(self.randNatIcon)
        else:
            self.randSong = False
            self.randSongButton.setIcon(self.randIcon)

    def repeatSongButton_cl(self):
        if self.repeatSong == False:
            self.repeatSong = True
            self.repeatSongButton.setIcon(self.repeatNatIcon)
        else:
            self.repeatSong = False
            self.repeatSongButton.setIcon(self.repeatIcon)

    def setVolyme_cl(self, value):

        if self.vol_btn == False:
            self.vol_btn = True

            if pygame.mixer.get_init() != None:
                self.save_lv = self.volumeSlider.value()
                self.setVolume(0)
                self.volumeSlider.setValue(0)
                self.volumeButton.setIcon(self.volumeNatIcon)

        else:
            self.vol_btn = False
            self.setVolume(self.save_lv)
            self.volumeSlider.setValue(self.save_lv)
            self.volumeButton.setIcon(self.volumeIcon)

    def setVolume(self, value):
        if pygame.mixer.get_init() != None:
            pygame.mixer.music.set_volume(value / 100)
            self.audioLevel = self.volumeSlider.value()
            self.volLabel.setText(str(value) + " %")
            self.saveSettings("AudioLevel", value)

    def seekMusic(self, value):
        if pygame.mixer.get_init() != None:
            try:
                pygame.mixer.music.rewind()
                pygame.mixer.music.set_pos(value - 1)
            except:
                pass

            self.timerCounter = value

    def loadSettings(self):

        if os.path.isfile("AudioLevel.config"):
            with open("AudioLevel.config", "r") as config:
                for line in config:
                    if "AudioLevel" in line:
                        self.savedAudioLevel = line.split(" !=! ", 1)[1]
                        try:
                            self.setVolume(int(self.savedAudioLevel))
                            self.volumeSlider.setValue(int(self.savedAudioLevel))
                        except:
                            self.setVolume(100)
                            self.volumeSlider.setValue(100)
            config.close()

    def updateSeekSlider(self):

        self.seekSlider.setValue(self.timerCounter)
        self.curSongTimeLabel.setText(time.strftime("%M:%S", time.gmtime(self.timerCounter)))

    def setCurrentSongHighlighted(self):
        """Функція для підсвічення пісні яка відтворюється в даний час в вікні пісень"""
        if self.fileDialogFilePath.endswith(".m3u"):
            for i in range(self.playlistModel.rowCount()):
                self.index = self.playlistModel.index(self.playlistCurrentSongIndex, 0, QModelIndex())
                self.selectionModel = self.playlistWindow.selectionModel()
                self.selectionModel.clear()
                self.selectionModel.select(self.index, self.selectionModel.Select)
        else:
            for i in range(self.playlistModel.rowCount()):
                self.index = self.playlistModel.index(0, 0, QModelIndex())
                self.selectionModel = self.playlistWindow.selectionModel()
                self.selectionModel.clear()
                self.selectionModel.select(self.index, self.selectionModel.Select)

    def addM3USongsToPlaylistWindow(self):

        self.playlistModel.removeRows(0, self.playlistModel.rowCount())
        i = 1
        for track in self.playlist:

            self.playlistSongFile = EasyMP3(track.path)
            if "title" in self.playlistSongFile:
                self.playlistSongFileTitle = self.playlistSongFile["title"][0]
            else:
                self.playlistSongFileTitle = track.path.split("\\", -1)[-1].split(".mp3")[0]

            if len(self.playlistSongFileTitle) > 39:
                self.playlistSongFileTitle = self.playlistSongFileTitle[:39] + '...'
            self.item = QStandardItem(str(i) + ": " + self.playlistSongFileTitle)
            i += 1
            self.playlistModel.appendRow(self.item)
            self.playlistWindow.setModel(self.playlistModel)

    def setPlayList(self, list_song, i):
        try:

            name_playlist = list_song[i]

            self.playAudioOnFileSelect(name_playlist, 0)
            self.setStyle_playList(i)
        except:
            pass

    def setStyle_playList(self, i):
        if i == 0:
            self.ui.pushButton_9.setStyleSheet("* { color: #ff7f00 }")
            self.ui.pushButton_10.setStyleSheet("* { color: #808080 }")
            self.ui.pushButton_11.setStyleSheet("* { color: #808080 }")
        elif i == 1:
            self.ui.pushButton_9.setStyleSheet("* { color: #808080}")
            self.ui.pushButton_10.setStyleSheet("* { color: #ff7f00 }")
            self.ui.pushButton_11.setStyleSheet("* { color: #808080 }")
        elif i == 2:
            self.ui.pushButton_9.setStyleSheet("* { color: #808080 }")
            self.ui.pushButton_10.setStyleSheet("* { color: #808080 }")
            self.ui.pushButton_11.setStyleSheet("* { color: #ff7f00 }")

    def showSongInfo(self, path):
        self.filePath = File(path)
        self.audioFrames = self.filePath.tags

        self.audioFile = EasyMP3(path)
        if "title" in self.audioFile:
            self.audioFileTitle = self.audioFile["title"][0]
        else:
            if self.fileDialogFilePath.endswith(".m3u"):
                self.audioFileTitle = \
                    self.playlist[self.playlistCurrentSongIndex].path.split("\\", -1)[-1].split(".mp3")[0]
            else:
                self.audioFileTitle = self.fileDialogFilePath.split("/", -1)[-1].split(".mp3")[0]
        self.songName.setText(self.audioFileTitle)
        if "artist" in self.audioFile:
            self.audioFileArtist = self.audioFile["artist"][0]
        else:
            self.audioFileArtist = "Unknown"
        self.artistName.setText(self.audioFileArtist)

        if ("artist" in self.audioFile) and ("title" in self.audioFile):
            try:
                self.lyricsWindow.setText(PyLyrics.getLyrics(self.audioFile["artist"][0], self.audioFile["title"][0]))
            except:
                self.lyricsWindow.setText("Sorry, no lyrics found for this song and artist combination.")
        else:
            self.lyricsWindow.setText("Sorry, no lyrics found for this song and artist combination.")
        if self.fileDialogFilePath.endswith(".m3u"):
            self.realSongNumber = self.playlistCurrentSongIndex + 1
            self.maxNumberOfSongs = len(self.playlist)
            self.songCount.setText(str(self.realSongNumber) + " / " + str(self.maxNumberOfSongs))
        else:
            self.songCount.setText("1 / 1")
        self.songFileToGetLengthFrom = MP3(path)
        self.songFileLength = self.songFileToGetLengthFrom.info.length
        self.songLengh.setText(time.strftime("%M:%S", time.gmtime(self.songFileLength)))

    def playlistItemDoubleClick(self):
        """Відтворення пісень по подвійному натиску на пісню"""
        if self.fileDialogFilePath.endswith(".m3u"):
            self.selectedIndexes = self.playlistWindow.selectedIndexes()
            for selected in self.selectedIndexes:
                for track in self.playlist:
                    self.song = EasyMP3(track.path)
                    if "title" in self.song:
                        self.songTitle = self.song["title"][0]
                    else:
                        self.songTitle = track.path.split("\\", -1)[-1].split(".mp3")[0]
                    self.selectedSongTitleFromWindow = selected.data().split(": ", 1)[1]
                    if self.songTitle == self.selectedSongTitleFromWindow:
                        self.currentSelectionSongNumber = selected.data().split(": ", 1)[0]
                        self.playlistCurrentSongIndex = int(self.currentSelectionSongNumber) - 1
                        self.playAudioFromSelectedFile(track.path)
                        break
        else:
            self.selectedIndexes = self.playlistWindow.selectedIndexes()
            for selected in self.selectedIndexes:
                self.song = EasyMP3(self.fileDialogFilePath)
                if "title" in self.song:
                    self.songTitle = self.song["title"][0]
                else:
                    self.songTitle = self.fileDialogFilePath.split("/", -1)[-1].split(".mp3")[0]
                self.selectedSongTitleFromWindow = selected.data().split(": ", 1)[1]
                if self.songTitle == self.selectedSongTitleFromWindow:
                    self.currentSelectionSongNumber = selected.data().split(": ", 1)[0]
                    self.playlistCurrentSongIndex = int(self.currentSelectionSongNumber) - 1
                    self.playAudioFromSelectedFile(self.fileDialogFilePath)
                    break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myapp = MusicPlayer()
    sys.exit(app.exec_())
