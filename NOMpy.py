import os

def findcurrentipts():

    """ Return the current IPTS number as a string. Assumes that you are located
    somewhere on the IPTS directory tree, preferably the shared directory
    """

    from os import getcwd

    currentdir=getcwd()
    foundipts=currentdir.find("IPTS")
    if (foundipts<0):
        print "Could not identify the current IPTS"
        ipts='9999'
    elif foundipts>-1:
        foundslash=currentdir[foundipts:].find("/")
        if foundslash >-1:
            ipts=currentdir[foundipts+5:foundipts+foundslash]
        elif foundslash <0:
            ipts=currentdir[foundipts+5:]
    return ipts

#    """ Return the current IPTS number as a string. Assumes that you are located
#    somewhere on the IPTS directory tree, preferably the shared directory
#    """
#    currentdir=os.getcwd()
#    ipts=9999
#
#    if "IPTS" in currentdir:
#        for level in curcurrentdir.split('/'):
#            if level.startswith("IPTS-"):
#                ipts=int(level[5:])#
#
#    if ipts == 9999:
#        print "Could not identify the current IPTS"
#
#    return ipts
#

def missing_all(allfiles):
    from os import path
    from subprocess import Popen
    import shlex
    from time import sleep
    alldir='./'
    if path.isdir('all_files'):
        alldir='all_files/'
    bindir='./'
    if path.isdir('binfiles'):
        bindir='binfiles/'
    for allfile in allfiles:
        if not test_fileexist([allfile],alldir):
            print 'Missing allfile: '+allfile
            missing_scan=allfile[3:8]
            if allfile[9]=='g':
                lookforbin='bin'+missing_scan+'_1.bat'
            elif True:
                lookforbin='bin'+missing_scan+'_0.bat'
            if test_fileexist([lookforbin],bindir):
                print 'but binfile: '+lookforbin+' exists'
                print "I'll try to run it, but it may not lead anywhere"
                Lline='xterm -e nice idl '+bindir+lookforbin+' &'
                Popen(shlex.split(Lline))
                while not test_fileexist([allfile],alldir):
                    sleep(10)
            elif True:
                print 'nor does binfile: '+lookforbin
                exit()

def delete_old_files(oldfiles,indir):
    from os import listdir,remove,path
    from time import sleep
    import pdb

    print '*************************************************'
    print '*                                               *'
    print '*   Deletes previous all and bin files in 10s   *'
    print '*  Press cntr-c if that is not what is intended *'
    print '*                                               *'
    print '*************************************************'
    sleep(10)
            
    for index,oldfile in enumerate(oldfiles):
        files=listdir(indir[index])
        for file in files:
            if file.startswith(oldfile):
                if not path.isdir(indir[index]+file):
                    Lline='rm -i '+indir[index]+file
                    print Lline
                    remove(indir[index]+file)


def parse_ndis(line):

    try:
        list1=line.split('#')[0]
    except IndexError:
        pass
    list1=list1.strip()
    list1=list1.split(',')
    return list1

def cleanup_files(flist):
    import os
    for filename in flist:
        if os.path.exists(filename):
            os.remove(filename)
def KroneckerDelta(i,j):
    KD=0
    if i==j:
        KD=1
    return KD

def findanyscan(scantofind):

    from os import listdir,getcwd
    import pdb

    NOMdir=listdir('/SNS/NOM')


    for ipts in NOMdir:
        if ipts[0:4] == 'IPTS':
	    print ipts
            try:
                scans=listdir('/SNS/NOM/'+ipts+'/0')
            except OSError:
                scans=[]
#            pdb.set_trace()
            if str(scantofind) in scans:
                return ipts[5::]
    print 'Did not find scan '+str(scantofind)
    return '9999'

def mod_time(filetocheck):
    import os, datetime
    t = os.path.getmtime(filetocheck)
    return datetime.datetime.fromtimestamp(t)	

def scandatetime(depth):

    import os
    import datetime
    import pdb	

    NOMdir=os.listdir('/SNS/NOM')


    ipts_list = [ (ipts, mod_time('/SNS/NOM/'+ipts)) for ipts in NOMdir if ipts[0:4] == 'IPTS']
    ipts_list.sort( key=lambda	x:x[1], reverse=True )		
    for ipts in ipts_list[0:depth]:
	print ipts[1], ipts[0]
    return 'These are the '+str(depth)+' most recent.'



def read_MADinput(MADinp):
    MADlib={}
    found_MADinput=False

    try:
        if os.path.exists(MADinp):
            handle=open(MADinp)
            lines=handle.readlines()
            handle.close()

            for line in lines:
                MADlib[line.split()[0]]=line.split()[1]
            found_MADinput=True
    except IOError:
        print 'Oh dear, no exp.ini. How am I going to do this?'

    # return null result if things don't work
    return (found_MADinput, MADlib)

def sendmail(address,title,body):
    from os import popen
    SENDMAIL='mail'
    p = popen("%s -t" % SENDMAIL, "w")
    p.write("To: "+address+"\n")
    p.write("Subject: "+title+"\n")
    p.write("\n") # blank line separating headers from body
    p.write(body+"\n")
    sts = p.close()

def read_losinput(losinp):
    loslib={}
    found_losinput=False

    try:
        if os.path.exists(losinp):
            f=open(losinp)
            lines=f.readlines()
            f.close()

            loslib[lines[0].split()[0]]=lines[0].split()[1]
            loslib[lines[1].split()[0]]=lines[1].split()[1].split(',')

            found_losinput=True
    except IOError:
        print 'Oh dear. How am I going to do this.'

    return (found_losinput,loslib)

def str2bool(v):
    # already boolean (really stupid that you have to do that)
    if type(v) == type(True):
        return v
    # or not
    return v.lower() in ("yes", "true", "t", "1",'uh-huh','yeah','ja','oui','jawohl')


def findscan(ipts,scannr):

    """ Looks for the presence of scan (scannr) in /SNS/NOM/IPTS-ipts/0
    and checks pro the presence of 6 files in /SNS/NOM/IPTS-ipts/0/preNeXus
    """

    from os import listdir,path

    necessary_files=['NOM_'+scannr+'_bmon_histo.dat',
                    'NOM_'+scannr+'_cvinfo.xml',
                    'NOM_'+scannr+'_pulseid.dat',
                    'NOM_'+scannr+'_runinfo.xml',
                    'NOM_'+scannr+'_neutron_event.dat',
                    'NOM_beamtimeinfo.xml']
    necessary_nexus=['NOM_'+scannr+'.nxs.h5']
#    if int(ipts)<>9999:
#    dirpath='/SNS/NOM/IPTS-'+str(ipts)+'/0'
#        filesindir = [f for f in listdir(dirpath)]
#        filesinnexus =[f for f in listdir(dirpathNeXuS)]
#        found=scannr in filesindir 
#    elif True:
#        found=False
    prenexusdir='/SNS/NOM/IPTS-'+str(ipts)+'/0/'+scannr+'/preNeXus'
    nexusdir='/SNS/NOM/IPTS-'+str(ipts)+'/nexus'
    if path.isdir(prenexusdir):
        print path.isdir(prenexusdir)
        found=test_fileexist(necessary_files,prenexusdir)
    elif path.isdir(nexusdir):
        found=test_fileexist(necessary_nexus,nexusdir)
    else:
        found=False
    return found

def find_Nprocess(procname):
    import psutil
    process_names=psutil.get_process_list() 
    names=[]
    for p in process_names:
        try:
            names.append(p.name())
        except psutil.NoSuchProcess:
            pass
    n_proc=len([p for p in names if procname in p])

    return n_proc

def search_new_files_16B(scan1,scanl,ipts):

    """ look for files in /SNS/NOM/IPTS-xxxx/0 that neither have a corresponding
    bin file or all file or is an equilibration scan
    """

    from os import listdir,path
    import pdb

    dirpath='/SNS/NOM/IPTS-'+str(ipts)+'/nexus'
    filesindir = [ (f[4:9]) for f in listdir(dirpath)]
    gescan1=[f for f in filesindir if (int(f) >=int(scan1) and int(f) <=int(scanl))]
#    pdb.set_trace()
    bindir='./'
    if path.isdir('binfiles'):
        bindir='binfiles/'
    alldir='./'
    if path.isdir('all_files'):
        alldir='all_files/'

    binfiles = [ f[3:8] for f in listdir(bindir) if f[0:3]=='bin']
    allfiles = [ f[3:8] for f in listdir(alldir) if f[0:3]=='all']
    new_files=[]
    for scan in gescan1:
        scan=str(scan)
        NeXuSfile='/SNS/NOM/IPTS-'+str(ipts)+'/nexus/NOM_'+scan+'.nxs.h5'
        if not ((scan in binfiles) or (scan in allfiles) or is_eq_scan_16B(NeXuSfile)):
#            if test_scan_complete(ipts,int(scan)):
            new_files.append(scan)
    return(new_files)

def test_scan_complete(ipts,scan):
    from os import path,listdir
    from time import sleep
    NeXuSpath='/SNS/NOM/IPTS-'+str(ipts)+'/nexus/'
    nexusfiles = [ int(f[4:9]) for f in listdir(NeXuSpath) if f[0:4]=='NOM_']
    return(scan <= max(nexusfiles)-1)

def search_new_files(scan1,scanl,ipts):

    """ look for files in /SNS/NOM/IPTS-xxxx/0 that neither have a corresponding
    bin file or all file or is an equilibration scan
    """

    from os import listdir,path
    import pdb

    dirpath='/SNS/NOM/IPTS-'+str(ipts)+'/0'
    filesindir = [ int(f) for f in listdir(dirpath)]
    gescan1=[str(f) for f in filesindir if (f >=int(scan1) and f <=int(scanl))]
    #   pdb.set_trace()
    bindir='./'
    if path.isdir('binfiles'):
        bindir='binfiles/'
    alldir='./'
    if path.isdir('all_files'):
        alldir='all_files/'

    binfiles = [ f[3:8] for f in listdir(bindir) if f[0:3]=='bin']
    allfiles = [ f[3:8] for f in listdir(alldir) if f[0:3]=='all']
    new_files=[]
    for scan in gescan1:
        if not ((scan in binfiles) or (scan in allfiles) or is_eq_scan(scan)):
            new_files.append(scan)
    return(new_files)

def search_failed():

    """ look for scans for which analysis failed as measured by the size of the all file
    """

    from os import listdir,stat
    import shlex
    import pdb
    from subprocess import Popen
    from time import sleep

    while True:
        failed_again=[]
        alllong = [ f for f in listdir('.') if f[0:3]=='all']
        failedg =  [ f for f in alllong if stat(f).st_size < 16000 and f[8:9] == 'g']
        failedp = [ f for f in alllong if stat(f).st_size < 3000 and f[8:9] <> 'g']
        newfailedg=[ f for f in failedg if not f in failed_again]
        newfailedp=[ f for f in failedg if not f in failed_again]
        new_files=[]
        for newfailed in newfailedg:
            cleanup_files([newfailed])
            if  find_Nprocess('idl') > 5:
                print 'There are '+str(find_Nprocess('idl'))+' idl processes. Waiting' 
            while find_Nprocess('idl') > 5:
                sleep(15)
            Lline = 'xterm -e nice idl bin'+newfailed[3:8]+'_1.bat'
            Popen(shlex.split(Lline))
            failed_again.append(newfailed)
            print newfailed
        for newfailed in newfailedp:
            cleanup_files([newfailed])
            if  find_Nprocess('idl') > 5:
                print 'There are '+str(find_Nprocess('idl'))+' idl processes. Waiting' 
            while find_Nprocess('idl') > 5:
                sleep(15)
            Lline = 'xterm -e nice idl bin'+newfailed[3:8]+'_0.bat'
            Popen(shlex.split(Lline))
            print newfailed
    return()

def find_backnr(template):
    f=open(template,'r')
    lines=f.readlines()
    for line in lines:
        pos=line.find('back')
        if pos >0:
            try:
                back_nr=int(line[pos+10:pos+14])
            except ValueError:
                back_nr=int(line[pos+10:pos+15])
    return back_nr


def runmakebin(listofscans,MTc=None,correct=False,sample_name=None,alltemplates=None,force=False,ipts=None,nexus=None,xwindow=None,pydir='/SNS/users/zjn/pytest'):
    import glob
    from subprocess import Popen
    import shlex
    from time import sleep
    import pdb
    from os import path

    if not alltemplates:
        alltemplates=glob.glob("bin_*")
    if not ipts:
        ipts=findcurrentipts()
    back_nrs=[]
#    for template in alltemplates:
#        back_nr=find_backnr(template)
#        back_nrs.append(back_nr)
    runbin=True
    if not alltemplates:
        raise  NoTemplateError
    if len(alltemplates)*len(listofscans) > 20:
        print str(len(alltemplates)*len(listofscans))+" Processes shouldn't be"
        print "run simultaneously. Binfiles created but not run"
        runbin=False
    bindir='./'
    if path.isdir('binfiles'):
        bindir='binfiles/'
                  


    for index,scan in enumerate(listofscans):
###        if not is_eq_scan(scan):
        if type(scan)<>'str':
            scan=str(scan)
        for template in alltemplates:
            f=open(template,'r')
            lines=f.readlines()
            f.close()
            newlines=[]
            for line in lines:
                line=line.replace("9999",scan)
                newlines.append(line)
            bincount=0
            existence=['a']
            while existence:
                lookforname=bindir+"bin"+scan+'_'+str(bincount)+'.bat'
                existence=glob.glob(lookforname)
                bincount+=1
            f=open(lookforname,'w')
            for line in newlines:
                f.write(line)
            f.close()
                #            pdb.set_trace()
            if nexus:
                necessary_files=['NOM_'+scan+'.nxs.h5']
                while not test_fileexist(necessary_files,'/SNS/NOM/IPTS-'+ipts+'/nexus'):
                    sleep(5)
            elif True:
                necessary_files=['NOM_'+scan+'_bmon_histo.dat','NOM_'+scan+'_pulseid.dat','NOM_'+scan+'_neutron_event.dat','NOM_'+scan+'_cvinfo.xml']
                while not test_fileexist(necessary_files,'/SNS/NOM/IPTS-'+ipts+'/0/'+scan+'/preNeXus'):
                    sleep(5)

# possible add something to ensure complete transfer

            if runbin or force:
                title='IDL for scan'+scan+ 'using template '+template
                args=''
                if xwindow:
                    args='xterm -T "'+title+'" -e'
                args=args+' nice -10 idl '
                args=shlex.split(args+lookforname)
                Popen(args)
            if correct:
                (has_properties,sampleid)=with_properties(scan,pydir=pydir)
                if has_properties:
                    Lline=''
                    if xwindow:
                        Lline='xterm -e '
                    Lline+='run_correct.py -f '+sample_name+'.ini'
                    Popen(shlex.split(Lline))

def run_diamond(ipts,diascan,calibrated=0):

    """Start an IDL process that bins diamond data
    with high resolution for
    later use by the IDL routine calibrate or visalign"""

    from subprocess import Popen
    import shlex

    diascans=interranges(diascan)
    if len(diascans) > 1:
        namecali='9998'
    elif True:
        namecali=str(diascans[0])
    if not calibrated:
        f=open("run_"+diascan+".bat","w")
        print>> f,"@idlstart"
        line="qbinning,hdia,ipts,[scan],maxq=20,deltaq=0.002,usecal=0,sil=1,"
        line+="normfactor=nf"
    elif True:
        f=open("run_"+diascan+"c.bat","w")
        print>> f,"@idlstart"
        line="qbinning,hdia,ipts,[scan],usecal=1"
        line+=",maxq=20,deltaq=0.002,calfile='nomad_namecali.calfile',sil=1,"
        line+="normfactor=nf"

    line=line.replace('scan',diascan)
    line=line.replace('ipts',ipts)
    line=line.replace('namecali',namecali)


    print>>f,line
    if not calibrated:
        print>>f,"save,hdia,nf,filen='all"+namecali+"hr.dat'"
        lline=  'xterm -T "Produce NOM'+namecali+'hr.dat (dia)"+ -e idl run_'
        lline+=diascan+'.bat'
    elif True:
        print>>f,"save,hdia,nf,filen='all"+namecali+"hrc.dat'"
        lline=  'xterm -T "Produce NOM'+namecali+'hrC.dat (dia)"+ -e idl run_'
        lline+=namecali+'c.bat'
    print>>f,"exit"
    f.close()
    args=shlex.split(lline)
    Popen(args)

def run_diabg(ipts,bgscan,diascan='12345',calibrated=0):

    """Start an IDL process that bins diamond background data with high
    resolution for later use by the IDL routine calibrate"""

    from subprocess import Popen
    import shlex

    diascans=interranges(diascan)
    if len(diascans) > 1:
        namecali='9998'
    elif True:
        namecali=str(diascans[0])
    bgscans=interranges(bgscan)
    if len(bgscans) > 1:
        namebg='9997'
    elif True:
        namebg=str(bgscans[0])

    if not calibrated:
        f=open("run_"+namebg+".bat","w")
        print>> f,"@idlstart"
        line="qbinning,hback,ipts,[scan],usecal=0,maxq=20,deltaq=0.002"
        line+=",sil=1,normfactor=nf"
    elif True:
        f=open("run_"+namebg+"c.bat","w")
        print>> f,"@idlstart"
        line="qbinning,hback,ipts,[scan],usecal=1,maxq=20,deltaq=0.002"
        line+=",calfile='nomad_namecali.calfile',sil=1,normfactor=nf"
        line=line.replace('namecali',namecali)
    line=line.replace('scan',bgscan)
    line=line.replace('ipts',ipts)

    print>>f,line
    if not calibrated:
        print>>f,"save,hback,nf,filen='all"+namebg+"hr.dat'"
        lline='xterm -T "Produce NOM'+namebg+'hr.dat (bg)"+ -e idl run_'
        lline+=bgscan+'.bat'
    elif True:
        print>>f,"save,hback,nf,filen='all"+namebg+"hrc.dat'"
        lline='xterm -T "Produce NOM'+namebg+'hrc.dat (bg)"+ -e idl run_'
        lline+=namebg+'c.bat'
    print>>f,"exit"
    f.close()
    args=shlex.split(lline)
    Popen(args)

def next_binfile(scan):

    """choose next available bin file
    """

    import glob

    bincount=0
    existence=['a']
    while existence:
        lookforname="bin"+scan+'_'+str(bincount)+'.bat'
        existence=glob.glob(lookforname)
        bincount+=1
    return lookforname

def test_fileexist(necessary_files,indir):
    """are all files in the list necessary_files present in the current
    directory"""
    if not indir:
        indir='.'

    from os import listdir

    a=listdir(indir)
    allexist=True
    for necessary_file in necessary_files:
        allexist=allexist and (necessary_file in a)
    return allexist

def interranges(scanranges):
    """interpret scan ranges that have the form '1000-1004,1008'
    and creates a list of start-stops"""
    from numpy import array,arange
    import pdb
    #scans=scanranges.split(',') 
    scans=scanranges
    scan_s_s=[]
    scanlist=[]
    how_many=[]
    #pdb.set_trace()
    for scanrangeelement in scans:

        if len(scanrangeelement)<6: # => we are only dealing with single scan ID # (not range)
             scan_s_s.extend([int(scanrangeelement)
                                      ,int(scanrangeelement)])  # add start,stop id pair
             how_many.append(1)
        elif len(scanrangeelement)>5: # => we are usig a range of scan IDs
             sscanrangeelement=scanrangeelement.split('-')
             s_s=[int(arg) for arg in sscanrangeelement] # add start, stop id pair
             how_many.append(s_s[1]-s_s[0]+1)            # tell how many scan ids between start,stop id pair
             scan_s_s.extend(s_s)
    list_o_scans=[]
    for i,how_many_now in enumerate(how_many):
        start=int(scan_s_s[2*i])    # the 2*i is because we save as start, stop pairs in scan_s_s 
                                    # where how_many just has the #-of-scan-ids-between single entry
        alos=arange(int(how_many_now))+start # create list of scans (los) from start id and how many to enter
        for s in alos:
            list_o_scans.append(s)
#    print list_o_scans

    return list_o_scans

def sumscansg(scans,sample_name,ipts,backipts,noninter):
    import pdb
    from time import sleep
    import shlex
    from subprocess import Popen
    from os import path

    alldir='./'
    if path.isdir('all_files'):
        alldir='all_files/'

    testfile=['sum'+sample_name+'_GSAS.pro']
    if test_fileexist(testfile,'.'):
        Lline='rm -f sum'+sample_name+'_GSAS.pro'
        Popen(shlex.split(Lline))
        sleep(2)
    isbackground=sample_name.lower() in ["mtc","back","background","bkg","empty"]
    f=open('sum'+sample_name+'_GSAS.pro','w')
    try:
        f1=open('bin_GSAS.bat','r')
    except IOError:
        print "COuldn't find bin_GSAS.bat"
        exit
    lines=f1.readlines()
    cgrlines=[]
    start=False
    for line in lines:
        if 'makeGSAStof' in line:
            start=True
        if start:
            line=line.replace('NOM9999tof.gsa','NOM_'+sample_name+'.gsa')
            line=line.replace('NOM9999tof.getN','NOM_'+sample_name+'.getN')
            line=line.replace('sqrt(b9999*nf9999)','esumb')
            line=line.replace(',9999,',','+str(scans[0])+',')
            cgrlines.append(line.strip())
    f1.close()
    print>>f,'@idlstart'
    line="restore,'"+alldir+"allscang.dat'"
    numbers="["
    As="["
    Bs="["
    nfs="if var_defined(nf"+str(scans[0])+") then nfs=["
    for scan in scans:
        sscan=str(scan)
        print>>f, line.replace('scan',sscan)
        numbers+=sscan+','
        As+='a'+sscan+','
        Bs+='b'+sscan+','
        nfs+='nf'+sscan+','
    numbers=numbers[:-1]
    As=As[:-1]
    Bs=Bs[:-1]
    nfs=nfs[:-1]

    print>>f,nfs+']'
    line='if var_defined(nfs) then sumscans,'+numbers+'],'+ipts+','+As+'],'+Bs
    if isbackground:
        line='if var_defined(nfs) then sumscans,'+numbers+'],'+backipts+','+As+'],'+Bs
    line+='],suma,sumb,esuma,esumb,normfactor=nfs'
    print>>f, line
    line='if not var_defined(nfs) then sumscans,'+numbers+'],'+ipts+','+As+'],'+Bs
    if isbackground:
        line='if not var_defined(nfs) then sumscans,'+numbers+'],'+backipts+','+As+'],'+Bs
    line+='],suma,sumb,esuma,esumb'
    print>>f, line
    if noninter:
        diadir='./'
        if path.isdir('diagnostics'):
            diadir='diagnostics/'
        print>>f,"set_plot,'ps'"
        print>>f,"device,file='"+diadir+"repro_"+sample_name+"g.ps'"
    print>>f,'plot,dspace(4,*),b'+str(scans[0])+'(4,*)/sumb(4,*),yno=1'
    print>>f,'oplot,dspace(4,*),b'+str(scans[-1])+'(4,*)/sumb(4,*),color=255'
    if not noninter:
        print>>f,'prtc'
    elif True:
        print>>f,"device,/close"
        print>>f,"set_plot,'x"
    if path.isdir('all_files'):
        print>>f,"save,suma,sumb,file='all_files/all"+sample_name+"g.dat"
    elif True:
        print>>f,"save,suma,sumb,file='all"+sample_name+"g.dat"

    if isbackground:
        print >>f,"makeback,suma,sumb,esuma,esumb,file='backMTcg.dat'"
        print >>f,"exit"
    elif True:
        for cgrline in cgrlines:
            found=cgrline.find('back')
            if found > 0:
                found1=cgrline.find('.dat')
                cgrline=cgrline[0:found+10]+'MTcg'+cgrline[found1:]

            cgrline=cgrline.replace('a9999','suma')
            cgrline=cgrline.replace('b9999','sumb')
            print>>f,cgrline
    f.close()

    lline='xterm -T '+sample_name+' -e idl sum'+sample_name+'_GSAS'
    Popen(shlex.split(lline))

    if sample_name.lower() in ["mtc","back","background","bkg"]:
#        pdb.set_trace()
        necessary_file=['backMTcg.dat']
        allexist=False
        subdir='.'
#        if path.isdir('all_files'):
#            subdir='all_files'
        while not allexist:
            allexist=test_fileexist(necessary_file,subdir)
            sleep(1)
    elif True:
        necessary_file=['NOM_'+sample_name+'.gsa']

        print necessary_file
        allexist=False
        GSASdir='.'
        if path.isdir('GSAS'):
            GSASdir='GSAS/'
        while not allexist:
            allexist=test_fileexist(necessary_file,GSASdir)
            sleep(1)

    return


def sumscans(scans,sample_name,ipts,corr,backipts,qmaxlist,noninter):
    import pdb
    from time import sleep
    import shlex
    from subprocess import Popen
    from os import path

    #    testfile=['sum'+sample_name+'_pdf.pro']
    #    if test_fileexist(testfile,'.'):
    #        Lline='rm -f sum'+sample_name+'_pdf.pro'
    #        Popen(shlex.split(Lline))

    subdir='./'
    if path.isdir('all_files'):
        subdir='all_files/'
    SQdir='./'
    if path.isdir('SofQ'):
        SQdir='SofQ/'
    gofrdir='./'
    if path.isdir('gofr'):
        gofrdir='gofr/'
    PDFdir='./'
    if path.isdir('PDF'):
        gofrdir='PDF/'
    toclean=['sum'+sample_name+'_pdf.pro',subdir+'all'+sample_name+'.dat']
    toclean.append(gofrdir+'NOM_9999_'+sample_name+'_ftf.dat')
    toclean.append(gofrdir+'NOM_9999_'+sample_name+'_ftl.dat')
    toclean.append(PDFdir+'NOM_9999_'+sample_name+'_ftfrgr.dat')
    toclean.append(PDFdir+'NOM_9999_'+sample_name+'_ftfrgr.gr')
    toclean.append(PDFdir+'NOM_9999_'+sample_name+'_ftlrgr.gr')
    toclean.append(SQdir+'NOM_9999_'+sample_name+'_SQ.dat')
    cleanup_files(toclean)

    f=open('sum'+sample_name+'_pdf.pro','w')
    try:
        f1=open('bin_gr.bat','r')
    except IOError:
        print "COuldn't find bin_gr.bat"
        exit
    isbackground=sample_name.lower() in ["mtc","back","background","bkg","empty"]
    lines=f1.readlines()
    cgrlines=[]
    start=False
    for line in lines:
        if 'creategr' in line:
            start=True
        if start:
            cgrlines.append(line.strip())
    f1.close()
    print>>f,'@idlstart'
    line="restore,'allscan.dat'"
    if path.isdir('all_files'):
        line="restore,'all_files/allscan.dat'"
    numbers="["
    As="["
    Bs="["
    nfs="if var_defined(nf"+str(scans[0])+") then nfs=["
    for scan in scans:
        sscan=str(scan)
        print>>f, line.replace('scan',sscan)
        numbers+=sscan+','
        As+='a'+sscan+','
        Bs+='b'+sscan+','
        nfs+='nf'+sscan+','
    numbers=numbers[:-1]
    As=As[:-1]
    Bs=Bs[:-1]
    nfs=nfs[:-1]


    print>>f,nfs+']'
    line='if var_defined(nfs) then sumscans,'+numbers+'],'+ipts+','+As+'],'+Bs
    if isbackground:
        line='if var_defined(nfs) then sumscans,'+numbers+'],'+backipts+','+As+'],'+Bs
    line+='],suma,sumb,esuma,esumb,normfactor=nfs'
    print>>f, line
    line='if not var_defined(nfs) then sumscans,'+numbers+'],'+ipts+','+As+'],'+Bs
    if isbackground:
         line='if not var_defined(nfs) then sumscans,'+numbers+'],'+backipts+','+As+'],'+Bs
    line+='],suma,sumb,esuma,esumb'
    print>>f, line
    diadir='./'
    if path.isdir('diagnostics'):
        diadir='diagnostics/'

    if noninter:
        print>>f,"set_plot,'ps'"
        print>>f,"device,file='"+diadir+"repro_"+sample_name+".ps'"
    print>>f,'plot,q,a'+str(scans[0])+'/suma,xra=[.5,50],yra=[.95,1.05]'
    print>>f,'oplot,q,a'+str(scans[-1])+'/suma,color=255'
    if not noninter:
        print>>f,'prtc'
    elif True:
        print>>f,"device,/close"
        print>>f,"set_plot,'x"
    if path.isdir('all_files'):
        print>>f,"save,suma,sumb,file='all_files/all"+sample_name+".dat"
    elif True:
        print>>f,"save,suma,sumb,file='all"+sample_name+".dat"


    if isbackground:
        print >>f,"makeback,suma,sumb,esuma,esumb,file='backMTc.dat'"
        print >>f,"exit"
    elif True:
        if corr:
            (found_Madinput,MADlib)=read_MADinput(exp.ini)
            if found_Madinp:
                normV=MADlib['Vana']
                anormV=interranges(normV)
                if len(anormV) == 1:
                    namenormV=str(anormV[0])
                elif True:
                    namenormV='9996'

            lines=["readmsdat,sample,file='samplename.msdat'",
               "restore,'backMTc.dat'",
               "muscat,suma-aback,ams9999,sample.muscat,normfile='normNM.dat'",
               "suma=ams9999+aback"]
            for line in lines:
                line=line.replace('samplename',sample_name)
                line=line.replace('NM',namenormV)
                print>>f,line
    cgrlines2=cgrlines[-2]
###    pdb.set_trace()
    found2=cgrlines2.find(',error=sqrt(a9999*nf9999)')
    if found2 > 0:
        cgrlines2=cgrlines2[0:found2]

    cgrlines[-2]=cgrlines2+",qual='_"+sample_name+"_c_',error=esuma"
    if not corr:
        cgrlines[-2]=cgrlines2+",qual='_"+sample_name+"_',error=esuma"
    for cgrline in cgrlines[0:-1]:
        found=cgrline.find('back')
        found1=cgrline.find('inter')
        if found > 0:
            ffound=cgrline.find('.dat')
            cgrline=cgrline[0:found+10]+'MTc'+cgrline[ffound:]
        if found1 > 0 and not noninter:
            cgrline=cgrline[0:found1+6]+'1'+cgrline[found1+7:]
        cgrline=cgrline.replace('a9999','suma')
        cgrline=cgrline.replace('b9999','sumb')
        print>>f,cgrline

    if qmaxlist:
            for qmax in qmaxlist:
                cgrlines[-2]=cgrlines2+",qual='_"+sample_name+"_c_"+str(qmax)+"',error=esuma"
                if not corr:
                    cgrlines[-2]=cgrlines2+",qual='_"+sample_name+"_"+str(qmax)+"_',error=esuma"
                for cgrline in cgrlines[0:-1]:
                    found=cgrline.find('back')
                    found1=cgrline.find('!pi*10')
                    found2=cgrline.find('31.414')
                    if found > 0:
                        ffound=cgrline.find('.dat')
                        cgrline=cgrline[0:found+10]+'MTc'+cgrline[ffound:]
                    if found1 > 0:
                        ffound=cgrline.find(',sc')
                        cgrline=cgrline[0:found1]+str(qmax)+cgrline[ffound:]
                    if found2 > 0:
                        ffound=cgrline.find(', Qdamp')
                        cgrline=cgrline[0:found2]+str(qmax)+cgrline[ffound:]
                    cgrline=cgrline.replace('a9999','suma')
                    cgrline=cgrline.replace('b9999','sumb')
                    print>>f,cgrline
    print>>f,'exit'

    f.close()

    lline='xterm -T '+sample_name+' -e idl sum'+sample_name+'_pdf'
    Popen(shlex.split(lline))

    if sample_name.lower() in ["mtc","back","background","bkg"]:
        necessary_file=['backMTc.dat']
        allexist=False
        while not allexist:
            allexist=test_fileexist(necessary_file,'.')
            sleep(1)
    elif True:
        PDFdir='./'
        if path.isdir('PDF'):
            gofrdir='PDF/'
        necessary_file=['NOM_9999_'+sample_name+'_ftlrgr.gr']
        print necessary_file
        allexist=False
        while not allexist:
            allexist=test_fileexist(necessary_file,gofrdir)
            sleep(1)

    return

def anyftl():

    """ Is there any ftl file in the current directory?
    """

    import glob

    ftlfiles=glob.glob('*ftl*')

    isanyftl=len(ftlfiles) <> 0
    return isanyftl

def lastftl():

    """ What is the last ftl file in the current directory
    """

    import glob
    from numpy import array,arange


    ftlfiles=glob.glob('*ftnat*')
    scannrs=[filenr[4:9] for filenr in ftlfiles]
    no9999=[]
    for scannr in scannrs:
         if scannr<>'9999_':
              no9999.append(scannr)
    scannrs=no9999
#    ascannrs=array(scannrs)
#    mscannr=max(ascannrs)
    return scannrs

def rstd(name):
    """ python version of the IDL function rstd, opens a file,
    ignores all lines starting with # and reads as n column ascii
    """
    f=open(name,'r')
    lines=f.readlines()
    a=[]
    for line in lines:
        if line[0:1] <> '#':
            zeil=line.split()
            a.append([float(element) for element in zeil])
    q=[b[0] for b in a]
    i=[b[1:] for b in a]
    f.close()
    return q,i

def wstd(q,i,name,comment=''):
    from time import localtime, strftime
    import pdb
#    pdb.set_trace()
    """ python version of the IDL function wstd, opens a file,
    writes as n column ascii
    """
    f=open(name,'w')

    ns=min(len(i),len(q))
    print>>f,'# '+str(ns)
    print>>f,'#file: '+name
    print>>f,'#created: '+strftime("%Y-%m-%d %H:%M:%S", localtime())
    print>>f,'# Comment:'+comment
    for counter,qelement in enumerate(q[0:ns-1]):
        print>>f,qelement,i[counter]
    f.close()

def what_sample(scanrange,ipts):

    import pdb

    Exptitles=[]
    isvalid=[]
    for scan in scanrange:
            fullname='/SNS/NOM/IPTS-'+ ipts + '/0/' + scan
            fullname+='/preNeXus/NOM_' + scan +'_runinfo.xml'
            try:
                f1=open(fullname,'r')

                for line in f1.readlines():
                    a=line.find('<Title>')
                    if a >0:
            		o=line.find('</Title>')
            		Exptitle=line[a+len('<Title>'):o]
                a=Exptitle.find('equilibration')
                if a >0:
                    isvalid.append(False)
                elif True:
                    isvalid.append(True)
                f1.close
            except IOError:
                Exptitle="Not found"
                isvalid.append(False)

            Exptitles.append(Exptitle)

    pdb.set_trace()
    sample_identifiers=[]
    temperature=[]

    for index,title in enumerate(Exptitles):
        if isvalid[index]:
            a=title.find('scan')
            sample_identifiers.append(title[0:a-1])
            if a+4 < len(title):
                o=title.find('K')
                temperature.append(title[a+5:o])
            elif True:
                temperature.append('298.15')

    return sample_identifiers,isvalid,temperature

def detpos():
    from numpy import array,arange,pi,cos,sin,arccos,arctan,sqrt
    import pdb


    n_eight=63
    n_eightf=38

    tt=arange((n_eight+n_eightf)*8*128.).reshape((n_eight+n_eightf)*8,128)
    phi=arange((n_eight+n_eightf)*8*128.).reshape((n_eight+n_eightf)*8,128)
    rr=arange((n_eight+n_eightf)*8*128.).reshape((n_eight+n_eightf)*8,128)
    x=arange((n_eight+n_eightf)*8*128.).reshape((n_eight+n_eightf)*8,128)
    xman=x
# x = up
# MANTID x=left (in beam direction)

    y=arange((n_eight+n_eightf)*8*128.).reshape((n_eight+n_eightf)*8,128)
    yman=y
#; y = right (in beam direction)
#; MANTID y = up
    z=arange((n_eight+n_eightf)*8*128.).reshape((n_eight+n_eightf)*8,128)
    zman=z
#; z=  in beam direction
#; MANTID  z=  beam direction
    dthere=arange((n_eight+n_eightf)*8*128.).reshape((n_eight+n_eightf)*8,128)
#;there([3,7,8,9,10,11,19],*)=1
    number=arange((n_eight+n_eightf)*8*128.).reshape((n_eight+n_eightf)*8,128)
    for i in range((n_eight+n_eightf)*8-1):
        number[i,:]=arange(128)+128.*i

    n_first=14
    z0_first=6.41/8.45*3.2
    x0_first=1.31/8.45*3.2
    z1_first=3.86/8.45*3.2
    x1_first=1.44/8.45*3.2
    dx_first=x1_first-x0_first
    dz_first=z1_first-z0_first
    section=360/float(n_first)

    onehundredtwentyeight=arange(128)
    dtor=pi/180.
 #   pdb.set_trace()

    for i in range(n_first):
        angle=(360*(i+.5)/float(n_first))*dtor
        x0=-x0_first*cos(section*i*dtor)
        y0=x0_first*sin(section*i*dtor)
        x1=-x1_first*cos(section*i*dtor)
        y1=x1_first*sin(section*i*dtor)

        for j in range(8):
            x0j=x0+j*(.0254+0.001)*sin(section*(i+.5)*dtor)
            y0j=y0+j*(.0254+0.001)*cos(section*(i+.5)*dtor)
            x1j=x1+j*(.0254+0.001)*sin(section*(i+.5)*dtor)
            y1j=y1+j*(.0254+0.001)*cos(section*(i+.5)*dtor)
            x[i*8+j,:]=x0j+(x1j-x0j)*(1-onehundredtwentyeight/128.)
            y[i*8+j,:]=y0j+(y1j-y0j)*(1-onehundredtwentyeight/128.)
            z[i*8+j,:]=z0_first+dz_first*(1-onehundredtwentyeight/128.)

    n_second=23
#;z0_second=5.05/8.45*3.2
#;x0_second=2.24/8.45*3.2
#;z1_second=2.54/8.45*3.2
#;x1_second=2.24/8.45*3.2
    z0_second=5.09/7.06*2.7-0.0095
    x0_second=2.22/7.06*2.7
    z1_second=2.45/7.06*2.7+0.0095
    x1_second=2.22/7.06*2.7
    dx_second=x1_second-x0_second
    dz_second=z1_second-z0_second
    section=360/float(n_second)



    for i in arange(n_second):
        angle=(360*(i+.5)/float(n_second))*dtor
        x0=-x0_second*cos(section*i*dtor)
        y0=x0_second*sin(section*i*dtor)
        x1=-x1_second*cos(section*i*dtor)
        y1=x1_second*sin(section*i*dtor)

        for j in arange(8):
            x0j=x0+j*(.0254+0.001)*sin(section*(i+.5)*dtor)
            y0j=y0+j*(.0254+0.001)*cos(section*(i+.5)*dtor)
            x1j=x1+j*(.0254+0.001)*sin(section*(i+.5)*dtor)
            y1j=y1+j*(.0254+0.001)*cos(section*(i+.5)*dtor)
            x[(i+n_first)*8+j,:]=x0j+(x1j-x0j)*onehundredtwentyeight/128.
            y[(i+n_first)*8+j,:]=y0j+(y1j-y0j)*onehundredtwentyeight/128.
            z[(i+n_first)*8+j,:]=z0_second+dz_second*onehundredtwentyeight/128.
    n_third=14
    ii=array([3,4,5,6,7,8,9,18,19,20,21,22,23,24])+.5
#;z0_third=2.60/8.45*3.2
#;x0_third=2.56/8.45*3.2
#;z1_third=0/8.45*3.2
#;x1_third=2.56/8.45*3.2
    z0_third=2.59/7.06*2.7-0.0076
#;x0_third=2.61/7.06*2.7
    x0_third=1.00
    z1_third=-0.04/7.06*2.7+.0076
#;x1_third=2.61/7.06*2.7
    x1_third=1.00
    dx_third=x1_third-x0_third
    dz_third=z1_third-z0_third
    section=360/float(29)



    for i in arange(n_third):
        angle=(360*(ii[i]+.5)/float(n_third))*dtor
        x0=-x0_third*cos(section*ii[i]*dtor)
        y0=x0_third*sin(section*ii[i]*dtor)
        x1=-x1_third*cos(section*ii[i]*dtor)
        y1=x1_third*sin(section*ii[i]*dtor)

        for j in arange(8):
            x0j=x0+j*(.0254+0.001)*sin(section*(ii[i]+.5)*dtor)
            y0j=y0+j*(.0254+0.001)*cos(section*(ii[i]+.5)*dtor)
            x1j=x1+j*(.0254+0.001)*sin(section*(ii[i]+.5)*dtor)
            y1j=y1+j*(.0254+0.001)*cos(section*(ii[i]+.5)*dtor)
            x[(i+n_first+n_second)*8+j,:]=x0j+(x1j-x0j)*(1-onehundredtwentyeight/128.)
            y[(i+n_first+n_second)*8+j,:]=y0j+(y1j-y0j)*(1-onehundredtwentyeight/128.)
            z[(i+n_first+n_second)*8+j,:]=z0_third+dz_third*(1-onehundredtwentyeight/128.)

    n_fourth=12
    ii=array([2,3,4,5,6,7,13,14,15,16,17,18])+1
#;z0_fourth=-.2/8.45*3.2
#;x0_fourth=2.67/8.45*3.2
#;z1_fourth=-2.8/8.45*3.2
#;x1_fourth=2.08/8.45*3.2
    z0_fourth=-.28/7.06*2.7+.0016
    x0_fourth=2.66/7.06*2.7
    z1_fourth=-2.79/7.06*2.7-.0016
    x1_fourth=2.09/7.06*2.7
    dx_fourth=x1_fourth-x0_fourth
    dz_fourth=z1_fourth-z0_fourth
    section=360/float(23)


    for i in range(n_fourth):
        angle=(360*(ii[i]+.5)/float(n_fourth))*dtor
        x0=-x0_fourth*cos(section*ii[i]*dtor)
        y0=x0_fourth*sin(section*ii[i]*dtor)
        x1=-x1_fourth*cos(section*ii[i]*dtor)
        y1=x1_fourth*sin(section*ii[i]*dtor)

#; check this +.5
        for j in range(8):
            x0j=x0+j*(.0254+0.001)*sin(section*(ii[i]+.5)*dtor)
            y0j=y0+j*(.0254+0.001)*cos(section*(ii[i]+.5)*dtor)
            x1j=x1+j*(.0254+0.001)*sin(section*(ii[i]+.5)*dtor)
            y1j=y1+j*(.0254+0.001)*cos(section*(ii[i]+.5)*dtor)
            x[(i+n_first+n_second+n_third)*8+j,:]=x0j+(x1j-x0j)*(1-onehundredtwentyeight/128.)
            y[(i+n_first+n_second+n_third)*8+j,:]=y0j+(y1j-y0j)*(1-onehundredtwentyeight/128.)
            z[(i+n_first+n_second+n_third)*8+j,:]=z0_fourth+dz_fourth*(1-onehundredtwentyeight/128.)

    n_back=19
    z0_back=-1.78/8.45*3.2
    y0_back=1.32/8.45*3.2
    for i in arange(n_back):
        iseven=0
        if (i/2)*2 == i:
            iseven=1
        for j in arange(8):
            ntube=i*8+j
            x[(i+n_first+n_second+n_third+n_fourth)*8+j,:]=(1-onehundredtwentyeight/128.)-0.5
            y[(i+n_first+n_second+n_third+n_fourth)*8+j,:]=y0_back-(.0254/2+.001)/2*ntube
            z[(i+n_first+n_second+n_third+n_fourth)*8+j,:]=z0_back-iseven*(.0254/2+.001)

    n_forward=19
    z0_forward=6.69/8.45*3.2
    y0_forward=1.34/8.45*3.2
    for i in arange(n_forward):
        iseven=0
        if (i/2)*2 == i:
            iseven=1

        for j in arange(8):
            ntube=i*8+j
            x[(i+n_first+n_second+n_third+n_fourth+n_back)*8+j,:]=(1-onehundredtwentyeight/128.)*.9-0.9/2
#;;; hack: shift the forward panel by some
            y[(i+n_first+n_second+n_third+n_fourth+n_back)*8+j,:]=y0_forward-(.0254/2+.001)/2*(ntube+32)+.062
            z[(i+n_first+n_second+n_third+n_fourth+n_back)*8+j,:]=z0_forward-iseven*(.0254/2+.001)



    tt=arctan(sqrt(x**2+y**2)/z)
    tt[tt < 0]=pi+tt[tt < 0]
    rr=sqrt(x**2+y**2+z**2)
    phi=arccos(x/sqrt(x**2+y**2))
    phi[y < 0]=-phi[y < 0]

    return (tt,phi,rr,x,y,z)

def there():
    from numpy import array,arange,pi


    nthere=38
    dthere=arange(nthere*8*128)*0
    eightpacks=array([3,7,8,9,10,11,19,20,26,28,30,31,32,34,36,40,44,45,46,47,
                48,49,50,54,57,58,59,60,61,62,74,75,76,77,92,93,94,95])
    banks=arange(6*20).reshape(6,20)*0+99
    banks[0,:6]=[3,7,8,9,10,11]
#;                0 1 2 3 4  5
    banks[1,:9]=[19,20,26,28,30,31,32,34,36]
#;                6  7  8  9  10 11 12 13 14
    banks[2,:8]=[40,44,45,46,47,48,49,50]
#;                15 16 17 18 19 20 21 22
    banks[3,:7]=[54,57,58,59,60,61,62]
#;                23 24 25 26 27 28 29
    banks[4,:4]=[74,75,76,77]
#;                30 31 32 33
    banks[5,:4]=[92,93,94,95]
#;                34 35 36 37
    for i in arange(nthere):
        dthere[i*8*128:(i+1)*8*128]=eightpacks[i]*8*128+arange(8*128)

    return (nthere,dthere,eightpacks)

def find_samplename(scan):
    ''' determine the sample name for scan from runinfo file
    '''
    iptsnr=findcurrentipts()

    fullname='/SNS/NOM/IPTS-'+ iptsnr + '/0/' + scan
    fullname+='/preNeXus/NOM_' + scan +'_runinfo.xml'
    try:
	f1=open(fullname,'r')

    	for line in f1.readlines():
            a=line.find('<Title>')
            if a >0:
                o=line.find('</Title>')
                Exptitle=line[a+len('<Title>'):o]
        f1.close
    except IOError:
	Exptitle="Not found"
    sample_name=Exptitle.split()
    if "MT" in  Exptitle:
        samplename='MT'
        return samplename
    if sample_name[0]=='Step':
        samplename=sample_name[2]
    else:
        samplename=sample_name[0]
    return samplename

def is_eq_scan(scan):
    """ check if the scan is an equilibration scan from the runinfo scan
"""
    iptsnr=findcurrentipts()

    fullname='/SNS/NOM/IPTS-'+ iptsnr + '/0/' + scan
    fullname+='/preNeXus/NOM_' + scan +'_runinfo.xml'
    Exptitle="Not found"
    try:
	f1=open(fullname,'r')

    	for line in f1.readlines():
            a=line.find('<Title>')
            if a >0:
                o=line.find('</Title>')
                Exptitle=line[a+len('<Title>'):o]
        f1.close
    except IOError:
	Exptitle="Not found"
    if 'equilibration' in Exptitle:
        return True
    return False
def is_eq_scan_16B(file):
    """ check if the scan is an equilibration scan from the runinfo scan
"""
    import sys
    sys.path.append('/usr/lib64/python2.7/site-packages')

    from h5py import File
    
    hf=File(file,'r') 
    Exptitle=hf['/entry/title'][0]
    hf.close()
    if 'equilibration' in Exptitle:
        return True
    return False

def with_properties(scan,sampleid,pydir='/SNS/users/zjn/pytest'):

    import pdb
    import shlex
    from subprocess import Popen

    """ check if the scan is an equilibration scan from the runinfo scan
"""
    if not pydir:
        pydir='~zjn/pytest'
    iptsnr=findcurrentipts()

    fullname='/SNS/NOM/IPTS-'+ iptsnr + '/0/' + scan
    fullname+='/preNeXus/NOM_' + scan +'_runinfo.xml'
    try:
	f1=open(fullname,'r')

    	for line in f1.readlines():
            a=line.find('<Notes>')
            if a >0:
                o=line.find('</Notes>')
                Expnotes=line[a+len('<Notes>'):o]
        f1.close
    except IOError:
	Exptitle="Not found"

    has_properties=('Sample' in Expnotes)
##    pdb.set_trace()
    if has_properties:
        props=Expnotes.split()
        if len(props) == 12:
            sampleid=props[1].strip(',')
            formula=props[3].strip(',')
            formula=formula.replace('_',' ')
            density=props[5].strip(',')
            radius=props[7].strip(',')
            shape=props[9].strip(',')
            packfrac=props[11].strip(',')
        elif True:
            has_properties=False
    if has_properties:
        if not test_fileexist([sampleid+'.ini'],'.'):
            f=open(sampleid+'.ini','w')
            print>>f, sampleid+'   # sample title'
            print>>f, formula+'  # sample formula'
            print>>f, density+'    # mass density'
            print>>f, radius+'   # radius'
            print>>f, packfrac+ '      # packing fraction'
            print>>f, shape+'   # sample shape'
            print>>f, 'go   # do abskorr in IDL'
            f.close()
            Lline='xterm -e python ~zjn/pytest/define_sample.py -f '
            Lline+=sampleid+'.ini -P '+pydir
            Popen(shlex.split(Lline))
    return (has_properties,sampleid)

def is_number(s):

    a=s.find('(')
    if a >0:
        s=s[0:a]

    s=s.replace("<i>i</i>","j")

    try:
        complex(s)
        return complex(s)
    except ValueError:
        return float('nan')

def interpret_samplename(sample,isotopelist):
    from numpy import array,arange,where

    samplesplit=sample.split()
    iso_in_sample=samplesplit[::2]
    conc_iso=samplesplit[1::2]
    conc_iso=array([is_number(val) for val in conc_iso])
    conc_iso=conc_iso.real
#    conc_iso=conc_iso/sum(conc_iso)
    where_iso=[]
    r=arange(len(isotopelist))
    for iso in iso_in_sample:
        if iso in isotopelist:
            where_iso.append(where(iso == isotopelist)[0][0])
        elif iso not in isotopelist:
            print iso, "is a strange isotope. Please check"
 #   print where_iso
 #   print isotopelist[ where_iso[0]],isotopelist[ where_iso[1]]
    return where_iso,conc_iso


def resonancecalc(formula,atconc,data,rhos1,radius,sample_title):
    import pdb
    from numpy import array,arange,where, linspace,zeros,exp
    from numpy import interp
#    from scipy.misc.common import factorial
#    from scipy.interpolate import interp1d
    import matplotlib.pyplot as plt


    isotopes=array(data["Isotope"])
    sig18=array(data["Abs_xs"])
    conc=array(data["conc"])
    lamda=linspace(0.1,6.1,601)
    xabstot=zeros(601)

    (where_iso,conc_iso)=interpret_samplename(formula,isotopes)
    si=zeros((len(where_iso),601))

    for counttype,val in enumerate(where_iso):

        iselement=conc[val] == '---'
        if iselement:
            natcomp=[]
            inisotopes=[]
            single_iso_element=(conc[val+1] == '---' or conc[val+1] == '100')
            if not single_iso_element:
                val1=val
                iniso=[]
                inisoconc=[]
                iniso_absxs=[]
                while conc[val1+1] <> '---' and conc[val1+1] <> '100':
                    iniso.append(isotopes[val1+1])
                    inisoconc.append(conc[val1+1])
                    iniso_absxs.append(sig18[val1+1].split('(')[0])
                    val1=val1+1
        if not iselement or single_iso_element:
            iniso=[isotopes[val]]
            inisoconc=['100']
            iniso_absxs=[sig18[val].split('(')[0]]
        for counter,thisiso in enumerate(iniso):
            nodata=False
            try:
                f1=open('/SNS/NOM/shared/scatlength/abslam/'+thisiso+'.dat','r')
            except IOError:
                nodata=True

            if not nodata:
                f1.close()
#                pdb.set_trace()
                (e,sigma)=rstd('/SNS/NOM/shared/scatlength/abslam/'+
                               thisiso+'.dat')
                l1 = array([(8.18145447496e-22/e1)**.5*1e10 for e1 in e])
                s1 = array([val[0] for val in sigma])
                f=interp(lamda,l1[::-1],s1[::-1])
#                f = interp1d(l1[::-1],s1[::-1])
#                si[counttype,:]+=f(lamda)*float(inisoconc[counter])/100.
                si[counttype,:]+=f*float(inisoconc[counter])/100.
#                si[counttype,:]*=float(iniso_absxs[counter])/f(1.8)
                si[counttype,:]*=float(iniso_absxs[counter])/f[170]
#                print thisiso,f(1.8),iniso_absxs[counter],float(inisoconc[counter])/100.
                print thisiso,f[170],iniso_absxs[counter],float(inisoconc[counter])/100.
            elif True:
                si[counttype,:]+=float(iniso_absxs[counter])*lamda/1.8*float(inisoconc[counter])/100.


#                si[counttype,:]+=lamda/1.8*float(iniso_absxs[counter])

        xabstot+=si[counttype,:]*float(atconc[counttype])
#    plt.plot(lamda,xabstot)
#    plt.yscale('log')
    wstd(lamda,xabstot,sample_title+'_ressigma.dat')
#    plt.show()
    mur=xabstot*rhos1*radius
    ahkl=mur*0
    ahkl[(mur<10)]=exp(-1.7133*mur[(mur<10)]+.0927*mur[(mur<10)]**2)
    wstd(lamda,ahkl,sample_title+'_resabs.dat')
    wstd(lamda[0:300],xabstot[0:300],sample_title+'_sigmaa.dat')
    plt.plot(lamda,1-ahkl,'-',lamda,zeros(601)+1/exp(1),'--')
    plt.xscale('log')
    plt.xlabel('wavelength/ A')
    plt.ylabel('absorption')
    plt.show()
#    pdb.set_trace()

    return

def testforisotopes(formula):
    ''' As the name states. Should return a tuple with a logic variable 
    (there are or not isotopes), a list of strings with the 
    atomtype that has two isopopes of the same element
    and a list of strings that contain the isotopes'''

    from string import digits
    from collections import Counter
    import pdb
    
    hasisotopes=False
    for element in formula:
        if isintstring(element[0]):
            hasisotopes=True
    twoisotopes=[]
    isotypes=[]
    #pdb.set_trace()
    if not hasisotopes:
        return (hasisotopes,twoisotopes,isotypes)
    elements=[element.translate(None,digits) for element in formula]
    if len(set(elements)) == len(elements):
        return (hasisotopes,twoisotopes,isotypes)
    C=Counter(elements).values()
    K=Counter(elements).keys()
    for index,key in enumerate(K):
        if C[index] > 1:
            twoisotopes.append(key)
    for index,element in enumerate(elements):
        if element in twoisotopes:
            isotypes.append(formula[index])
    
    return (hasisotopes,twoisotopes,isotypes)

def isintstring(a):
    try:
        b=int(a)
        itis=True
    except ValueError:
        itis=False
    return itis
        



'''def read_calfile(file=file):

    try:
        f1=open(file,'r')
    except IOError:
        print 'Calfile ',file,' does not exist'

if (err ne 0) then begin&$
print,!ERROR_STATE.MSG
print,'calfile name'
read,file
end
end
rstd,a,b,file,nz=5
corrf=b(*,1)+1
return'''
