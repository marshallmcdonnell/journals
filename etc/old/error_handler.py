#!/usr/bin/env python

import sys, re

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


