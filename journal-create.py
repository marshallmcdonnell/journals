#!/usr/bin/env python


import numpy as np

from os import listdir,getcwd
import xml.etree.ElementTree as ET
import sys
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
parser.add_argument("-H", "--home", default="/SNS/NOM/", type=str,
                    help="Home directory of instrument that contains IPTSs." )
parser.add_argument("-I", "--IPTS", dest="ipts",
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
        

def findacipts(NOMhome):
    from os.path import abspath,lexists
# find all accessible IPTS
    c=listdir(NOMhome)
    allipts=[arg for arg in c if arg[:5] == 'IPTS-']
    alliptsnr=[(arg[5:]) for arg in c if arg[:5] == 'IPTS-']
    return alliptsnr

def findscans(inipts):
    from os import listdir
    import pdb

    allexp=[]
    whichipts=[]
    c=[]
    for ipts in inipts:
        try:
            c=listdir('/SNS/NOM/IPTS-'+ipts+'/0')
            allexp.extend(c)
            whichipts.extend([ipts]*len(c))
        except OSError:
            c=c
       
        try:
            c=listdir('/SNS/NOM/IPTS-'+ipts+'/nexus')
            c=[int(f[4:9]) for f in c]
            allexp.extend(c)
            whichipts.extend([ipts]*len(c))
        except OSError:
            c=c
    return allexp,whichipts
  
#-----------------------interpret command line options -------------------------

filename=options.file
nexus=str2bool(options.nexus)

checkCurrent(options.current, options.all)

ipts=[]
if  options.current:
# try to find the current IPTS from the current directory string
    currentdir=getcwd()
    foundipts=currentdir.find("IPTS")
    if (foundipts<0) and (not options.ipts) :
        print "Could not identify the current IPTS"
        print "Continue with all:True and current: False"
        print "If that is not what is intented use the -I option"
        options.all=True
        options.current=False
        ipts.append('9999')
    elif foundipts>-1:
        foundslash=currentdir[foundipts:].find("/")
        if foundslash >-1:
            ipts.append(currentdir[foundipts+5:foundipts+foundslash])
        elif foundslash <0:
            ipts.append(currentdir[foundipts+5:])

    
if options.ipts:
    ipts=options.ipts.split(",")




NOMhome='/SNS/NOM'
if options.all:
    ipts=findacipts(NOMhome)

#print(ipts),type(ipts)

                       
tup_exp_ipts=findscans(ipts)  # appears to return tup_exp_ipts[0] == nexus #'s / scan #'s 
                              #    and associated tup_exp_ipts[1] == IPTS  #'s
scanranges=interranges(options.scans)  # returns a list of scans based on the range(s) specified (i.e. for 555, 997-999, returns [555, 997,998,999]
ascans=np.array([int(arg) for arg in tup_exp_ipts[0]])  # nexus #'s / scan #'s
aipts=np.array([int(arg) for arg in tup_exp_ipts[1]])   # IPTS #'s


''' DEBUG lines
zipped=zip(ascans, aipts)
for x, y in sorted( zipped, key = lambda t: 10000 < t[1] < 17000) :
    print "Scan: %(scan)05d IPTS: %(ipts)05d" % { "scan" : x, "ipts" : y }
'''

mask=np.ones(len(tup_exp_ipts[0]))== 0.                 # Initialize mask for scans to False for comparing if scans within range specified
#pdb.set_trace()

'''OLD CODE

for i in xrange(0,len(scanranges),2):
    try:
        mask=(mask | ((ascans >= scanranges[i]) & (ascans <= scanranges[i+1]))) # does a BitWise-Or (|) operator comparing
                                                                                # if the mask == True and the ascans is between the scan ranges specified
    except IndexError:
        pass
'''

for i in xrange(0,len(scanranges)):
    try:
        mask=(mask | (ascans == scanranges[i])) # does a BitWise-Or (|) operator comparing
                                                # if the mask == True and the ascans is a scanrange
    except IndexError:
        pass

zipped=zip(ascans[mask], aipts[mask])
for x, y in sorted( zipped, key=lambda t: t[1]  ) :
    print "Scan: %(scan)05d IPTS: %(ipts)05d" % { "scan" : x, "ipts" : y }


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
