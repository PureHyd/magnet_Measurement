# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 15:49:55 2019

@author: wangc
"""

import time
from datetime import datetime, timedelta
import numpy as np
import newvisaOxf
import os
import sys
import visa

def timeFloat(DT):
    DN = (DT - datetime(2019,1,1)).total_seconds()
    return(DN)
    
def linkLockin(addr, rm):
    try:
        lockin = rm.open_resource('GPIB0::{}::INSTR'.format(addr))
        clearCache(lockin)
        return lockin
    except:
        print('Lockin {} not linked\n'.format(addr))
        return None

def clearCache(lockin):
    while True:
        try:
            lockin.read()
            print('Cache cleared\n')
        except:
            break

def finalClear(lockinAddrs):
    rm = visa.ResourceManager()
    for addr in lockinAddrs:
        lockin = rm.open_resource('GPIB0::{}::INSTR'.format(addr))
        clearCache(lockin)
    sys.exit()
        
def setLockin(lockin, **kwargs):
    sens = kwargs['sens']
    tconst = kwargs['tconst']
    ampl = kwargs['ampl']
    freq = kwargs['freq']
    harm = kwargs['harm']
    sync = kwargs['sync']
    reserve = kwargs['reserve']
    dB = kwargs['dB']
    adc = kwargs['adc']
    gnd = kwargs['gnd']
    lfilter = kwargs['lfilter']
    ab = kwargs['ab']
    phase = kwargs['phase']
    intrn = kwargs['intern']
    ttl = kwargs['ttl']
    try:
        readout = []
        readout += lockin.write('SENS'+str(sens))
        readout += lockin.write('OFLT'+str(tconst))
        readout += lockin.write('SLVL'+str(ampl))
        readout += lockin.write('FREQ'+str(freq))
        readout += lockin.write('HARM'+str(harm))
        readout += lockin.write('SYNC'+str(sync))
        readout += lockin.write('RMOD'+str(reserve))
        readout += lockin.write('OFSL'+str(dB))
        readout += lockin.write('ICPL'+str(adc))
        readout += lockin.write('IGND'+str(gnd))
        readout += lockin.write('ILIN'+str(lfilter))
        readout += lockin.write('ISRC'+str(ab))
        readout += lockin.write('PHAS'+str(phase))
        readout += lockin.write('FMOD'+str(intrn))
        readout += lockin.write('RSLP'+str(ttl))
        print(readout)
        return kwargs
    except:
        print('!!! lockin not properly set\n')
        return None

def readLockin(lockin):
    # Read X, Y
    try:
        readout = lockin.query('SNAP?1,2').strip('\n')
        return readout + ','
    except:
        return None

def setFilename(fname, lockinAddrs, i=1):
    while True:
        if os.path.isfile('results/{}_{:03d}.dat'.format(fname, i)):
            i += 1
        else:
            break
    filepath = 'results/{}_{:03d}.dat'.format(fname, i)
    with open(filepath, "x") as f:
        header = 'Time, B_digital, Timefloat, '
        for addr in lockinAddrs:
            header += 'V_real_{}, V_imag_{}, '.format(addr, addr)
        header += '\n'
        f.write(header)
        print('file saved at results/{}_{:03d}.dat'.format(fname, i))
    logpath = 'results/{}_log_{:03d}.dat'.format(fname, i)
    return filepath, logpath

def magClear(mag):
    mag.setControl(3)
    # Clearing Cache
    while True:
        try:
            a = mag._visa_resource.read()
            print(a)
        except:
            break

def tMap(B):
    if np.abs(B) > 16:
        raise Exception('Magnet field B = {} out of bound'.format(B))
    if np.abs(B) < 12:
        return B * 60 / 0.3
    elif B < 15 and B > 0:
        return (12 + 2*(B-12)) * 60 / 0.3
    elif B > 15:
        return (12 + 2*3 + 4*(B-15)) * 60 / 0.3
    elif B > -15:
        return (-12 + 2*(B+12)) * 60 / 0.3
    else:
        return (-12 - 2*3 + 4*(B+15)) * 60 / 0.3

def deltaTime(B0, B1, extra):
    return np.abs(tMap(B0) - tMap(B1) + extra)

def measure_multi(tot_time, delta, lockins, mag, target, filepath, logpath, flag=''):
    tic = datetime.now()
    toc = datetime.now()
    
    with open(logpath, 'a') as f:
        f.write(str(datetime.now()) + '\n')
        f.write('Field now: {}\n'.format(mag.readField()))
        f.write('set:       {}\n'.format(mag.readFieldSetpoint()))
        f.write('ETA:       {}\n\n'.format(datetime.now() + timedelta(seconds=tot_time)))
    
    print("\n=============")
    print(datetime.now())
    mag.setFieldSweepRate(0.3)
    print("rate:      {}".format(mag.readFieldSweepRate()))
    mag.setFieldSetpoint(target)
    print("set:       {}".format(mag.readFieldSetpoint()))
    print("Field now: {}".format(mag.readField()))
    mag.setActivity(1)
    print("ramp started.")
    time.sleep(1)
    print("Field now: {}".format(mag.readField()))
    print("ETA:       {}".format(datetime.now() + timedelta(seconds=tot_time)))
    
    while toc < tic + timedelta(seconds=tot_time):
        toc = datetime.now()
        print(toc - tic)
        Bnow = mag.readField()
        result = str(datetime.now()) + ',' + str(Bnow) + ',' +\
                 str(timeFloat(toc)) + ','
        for lockin in lockins:
            result += readLockin(lockin)
        result += '\n'
        print(str(flag) + ', ' + result)
        with open(filepath, 'a') as f:
            f.write(result)
        time.sleep(delta)
    return

def experiment(lockinAddrs, masterAddr, magnetAddr, rampSequence, **kwargs):
    if not os.path.isdir('results/'):
        os.mkdir('results/')
    name = kwargs['name_file']
    idx = kwargs['idx_file']
    extra = kwargs['extra_time']
    delta = kwargs['delta_time']
    
    rm = visa.ResourceManager()
    print(rm.list_resources())
    filepath, logpath = setFilename(name, lockinAddrs, idx)
    
    with open(logpath, 'w') as f:
        f.write('lockin : {} ,\n'.format(lockinAddrs))
        f.write('master : {} ,\n'.format(masterAddr))
        f.write('magnet : {} ,\n'.format(magnetAddr))
        f.write('ramp : {} ,\n'.format(rampSequence))
        for a in kwargs:
            f.write('{} : {} ,\n'.format(a, kwargs[a]))
    
    lockins = []
    for addr in lockinAddrs:
        lockin = linkLockin(addr, rm)
        lockins.append(lockin)
        out = setLockin(lockin, **kwargs)
        if out == None:
            raise ValueError('Lockin address incorrect')
        if addr in masterAddr:
            lockin.write('FMOD1')
    
    mag = newvisaOxf.ips120(magnetAddr)
    magClear(mag)
    Bnow = mag.readField()
    BnowStore = Bnow
    totTime = 0

    for B in rampSequence:
        totTime += deltaTime(B, Bnow, extra)
        Bnow = B
    print("Final ETA:  {}".format(datetime.now() + timedelta(seconds=totTime)))
    
    Bnow = BnowStore
    for B in rampSequence:
        dtime = deltaTime(B, Bnow, extra)
        measure_multi(dtime, delta, lockins, mag, B, filepath, logpath, flag='')
        Bnow = B
    
    with open(logpath, 'a') as f:
        f.write(str(datetime.now()) + '\n')
        f.write('Field now: {}\n'.format(mag.readField()))
        f.write('\nMeasurement complete.\n')
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

reserve:    0 for High, 1 for Normal, 0 for Low-N
ab:         0 for A, 1 for A-B
gnd:        0 for FLOAT, 1 for GND
adc:        0 for AC, 1 for DC
lfilter:    0 for OFF, 1 for 1x, 2 for 2x
internal:   0 for external, 1 for internal
ttl:        0 for zero crossing, 1 for rising edge, 2 for falling edge
sync:       0 for OFF, 1 for ON (Almost always use 0)
dB:         0 for 6dB/oct, 1 for 12dB, 2 for 18 dB, 3 for 24 dB

ampl:       Output Vrms (float)
harm:       Harmonic # (int)
freq:       Frequency (float)
phase:      Reference phase (float)
"""
