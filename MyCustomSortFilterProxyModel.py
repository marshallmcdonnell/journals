from PyQt4 import QtGui, QtCore

class CustomSortFilterProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(CustomSortFilterProxyModel, self).__init__(parent)
        self.filterHeaders = {}
        self.filterValues = {}
        self.filterFunctions = {} 

    def addFilterHeaders(self, header_name, row):
        self.filterHeaders[header_name] = row

    def setFilterValues(self, header_name, value):
        self.filterValues[header_name] = value
        self.invalidateFilter()

    def createStringCompare(self, row_num):
        return lambda r, s: (s in r[row_num])

    def createRegExpCompare(self, row_num):
        return lambda r, s: (re.search(s, r[row_num]))

    def createMin(self, row_num, minval):
        return lambda r, s: r[row_num] >= minval

    def createMax(self, row_num, maxval):
        return lambda r, s: r[row_num] <= maxval

    def setDateColumnsToConvert( self, colList ):
        self.string2date = colList

    def addFilterFunction(self, name, new_func):
        self.filterFunctions[name] = new_func
        self.invalidateFilter()

    def removeFilterFunction(self, name):
        if name in self.filterFunctions.keys():
            del self.filterFunctions[name]
            self.invalidateFilter()

    def filterAcceptsRow(self, row_num, parent):
        model = self.sourceModel()

        rowData  = []
        rowTypes = [ model.data(model.index(row_num,c,parent)).toPyObject() 
                     for c in range(model.columnCount()) ]

        for c in range(model.columnCount()):
            index = model.index(row_num,c,parent)
            pyobj = model.data(index).toPyObject()

            if c in self.string2date:
                if isinstance( pyobj, QtCore.QDate ):
                    pass
                else:
                    date, time = pyobj.split("T")
                    date = [ int(d) for d in str(date).split("-") ]
                    time = [ int(t) for t in str(time).split(":") ]
                    date = QtCore.QDate(date[0],date[1],date[2])
                    time = QtCore.QTime(time[0],time[1],time[2])
                    pyobj = QtCore.QDateTime(date,time)
            
            if isinstance(pyobj, QtCore.QString):
                rowData.append( str(model.data(index).toString()) )
            elif isinstance( pyobj, QtCore.QDateTime ):
                rowData.append( pyobj.date() )
            else:
                rowData.append( pyobj )

        tests = [func(rowData, self.filterValues[key])
                 for key, func in self.filterFunctions.items()]

        return not False in tests
