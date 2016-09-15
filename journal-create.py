#!/usr/bin/env python


import numpy as np

from os import listdir,getcwd
import xml.etree.ElementTree as ET
import sys, re
import argparse 
from h5py import File
import pdb

from error_handler import *
from scans         import * 

# command line options

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
parser.add_argument("-P", "--pydir", default='./',
                  help="""Allows manual configuration of the directory 
                  where NOMpy resides""")
parser.add_argument("-v", "--verbose", action='store_true',
                  help="Will print out helpful messages. May flood stdout with info (mainly, for debugging.) ")

options = parser.parse_args()
pydir=options.pydir
sys.path.append(pydir)
from NOMpy import *

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
    import pdb

    path=options.root+'IPTS-'+str(ipts)
    if os.path.isdir(path+'/nexus'):
        scanList=listdir(path+'/nexus')
        return len(scanList)

    elif os.path.isdir(path+'/0'):
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
    from os import listdir
    import pdb

    scans=[]
    for ipts in iptsList:

        path=options.root+'IPTS-'+str(ipts)

        # . NeXus directory

        if os.path.isdir(path+'/nexus'):

            scanList=listdir(path+'/nexus')

            for NeXusFile in sorted(scanList):

                # FUTURE - multi-thread this part of code

                scan = int(re.search(r'\d+', NeXusFile).group())
                s = Scan(iptsID=ipts, scanID=scan)
                nx=File(path+'/nexus/'+NeXusFile,'r')
                
                s.start_time.getDateTime(str(nx['/entry/start_time'][0])[0:19])
                s.end_time.getDateTime(str(nx['/entry/end_time'][0])[0:19])
                s.title = str(nx['/entry/title'][0])
                s.beamlineID = str(nx['/entry/instrument/beamline'][0])
                s.beamlineName = str(nx['/entry/instrument/name'][0])
                s.proton_charge = float(nx['/entry/proton_charge'][0])
                s.total_pulses = int(nx['/entry/total_pulses'][0])
                s.sample.name = str(nx['/entry/sample/name'][0])
                s.sample.mass = str(nx['/entry/sample/mass'][0])
                s.sample.chemical_formula = str(nx['/entry/sample/chemical_formula'][0])
                s.sample.nature = str(nx['/entry/sample/nature'][0])
                if '/entry/sample/container_id' in nx:
                    s.container.id   = str(nx['/entry/sample/container_id'][0])
                if '/entry/sample/container_name' in nx:
                    s.container.type = str(nx['/entry/sample/container_name'][0])
                
                s.temp['sample'] = dasGroup()
                s.temp['sample'].getDAS(nx,'/entry/DASlogs/BL1B:SE:SampleTemp')
                s.temp['cryostream'] = {}
                s.temp['cryostream']['target'] = dasGroup()
                s.temp['cryostream']['actual'] = dasGroup()
                s.temp['cryostream']['temp'] = dasGroup()
                s.temp['cryostream']['actual'].getDAS(nx,'/entry/DASlogs/BL1B:SE:Cryo:TempActual')
                s.temp['cryostream']['target'].getDAS(nx,'/entry/DASlogs/BL1B:SE:Cryostream:TARGETTEMP')
                s.temp['cryostream']['temp'].getDAS(nx,'/entry/DASlogs/BL1B:SE:Cryostream:TEMP')

                s.proton_charge_das.getDAS(nx,'/entry/DASlogs/proton_charge')
                if '/entry/DASlogs/chopper1_TDC' in nx:
                    s.chopper['1'] = dasGroup()
                    s.chopper['1'].getDAS(nx,'/entry/DASlogs/chopper1_TDC')
                if '/entry/DASlogs/chopper2_TDC' in nx:
                    s.chopper['2'] = dasGroup()
                    s.chopper['2'].getDAS(nx,'/entry/DASlogs/chopper2_TDC')
                if '/entry/DASlogs/chopper3_TDC' in nx:
                    s.chopper['3'] = dasGroup()
                    s.chopper['3'].getDAS(nx,'/entry/DASlogs/chopper3_TDC')
                s.freq.getDAS(nx,'/entry/DASlogs/frequency')

                scans.append(s)

            #ENDFOR

        #ENDIF

        elif os.path.isdir(path+'/0'):

            scanList=listdir(path+'/0')

            for scan in scanList:

                NeXusFile='NOM_'+scan+'_event.nxs'

                if not os.path.exists(path+'/0/'+scan+'/NeXus/'+NeXusFile):
                    printWarning("Did not find NeXus file: "+NeXusFile+" in "+\
                                 "IPTS-"+str(ipts)+" with Scan ID:"+scan)
                else:    
                
                    s = Scan(iptsID=ipts, scanID=scan)
                    nx=File(path+'/0/'+scan+'/NeXus/'+NeXusFile,'r')
                
                    s.start_time.getDateTime(str(nx['/entry/start_time'][0])[0:19])
                    s.end_time.getDateTime(str(nx['/entry/end_time'][0])[0:19])
                    s.title = str(nx['/entry/title'][0])
                    s.beamlineID = str(nx['/entry/instrument/beamline'][0])
                    s.beamlineName = str(nx['/entry/instrument/name'][0])
                    s.proton_charge = float(nx['/entry/proton_charge'][0])
                    s.total_pulses = int(nx['/entry/total_pulses'][0])
                    s.sample.name = str(nx['/entry/sample/name'][0])
                    s.sample.mass = str(nx['/entry/sample/mass'][0])
                    s.sample.chemical_formula = str(nx['/entry/sample/chemical_formula'][0])
                    s.sample.nature = str(nx['/entry/sample/nature'][0])
                    s.container.type = str(nx['/entry/sample/container_identifier'][0])
                    s.container.id = str(nx['/entry/sample/container_identifier'][0])
                    s.proton_charge_das.getDAS(nx,'/entry/DASlogs/proton_charge')
                    if '/entry/DASlogs/ChopperStatus1' in nx:
                        s.chopper['1'] = dasGroup()
                        s.chopper['1'].getDAS(nx,'/entry/DASlogs/ChopperStatus1')
                    if '/entry/DASlogs/ChopperStatus2' in nx:
                        s.chopper['2'] = dasGroup()
                        s.chopper['2'].getDAS(nx,'/entry/DASlogs/ChopperStatus2')
                    if '/entry/DASlogs/ChopperStatus3' in nx:
                        s.chopper['3'] = dasGroup()
                        s.chopper['3'].getDAS(nx,'/entry/DASlogs/ChopperStatus3')
                    s.freq.getDAS(nx,'/entry/DASlogs/frequency')
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
    iptsranges=interranges( options.ipts)  # returns a list of ipts based on the range(s) specified (i.e. for 555, 997-999, returns [555, 997,998,999]
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
scans = createScans( ipts )

#---filter the list---

print options.dates
if options.dates:
    dateRanges = []
    for start, stop in options.dates:
        a, b = getDateRange(start, stop )
        dateRanges.append( [a, b] )
        
    scans = filterOnDate( scans,  dateRanges )


for scan in scans:
    scan.printScanDate()
print options.dates

if options.scans:
    scanRanges = interranges(options.scans)
    scans = filterOnScans( scans, scanRanges )


for scan in scans:
    scan.printScanSample()
print options.scans

if options.samples:
    scans = filterOnSamples( scans, options.samples )

for scan in scans:
    scan.printScanSample()
print options.samples

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
