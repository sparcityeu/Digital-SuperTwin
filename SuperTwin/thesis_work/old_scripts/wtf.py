import matplotlib.pyplot as plt
import numpy as np

# Set the dimensions of the data
dimensions = 8

# Create random data for the plot
data = np.random.rand(dimensions, dimensions)

# Set the width and height of the plot
width = 12
height = 12

# Create the figure and set the title
fig, ax = plt.subplots(figsize=(width, height))
ax.set_title("I TOLD YOU")

# Loop through the dimensions and create a subplot for each two-way combination
for i in range(dimensions):
    for j in range(dimensions):
        if i < j:
            ax = fig.add_subplot(dimensions, dimensions, i * dimensions + j + 1)
            ax.bar(data[i, :], data[j, :])

# Show the plot
plt.show()
