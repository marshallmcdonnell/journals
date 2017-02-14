from __future__ import print_function
from builtins import range
from journals.databases.icat.sns.communicate import SnsICat


comm = SnsICat()

# Serial
#-----------
def serial_run_info(runList, inst, nproc):
    return { run : comm.get_run_info_lite(inst,run) for run in runList }

# Threads
#-----------
import Queue
import threading
import math
def threaded_run_info(runList, inst, nthreads):
    def worker(workerList, inst, outdict):
        for run in workerList:
            outdict[run] = comm.get_run_info_lite(inst,run)

    chunksize = int(math.ceil(len(runList) / float(nthreads)))
    threads = []
    outs = [ dict() for i in range(nthreads) ]
    
    for i in range(nthreads):
        t = threading.Thread(
                target=worker, 
                args=(runList[chunksize*i:chunksize*(i+1)], inst, outs[i]))
        threads.append(t)
        t.start()

    for i in threads:
        t.join()

    return {k: v for out_d in outs for k, v in out_d.iteritems() }



# Processes
#-----------
import itertools
import multiprocessing
def mp_run_info(runList,inst, nprocs):
    def worker(workerList, inst, out_q):
        local_dict = dict() 
        for run in workerList:
            local_dict[run] = comm.get_run_info_lite(inst,run)
        out_q.put(local_dict)
    out_q = multiprocessing.Queue()
    chunksize = int(math.ceil(len(runList) / float(nprocs)))
    procs = []

    for i in range(nprocs):
        p = multiprocessing.Process(
                target=worker,
                args=(runList[chunksize*i:chunksize*(i+1)],inst,out_q))
        procs.append(p)
        p.start()

    result_dict = dict()
    for i in range(nprocs):
        result_dict.update(out_q.get())
    
    for p in procs:
        p.join()

    return result_dict
        
# Inputs
#---------
mode_selection = ['output','profile']

mode = 'profile'
nthreads = nprocs = 2
inst = 'NOM'
runList = list(range(80000,81000))

if mode not in mode_selection:
    raise Exception("Use mode from mode_selection list")
# Output
#---------

if mode == 'output':
    serial_result   = serial_run_info(runList,inst,1)
    threaded_result = threaded_run_info(runList,inst,nthreads)
    mp_result       = mp_run_info(runList,inst,nprocs)

    def output_result(rtype,result,key):
        print(rtype)
        for k in result.keys():
            print(k,result[k][key])
        

    output_result('serial',serial_result,'protonCharge')
    output_result('threaded',threaded_result,'protonCharge')
    output_result('mp',mp_result,'protonCharge')
    exit()

# Profiling
#-----------
if mode == 'profile':
    import timeit

    def run_timeit(rtype,nodes=1):
        func_string = str(rtype)+"_run_info(runList,inst,"+str(nodes)+")"
        setup_string = "from __main__ import runList,inst,"+rtype+"_run_info"
        print('%s - %d threads/procs:'%(rtype,nodes),
              timeit.timeit(func_string,number=1,setup=setup_string),'sec')

    run_timeit('serial')
    for np in [1,2,4,8,16,32,64,128,256,512]:
        run_timeit('threaded',nodes=np)
        #run_timeit('mp',nodes=np)

