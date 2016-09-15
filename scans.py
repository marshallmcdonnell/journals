#!/usr/bin/env python

from os import listdir,getcwd
import sys, re
from h5py import File
import pdb

from error_handler import *

class dasGroup(object):
    def __init__(self):
        self.average_value = None
        self.average_value_error = None
        self.max_value = None
        self.min_value = None
        self.times      = None
        self.values     = None

    def getDAS(self, nx, string):
        self.average_value =  nx[string]['average_value'][0]
        self.average_value_error =  nx[string]['average_value_error'][0]
        self.max_value =  nx[string]['maximum_value'][0]
        self.min_value =  nx[string]['minimum_value'][0]
        self.times =  nx[string]['time'][:]
        self.values =  nx[string]['value'][:]
        

    def printTemp(self):
        try:
            return self.average_value + " +- ", self.average_value_error
        except:
            return

class DateTime(object):
    def __init__(self):
        self.year = None
        self.month = None
        self.day = None
        self.hour = None
        self.minute = None
        self.second = None

    def getDateTime(self, string):
        date, time = string.split('T')
        self.year, self.month, self.day = date.split('-')
        self.hour, self.minute, self.second = time.split(':')
        return

    def printDateTime(self):
        return self.month + "/" + self.day + "/" + self.year + \
               " at " + self.hour + ":" + self.minute + ":" + self.second

    def isLessThan( self, upper ):
        if self.year < upper.year:
            return True
        if self.year == upper.year:
            if self.month < upper.month:
                return True
            if self.month == upper.month:
                if self.day <= upper.day:
                    return True
        return False 

    def isGreaterThan( self, lower ):
        if lower.year < self.year:
            return True
        if lower.year == self.year:
            if lower.month < self.month:
                return True
            if lower.month == self.month:
                if lower.day <= self.day:
                    return True
        return False 


    def isDateInRange(self, dateRange):
        begin, end = dateRange
        return (self.isGreaterThan(begin) and self.isLessThan(end) )

def getDateRange(start, stop):
    startDate = DateTime()
    stopDate  = DateTime()

    if len(start.split('/')) == 2:
        startDate.month, startDate.year = start.split('/')
    elif len(start.split('/')) == 3:
        startDate.month, startDate.day, startDate.year = start.split('/')
    else:
        error("Incorrect start date format. Either MM/YYYY or MM/DD/YYYY")
    
    if len(stop.split('/')) == 2:
        stopDate.month, stopDate.year = stop.split('/')
    elif len(stop.split('/')) == 3:
        stopDate.month, stopDate.day, stopDate.year = stop.split('/')
    else:
        error("Incorrect stop date format. Either MM/YYYY or MM/DD/YYYY")

    # check that start date < stop date
    if startDate.year > stopDate.year:
        error("For dates, stop date year occurs before start date year.")
    elif startDate.year == stopDate.year:
        if startDate.month > stopDate.month:
            error("For dates, stop date occurs month before start date month.")
        elif startDate.month == stopDate.month:
            if startDate.day > stopDate.day:
                error("For dates, stop date day occurs before start date day.")

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
        self.beamlineID   = None
        self.beamlineName = None
        self.proton_charge = None
        self.total_pulses = None

        self.sample      = Sample()
        self.container   = Container()
        self.temp        = {} 
        self.chopper     = {} 
        self.proton_charge_das = dasGroup()
        self.freq        = dasGroup()

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
        print "Beamline:", self.beamlineName, self.beamlineID
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
