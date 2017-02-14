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
def threaded_queue_run_info(runList, inst, nthreads):
    def worker(workerList, inst, outdict):
        for run in workerList:
            outdict[run] = comm.get_run_info_lite(inst,run)

    chunksize = int(math.ceil(len(runList) / float(nthreads)))
    threads = []
    outs = [ {} for i in range(nthreads) ]
    
    for i in range(nthreads):
        t = threading.Thread(
                target=worker, 
                args=(runList[chunksize*i:chunksize*(i+1)], inst, outs[i]))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return {k: v for out_d in outs for k, v in out_d.iteritems() }

from multiprocessing.pool import ThreadPool
def threaded_pool_run_info(runList, inst, nthreads):
    def worker(input_tuple):
        run, inst = input_tuple
        return (run,comm.get_run_info_lite(inst,run))

    pool = ThreadPool(processes=nthreads)
    inputs = [ (run,inst) for run in runList]
    result = dict(pool.map(worker, inputs))
    return result 



# Processes
#-----------
import itertools
import multiprocessing
def mp_queue_run_info(runList,inst, nprocs):
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
inst = 'NOM'
start = 80000
end   = 80064
interval = 1
runList = list(range(start,end+interval,interval))

if mode not in mode_selection:
    raise Exception("Use mode from mode_selection list")
# Output
#---------

if mode == 'output':
    nthreads = nprocs = 4 

    def output_result(rtype,result,key):
        print(rtype)
        for k in result.keys():
            print(k,result[k][key])
    
    serial_result   = serial_run_info(runList,inst,1)
    threaded_queue_result = threaded_queue_run_info(runList,inst,nthreads)
    threaded_pool_result = threaded_pool_run_info(runList,inst,nthreads)
    mp_queue_result       = mp_queue_run_info(runList,inst,nprocs)

    output_result('serial',serial_result,'protonCharge')
    output_result('threaded_queue',threaded_queue_result,'protonCharge')
    output_result('threaded_pool',threaded_pool_result,'protonCharge')
    output_result('mp_queue',mp_queue_result,'protonCharge')
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
    for np in [2,4,8,16]:
        run_timeit('threaded_queue',nodes=np)
        run_timeit('threaded_pool',nodes=np)
        run_timeit('mp_queue',nodes=np)

