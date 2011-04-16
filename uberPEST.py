#uberPEST - PEST running and notification

import gmail_sender
import os
import time
import getpass

######
# get the file name for the .rec file from the .par file
######
def read_par_file(infilename):
    
    import string
    infile=open(infilename,"r")
    tmp=string.split(infile.next())
    pestcall=tmp[0]
    tmp=string.split(infile.next())
    casename = tmp[0]
    tmp=infile.next()
    #read up to the '#' character to pull out the flags
    indies = [i for i in xrange(len(tmp)) if tmp.startswith('#',i)]
    flags = tmp[0:indies[0]]
    if (string.lower(flags.strip())=='none'):
        flags=False
    tmp=string.split(infile.next())
    email_recipient = tmp[0]
    tmp=string.split(infile.next())
    if(string.lower(tmp[0])=='none'):
        batchfile=False
    else:
        batchfile = tmp[0]
    attachment = []
    while 1:
        try:
            tmp=string.split(infile.next())
            if(string.lower(tmp[0])=='none'):
                attachment=False
                infile.close()
                return pestcall,casename,email_recipient,attachment,batchfile,flags
            else:
                attachment.append(tmp[0])
        except:
            infile.close()
            return pestcall,casename,email_recipient,attachment,batchfile,flags
    infile.close()
    return pestcall,casename,email_recipient,attachment,batchfile,flags


#######################
#      M A I N        #
#######################

# get the email account information
gmail_user = "wwsc.modeling.center@gmail.com"
gmail_pwd = getpass.getpass('PLease enter GMAIL password for account:\n ' + gmail_user + '\n>>')


# read in the parfile values
(pestcall,casename,email_recipient,attachment,batchfile,flags) = read_par_file("uberPEST.par")

# get the starting time
t1 = time.localtime()

# concatenate and run the system call 
scall = pestcall + ' ' + casename
if (flags):
    scall += ' ' + flags
os.system(scall)


#  run the (optional) batch file here
if (batchfile):
    os.system(batchfile)

# get the end time and elapsed time
t2 = time.localtime()
etime = int(round((time.mktime(t2)-time.mktime(t1))))

eday  = etime/60/60/24
edaystr = str(eday) + " Day"
if (eday>1):
    edaystr += "s "
else:
    edaystr += " "
ehour = etime/60/60%60%24
ehourstr = str(ehour) + " Hour"
if (ehour>1):
    ehourstr += "s "
else:
    ehourstr += " "
emin  = etime/60%60
eminstr = str(emin) + " Min"
if (emin>1):
    eminstr += "s "
else:
    eminstr += " "
esec  = etime%60
esecstr = str(esec) + " Sec"
if (esec>1):
    esecstr += "s "
else:
    esecstr += " "
etimeSTRING = edaystr + ehourstr + eminstr + esecstr

# compose the email here
# header
header = scall + " is done"

# body text
body = scall + " finished.\n\n" + "run start time: " + time.asctime(t1) \
	+ "\n run end time: " + time.asctime(t2) \
	+ "\n\nel. time: " + etimeSTRING

# write the output to the email and send it
if (attachment):
    gmail_sender.mail(email_recipient,header,body,gmail_user,gmail_pwd, attachment)
else:
    gmail_sender.mail(email_recipient,header,body,gmail_user,gmail_pwd)
    