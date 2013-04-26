# Program to monitor folder size over time

import os
import sched, time
import datetime

interval=600 # seconds
folder='condor\\execute\\dir_5780' # no trailing slashes
outfile='foldersize_log.txt'

s = sched.scheduler(time.time, time.sleep)

ofp=open(outfile,'w')
ofp.write('datetime  folder_size(KB)\n')


def get_folder_size(sc):
    print "Getting folder size..."
    def get_size(start_path = folder+'\\.'):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size
    now=datetime.datetime.now()
    total_size=get_size()
    print total_size
    print str(total_size*1.0/1024.0) + ' KB'
    print sc.queue
    ofp.write(now.strftime("%Y-%m-%d %H:%M:%S  ")+str(total_size*1.0/1024.0)+'\n')
    
    #could add closure criteria here. Didn't troubleshoot enough to get these lines to work.
    #if total_size != prev_total_size:
    sc.enter(interval, 1, get_folder_size, (sc,))
    #else:
        #sc.cancel(sc.queue[0])
       # ofp.close()

s.enter(interval, 1, get_folder_size, (s,))
s.run()
