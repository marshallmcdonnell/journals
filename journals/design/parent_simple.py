import sys
from PyQt4 import QtCore, QtGui
from journal_design import Journals_MainWindow

class setupJournals(QtGui.QMainWindow, Journals_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Journals_MainWindow.__init__(self)
        self.setupUi(self)

class TheMainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        self.central = QtGui.QTabWidget(self)
        self.setCentralWidget(self.central)
        self.central.addTab(setupJournals(),'Journals')

app = QtGui.QApplication([])
mainWindow = TheMainWindow()
mainWindow.show()
sys.exit(app.exec_())


