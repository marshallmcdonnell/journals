#!/usr/bin/env python


import numpy as np

from os import listdir,getcwd
import xml.etree.ElementTree as ET
import sys, re
import argparse 
import datetime
import pdb

from error_handler import *
from scans         import *

sys.path.append('/opt/Mantid/bin')

from mantid.simpleapi import LoadEventNexus 

# command line options

def parseInt(number):
    try:
        return int(number)
    except ValueError, e:
        logging.info("Invalid run numbers: %s" % str(e))

    return 0


def procNumbers(numberList):
    # simply see if it is an integer
    try:
        return [int(numberList)]
    except ValueError and TypeError:
        pass

    # split on commas
    result = []
    for item in numberList:
        # if there is a dash then it is a range
        if "-" in item:
            item = [parseInt(i) for i in item.split("-")]
            item.sort()
            if item[0]:
                result.extend(range(item[0], item[1]+1))
        else:
            item = parseInt(item)
            if item:
                result.append(item)

    result.sort()
    return result


def pair(arg):
    return [str(x) for x in arg.split('-')]
  
usage="Make a python analog to readtitles"

parser = argparse.ArgumentParser(description=usage )
parser.add_argument("-a", "--all", default=False, action="store_true",
                  help="look in all accessible IPTS")
parser.add_argument("-c", "--current", default=False, action="store_true",
                  help="look in the current IPTS")
parser.add_argument("-R", "--root", default="/SNS/NOM/", type=str,
                    help="Root directory of instrument that contains IPTSs." )
parser.add_argument("-I", "--IPTS", dest="ipts", nargs='*',
                  help="look in the specified IPTS")
parser.add_argument("-s", "--scans", default=None,nargs='*',
                  help="look in the specified scan #'s (usage: -s 55555 19000-19005 ")
parser.add_argument("-S", "--samples", default=None,nargs='*', 
                  help="look for the specified Samples ")
parser.add_argument("-d", "--dates",  dest="dates", 
                  type=pair, action='append',
                  help="look by specified date ranges (usage: -d <startDate>-<stopDate> w/ format: MM/YYYY or MM/DD/YYYY")
parser.add_argument("-f", "--file", default='los.txt',
                  help="output filename", metavar="FILE")
parser.add_argument("-v", "--verbose", action='store_true',
                  help="Will print out helpful messages. May flood stdout with info (mainly, for debugging.) ")

options = parser.parse_args()

def getCurrentIPTS(ipts):
    # try to find the current IPTS from the current directory string
    currentdir=getcwd()
    foundipts=currentdir.find("IPTS")
    if (foundipts<0):
        error("Current directory is not itself or in an IPTS directory.")
    elif foundipts>-1:
        foundslash=currentdir[foundipts:].find("/")
        if foundslash >-1:
            ipts.append(currentdir[foundipts+5:foundipts+foundslash])
        elif foundslash <0:
            ipts.append(currentdir[foundipts+5:])
    return ipts

def getAllIPTS(root):
    from os.path import abspath,lexists
# find all accessible IPTS
    c=listdir(root)
    allipts=[arg for arg in c if arg[:5] == 'IPTS-']
    alliptsnr=[int((arg[5:])) for arg in c if arg[:5] == 'IPTS-']
    return alliptsnr

def getNumScansForIPTS( ipts ):
    from os import listdir
    from os.path import isdir
    import pdb

    path=options.root+'IPTS-'+str(ipts)
    if isdir(path+'/nexus'):
        scanList=listdir(path+'/nexus')
        return len(scanList)

    elif isdir(path+'/0'):
        scanList=listdir(path+'/0')
        return len(scanList)

    else:
        return 0

def printFoundIPTSinfo( ipts ):
    total = 0
    for x in ipts:
        nscans =  getNumScansForIPTS( x )
        print "     ", x, "w/", nscans, "# of scans"
        total += nscans
    print "Total # of scans:", total 
    print



def createScans( iptsList ):
    import os
    import pdb

    scans=[]
    for ipts in iptsList:

        path=options.root+'IPTS-'+str(ipts)

        # . NeXus directory

        if os.path.isdir(path+'/nexus'):

            scanList=os.listdir(path+'/nexus')

            if options.scans:
                print "filtering on scans"
                scanRanges = procNumbers(options.scans)
                scanList = filterOnScans( scanList, scanRanges )

            for NeXusFile in sorted(scanList):

                # FUTURE - multi-thread this part of code

                scan = int(re.search(r'\d+', NeXusFile).group())
                s = Scan(iptsID=ipts, scanID=scan)

                nx = LoadEventNexus(path+'/nexus/'+NeXusFile,MetaDataOnly=True)
                s.extractNexusData( nx, benchmark=False)
                scans.append(s)

            #ENDFOR

        #ENDIF

        elif os.path.isdir(path+'/0'):

            scanList=os.listdir(path+'/0')

            if options.scans:
                scanRanges = procNumbers(options.scans)
                scanList = filterOnScans( scanList, scanRanges )

            for scan in scanList:

                NeXusFile='NOM_'+scan+'_event.nxs'

                if not os.path.exists(path+'/0/'+scan+'/NeXus/'+NeXusFile):
                    printWarning("Did not find NeXus file: "+NeXusFile+" in "+\
                                 "IPTS-"+str(ipts)+" with Scan ID:"+scan)
                else:    
                
                    s = Scan(iptsID=ipts, scanID=scan)

                    nx = LoadEventNexus(path+'/0/'+scan+'/NeXus/'+NeXusFile,MetaDataOnly=True)
                    s.extractNexusData( nx, benchmark=False )
                    scans.append(s)

            #ENDFOR
            
        #ENDIF

        else:
            printWarning("No NeXus data found for IPTS-"+str(ipts))
                
    #ENDFOR

    return scans

#---interpret command line options---

filename=options.file

# check conflict of searching in current directory or all directories
checkCurrent(options.current, options.all)


#---create IPTS lists---

ipts=[]
if  options.current:
    ipts = getCurrentIPTS(ipts)
    
if options.ipts:
    iptsranges=procNumbers( options.ipts) 
    ipts = ipts + iptsranges

if options.all:
    ipts=getAllIPTS(options.root)

#---get intersection of User Input IPTS list and list of all acutal IPTS---
ipts_all = getAllIPTS(options.root)
ipts = [ x for x in ipts if x in ipts_all ]

#---print helpful ipts, scans message---
if options.verbose:
    print "I found these IPTS #'s:"
    printFoundIPTSinfo( ipts )


# FUTURE - add core parallelism here for scan id search
#        - would require a scanID, iptsID pair to then
#          use in createScans for each core. 
#        - would add thread parallelism inside createScans

#---create Scans list based on IPTS #'s---
print options.scans
print procNumbers(options.scans)
scans = createScans( ipts )

#---filter the list---

if options.dates:
    print "filtering on dates"
    dateRanges = []
    for start, stop in options.dates:
        a, b = getDateRange(start, stop )
        dateRanges.append( [a, b] )
        
    scans = filterOnDate( scans,  dateRanges )


for scan in scans:
    scan.printScanDate()

if options.samples:
    print "filtering on samples"
    scans = filterOnSamples( scans, options.samples )

for scan in scans:
    scan.printScanSample()

#---output the list---
error("Stop")
'''
f = open(filename, 'w')
fcsv = open('los.csv','w')
f.write("#Scan IPTS  time   starttime         PP's     PC/C          title\n")
fcsv.write("#Scan , IPTS ,  time ,  starttime    ,     PP's  ,   PC/pC   ,       title\n")


for i,currentexp in enumerate(scan_final):
    iptsnr=str(aipts[mask][i])
    scannr=str(currentexp)

    preNeXusname='/SNS/NOM/IPTS-'+ iptsnr + '/0/' + scannr 
    preNeXusname+='/preNeXus/NOM_' + scannr +'_runinfo.xml'

    Starttime='Not found'
    preNeXusstat = True
    try:
        f1=open(preNeXusname,'r')
        for line in f1.readlines():
            a=line.find('<AcceleratorPulses>')
            if a >0:
                o=line.find('</AcceleratorPulses>')
                AccelP=line[a+len('<AcceleratorPulses>'):o]
            a=line.find('<PCurrent units="pC">')
            if a >0:
                o=line.find('</PCurrent>')
                Pchar=line[a+len('<PCurrent units="pC">'):o]
            a=line.find('<Title>')
            if a >0:
                o=line.find('</Title>')
                Exptitle=line[a+len('<Title>'):o]
            a=line.find('<StartTime>')
            if a >0:
                o=line.find('</StartTime>')
                Starttime=line[a+len('<StartTime>'):o-10]               
        f1.close
    except IOError:
        AccelP="99999"
        Pchar="99999"
        Exptitle="Not found"
        preNeXusstat = False


    NeXusdir='/SNS/NOM/IPTS-'+ iptsnr + '/nexus/'
    NeXusfile=NeXusdir+'NOM_'+scannr+'.nxs.h5'
    NeXusstat = True

    try:
        f1=open(NeXusfile,'r')
        f1.close()
       
        nf=File(NeXusfile,'r')
        Pchar=str(nf['/entry/proton_charge'][0])
        AccelP=str(nf['/entry/total_pulses'][0])
        try:
            Exptitle=str(nf['/entry/title'][0])
        except KeyError:
            Exptitle='No title NeXus'
        Starttime=str(nf['/entry/start_time'][0])[0:19]
    except IOError:
        NeXusstat = False
        pass

    minutes=int(float(AccelP)/3600.)
    minutes=str(minutes)+ 'min'
    Pchar=str(int(float(Pchar)*1e-9)/1000.)

    outstring=scannr + ' ' + iptsnr + ' ' + minutes + ' ' +Starttime+' '+ AccelP + ' ' + Pchar
    outstring+= ' ' + Exptitle.replace(',','') +  '\n'
    #    print outstring,Pchar,Exptitle
    f.write(outstring)
    outstringcsv=scannr + ', ' + iptsnr + ', ' + minutes + ', ' +Starttime+', '+ AccelP + ', ' + Pchar
    outstringcsv+= ',' + Exptitle.replace(',','') + '\n'
        #    print outstring,Pchar,Exptitle
    fcsv.write(outstringcsv) 
f.close()
fcsv.close()
'''
