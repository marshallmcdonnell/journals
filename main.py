import sys
from PyQt4 import QtGui, QtCore
from journals.app import App
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    form = App()
    form.show()
    app.exec_()


