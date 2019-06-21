# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 18:48:07 2019

@author: wangc
"""

import utils_Charlie
kwargs = {}

lockinAddrs = [8, 12,10] # addresses of all lockins. Must be a list.
masterAddrs = [12] # address of the master lockin. Must be a list.
magnetAddr = 25 # address of the magnet power supply.
rampSequence = [0] # a sequence of set points. Must be a list.

"""
Lockin  sens        tconst
0       2 nV/fA     10 µs 
1       5 nV/fA     30 µs
2       10 nV/fA    100 µs
3       20 nV/fA    300 µs
4       50 nV/fA    1 ms
5       100 nV/fA   3 ms 
6       200 nV/fA   10 ms
7       500 nV/fA   30 ms
8       1 µV/pA     100 ms
9       2 µV/pA     300 ms
10      5 µV/pA     1 s
11      10 µV/pA    3 s
12      20 µV/pA    10 s
13      50 µV/pA    30 s
14      100 µV/pA
15      200 µV/pA
16      500 µV/pA
17      1 mV/nA
18      2 mV/nA
19      5 mV/nA
20      10 mV/nA
21      20 mV/nA
22      50 mV/nA
23      100 mV/nA
24      200 mV/nA
25      500 mV/nA
26      1 V/µA
"""
kwargs['sens'] = 19
kwargs['tconst'] = 10
"""
reserve:    0 for High, 1 for Normal, 2 for Low-N
ab:         0 for A, 1 for A-B
gnd:        0 for FLOAT, 1 for GND
adc:        0 for AC, 1 for DC
lfilter:    0 for OFF, 1 for 1x, 2 for 2x
internal:   0 for external, 1 for internal
ttl:        0 for zero crossing, 1 for rising edge, 2 for falling edge
sync:       0 for OFF, 1 for ON (Almost always use 0)
dB:         0 for 6dB/oct, 1 for 12dB, 2 for 18 dB, 3 for 24 dB
"""
kwargs['reserve'] = 2
kwargs['ab'] = 1
kwargs['gnd'] = 1
kwargs['adc'] = 1
kwargs['lfilter'] = 0
kwargs['intern'] = 0
kwargs['ttl'] = 1
kwargs['sync'] = 0
kwargs['dB'] = 3
"""
ampl:       Output Vrms (float)
harm:       Harmonic # (int)
freq:       Frequency (float)
phase:      Reference phase (float)
"""
kwargs['ampl'] = 5
kwargs['harm'] = 1
kwargs['freq'] = 13
kwargs['phase'] = 0

kwargs['name_file'] = 'BaSbTeS-300K-r' # name of your project
#kwargs['name_file'] = 'test_Chulin' # name of your project

kwargs['idx_file'] = 5 # the index of saved files. WILL add 1 until this index is not occupied
kwargs['extra_time'] = 60 # Seconds after each magnetic field ramp
kwargs['delta_time'] = 1 # wait time between datapoints

try:
    utils_Charlie.experiment(lockinAddrs, masterAddrs, magnetAddr, rampSequence, **kwargs)
except (KeyboardInterrupt, SystemExit):
    utils_Charlie.finalClear(lockinAddrs)
    