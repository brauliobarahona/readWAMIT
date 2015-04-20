# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 13:47:56 2015

@author: bbarahon

Example of loading two WAMIT *.out files with different number of modes saved
to output.

"""

import matplotlib.pyplot as plt

from readwamit_v01 import readWamit

# read file with one mode
rwd = readWamit()     #create class instance and pass WAMIT file name
wT1, nms1, dAB1 = rwd.ReadOutFile('./files/opt_x.out')    # read file

AdM1, Damp1 = rwd.ReadMode(['3','3'], wT1, nms1, dAB1) 

# read file with many modes/nodies
rwd = readWamit()     #create class instance and pass WAMIT file name
wT2, nms2, dAB2 = rwd.ReadOutFile('./files/opt_ALL.out')    # read file

AdM2, Damp2 = rwd.ReadMode(['3','3'], wT2, nms2, dAB2) 

# Plot stuff
plt.subplot(2, 1, 1)
plt.plot(wT1, AdM1, label='opt_x')
plt.plot(wT2, AdM2, label='opt_ALL')

plt.xlabel('wave period (s)')
plt.title('Non-dimensional added mass coefficients')
plt.legend(loc='lower right', frameon= False)
plt.show()
 
plt.subplot(2, 1, 2)
plt.plot(wT1, Damp1, label='opt_x')
plt.plot(wT1, Damp1, label='opt_ALL')
plt.xlabel('wave period (s)')
plt.title('Non-dimensional damping coefficients')
plt.show()
