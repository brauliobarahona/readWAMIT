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

# >>WAMIT file name
wamOUT = './files/opt_x.out'

# >>Define rules to look up for landmarks in the file and load data for visualization. These rules should make the structure of the script flexible and general, considering that the structure of the output file for a specific code is essentially the same but there will be different files depending on the run setup.
# Laws of the landmarks of WAMIT defined by observation:
# (1) First law: between each 'Wave period (sec)=' landmark there are 11 lines plus the number of lines
# corresponding to the number of modes
law1 = 11

# (2) Second law: there are 7 lines from 'Wave period (sec)=' to first line with added mass and
# damping coefficients
law2 = 7

# (3) Thrid Law: hydrostatic and restoring coeffcients lie in the next 3 lines from 'Water depth:'-line
# plus 17 lines; that is the next 3 lines after 'Hydrostatic and gravitational restoring coefficients:'
law3 = 17
law4 = 2    # better, from 'Center of Buoyancy (Xb, Yb, Zb)' two lines to the these coefficients
law5 = 3    # there are 3 lines with the hydrostatic restoring coefficients for each body

# initialize variables
# >> variables/arrays
nbodies = 0    # number of bodies
nwaveperiods = 0    # number of wave periods
countlines = 0
linnum = 0    # line number counter ?
flgWD = 0     # flag to refer to 'Water depth:' line
flgBP = 0     # flag to refer to 'BODY PARAMETERS:' line
flgHR = 0

# >> lists
flgHR2 = []
gravity = []
length_scale = []
water_depth = []
sim_flags = []
body_par = []
volumesXYZ = []
center_bouyancy = []
hydrostatic_restoring = []
center_gravity= []

ixwp = []    # line index for 'Wave period (sec) =' line
charnum = []  # character number

with open(wamOUT) as fl_wd:  # keeps the flow controlled :)

    # get file 'landmarks'
    mmFW = mmap.mmap(fl_wd.fileno(), 0, access=mmap.ACCESS_COPY)  # create memory mapped file object
    for line in iter(mmFW.readline, ""):
        linnum += 1  # count lines (!)
        charnum.append(mmFW.tell())  # current file "seek location", this is the end of the current line
        if 'Body number: N=' in line:
            nbodies += 1  # counter to get number of bodies

        if 'Wave period (sec) =' in line:
            # ixwp.append(mmFW.find('Wave period (sec)'))     # (!) this does not get it quite right
            ixwp.append(linnum - 1)  # save line index
            nwaveperiods += 1  # ... number of wave periods (or body oscillations)

        if 'Wave period = zero' in line:
            infwaveIDX = 0
            
        if 'Gravity:'in line:
            gravity = line.split()[1]
            length_scale = line.split()[-1]
            
        if 'Water depth:' in line:
            water_depth = line.split()[-1]
            flgWD = linnum
            flgHR = linnum + law3 - 1    # (python-index) flag is set here, later coefficients are read - valid for 1 body only
            
        if 'Volumes (VOLX,VOLY,VOLZ):' in line:    # here volumes, one set per body
            volumesXYZ.append(line.split()[-3:])
            
        if 'Center of Buoyancy (Xb,Yb,Zb):' in line:    # here bouyancy center, one set per body
            center_bouyancy.append(line.split()[-3:])
            flgHR2.append(linnum + law4 - 1) # (python-index for lines)
            
        if 'Center of Gravity  (Xg,Yg,Zg):' in line:    # here bouyancy center, one set per body
            center_gravity.append(line.split()[-3:])
            
# (!) TODO: define laws for       
# sim_flags = []
# body_par = []

# >> Check that things are making sense
Aixwp = np.array(ixwp[:])  # this is for error checking: TODO: write method for error checking
if len(set(Aixwp[1:-1] - Aixwp[0:-2])) == 1:
# i) calculate number of modes, using 1st law
    nmodes = Aixwp[1] - Aixwp[0] - law1     # TODO: split this, make an error checking module
                                            # TODO: move this out of the way
    print '\n all good - there is ', nmodes, ' rigid body mode(s) for each of the ', nwaveperiods, 			' wave period(s) in the output file, and there are ', nbodies, ' body (-ies) \n'  
    if nmodes == 1:
        print '(!) Note: take a look at the input files to be sure which body this mode corresponds to.'
else:
    print '\n error'   # TODO: how to exit the program if this case is true?

# here: crunch the lines in between each landmark to get, wave period, added mass and damping
# use cache lines
theseLs = linecache.getlines(wamOUT) # these are the lines in the file and can be accessed randomly

Ldat_C = []    # create empty list
for i in range(2):    # populate list with arrays
    Ldat_C.append( np.zeros((6, 6), dtype=np.float) )

# index for filling up C matrices
iixC3 = range(2,5)
iixC4 = range(3,6)

# use flgHR2 to store hydrostatic restoring coefficients
for i in flgHR2:
    hydrostatic_restoring.append(theseLs[i:i + law5])

# use nbodies
for i in range(nbodies):    # loop for each body
    for j in range(law5):    # loop the three rows of hydrostatic coefficients    
        for k in range(-1,-4,-1):    # loop the last 3 elements of each split line

            try:                 
                # check if string is ' C(3,3),C(3,4),C(3,5): '
                if hydrostatic_restoring[i][j].split()[0] == hydrostatic_restoring[0][0].split()[0]:
                
                    Ldat_C[i][j + 2, iixC3[k]] = np.float(hydrostatic_restoring[i][j].split()[k])
                    
                else:
                    
                    Ldat_C[i][j + 2, iixC4[k]] = np.float(hydrostatic_restoring[i][j].split()[k])

            except ValueError:
                print 'There is a string in hydrostatic_restoring[i][j].split()[k]'
                print hydrostatic_restoring[i][j].split()[k], '--- (!) WAMIT index'
                print 'For body ',i + 1, ', C(', j+2, ',', iixC4[k],') will be kept to zero --- (!) Python index\n'
                
for i in range(len(Ldat_C)):
    print 'Hydrostatic restoring coefficients of body ', i + 1, ':\n', Ldat_C[i][:]

# >>
dat_IJ_AB = [] # rigid-body mode (I, J), added mass (A) and damping (B)
waveT = np.array([])  # wave period in units of time
kL_number = []  # wave number

for i in Aixwp:

    lineDat = theseLs[i].split()

# wave periods, K numbers, and so on ... 
    waveT = np.append(waveT, np.float(lineDat[4]))
    kL_number = np.append(kL_number, np.float(lineDat[-1]))

# ii) setup line indexes and get values for added mass and damping coefficients
    # get modes and coefficients into list
    dat_IJ_AB.append(theseLs[i + law2:i + law2 + nmodes])

# >> At this stage you can use `dat_IJ_AB` to extract modes as follows,	
# dat_IJ_AB[ nwaveperiods or len(waveT)  ][ nmodes ]

ico = 0
for i in range(nmodes):
    
    if dat_IJ_AB[-1][i].split()[0:2] == ['3','3'] or dat_IJ_AB[-1][i].split()[0:2] == ['9','9']:    # make this to automatically scale with nbodies
        ico += 1
        print 'Heave mode for body', ico, '=> ', dat_IJ_AB[-1][i]

# > Once the most important parameters from the *.out file are mapped, the dependency of added mass and damping to wave periods can be easily analyzed.
# * Get added mass and damping of a given mode of a given body across wave periods

# In[17]:

AdddedMassHeave = []
DampingHeave = []

# get a specific mode for all wave periods
for i in range(len(waveT)):
    for j in range(nmodes):
    
        if dat_IJ_AB[i][j].split()[0:2] == ['3','3']:
            AdddedMassHeave.append( dat_IJ_AB[i][j].split()[-2] )
            DampingHeave.append( dat_IJ_AB[i][j].split()[-1] )


# > * Plot coefficients versus wave period

# In[18]:

get_ipython().magic(u'pylab inline')

figure()
plt.plot(waveT, AdddedMassHeave)
xlabel('wave period (s)')
title('Non-dimensional added mass coefficients')
show()

figure()
plt.plot(waveT, DampingHeave)
xlabel('wave period (s)')
title('Non-dimensional damping coefficients')
show()
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
