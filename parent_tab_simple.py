import sys
from PyQt4 import QtCore, QtGui
from journals.app import Journals_App

class setupJournals(Journals_App):
    def __init__(self):
        Journals_App.__init__(self)

class TheMainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        self.central = QtGui.QTabWidget(self)
        self.setCentralWidget(self.central)
        self.central.addTab(setupJournals(),'Journals')

        self.central.addTab(QtGui.QPushButton('Test'), 'OtherTab')
        

app = QtGui.QApplication([])
mainWindow = TheMainWindow()
mainWindow.show()
sys.exit(app.exec_())


