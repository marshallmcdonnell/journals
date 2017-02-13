from __future__ import print_function
from builtins import range
from journals.databases.icat.sns.communicate import SnsICat


runList = list(range(80000,80010))
comm = SnsICat()

# Serial
#-----------
def serial():
    result = dict()
    for run in runList:
        result[run] = comm.get_run_info_lite('NOM',run)
    return result

# Threads
#-----------
import Queue
import threading
def queue_get_run_info(inst,run,queue):
    queue.put(comm.get_run_info_lite(inst,run))

def launchThreads(func,queue=None,args=None):
    threads = [threading.Thread(target=func, args=(args[0],run,queue) ) for run in args[1] ]
    print("Starting threads")
    for thread in threads:
        thread.start()
    print("Joining threads")
    for thread in threads:
        thread.join()
    print("Finished threads")

def parallelThreads():
    q = Queue.Queue()
    launchThreads(queue_get_run_info,queue=q,args=('NOM',runList))

    result = dict()
    for run in runList:
        result[run] = q.get()
    return result
    #return [q.get() for _ in xrange(len(runList))]

# Processes
#-----------
import itertools
import multiprocessing
def wrapper_func(q,inst,runList):
    for run in runList:
        q.put(comm.get_run_info_lite(inst,run))

def parallelProcesses():
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=wrapper_func,args=(q,'NOM',runList,))
    p.start()
    p.join()

# Output
#---------
serial_result = serial()
parallel_result = parallelThreads()
mp_result = parallelProcesses()
print('Serial:',serial_result[80000])
print('ParallelThread:',parallel_result[80000])
print("ERROR in Parallel thread. Not thread safe!!!!")
print('ParallelProcess:',parallel_result[80000])

# Profiling
#-----------
import timeit
print(timeit.timeit(serial,number=1),'sec')
print(timeit.timeit(parallelThreads,number=1),'sec')
print(timeit.timeit(parallelProcesses,number=1),'sec')

