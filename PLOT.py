# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 13:30:51 2019

@author: CRYOGENIC
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import pandas as pd
from IPython import get_ipython
mgc = get_ipython().magic
mgc(u'%matplotlib qt')

fname = 'test1.dat'
x_column = 'aaa'
y_column = 'bbb'

# style.use('fivethirtyeight')

fig = plt.figure()
ax = fig.add_subplot(1,1,1)


graph_data = pd.read_csv(fname, skipinitialspace=True)
x = graph_data[x_column].to_numpy()
y = graph_data[y_column].to_numpy()
curve, = ax.plot(x, y)


def animate(i):
    graph_data = pd.read_csv(fname, skipinitialspace=True)
    x = graph_data[x_column].to_numpy()
    y = graph_data[y_column].to_numpy()
    curve.set_data([x, y])
    return curve, ax
    

ani = animation.FuncAnimation(fig, animate, interval=1000, blit=True)
plt.xlabel(x_column)
plt.ylabel(y_column)
plt.tight_layout()
ax.callbacks.connect('xlim_changed', lambda event: ani._blit_cache.clear())
ax.callbacks.connect('ylim_changed', lambda event: ani._blit_cache.clear())
plt.show()