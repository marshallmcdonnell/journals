#!/usr/bin/env python


import numpy as np

from os import listdir,getcwd
import xml.etree.ElementTree as ET
import sys, re
import argparse 
from h5py import File
import pdb

# command line options

usage="Make a python analog to readtitles"

parser = argparse.ArgumentParser(description=usage )
parser.add_argument("-a", "--all", default=False, dest="all", action="store_true",
                  help="look in all accessible IPTS")
parser.add_argument("-c", "--current", default=False, dest="current", action="store_true",
                  help="look in the current IPTS")
parser.add_argument("-R", "--root", default="/SNS/NOM/", type=str,
                    help="Root directory of instrument that contains IPTSs." )
parser.add_argument("-I", "--IPTS", dest="ipts", nargs='*',
                  help="look in the specified IPTS")
parser.add_argument("-s", "--scans", default='0-99999',dest="scans",nargs='*',
                  help="look in the specified scan #'s (usage: -s 55555 19000-19005 ")
parser.add_argument("-S", "--Sample",dest="sample",
                  help="look for the specified Samples (not yet implemented...)")
parser.add_argument("-f", "--file", dest="file",default='los.txt',
                  help="output filename", metavar="FILE")
parser.add_argument("-n", "--nexus", dest="nexus",default='False',
                  help="read the run information from NeXuS", metavar="FILE")
parser.add_argument("-P", "--pydir", dest="pydir",default='./',
                  help="""Allows manual configuration of the directory 
                  where NOMpy resides""")

options = parser.parse_args()
pydir=options.pydir
sys.path.append(pydir)
from NOMpy import *


def printWarning(message):
    print
    print "*------------------------------------------------------------------*"
    print "WARNING:", message
    print "*------------------------------------------------------------------*"
    print 
    

def printError(message):
    print
    print "*------------------------------------------------------------------*"
    print "ERROR:", message
    print "*------------------------------------------------------------------*"
    print 

def error(message):
    printError(message)
    sys.exit()

def errorWithUsage(message):
    printError(message)
    print parser.print_help()
    sys.exit()

def checkCurrent( checkCurrent, checkAll ):
    if checkCurrent and checkAll:
        errorWithUsage("current (-c) and all (-a) both selected. Choose one.")

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
        self.temp['sample'] = dasGroup()
        self.temp['cryostream'] = {}
        self.temp['cryostream']['target'] = dasGroup()
        self.temp['cryostream']['actual'] = dasGroup()
        self.temp['cryostream']['temp'] = dasGroup()
        self.chopper     = {} 
        self.proton_charge_das = dasGroup()
        self.freq        = dasGroup()

    def printScanInfo(self):
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
        

def getAllIPTS(root):
    from os.path import abspath,lexists
# find all accessible IPTS
    c=listdir(root)
    allipts=[arg for arg in c if arg[:5] == 'IPTS-']
    alliptsnr=[int((arg[5:])) for arg in c if arg[:5] == 'IPTS-']
    return alliptsnr

def createScans( iptsList ):
    from os import listdir
    import pdb

    scans={}
    for ipts in iptsList:

        path=options.root+'IPTS-'+str(ipts)

        # . NeXus directory

        if os.path.isdir(path+'/nexus'):

            scanList=listdir(path+'/nexus')

            for NeXusFile in sorted(scanList):

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
                
                s.temp['sample'].getDAS(nx,'/entry/DASlogs/BL1B:SE:SampleTemp')
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

                scans[scan] = s

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
               

            #ENDFOR
            
        #ENDIF

        else:
            printWarning("No NeXus data found for IPTS-"+str(ipts))
                
    #ENDFOR

    return scans

        

def findscans(inipts, begin=4, end=9):
    from os import listdir
    import pdb

    allexp=[]
    whichipts=[]
    c=[]
    for ipts in inipts:
        try:
            c=listdir(options.root+'IPTS-'+ipts+'/0')
            allexp.extend(c)
            whichipts.extend([ipts]*len(c))
        except OSError:
            c=c
       
        try:
            c=listdir(options.root+'IPTS-'+ipts+'/nexus')
            c=[int(f[begin:end]) for f in c]
            allexp.extend(c)
            whichipts.extend([ipts]*len(c))
        except OSError:
            c=c
    return allexp,whichipts
  
#---interpret command line options---

filename=options.file
nexus=str2bool(options.nexus)

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

# FUTURE - would add parallelism here for search over IPTS

#---create Scan lists---
scans = createScans( ipts )
#ipts_scans=findscans(ipts)                            # Using input ipts #'s, returns the scans found (ipts_scans[0] ) and the associated ipts(ipts_scans[1])

'''
scanranges=interranges(options.scans)                 # returns scans based on the user range(s) specified (i.e. for 555, 997-999, returns [555, 997,998,999]
ascans=np.array([int(arg) for arg in ipts_scans[0]])  # nexus #'s / scan #'s
aipts=np.array([int(arg) for arg in ipts_scans[1]])   # IPTS #'s

mask=np.ones(len(ipts_scans[0]))== 0.                 # Initialize mask for scans to False for comparing if scans within range specified

for i in xrange(0,len(scanranges)):
    try:
        mask=(mask | (ascans == scanranges[i])) # does a BitWise-Or (|) operator comparing
                                                # if the mask == True and the ascans is a scanrange
    except IndexError:
        pass


#print ascans[mask],aipts[mask]
#raise Exception("STOP")

# these are the scans to use for searching over
scan_final=ascans[mask]
scan_final=sorted(scan_final)

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
