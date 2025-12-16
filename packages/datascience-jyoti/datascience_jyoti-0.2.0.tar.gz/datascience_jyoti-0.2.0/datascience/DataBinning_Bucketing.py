import numpy as np
import matplotlib.pyplot as plt
#mlab.normpdf is removed from Matplotlib. hence using NUMPy
np.random.seed(0)

mu = 90     # mean
sigma = 25  # standard deviation

x = mu + sigma * np.random.randn(5000)

num_bins = 25
fig, ax = plt.subplots()

# Histogram
n, bins, patches = ax.hist(x, num_bins, density=True, alpha=0.6)

# Best-fit normal distribution using NumPy
y = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((bins - mu) / sigma)**2)
ax.plot(bins, y, '--')

ax.set_xlabel('Example Data')
ax.set_ylabel('Probability Density')

# Title with raw string to avoid escape errors
sTitle = (
    r'Histogram ' + str(len(x)) + ' entries into ' + str(num_bins) +
    r' Bins: $\mu=' + str(mu) + r'$, $\sigma=' + str(sigma) + r'$'
)
ax.set_title(sTitle)

fig.tight_layout()

sPathFig = 'C:/Users/JYOTI RAHATE/Downloads/DataScience/Outputfile/DU-Histogram.png'
fig.savefig(sPathFig)

plt.show()
