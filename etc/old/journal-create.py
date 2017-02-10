#!/usr/bin/env python


import numpy as np
import pandas as pd

import os, sys, re, argparse, datetime 

import error_handler
import scanClass
import utils

sys.path.append('/opt/Mantid/bin')

from mantid.simpleapi import LoadEventNexus 

_supported_formats = ['csv', 'hdf']

def pair(arg):
    return [str(x) for x in arg.split('-')]

def parseInt(number):
    try:
        return int(number)
    except ValueError, e:
        logging.info("Invalid run numbers: %s" % str(e))

    return 0

def getCurrentIPTS(ipts):
    # try to find the current IPTS from the current directory string
    currentdir=os.getcwd()
    foundipts=currentdir.find("IPTS")
    if (foundipts<0):
        error_handler.error("Current directory is not itself or in an IPTS directory.")
    elif foundipts>-1:
        foundslash=currentdir[foundipts:].find("/")
        if foundslash >-1:
            ipts.append(currentdir[foundipts+5:foundipts+foundslash])
        elif foundslash <0:
            ipts.append(currentdir[foundipts+5:])
    return ipts

def getAllIPTS(root):
    # find all accessible IPTS
    c=os.listdir(root)
    allipts=[arg for arg in c if arg[:5] == 'IPTS-']
    alliptsnr=[int((arg[5:])) for arg in c if arg[:5] == 'IPTS-']
    return alliptsnr

def getNumScansForIPTS( ipts, root ):

    path=root+'IPTS-'+str(ipts)
    if os.path.isdir(path+'/nexus'):
        scanList=os.listdir(path+'/nexus')
        return len(scanList)

    elif os.path.isdir(path+'/0'):
        scanList=os.listdir(path+'/0')
        return len(scanList)

    else:
        return 0

def printFoundIPTSinfo( ipts, root ):
    total = 0
    for x in ipts:
        nscans =  getNumScansForIPTS( x, root )
        print "     ", x, "w/", nscans, "# of scans"
        total += nscans
    print "Total # of scans:", total 
    print



def createScans( iptsList, root, scansFilter ):

    scans=[]
    for ipts in iptsList:

        path=root+'IPTS-'+str(ipts)

        # . NeXus directory

        if os.path.isdir(path+'/nexus'):

            scanList=os.listdir(path+'/nexus')

            if scansFilter:
                print "filtering on scans"
                scanRanges = utils.procNumbers(scansFilter)
                scanList = scanClass.filterOnScans( scanList, scanRanges )

            for NeXusFile in sorted(scanList):

                # FUTURE - multi-thread this part of code

                scan = int(re.search(r'\d+', NeXusFile).group())
                s = scanClass.Scan(iptsID=ipts, scanID=scan)

                print "File:", NeXusFile
                nx = LoadEventNexus(path+'/nexus/'+NeXusFile,MetaDataOnly=True)
                s.extractNexusData( nx, benchmark=False)
                scans.append(s)

            #ENDFOR

        #ENDIF

        elif os.path.isdir(path+'/0'):

            scanList=os.listdir(path+'/0')

            if scansFilter:
                scanRanges = utils.procNumbers(scansFilter)
                scanList = scanClass.filterOnScans( scanList, scanRanges )

            for scan in sorted(scanList):

                NeXusFile='NOM_'+scan+'_event.nxs'

                print "File:", NeXusFile
                if not os.path.exists(path+'/0/'+scan+'/NeXus/'+NeXusFile):
                    printWarning("Did not find NeXus file: "+NeXusFile+" in "+\
                                 "IPTS-"+str(ipts)+" with Scan ID:"+scan)
                else:    
                
                    s = scanClass.Scan(iptsID=ipts, scanID=scan)

                    nx = LoadEventNexus(path+'/0/'+scan+'/NeXus/'+NeXusFile,MetaDataOnly=True)
                    s.extractNexusData( nx, benchmark=False )
                    scans.append(s)

            #ENDFOR
            
        #ENDIF

        else:
            printWarning("No NeXus data found for IPTS-"+str(ipts))
                
    #ENDFOR

    return scans


#---Main Driver Function---

def createJournal( options ):

    #---create IPTS lists---

    ipts=[]
    if  options.current:
        ipts = getCurrentIPTS(ipts)
    
    if options.ipts:
        iptsranges=utils.procNumbers( options.ipts) 
        ipts = ipts + iptsranges

    if options.all:
        ipts=getAllIPTS(options.root)

    #---get intersection of User Input IPTS list and list of all acutal IPTS---
    ipts_all = getAllIPTS(options.root)
    ipts = [ x for x in ipts if x in ipts_all ]

    #---print helpful ipts, scans message---
    if options.verbose:
        print "I found these IPTS #'s:"
        printFoundIPTSinfo( ipts, options.root )


    # FUTURE - add core parallelism here for scan id search
    #        - would require a scanID, iptsID pair to then
    #          use in createScans for each core. 
    #        - would add thread parallelism inside createScans

    #---create Scans list based on IPTS #'s---
    scans = createScans( ipts, options.root, options.scans )

    #---filter the list---

    if options.dates:
        print "filtering on dates"
        dateRanges = []
        for start, stop in options.dates:
            a, b = getDateRange(start, stop )
            dateRanges.append( [a, b] )
        
        scans = scanClass.filterOnDate( scans,  dateRanges )


    for scan in scans:
        scan.printScanDate()

    if options.samples:
        print "filtering on samples"
        scans = scanClass.filterOnSamples( scans, options.samples )

    for scan in scans:
        scan.printScanSample()

    #---output the list---

    print "*** Pandas dataframe ***"
    headers = ['Scan','IPTS','time','starttime','stoptime',"PPs",'PC_pC','user','title']
    fields = ['scanID','iptsID','time','start_time','end_time',"total_pulses",'total_proton_charge','user','title']

    main_df = pd.DataFrame( )
    for header, field in zip( headers, fields ):
        if field in ['start_time', 'end_time']:
            datetimes = [ str(getattr(scan,field).datetime) for scan in scans ]
            main_df[header] = [ 'T'.join(dt.split()) for dt in datetimes ]
        else:
            main_df[header] = [ getattr( scan, field ) for scan in scans ]
        if header == 'time':
            print 'time:', main_df[header]
    
    main_df = main_df[headers]

    props = ['beamlineName', 'proton_charge']
    scans_dfs = {}
    for scan in scans:
        scans_dfs[scan] = pd.DataFrame()
        for prop in props:
            scans_dfs[scan][prop] = getattr( scan, prop )

    if options.output:
        fileformat, filename = options.output
        if fileformat == 'csv':
            main_df.to_csv(filename, index=False)

        if fileformat == 'hdf':
            if os.path.isfile(filename):
                os.remove(filename)
            f = pd.HDFStore(filename)
            f.put( 'main', main_df, data_columns=True)
            f.close()
            for scan in scans:
                filename='journal_scan'+str(scan.scanID)+'.hdf5'
                if os.path.isfile(filename):
                    os.remove(filename)
                f = pd.HDFStore(filename)
                f.put('props',scans_dfs[scan],data_columns=True)
                f.close()
                

if __name__ == '__main__':

    #---interpret command line options---
  
    usage="Make a python analog to readtitles"
    parser = argparse.ArgumentParser(description=usage, formatter_class=argparse.RawTextHelpFormatter )
    parser.add_argument("-a", "--all", default=False, action="store_true",
                      help="look in all accessible IPTS")
    parser.add_argument("-c", "--current", default=False, action="store_true",
                      help="look in the current IPTS")
    parser.add_argument("-R", "--root", default="/SNS/NOM/", type=str,
                        help="Root directory of instrument that contains IPTSs." )
    parser.add_argument("-i", "--IPTS", dest="ipts", nargs='*',
                      help="look in the specified IPTS")
    parser.add_argument("-s", "--scans", default=None,nargs='*',
                      help="look in the specified scan #'s (usage: -s 55555 19000-19005 ")
    parser.add_argument("-S", "--samples", default=None,nargs='*', 
                      help="look for the specified Samples ")
    parser.add_argument("-d", "--dates",  dest="dates", 
                      type=pair, action='append',
                      help="look by specified date ranges " + 
                           "(usage: -d <startDate>-<stopDate> w/ format: " + 
                           "MM/YYYY or MM/DD/YYYY")
    parser.add_argument("--output", nargs=2, type=str,  metavar=("FORMAT", "FILE"),
                           default=('hdf','journal_main.hdf5'),
                      help="output file format and filename. \n"
                           "Current supported formats:\n    " + ', '.join(_supported_formats) )
    parser.add_argument("-v", "--verbose", action='store_true',
                      help="Will print out helpful messages. May flood stdout with " + 
                           "info (mainly, for debugging.) ")

    options = parser.parse_args()


    # check conflict of searching in current directory or all directories
    scanClass.checkCurrent(options.current, options.all)

    # create the journal entry
    createJournal( options )

