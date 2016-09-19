#!/usr/bin/env python

from os import listdir,getcwd
import sys, re
from h5py import File
import pdb
from datetime import datetime

from error_handler import *

class dasGroup(object):
    def __init__(self):
        self.average_value = None
        self.average_value_error = None
        self.max_value = None
        self.min_value = None
        self.times      = None
        self.values     = None
        self.sum        = None

    def getDAS(self, run ):
        self.time_average =  run.timeAverageValue()
        #self.times = [ DateTime(x) for x in str(run.times) ]
        self.times = [ x for x in str(run.times) ]
        self.values = run.value

        stats = run.getStatistics()
        self.duration  = stats.duration
        self.mean  = stats.mean
        self.median  = stats.median
        self.maximum  = stats.maximum
        self.minimum  = stats.minimum
        self.standard_deviation  = stats.standard_deviation

    def printTemp(self):
        try:
            return self.average_value + " +- ", self.average_value_error
        except:
            return

class DateTime(object):
    def __init__(self, datetime=None):
        self.datetime = None
        
        if datetime:
            self.datetime = datetime

    def getDateTime(self, string):
        date, time = string.split('T')
        year, month, day = [ int(x) for x in date.split('-') ]
        hour, minute, second = [ int(float(x)) for x in time.split(':') ]
        self.datetime = datetime( year, month, day, hour=hour, minute=minute, second=second )
        return

    def printDateTime(self):
        return '%(mnth) 02d/%(d)02d/%(y)4d at %(h)02d:%(min)02d:%(s)02d' % \
               { 'mnth': self.datetime.month, \
                 'd':    self.datetime.day, \
                 'y':    self.datetime.year, \
                 'h':    self.datetime.hour, \
                 'min':  self.datetime.minute, \
                 's':    self.datetime.second }

    def isDateInRange(self, dateRange):
        begin, end = dateRange
        return (self >= begin and self <= end) 

def getDateRange(start, stop):
    startDate = DateTime()
    stopDate  = DateTime()

    if len(start.split('/')) == 2:
        month, year = start.split('/')
        startDate = datetime.datetime( year, month, 1 )
    elif len(start.split('/')) == 3:
        month, day, year = start.split('/')
        startDate = datetime.datetime( year, month, day )
    else:
        error("Incorrect start date format. Either MM/YYYY or MM/DD/YYYY")
    
    if len(stop.split('/')) == 2:
        month, year = stop.split('/')
        stopDate = datetime.datetime( year, month, 1 )
    elif len(stop.split('/')) == 3:
        month, day, year = stop.split('/')
        stopDate = datetime.datetime( year, month, day )
    else:
        error("Incorrect stop date format. Either MM/YYYY or MM/DD/YYYY")

    # check that start date < stop date
    if startDate > stopDate:
        error("For dates, stop date occurs before start date year.")

    return [startDate, stopDate]

class Sample(object):
    def __init__(self):
        self.name = None
        self.mass = None 
        self.chemical_formula = None
        self.description = None

    def getSampleFromItems(self,run, items=None):
        if items==None:
            error("Items object passed to getSampleFromItems is None.")

        for x in items:
            if 'Name' in x:
                self.name = run[x].value[0]
            if 'Mass' in x:
                self.mass = run[x].value[0]
            if 'Formula' in x:
                self.chemical_formula = run[x].value[0]
            if 'Description' in x:
                self.description = run[x].value[0]
        return
    
class Container(object):
    def __init__(self):
        self.type = None
        self.id   = None

    def getContainerFromItems(self, run, items=None):
        if items==None:
            error("Items object passed to getContainerFromItems is None.")

        for x in items:
            if 'Container' in x:
                self.type = run[x].value
        return
 
class User(object):
    def __init__(self):
        self.facility_user_id = None
        self.firstname = None
        self.lastname = None    


def benchTime( start, stop ):
    time = stop - start
    print time.seconds, "seconds",time.microseconds,"microseconds"
    return time

class Scan( object ):
    def __init__(self, iptsID=None, scanID=None ):
        self.iptsID       = iptsID
        self.scanID       = scanID
        self.start_time   = DateTime()
        self.end_time     = DateTime()
        self.title        = None
        self.beamlineName = None
        self.total_pulses = None
        self.proton_charge = None

        self.sample      = Sample()
        self.container   = Container()
        self.temp        = {} 
        self.chopper     = {} 
        self.freq        = dasGroup()
        self.proton_charge = dasGroup()

    def printScanTitle(self):
        return "IPTS-",self.iptsID, self.scanID, "Title:", self.title

    def printScanDate(self):
        print "IPTS-",self.iptsID, self.scanID, \
              "Began on:", self.start_time.printDateTime(), \
              "Ended on:", self.end_time.printDateTime()

    def printScanSample(self):
        print "IPTS-",int(self.iptsID), self.scanID, \
              "Sample:", self.sample.name,      \
              "Mass:", self.sample.mass,        \
              "Formula:", self.sample.chemical_formula, \
              "Form:", self.sample.description

    def printScanInfoLong(self):
        print
        print "IPTS:", self.iptsID, "Scan #:", self.scanID, "Scan Title:", self.title
        print 
        print "Sample:", self.sample.name
        print "    with Mass:", self.sample.mass,
        print "         Chemical Formula:", self.sample.chemical_formula
        print "         Form:", self.sample.nature
        print
        print "Began on:", self.start_time.printDateTime()
        print "Ended on:", self.end_time.printDateTime()
        print
        print "Beamline:", self.beamlineName
        print "Proton charge:", self.proton_charge
        print "Total pulses:", self.total_pulses
        print
        print "Container:", self.container.type, self.container.id
        print
        print "Sample temp. (K):", self.temp['sample'].printTemp()
        print "Cryo       actual temp. (K):", self.temp['cryostream']['actual'].printTemp()
        print "Cryostream target temp. (K):", self.temp['cryostream']['target'].printTemp()
        print "Cryostream temp. (K):", self.temp['cryostream']['temp'].printTemp()
        # ... need to add more but really for debugging 

    def getTemps(self, run, temps):
        self.temp['sample'] = {}
        self.temp['cryo'] = {}
        self.temp['cryostream'] = {}

        if temps == None:
            error("Temps object passed to getTemps is None.")

        for x in temps:

            if 'SampleTemp' in x:
                self.temp['sample'] = dasGroup()
                self.temp['sample'].getDAS(run[x])

            if 'Cryo' in x:
                if 'TempAcutal' in x:
                    self.temp['cryo']['actual'] = dasGroup()
                    self.temp['cryo']['actual'].getDAS(run[x])

            if 'Cryostream' in x:
                if 'TARGETTEMP' in x:
                    self.temp['cryostream']['target'] = dasGroup()
                    self.temp['cryostream']['target'].getDAS(run[x])
                elif 'TEMP' in x:
                    self.temp['cryostream']['temp'] = dasGroup()
                    self.temp['cryostream']['temp'].getDAS(run[x])
                
        return

    def getChoppers( self, run, choppers ):
        if choppers == None:
            error("Choppers object passed to getChoppers is None.")

        for x in choppers:
            if 'chopper' in x:
                chopperIndex = re.search(r'chopper(\d+)_', x).group(1)
                self.chopper[chopperIndex] = dasGroup()
                self.chopper[chopperIndex].getDAS( run[x] )
            elif 'ChopperStatus' in x:
                chopperIndex = re.search(r'ChopperStatus(\d+)', x).group(1)
                self.chopper[chopperIndex] = dasGroup()
                self.chopper[chopperIndex].getDAS( run[x] )
    

        return

    def extractNexusData(self, nx, benchmark=False):

        if benchmark:
            print "Loaded file"

        run = nx.getRun()

        # Times, title, and beamline

        if benchmark:
            print "getting times",
            start = datetime.now()

        self.start_time.getDateTime(run['start_time'].value)
        self.end_time.getDateTime(run['end_time'].value)
        self.title = nx.getTitle()
        self.beamlineName = nx.getInstrument().getName()

        if benchmark:
            stop = datetime.now()
            timeDelta = benchTime( start, stop )
        
        # Proton charge  information

        if benchmark:
            print "getting proton_info",
            start = datetime.now()

        self.proton_charge.getDAS(run['proton_charge'])
        self.total_pulses = len(self.proton_charge.values)

        if benchmark:
            stop = datetime.now()
            timeDelta = benchTime( start, stop )

        # Frequency  information

        if benchmark:
            print "getting frequency",
            start = datetime.now()

        self.freq.getDAS(run['frequency'])

        if benchmark:
            stop = datetime.now()
            timeDelta = benchTime( start, stop )

        # Sample information

        if benchmark:
            print "getting items",
            start = datetime.now()

        items = [x for x in run.keys() if 'ITEMS' in x]

        print run.keys()
        print items
        if items:
            self.sample.getSampleFromItems(run, items)
            self.container.getContainerFromItems(run, items)
       
        if benchmark:
            stop = datetime.now()
            timeDelta = benchTime( start, stop )

        # Temperature information

        if benchmark:
            print "getting temps",
            start = datetime.now()

        temps = [x for x in run.keys() if any( s in x for s in ('Temp','TEMP'))]
        print temps
        if temps:
            self.getTemps(run,temps)

        if benchmark:
            stop = datetime.now()
            timeDelta = benchTime( start, stop )

        # Chopper information

        if benchmark:
            print "getting choppers",
            start = datetime.now()

        choppers = [x for x in run.keys() if any( s in x for s in ('chopper', 'Chopper'))]
        print choppers
        if choppers:
            self.getChoppers(run, choppers)

        if benchmark:
            stop = datetime.now()
            timeDelta = benchTime( start, stop )

        return

def filterOnDate( scans, dateRanges ):

    newscans = []

    for scan in scans:
        added = False
        for dateRange in dateRanges:
            if scan.start_time.isDateInRange( dateRange ) and not added:
                newscans.append( scan )
                added = True
    return newscans

def filterOnScans( scans, scanRanges ):
    newscans = []

    if isinstance(scans, list):
        for scanName in scans:
            scan = int(re.search(r'\d+', scanName).group())
            if scan in scanRanges:
                newscans.append(scanName)

    else: 
        for scan in scans:
            if int(scan.scanID) in scanRanges:
                newscans.append(scan)

    return newscans

def filterOnSamples( scans, samples ):
    newscans = []
    for scan in scans:
        if scan.sample.name in samples:
            newscans.append(scan)    
    return newscans

