#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pandas as pd

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

instrumentList = ["NOM"]
userList = ['ntm', 'benfrandsen', 'mth' ]

def csv2data( filename ):
    df = pd.read_csv( filename, index_col=0)
    return df

class MainWindow( QMainWindow):
    def __init__(self, data, parent=None):
        super(MainWindow, self).__init__(parent)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.mainLayout = QVBoxLayout(centralWidget)

        self.tabs = QTabWidget(centralWidget)
        self.createMenu()
        self.createStatusBar()

        self.create_table_tab(data)
        self.create_plot_tab()

        self.setLayout(self.mainLayout)
        self.showMaximized()
        self.show()

    def create_table_tab(self,data):
        tableTab = QWidget() 
        self.tableLayout = QVBoxLayout(tableTab)

        self.createFilterHeader()
 
        self.createComboBox(["IPTS","Scan ID"], \
                            self.tableLayout, \
                            label="Filter:" )
        self.createItemsModel(data)
        self.createSortFilter()
        self.createTable()

        tableTab.setLayout(self.tableLayout)
        self.tabs.addTab(tableTab, "Journal")
        self.mainLayout.addWidget(self.tabs)

    def createFilterHeader(self):
        header  = QHBoxLayout()
        header.addWidget( self.createDisplayGroupBox())
        header.addWidget( self.createFilterGroupBox() )
        self.tableLayout.addLayout(header)

    def createDisplayGroupBox(self):
        displayLayout   = QHBoxLayout()
        displayGroupBox = QGroupBox("Display")
        displayGroupBox.
        self.createComboBox( instrumentList, 
                             displayLayout, 
                             label="Instrument: ")
        displayGroupBox.setLayout(displayLayout)
        return displayGroupBox

    def createFilterGroupBox(self):
        filterGroupBox  = QGroupBox("Filter")
        filterLayout    = QHBoxLayout()
        self.createComboBox( instrumentList, filterLayout, label="Title: ")
        self.createComboBox( userList, filterLayout, label="User: ")
        filterGroupBox.setLayout(filterLayout)
        return filterGroupBox

    def create_plot_tab(self):
        plotTab = QWidget()
        self.tabs.addTab(plotTab, "Plots")

    def createMenu(self):
        mainMenu = QMenuBar()
        fileMenu = mainMenu.addMenu("&File")
        loadFileAction = self.createAction("&Save plot",
            shortcut="Ctrl+S", slot=self.savePlot,
            tip="Save current plot")
        quitAction = self.createAction("&Quit", slot=self.close,
            shortcut="Ctrl+Q", tip="Close application")
        
        self.addActions(fileMenu, (loadFileAction,None,quitAction) )

        self.mainLayout.addWidget(mainMenu)

    def createStatusBar(self):
        self.statusText = QLabel("Welcome to the Journal-Viewer!")
        self.statusBar().addWidget(self.statusText,1)
        

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def createAction(self, text, shortcut=None, slot=None,
                     icon=None, tip=None, checkable=False,
                     signal='triggered()' ):
        action = QAction(text,self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def savePlot(self):
        fileChoices = "PNG (*.png)|*.png"

        path = unicode(QFileDialog.getSaveFileName(self,'Save file','',fileChoices) )
        
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)

    def createComboBox(self, items, layout, label=None):
        if not items:
            print "ERROR: Must have items for createComboBox"
            exit()
        newBox =  QComboBox() 
        labelWidget = self.addComboItems( newBox, items, label=label)
        if label:
            layout.addWidget(labelWidget)
        layout.addWidget(newBox)
        return labelWidget

    def addComboItems( self, target, items, label=None ):
        labelWidget = None
        for item in items:
            target.addItem(item)
        if label:
            labelWidget = QLabel()
            labelWidget.setText(label)
            labelWidget.setBuddy(target)
        return labelWidget
        

    def createItemsModel(self, data):
        self.model = QStandardItemModel( len(data.index), len(data.columns) )
        self.setData(data)
        for i in range(len(self.df.index)):
            for j in range(len(self.df.columns)):
                self.model.setItem(i,j,QStandardItem(str(self.df.iat[i,j])))

    def setData(self, data):
        self.df = data
        horHeaders = []
        for n, key in enumerate( self.df.keys() ):
            horHeaders.append(key)
        self.model.setHorizontalHeaderLabels( horHeaders )


    def createSortFilter(self):
        self.filterModel = QSortFilterProxyModel()
        self.filterModel.setSourceModel(self.model)
        self.filterModel.setFilterKeyColumn(2) # 1st column sort filter

        self.line_edit = QLineEdit()
        self.line_edit.textChanged.connect(self.filterModel.setFilterRegExp)
        self.tableLayout.addWidget(self.line_edit)
        

    def createTable(self):
        self.table = QTableView()
        self.table.setModel(self.filterModel)
        self.table.setSortingEnabled(True)
        self.tableLayout.addWidget(self.table)

if __name__ == '__main__':
    import sys
    from argparse import ArgumentParser

    parser = ArgumentParser("Program to launch a PyQt GUI for displaying journal files of NOMAD data.")
    parser.add_argument("--csv", type=str, 
                      help="Filename for importing in CSV data." )

    args = parser.parse_args()

    if args.csv:
        dataframe = csv2data(args.csv)

    app    = QApplication(sys.argv)
    window = MainWindow(dataframe)
    app.exec_()
