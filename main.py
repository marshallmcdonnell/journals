#!/usr/bin/env python

import sys, os
import pandas as pd
from PyQt4 import QtGui, QtCore


import journal_design


class App( QtGui.QMainWindow, journal_design.Ui_MainWindow):
    def __init__(self, data, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)

        self.createItemsModel(data)
        self.createSortFilter()
        self.createTable()

    def createItemsModel(self, data):
        self.model = QtGui.QStandardItemModel( len(data.index), len(data.columns) )
        self.setData(data)
        for i in range(len(self.df.index)):
            for j in range(len(self.df.columns)):
                self.model.setItem(i,j,QtGui.QStandardItem(str(self.df.iat[i,j])))

    def setData(self, data):
        self.df = data
        horHeaders = []
        for n, key in enumerate( self.df.keys() ):
            horHeaders.append(key)
        self.model.setHorizontalHeaderLabels( horHeaders )

    def createSortFilter(self):
        self.filterModel = QtGui.QSortFilterProxyModel()
        self.filterModel.setSourceModel(self.model)
        self.filterModel.setFilterKeyColumn(5)
        self.filterModel.setFilterCaseSensitivity(0)
        self.titleLineEdit.textChanged.connect(self.filterModel.setFilterRegExp )
        self.titleCaseCheckBox.toggled.connect( self.filterModel.setFilterCaseSensitivity )
        self.titleSyntaxComboBox.addItem( 'Text', QtCore.QRegExp.FixedString )
        self.titleSyntaxComboBox.addItem( 'Wildcard', QtCore.QRegExp.Wildcard )
        self.titleSyntaxComboBox.addItem( 'RegExp', QtCore.QRegExp.RegExp )

    def titleFilterChanged(self):
        syntax = self.titleSyntaxComboBox.itemData( self.titleSyntaxComboBox.currentIndex() )
        syntax = QtCore.RegExp.PatternSyntax( syntax )

        if self.titleCaseCheckBox.isChecke():
            case = QtCore.Qt.CaseSensitive
        else:
            case = QtCore.Qt.CaseInsensitive

        regexp = QtCore.QRegExp( self.titleLineEdit.text(), case, syntax )
        self.filterModel.setFilterRegExp(regexp)

    def createTable(self):
        self.tableView.setModel(self.filterModel)
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setResizeMode(1)


    '''
        #self.btnBrowse.clicked.connect(self.browse_folder)
    def browse_folder(self):
        self.listWidget.clear()
        directory = QtGui.QFileDialog.getExistingDirectory(self,"Pick a Folder")

        if directory:
            for filename in os.listdir(directory):
                self.listWidget.addItem(filename)
    '''
def csv2data( filename ):
    df = pd.read_csv( filename, index_col=0)
    return df

def main(data):
    app = QtGui.QApplication(sys.argv)
    form = App(data)
    form.show()
    app.exec_()


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser("Program to launch a PyQt GUI for displaying journal files of NOMAD data.")
    parser.add_argument("--csv", type=str,
                      help="Filename for importing in CSV data." )

    args = parser.parse_args()

    if args.csv:
        data = csv2data(args.csv)

    main(data)
