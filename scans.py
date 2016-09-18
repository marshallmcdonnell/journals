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
        self.times = [ DateTime(x) for x in str(run.times) ]
        self.values = run.value

        stats = run.getStatistics()
        self.duration  = stats.duration
        self.mean  = stats.mean
        self.median  = stats.median
        self.maximum  = stats.maximum
        self.minimum  = stats.minimum
        self.standard_deviation  = stats.standard_deviation

    '''
    def getDAS(self, run ):
        self.average_value =  nx[string]['average_value'][0]
        self.average_value_error =  nx[string]['average_value_error'][0]
        self.max_value =  nx[string]['maximum_value'][0]
        self.min_value =  nx[string]['minimum_value'][0]
        self.times =  nx[string]['time'][:]
        self.values =  nx[string]['value'][:]
        self.sum = sum(self.values)
    '''
        

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
        return self.month + "/" + self.day + "/" + self.year + \
               " at " + self.hour + ":" + self.minute + ":" + self.second

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
        self.nature = None
    
class Container(object):
    def __init__(self):
        self.type = None
        self.id   = None

class User(object):
    def __init__(self):
        self.facility_user_id = None
        self.firstname = None
        self.lastname = None    


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
              "Start:", self.start_time.month, "-", self.start_time.day, "-", self.start_time.year, \
              "Stop:",  self.end_time.month,   "-", self.end_time.day,   "-", self.end_time.year 

    def printScanSample(self):
        print "IPTS-",int(self.iptsID), self.scanID, \
              "Sample:", self.sample.name,      \
              "Mass:", self.sample.mass,        \
              "Formula:", self.sample.chemical_formula, \
              "Form:", self.sample.nature

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
        print "Ended on:", self.start_time.printDateTime()
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
