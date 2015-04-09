"""
/* ala Poul-Henning Kamp, http://people.freebsd.org/~phk/
 * ----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <braulio barahona> wrote this file.  As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return.
 * ----------------------------------------------------------------------------
 */

Script to read a WAMIT output file
"""

import re
import mmap
import linecache
import numpy as np

"""
Read file to get characteristic input parameters
"""

# initialize variables
# strings
wamOUT = './files/opt_x.out'
# variables/arrays
nbodies = 0  # number of bodies
nwaveperiods = 0  # number of wave periods
countlines = 0
linnum = 0  # line number counter ?

# lists
waveT = np.array([])  # wave period in units of time
kL_number = []  # wave number
ixwp = []
charnum = []  # character number
dat_IJ_AB = [] # rigid-body mode (I, J), added mass (A) and damping (B)

# Laws of the landmarks of WAMIT defined by observation:
# (1) first law: between each 'Wave period (sec)=' landmark there are 11 lines plus the number of lines
# corresponding to the number of modes
law1 = 11
# (2) second law: there are 7 lines from 'Wave period (sec)=' to first line with added mass and
# damping coefficients
law2 = 7

with open(wamOUT) as fl_wd:  # keeps the flow controlled :)

    # get file 'landmarks'
    mmFW = mmap.mmap(fl_wd.fileno(), 0, access=mmap.ACCESS_COPY)  # create memory mapped file object
    for line in iter(mmFW.readline, ""):
        linnum += 1  # count lines (!)
        charnum.append(mmFW.tell())  # current file "seek location", this is the end of the current line
        if 'Body number: N=' in line:
            nbodies += 1  # counter to get number of bodies
            # maybe save index??
        if 'Wave period (sec) =' in line:
            # ixwp.append(mmFW.find('Wave period (sec)'))     # (!) this does not get it quite right
            ixwp.append(linnum - 1)  # save line index
            nwaveperiods += 1  # ... number of wave periods (or body oscillations)

        if 'Wave period = zero' in line:
            infwaveIDX = 0

    # mmFWLs = fl_wd.readlines()  # this is an option to search by line

Aixwp = np.array(ixwp[:])  # this is for error checking: TODO: write method for error checking
if len(set(Aixwp[1:-1] - Aixwp[0:-2])) == 1:
# i) calculate number of modes, using 1st law
    nmodes = Aixwp[1] - Aixwp[0] - law1     # TODO: split this from error checking module
                                            # TODO: move this out of the way
    print '\n all good - there is ', nmodes, ' rigid body mode(s) for each of the ', nwaveperiods, \
			' wave period(s) in the output file, and there are ', nbodies, ' body (ies) \n'  
else:
    print '\n error'   # TODO: how to exit the program if this case is true?

# here: crunch the lines in between each landmark to get, wave period, added mass and damping
# use cache lines

theseLs = linecache.getlines(wamOUT) # these are the lines in the file and can be accessed randomly
for i in Aixwp:

    lineDat = theseLs[i].split()

# wave periods, K numbers, and so on ... TODO: check units automatically, and so on ...
    waveT = np.append(waveT, np.float(lineDat[4]))
    kL_number = np.append(kL_number, np.float(lineDat[-1]))

# ii) setup line indexes and get values for added mass and damping coefficients
    # get modes and coefficients into list
    dat_IJ_AB.append(theseLs[i + law2:i + law2 + nmodes])

"""
At this stage you can use dat_IJ_AB to extract modes as follows, for a wave 
period equal to the value in waveT[-1], for example:

"""
tempDat = str(dat_IJ_AB[-1]).split() #TODO: implement interpolation
IJ_mode = [tempDat[1], tempDat[2]]
AddedM  = tempDat[3]
Damping = tempDat[4].split('\\n')[0]

print 'From Wamit file: ', wamOUT, ': \n'
print '\n Rigid body mode, corresponding to ', IJ_mode, ' degree-of-freedom \n', \
      'has non-dimensional added mass coefficient of ', AddedM, '\n and damping', \
      Damping  

# TODO:
# iii) define which modes correspond to which bodies
# (!) this is not so trivial because for each body, different number of modes can be outputted
#   (!) simplest case is all modes of all bodies are outputted -> 6 x nbodies
#   (!) second simplest case is the same number of bodies are outputted for each body -> #modes/nbodies
# iv) sort out the other variables I need to extract
#
# > other stuff more software related
# -> move from procedural to object oriented if is necessary 
# -> see how this could fit into Bemio ?
