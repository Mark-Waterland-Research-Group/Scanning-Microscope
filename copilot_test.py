# q: write me a helloworld program
# a: print("Hello World")   

# a program that uses matplotlib to plot a sine wave

import matplotlib.pyplot as plt
import numpy as np

x = np.arange(0, 2*np.pi, 0.1)
y = np.sin(x)

plt.plot(x, y)
# turn off the axes
plt.axis('off')


plt.show()

