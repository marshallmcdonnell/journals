import sys
from PyQt4 import QtGui, QtCore
from journals.app import Journals_App 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    form = Journals_App()
    form.show()
    app.exec_()


