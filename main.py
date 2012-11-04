from PyQt4.Qt import QApplication
from PyQt4.QtGui import QMainWindow
from accessDatesList import AccessDatesList
import sys

def startApp():
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    datesWindow = AccessDatesList(mainWindow, rootDir='/home/')
    mainWindow.setCentralWidget(datesWindow)
    mainWindow.setMinimumWidth(500)
    mainWindow.setMinimumHeight(500)
    mainWindow.show()
    app.exec_()


if __name__ == '__main__':
    startApp()