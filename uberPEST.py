#uberPEST - PEST running and notification

import gmail_sender
import os

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
    tmp=string.split(infile.next())
    email_recipient = tmp[0]
    tmp=string.split(infile.next())
    if(string.lower(tmp[0])=='none'):
        attachment=False
    else:
        attachment = tmp[0]
    infile.close()
    return pestcall,casename,email_recipient,attachment




#######################
#      M A I N        #
#######################

# read in the parfile values
(pestcall,casename,email_recipient,attachment) = read_par_file("uberPEST.par")

# concatenate and run the system call 
scall = pestcall + ' ' + casename
os.system(scall)

#
#  add any post-processing here
#


# compose the email here
# header
header = "King Kong!"

# body text
body = "This is your new Prez.  \n He's from Hawai'i"

# write the output to the email and send it
if (attachment):
    gmail_sender.mail(email_recipient,header,body,attachment)
else:
    gmail_sender.mail(email_recipient,header,body)
    