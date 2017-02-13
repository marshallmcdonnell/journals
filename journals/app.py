#!/usr/bin/env python

from __future__ import print_function
import sys, os, re
import pandas 

from PyQt4 import QtGui, QtCore

from journals.utilities import process_numbers
from journals.design import journal_design
from journals.model.models import CustomSortFilterProxyModel
from journals.databases import Interface
from journals.databases.icat.sns.interface import SnsICatInterface

runDatabaseList = ['ICAT-SNS', 'CSV File']
sampleDatabaseList = ['ITEMS']
instrumentDict = { "ARCS"    : "ARCS",
                   "BASIS"   : "BSS",
                   "CNCS"    : "CNCS",
                   "CORELLI" : "CORELLI",
                   "EQ-SANS" : "EQSANS",
                   "FNPB"    : "FNPB",
                   "HYSPEC"  : "HYS",
                   "MaNDI"   : "MANDI",
                   "NOMAD"   : "NOM",
                   "NSE"     : "NSE",
                   "POWGEN"  : "PG3",
                   "LiqREF"  : "REF_L",
                   "MagREF"  : "REF_M",
                   "SEQUOIA" : "SEQ",
                   "SNAP"    : "SNAP",
                   "TOPAZ"   : "TOPAZ",
                   "USANS"   : "USANS",
                   "VISION"  : "VIS",
                   "VULCAN"  : "VULCAN" }

class Journals_App( QtGui.QMainWindow, journal_design.Journals_MainWindow):
    def __init__(self, parent=None):
        super(Journals_App, self).__init__(parent)
        self.setupUi(self)

        self._filterHeadersList = [ 'title', 'ipts', 'starttime',  'user', 'scan' ]
        self._filterHeaders = {}
        self._db = None
        self._ipts_list = None
        self._meta_ipts_data = None

        self.createInstrumentList()
        self.createRunDatabaseList()
        self.createSampleDatabaseList()
        self.createItemsModel()
        self.createSortFilters()
        self.createTable()

    def createSortFilters(self):

        self.proxyModel = CustomSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)

        self._getFilterHeaders()

        self.createUserSortFilter(self.proxyModel)
        self.createIptsSortFilter(self.userProxyModel)
        self.createDateFilter(self.iptsProxyModel)
        self.createScanIdFilter(self.dateProxyModel)
        self.createTitleSortFilter(self.scanProxyModel)
       
        self.databaseButton.clicked.connect(self.pullFromRunDatabase)
     
        self.childProxyModel = self.titleProxyModel

    def pullFromRunDatabase(self):
        start = self.dateStart.date()
        stop  = self.dateEnd.date()
        if self.iptsLineEdit.text().isEmpty():
            ipts_list = None
        else:
            ipts_list = str(self.iptsLineEdit.text())
            ipts_list = process_numbers(ipts_list)
            print(ipts_list)
        if self.scanLineEdit.text().isEmpty():
            scan_list = None
        else:
            scan_list = self.scanLineEdit.text()

        print("pull from database")
        data = self.update_db_data(start=start,stop=stop,ipts_list=ipts_list,run_list=scan_list)
        self.updateModel(data)
        self.createSortFilters()
        self.createTable()


    def createRunDatabaseList(self):
        for database in runDatabaseList:
            self.runDatabaseComboBox.addItem(database)
        self.runDatabaseComboBox.setCurrentIndex(runDatabaseList.index('ICAT-SNS'))
        self.runDatabaseComboBox.setDisabled(True)
    def createSampleDatabaseList(self):
        for database in sampleDatabaseList:
            self.sampleDatabaseComboBox.addItem(database)
        self.sampleDatabaseComboBox.setCurrentIndex(sampleDatabaseList.index('ITEMS'))
        self.sampleDatabaseComboBox.setDisabled(True)



    def createInstrumentList(self):
        for instrument in sorted(instrumentDict):
            self.instrumentComboBox.addItem(instrument)
        self.instrumentComboBox.setCurrentIndex(sorted(instrumentDict).index('NOMAD'))
        self.instrumentComboBox.currentIndexChanged.connect( self.createItemsModel )

    def createItemsModel(self):
        instrument = instrumentDict[str(self.instrumentComboBox.currentText())]
        source = str(self.runDatabaseComboBox.currentText())
        sourceType = self.getDataSourceType( source )
        if sourceType == "database":
            data = self.initialRunDatabasePull(source,instrument)
        self.updateModel(data)
        
    def updateModel(self,data):
        self.model = QtGui.QStandardItemModel( len(data.index), len(data.columns) )
        self.setData(data)
        for i in range(len(self.df.index)):
            for j in range(len(self.df.columns)):
                self.model.setItem(i,j,QtGui.QStandardItem(str(self.df.iat[i,j])))

    def getDataSourceType(self,source):
        if "File" in source:
            return "file"
        return "database"

    def initialRunDatabasePull(self,source,instrument):
       
        currentDate = QtCore.QDate.currentDate()
        currentTime = QtCore.QTime.currentTime()
 
        startDate = currentDate.addMonths(-2)
        startTime = currentTime


        self._db = Interface(source,instrument)
        data = self.initialize_database(startDate,currentDate)

        return data

    def initialize_database(self,startDate,currentDate):
        db = self._db
        db.initialize()
        self._meta_ipts_data = db.get_meta_data()
        print("initialize_database")
        data = self.update_db_data(start=startDate,stop=currentDate)
        return data
                    
    def update_db_data(self,ipts_list=None,start=None,stop=None,run_list=None):
        filtered_data = self._meta_ipts_data.copy()
        
        # IPTS filter
        print(ipts_list)
        print(filtered_data.keys())
        if ipts_list:
            filtered_data = dict( (k, filtered_data[k]) for k in ipts_list if k in filtered_data)
        print('Filtered data:', filtered_data.keys())

        # Time filter
        if start or stop:
            pop_list = list()
            for k, v in filtered_data.iteritems():
                for time in v['createtime']:
                    year, month, day = time.split('T')[0].split('-')
                    date = QtCore.QDate(int(year),int(month),int(day))
                    if start:
                        if start > date:
                            pop_list.append(k)
                    if stop:
                        if stop < date:
                            pop_list.append(k)
            for k in pop_list:
                filtered_data.pop(k,None)
                        
        print('Filtered data 2:', filtered_data.keys())

        # Scan filter
        if run_list:
            for run in run_list:
                for k, v in filtered_data.iteritems():
                    if run in v['runs']:
                        filtered_data[k]

        print('Filtered data 3:', filtered_data.keys())
        if filtered_data:
            db = self._db
            db.apply_ipts_filter(filtered_data.keys())
            df = db.get_dataframe()
            return df
        else:
            # TODO return the current view instead w/ warning message of empty filter
            return

    def csv2data( filename ):
        df = pandas.read_csv( filename)
        return df

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
                print(key, " is not in header. Disabling this filter.")
            self._filterHeaders[key] = index
        return

    def _getHeaderIndex( self, string ):
        for x in range(0,self.model.columnCount()):
            entry =  str(self.model.horizontalHeaderItem(x).text()).strip().lower().strip('#')
            if entry == string:
                return x
        return None

    def createTitleSortFilter(self, parentProxyModel):
        self.titleProxyModel = CustomSortFilterProxyModel()
        self.titleProxyModel.setSourceModel(parentProxyModel)

        titleColumnIndex = self._getHeaderIndex('title')
        if titleColumnIndex is None:
            titleColumnIndex = self._getHeaderIndex('Title')
            if titleColumnIndex is None:
                self.titleLineEdit.setPlaceholderText('Disabled')
                self.titleLineEdit.setDisabled(True)
                return

        self.titleColumnIndex = titleColumnIndex
        self.titleProxyModel.addFilterHeaders( 'title', titleColumnIndex )
        self.titleProxyModel.addFilterFunction('title', lambda r,s : (s in r[titleColumnIndex]) )

        self.titleCaseCheckBox.toggled.connect( self.titleFilterChanged )

        self.titleSyntaxComboBox.addItem( 'Text', QtCore.QRegExp.FixedString )
        self.titleSyntaxComboBox.addItem( 'Wildcard', QtCore.QRegExp.Wildcard )
        self.titleSyntaxComboBox.addItem( 'RegExp', QtCore.QRegExp.RegExp )
        self.titleSyntaxComboBox.currentIndexChanged.connect( self.titleFilterChanged )
        
        self.titleFilterChanged()    
        self.titleLineEdit.editingFinished.connect(self.titleFilterChanged )
        

    def titleFilterChanged(self):
        self.titleProxyModel.removeFilterFunction('title')
        v = self.titleColumnIndex

        syntax_nr = self.titleSyntaxComboBox.itemData( self.titleSyntaxComboBox.currentIndex() ).toString()
        syntax = QtCore.QRegExp.PatternSyntax( syntax_nr )

        if self.titleCaseCheckBox.isChecked():
            case_sensitive = True
        else:
            case_sensitive = False

        if syntax == 0: # regular expression
            if case_sensitive:
                self.titleProxyModel.addFilterFunction('title', 
                                     lambda r,s : re.search(s, r[v] ) is not None )
            else:
                self.titleProxyModel.addFilterFunction('title', 
                                     lambda r,s : re.search(s, r[v], re.IGNORECASE ) is not None)
        elif syntax == 1 or syntax == 2: # wildcard or fixed string
            if case_sensitive:
                self.titleProxyModel.addFilterFunction('title', lambda r,s : (s in r[v]) )
            else:
                self.titleProxyModel.addFilterFunction('title', lambda r,s : (s.lower() in r[v].lower()) )

        self.titleProxyModel.setFilterValues('title', str(self.titleLineEdit.text()) )

    def createIptsSortFilter(self, parentProxyModel):
        self.iptsProxyModel = CustomSortFilterProxyModel()
        self.iptsProxyModel.setSourceModel(parentProxyModel)

        iptsColumnIndex = self._getHeaderIndex('IPTS')
        if iptsColumnIndex is None:
            iptsColumnIndex = self._getHeaderIndex('ipts')
            if iptsColumnIndex is None:
                self.iptsLineEdit.setPlaceholderText('Disabled')
                self.iptsLineEdit.setDisabled(True)
                return
        ipts_list = set([ int(self.model.data( self.model.index(r, iptsColumnIndex)).toPyObject())
                      for r in range(self.model.rowCount()) ])
        iptsRange = ' '.join(str(ipts) for ipts in sorted(ipts_list) )
        self.iptsProxyModel.addFilterHeaders( 'ipts', iptsColumnIndex )
        self.iptsProxyModel.addFilterFunction('ipts', lambda r,s : (int(r[iptsColumnIndex]) in s) )
        self.iptsLineEdit.setText(iptsRange)
        self.iptsFilterChanged()    
        self.iptsLineEdit.editingFinished.connect(self.iptsFilterChanged )

    def iptsFilterChanged(self):
        self.iptsProxyModel.setFilterValues('ipts', process_numbers(str(self.iptsLineEdit.text())) )

    def createUserSortFilter(self, parentProxyModel):
        self.userProxyModel = CustomSortFilterProxyModel()
        self.userProxyModel.setSourceModel(parentProxyModel)

        userColumnIndex = self._getHeaderIndex('User')
        if userColumnIndex is None:
            userColumnIndex = self._getHeaderIndex('user')
            if userColumnIndex is None:
                self.userLineEdit.setPlaceholderText('Disabled')
                self.userLineEdit.setDisabled(True)
                return
        self.userProxyModel.addFilterHeaders( 'user', userColumnIndex )
        self.userProxyModel.addFilterFunction('user', lambda r,s : (s in r[userColumnIndex]) )
        self.userFilterChanged()    
        self.userLineEdit.editingFinished.connect(self.userFilterChanged )

    def userFilterChanged(self):
        self.userProxyModel.setFilterValues('user', str(self.userLineEdit.text()) )

    def createDateFilter(self, parentProxyModel):
        self.dateProxyModel = CustomSortFilterProxyModel()
        self.dateProxyModel.setSourceModel(parentProxyModel)

        currentDate = QtCore.QDate.currentDate()
        currentTime = QtCore.QTime.currentTime()

        starttimeColumnIndex = self._getHeaderIndex('starttime')
        if starttimeColumnIndex is None:
            starttimeColumnIndex = self._getHeaderIndex('StartTime')
            if starttimeColumnIndex is None:
                self.dateStart.setDisabled(True)
                return

        stoptimeColumnIndex = starttimeColumnIndex # bit of a hack
       
        times = [ str(self.model.data( self.model.index(r, starttimeColumnIndex)).toPyObject())
                  for r in range(self.model.rowCount()) ]
        times = [ t.split('T')[0] for t in times ]
        times = [ QtCore.QDate.fromString( t, 'yyyy-MM-dd') for t in times]

        self.dateStart.setDate( min(times) )
        self.dateProxyModel.setDateColumnsToConvert( starttimeColumnIndex )
        self.dateProxyModel.addFilterHeaders( 'startDate', starttimeColumnIndex )
        self.dateProxyModel.addFilterFunction( 'minDate', 
                            lambda r, s :    self.dateStart.date() <= r[starttimeColumnIndex] 
                                          or self.dateStart.date() <= r[stopttimeColumnIndex] )
        self.dateStartFilterChanged()    
        self.dateStart.dateChanged.connect(self.dateStartFilterChanged )
       
        self.dateEnd.setDate(currentDate)
        self.dateEnd.setTime(currentTime)

        stoptimeColumnIndex = self._getHeaderIndex('stoptime')
        if stoptimeColumnIndex is None:
            stoptimeColumnIndex = self._getHeaderIndex('StopTime')
            if stoptimeColumnIndex is None:
                self.dateProxyModel.setDateColumnsToConvert( stoptimeColumnIndex )
                self.dateProxyModel.addFilterHeaders( 'stopDate', stoptimeColumnIndex )

        self.dateProxyModel.addFilterFunction( 'maxDate', 
                            lambda r, s :    self.dateEnd.date()   >= r[starttimeColumnIndex] 
                                          or self.dateEnd.date()   >= r[stopttimeColumnIndex] )
        self.dateEndFilterChanged()    
        self.dateEnd.dateChanged.connect(self.dateEndFilterChanged )

        return

    def dateStartFilterChanged(self):
        start = self.dateProxyModel.filterHeaders['startDate']
        if 'stopDate' in self.dateProxyModel.filterHeaders:
            stop  = self.dateProxyModel.filterHeaders['stopDate']
        else:
            stop = None
        self.dateProxyModel.setFilterValues('minDate', self.dateStart.date() )
        self.dateProxyModel.removeFilterFunction('minDate')
        if stop is None:
            self.dateProxyModel.addFilterFunction( 'minDate', lambda r, s :    self.dateStart.date() <= r[start] )
        else:
            self.dateProxyModel.addFilterFunction( 'minDate', lambda r, s :    self.dateStart.date() <= r[start] 
                                                                            or self.dateStart.date() <= r[stop] )
    def dateEndFilterChanged(self):
        start = self.dateProxyModel.filterHeaders['startDate']
        stop  = self.dateProxyModel.filterHeaders['stopDate']
        self.dateProxyModel.setFilterValues('maxDate', self.dateEnd.date() )
        self.dateProxyModel.removeFilterFunction('maxDate')
        if stop is None:
            self.dateProxyModel.addFilterFunction( 'maxDate', lambda r, s :    self.dateEnd.date()   >= r[start] )
        else:
            self.dateProxyModel.addFilterFunction( 'maxDate', lambda r, s :    self.dateEnd.date()   >= r[start] 
                                                                            or self.dateEnd.date()   >= r[stop] )

    def createScanIdFilter(self, parentProxyModel):
        self.scanProxyModel = CustomSortFilterProxyModel()
        self.scanProxyModel.setSourceModel(parentProxyModel)

        scanColumnIndex = self._getHeaderIndex('Scan')
        if scanColumnIndex is None:
            scanColumnIndex = self._getHeaderIndex('scan')
            if scanColumnIndex is None:
                self.scanLineEdit.setPlaceholderText('Disabled')
                self.scanLineEdit.setDisabled(True)
                return
        scans = [ int(self.model.data( self.model.index(r, scanColumnIndex)).toPyObject())
                  for r in range(self.model.rowCount()) ]
        scanRange = str(min(scans))+"-"+str(max(scans))
        self.scanProxyModel.addFilterHeaders( 'scan', scanColumnIndex )
        self.scanProxyModel.addFilterFunction('scan', lambda r,s : (int(r[scanColumnIndex]) in s) )
        self.scanLineEdit.setText(scanRange)
        self.scanFilterChanged()    
        self.scanLineEdit.editingFinished.connect(self.scanFilterChanged )

    def scanFilterChanged(self):
        self.scanProxyModel.setFilterValues('scan', process_numbers(str(self.scanLineEdit.text())) )

        return

    def createTable(self):
        self.treeView.setModel(self.childProxyModel)
        self.treeView.setSortingEnabled(True)
        self.treeView.customContextMenuRequested.connect(self.rightClickMenu)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.setSizePolicy( QtGui.QSizePolicy().Expanding, QtGui.QSizePolicy().Expanding )
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSelectionMode( QtGui.QAbstractItemView.ExtendedSelection )
        self.treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)

    def rightClickMenu(self, pos=None):
        index = self.treeView.indexAt(pos)
        if not index.isValid():
            return
        r   = index.row()
        print(index, r)
        self._selected_scans = [ str(self.model.data(self.model.index(r,c)).toPyObject())
                               for c in range(self.model.columnCount()) ] 

        _plot = QtGui.QAction(self)
        _plot.setObjectName('PlotAction')
        _plot.setText('Plot')

        _menu = QtGui.QMenu('Menu', self.treeView)
        _menu.addAction(_plot)
        _plot.triggered.connect( self.launchPlot)
        _menu.popup(self.treeView.mapToGlobal(pos))

    def launchPlot(self):
        print("Launch the plot for ", self._selected_scans, "! ....well?!?")




    '''
        #self.btnBrowse.clicked.connect(self.browse_folder)
    def browse_folder(self):
        self.listWidget.clear()
        directory = QtGui.QFileDialog.getExistingDirectory(self,"Pick a Folder")

        if directory:
            for filename in os.listdir(directory):
                self.listWidget.addItem(filename)
    '''

