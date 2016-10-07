#!/usr/bin/env python

import sys, os, re
import pandas as pd
from PyQt4 import QtGui, QtCore

import utils
import journal_design
from MyCustomSortFilterProxyModel import CustomSortFilterProxyModel

instrumentList = { "NOMAD"  : "NOM",
                   "SNAP"   : "SNAP",
                   "POWGEN" : "PG3",
                   "VISION" : "VIS" }

def error(message):
    print
    print "#---------------------------------------------------------------------#"
    print "# ERROR:", message
    print "#---------------------------------------------------------------------#"
    print
    sys.exit()

class App( QtGui.QMainWindow, journal_design.Ui_MainWindow):
    def __init__(self, data, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)

        self._filterHeadersList = [ 'title', 'ipts', 'starttime', 'stoptime', 'user', 'scan' ]
        self._filterHeaders = {}

        self.createInstrumentList()
        self.createItemsModel(data)
        self.createSortFilters()
        self.createTable()

    def createSortFilters(self):

        self.proxyModel = CustomSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)

        self._getFilterHeaders()

        self.createTitleSortFilter()
        self.createIptsSortFilter()
        self.createUserSortFilter()
        self.createDateFilter()
        self.createScanIdFilter()

    def createInstrumentList(self):
        for instrument in instrumentList:
            self.instrumentComboBox.addItem(instrument)

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

    def _getFilterHeaders( self):
        for key in self._filterHeadersList:
            index = self._getHeaderIndex( key.lower() )
            if index is None:
                error(str(key)+" is not in header")
            self._filterHeaders[key] = index
        return

    def _getHeaderIndex( self, string ):
        for x in range(0,self.model.columnCount()):
            entry =  str(self.model.horizontalHeaderItem(x).text()).strip().lower().strip('#')
            if entry == string:
                return x
        return None

    def createTitleSortFilter(self):
        titleColumnIndex = self._getHeaderIndex('title')
        if titleColumnIndex is None:
            titleColumnIndex = self._getHeaderIndex('Title')
            if titleColumnIndex is None:
                return

        self.titleColumnIndex = titleColumnIndex
        self.proxyModel.addFilterHeaders( 'title', titleColumnIndex )
        self.proxyModel.addFilterFunction('title', lambda r,s : (s in r[titleColumnIndex]) )

        self.titleCaseCheckBox.toggled.connect( self.titleFilterChanged )

        self.titleSyntaxComboBox.addItem( 'Text', QtCore.QRegExp.FixedString )
        self.titleSyntaxComboBox.addItem( 'Wildcard', QtCore.QRegExp.Wildcard )
        self.titleSyntaxComboBox.addItem( 'RegExp', QtCore.QRegExp.RegExp )
        self.titleSyntaxComboBox.currentIndexChanged.connect( self.titleFilterChanged )
        
        self.titleFilterChanged()    
        self.titleLineEdit.textChanged.connect(self.titleFilterChanged )
        

    def titleFilterChanged(self):
        self.proxyModel.removeFilterFunction('title')
        v = self.titleColumnIndex

        syntax_nr = self.titleSyntaxComboBox.itemData( self.titleSyntaxComboBox.currentIndex() ).toString()
        syntax = QtCore.QRegExp.PatternSyntax( syntax_nr )

        if self.titleCaseCheckBox.isChecked():
            case_sensitive = True
        else:
            case_sensitive = False

        if syntax == 0: # regular expression
            if case_sensitive:
                self.proxyModel.addFilterFunction('title', lambda r,s : re.search(s, r[v] ) is not None )
            else:
                self.proxyModel.addFilterFunction('title', lambda r,s : re.search(s, r[v], re.IGNORECASE ) is not None)
        elif syntax == 1 or syntax == 2: # wildcard or fixed string
            if case_sensitive:
                self.proxyModel.addFilterFunction('title', lambda r,s : (s in r[v]) )
            else:
                self.proxyModel.addFilterFunction('title', lambda r,s : (s.lower() in r[v].lower()) )

        self.proxyModel.setFilterValues('title', str(self.titleLineEdit.text()) )

    def createIptsSortFilter(self):
        iptsColumnIndex = self._getHeaderIndex('IPTS')
        if iptsColumnIndex is None:
            iptsColumnIndex = self._getHeaderIndex('ipts')
            if iptsColumnIndex is None:
                return
        self.proxyModel.addFilterHeaders( 'ipts', iptsColumnIndex )
        self.proxyModel.addFilterFunction('ipts', lambda r,s : (s in r[iptsColumnIndex]) )
        self.iptsFilterChanged()    
        self.iptsLineEdit.textChanged.connect(self.iptsFilterChanged )

    def iptsFilterChanged(self):
        self.proxyModel.setFilterValues('ipts', str(self.iptsLineEdit.text()) )

    def createUserSortFilter(self):
        userColumnIndex = self._getHeaderIndex('User')
        if userColumnIndex is None:
            userColumnIndex = self._getHeaderIndex('user')
            if userColumnIndex is None:
                return
        self.proxyModel.addFilterHeaders( 'user', userColumnIndex )
        self.proxyModel.addFilterFunction('user', lambda r,s : (s in r[userColumnIndex]) )
        self.userFilterChanged()    
        self.userLineEdit.textChanged.connect(self.userFilterChanged )

    def userFilterChanged(self):
        self.proxyModel.setFilterValues('user', str(self.userLineEdit.text()) )

    def createDateFilter(self):
        starttimeColumnIndex = self._getHeaderIndex('starttime')
        if starttimeColumnIndex is None:
            starttimeColumnIndex = self._getHeaderIndex('StartTime')
            if starttimeColumnIndex is None:
                return
       
        stoptimeColumnIndex = self._getHeaderIndex('stoptime')
        if stoptimeColumnIndex is None:
            stoptimeColumnIndex = self._getHeaderIndex('StopTime')
            if stoptimeColumnIndex is None:
                return


        currentDate = QtCore.QDate.currentDate()
        currentTime = QtCore.QTime.currentTime()

        self.dateEnd.setDate(currentDate)
        self.dateEnd.setTime(currentTime)

        self.dateStart.setDate( currentDate.addMonths(-6) )
        self.dateStart.setTime( currentTime )

        self.proxyModel.setDateColumnsToConvert( [starttimeColumnIndex, stoptimeColumnIndex] )
        self.proxyModel.addFilterHeaders( 'startDate', starttimeColumnIndex )
        self.proxyModel.addFilterHeaders( 'stopDate', stoptimeColumnIndex )

        self.proxyModel.addFilterFunction( 'minDate', lambda r, s :    self.dateStart.date() <= r[starttimeColumnIndex] 
                                                                    or self.dateStart.date() <= r[stopttimeColumnIndex] )

        self.proxyModel.addFilterFunction( 'maxDate', lambda r, s :    self.dateEnd.date()   >= r[starttimeColumnIndex] 
                                                                    or self.dateEnd.date()   >= r[stopttimeColumnIndex] )
        self.dateFilterChanged()    
        self.dateStart.dateChanged.connect(self.dateFilterChanged )
        self.dateEnd.dateChanged.connect(self.dateFilterChanged )
        return

    def dateFilterChanged(self):
        start = self.proxyModel.filterHeaders['startDate']
        stop  = self.proxyModel.filterHeaders['stopDate']
        self.proxyModel.setFilterValues('minDate', self.dateStart.date() )
        self.proxyModel.setFilterValues('maxDate', self.dateEnd.date() )
        self.proxyModel.removeFilterFunction('minDate')
        self.proxyModel.removeFilterFunction('maxDate')
        self.proxyModel.addFilterFunction( 'minDate', lambda r, s :    self.dateStart.date() <= r[start] 
                                                                    or self.dateStart.date() <= r[stop] )

        self.proxyModel.addFilterFunction( 'maxDate', lambda r, s :    self.dateEnd.date()   >= r[start] 
                                                                    or self.dateEnd.date()   >= r[stop] )

    def createScanIdFilter(self):
        scanColumnIndex = self._getHeaderIndex('Scan')
        if scanColumnIndex is None:
            scanColumnIndex = self._getHeaderIndex('scan')
            if scanColumnIndex is None:
                return
        self.proxyModel.addFilterHeaders( 'scan', scanColumnIndex )
        self.proxyModel.addFilterFunction('scan', lambda r,s : (int(r[scanColumnIndex]) in s) )
        self.scanLineEdit.setText('0-99999')
        self.scanFilterChanged()    
        self.scanLineEdit.returnPressed.connect(self.scanFilterChanged )

    def scanFilterChanged(self):
        self.proxyModel.setFilterValues('scan', utils.procNumbers(str(self.scanLineEdit.text())) )

        return

    def createTable(self):
        self.treeView.setModel(self.proxyModel)
        self.treeView.setSortingEnabled(True)
        self.treeView.setSizePolicy( QtGui.QSizePolicy().Expanding, QtGui.QSizePolicy().Expanding )
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSelectionMode( QtGui.QAbstractItemView.ExtendedSelection )
        self.treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)


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
    df = pd.read_csv( filename)
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
