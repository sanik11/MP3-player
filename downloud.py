from PyQt5.QtWidgets import *
from PyQt5 import uic
import requests, re, os


class DownloudSong(QWidget):

    def __init__(self):
        super(DownloudSong, self).__init__()

    def start_downl(self):
        self.ui = uic.loadUi('download_song.ui')
        self.ui.setWindowTitle('Download the song')
        self.ui.show()

        self.ui.commandLinkButton.clicked.connect(self.down_song)

    def down_song(self):
        try:
            if len(self.ui.lineEdit.text()) != 0:

                if '-' in self.ui.lineEdit.text():
                    name_song = self.ui.lineEdit.text().replace('-', '–')
                else:
                    name_song = self.ui.lineEdit.text()
                name_url = requests.get("http://zaycev.net/search.html?query_search=" + name_song)
                try:
                    number_song = re.search('%s(.*)%s' % ('link href="/pages/', '.shtml" itemprop="url"'),
                                            name_url.text).group(1)
                    a = requests.get('http://cdndl.zaycev.net/' + number_song + '/' + name_song + '.mp3')
                    self.ui.close()
                    with open(os.path.join("Music", name_song + '.mp3'),
                              "wb") as file:
                        file.write(a.content)
                    self.msgInf = QMessageBox()
                    self.msgInf.setIcon(QMessageBox.Information)
                    self.msgInf.setInformativeText("Your song has been uploaded.")
                    self.msgInf.setStandardButtons(QMessageBox.Ok)
                    self.msgInf.exec_()

                except:
                    self.msgInf = QMessageBox()
                    self.msgInf.setIcon(QMessageBox.Information)
                    self.msgInf.setInformativeText("This song was not found. Check the entered data.")
                    self.msgInf.setStandardButtons(QMessageBox.Ok)
                    self.msgInf.exec_()
            else:
                self.msgCr = QMessageBox()
                self.msgCr.setIcon(QMessageBox.Critical)
                self.msgCr.setText("Enter song name!")
                self.msgCr.setStandardButtons(QMessageBox.Ok)
                self.msgCr.buttonClicked.connect(self.msgCr.close)
                self.msgCr.exec_()
        except:
            self.ui.close()
