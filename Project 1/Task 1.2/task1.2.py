
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def plotData2D(data, sigma, mu, filename=None):
    # create a figure and its axes
    fig = plt.figure()
    axs = fig.add_subplot(111)
    
    # plot the data 
    x_min, x_max = 140, 210
    x = np.linspace(x_min, x_max, 1000)
    y = norm.pdf(x, mu, sigma)
    axs.plot(x, norm.pdf(x, mu, sigma), label='normal')
    axs.plot(data[:,1], np.zeros_like(data[:,1]), 'ro', markersize=4,
             label='data',  alpha=0.3)

    # set x and y limits of the plotting area
    axs.set_xlim(x_min, x_max)
    axs.set_ylim(0., y.max()+0.01)

    # set properties of the legend of the plot
    leg = axs.legend(loc='upper right', shadow=True, fancybox=True, numpoints=1)
    leg.get_frame().set_alpha(0.5)
            
    # either show figure on screen or write it to disk
    if filename == None:
        plt.show()
    else:
        plt.savefig(filename, facecolor='w', edgecolor='w',
                    papertype=None, format='pdf', transparent=False,
                    bbox_inches='tight', pad_inches=0.1)
    plt.close()
    
    
if __name__ == "__main__":
    #######################################################################
    # 1st alternative for reading multi-typed data from a text file
    #######################################################################
    # define type of data to be read and read data from file
    dt = np.dtype([('w', np.float), ('h', np.float), ('g', np.str_, 1)])
    data = np.loadtxt('whData.dat', dtype=dt, comments='#', delimiter=None)

    # read height, weight and gender information into 1D arrays
    ws = np.array([d[0] for d in data])
    hs = np.array([d[1] for d in data])
    gs = np.array([d[2] for d in data]) 
    
    # Task 1.1
    outlierInd = np.where( ws != -1 ) 
    ws, hs, gs = ws[outlierInd], hs[outlierInd], gs[outlierInd]

    ##########################################################################
    # 2nd alternative for reading multi-typed data from a text file
    ##########################################################################
    # read data as 2D array of data type 'object'
    data = np.loadtxt('whData.dat',dtype=np.object,comments='#',delimiter=None)

    # read height and weight data into 2D array (i.e. into a matrix)
    X = data[:,0:2].astype(np.float)

    # read gender data into 1D array (i.e. into a vector)
    y = data[:,2]
    
    # Task 1.1
    outlierInd = np.where( X[:,0] != -1 ) 
    X, y = X[outlierInd], y[outlierInd]
    
    # Stat. of students
    sigma = np.std(X[:,1])
    mu = np.mean(X[:,1])

    # now, plot weight vs. height using the function defined above
    plotData2D(X, sigma, mu, 'plotNormal.pdf')

