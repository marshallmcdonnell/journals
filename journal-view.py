#!/usr/bin/env python

from PyQt4 import QtGui
import pandas as pd

def csv2data( filename ):
    df = pd.read_csv( filename, index_col=0)
    return df

class MainWindow( QtGui.QMainWindow):
    def __init__(self, data, parent=None):
        super(MainWindow, self).__init__(parent)
        centralWidget = QtGui.QWidget(self) 
        self.setCentralWidget( centralWidget )
        self.mainLayout = QtGui.QVBoxLayout(centralWidget)

        self.createItemsModel(data)
        self.createSortFilter()
        self.createTable()
        self.showMaximized()


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
        self.filterModel.setFilterKeyColumn(2) # 1st column sort filter

        self.line_edit = QtGui.QLineEdit()
        self.line_edit.textChanged.connect(self.filterModel.setFilterRegExp)
        self.mainLayout.addWidget(self.line_edit)
        

    def createTable(self):
        self.table = QtGui.QTableView()
        self.table.setModel(self.filterModel)
        self.table.setSortingEnabled(True)
        self.mainLayout.addWidget(self.table)


if __name__ == '__main__':
    import sys
    from argparse import ArgumentParser

    parser = ArgumentParser("Program to launch a PyQt GUI for displaying journal files of NOMAD data.")
    parser.add_argument("--csv", type=str, 
                      help="Filename for importing in CSV data." )

    args = parser.parse_args()

    if args.csv:
        dataframe = csv2data(args.csv)

    app    = QtGui.QApplication(sys.argv)
    window = MainWindow(dataframe)
    window.show()
    app.exec_()
