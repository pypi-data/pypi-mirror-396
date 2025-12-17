import matplotlib.pyplot as plt


class PickClusters:
    """Class for picking cluster positions by clicking in a figure"""

    def __init__(self, figure, r):
        ### TODO: Figure out how to set the radius of the circle interactively
        self.figure = figure  # this is where the circle lives
        self.centroid = []
        self.rs = []
        self.r = r  # remove once the todo is fixed

    def connect(self):
        self.press = self.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.release = self.figure.canvas.mpl_connect('button_release_event', self.on_release)

    def on_press(self, event):
        self.centroid.append((event.ydata, event.xdata))
        self.rs.append(self.r)  # this should be updated interactively

    def on_release(self, event):
        c = plt.Circle((event.xdata, event.ydata), self.rs[-1], color='b', fill=False)
        self.figure.gca().add_patch(c)


        