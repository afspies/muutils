# ------------------------------------------------------------
# WARNING: this script is auto-generated by `convert_ipynb_to_script.py`
# showing plots has been disabled, so this is presumably in a temp dict for CI or something
# so don't modify this code, it will be overwritten!
# ------------------------------------------------------------


# ------------------------------------------------------------
# Disable matplotlib plots, done during processing by `convert_ipynb_to_script.py`
import matplotlib.pyplot as plt

# %%
import numpy as np

plt.show = lambda: None
# ------------------------------------------------------------


# %%
"""
# heading

this is a markdown cell, it should appear in the output as a comment
"""

# %%
print("Hello world!")

# %%
array = np.array([1, 2, 3])
print(array)

# %%
plt.plot(array)
plt.show()
