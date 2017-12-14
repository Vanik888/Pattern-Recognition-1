#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: canyuce
"""
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import time

# train and test file str
train_f = "data2-train.dat"
test_f  = "data2-test.dat"
split_method='median'
sel_method='alternate'

class Node:
    # Node of a kd-tree
    # params: 
    #   x, y, label: x, y coordinates and label of the split
    #   l_child, r_child: left and right children of the node
    # 
    #   r1, r2: left and right rectangles that the nodes split
    #   r_1 : arr[x,y,width, height]
    #   r_2 : arr[x,y,width, height]
    def __init__(self, x, y, split_dim, label, l_child, r_child, r_1, r_2):
        self.x = x
        self.y = y
        self.split_dim = split_dim
        self.label = label
        self.l_child = l_child
        self.r_child = r_child
        self.is_leaf = (l_child == r_child)
        self.r_1 = r_1
        self.r_2 = r_2       

# construct the tree in recursive fashion
#   depth : current depth in the tree
#   frame_coord: frame coordinates of the current cell
#   sel_method: determines how to select the splitting dimension
#           'alternate': alternate between the x and  the y dimension 
#           'variance': split the data along the dimension of higher variance.
#   split_method: determines how to compute the split point
#           'midpoint': split at the midpoint of the data
#           'median': split at the median of the data
def kd_tree(data, depth, frame_coord):
    global k
    
    try: # is leaf node?
        data[1]
    except IndexError:
        return None

    if sel_method == 'alternate':
        d = depth % k
    elif sel_method == 'variance':
        d = 0 if np.std(data[:,0]) > np.std(data[:,1]) else 1
        
    # sort array wrt. split column/row
    d_sorted = data[data[:,d].argsort()]
    X_len = len(d_sorted)
    # argmedian
    if split_method == 'median':
        split_ind = X_len // 2
        split_x = d_sorted[split_ind, 0]
        split_y = d_sorted[split_ind, 1]
        split_label = d_sorted[split_ind, 2]
    elif split_method == 'midpoint':
        mid_p = (d_sorted[:,d][0]+d_sorted[:,d][-1])/2
        split_label = -1 # no split labels when midpoint split is used
        split_ind=np.min(np.where(d_sorted[:,d] >= mid_p))

        if d == 0:
            split_x = mid_p
            split_y = -1  # irrelevant when we split on the x coordinate system.
        else:
            split_y = mid_p
            split_x = -1
           
    # divides horizontally/vertically 
    r_1, r_2, fc_1, fc_2 = None, None, None, None
        
    if d == 0:     
        # rectangle coordinates(will help while plotting the tree splits)
        r_1 = [frame_coord[0], frame_coord[2], split_x-frame_coord[0],
               frame_coord[3]-frame_coord[2]]
        r_2 = [split_x, frame_coord[2], frame_coord[1]-split_x, 
               frame_coord[3]-frame_coord[2]]
        # frame_coord: frame coordinates of the cells splitted
        fc_1 = [frame_coord[0], split_x, frame_coord[2], frame_coord[3]]
        fc_2 = [split_x, frame_coord[1], frame_coord[2], frame_coord[3] ]
    else:
        # rectangle coordinates(will help while plotting the tree splits)
        r_1 = [ frame_coord[0], frame_coord[2], frame_coord[1]-frame_coord[0], 
               split_y-frame_coord[2] ]
        r_2 = [ frame_coord[0], split_y, frame_coord[1]- frame_coord[0],
               frame_coord[3]-split_y ]
        # frame_coord: frame coordinates of the cells splitted
        fc_1 = [frame_coord[0], frame_coord[1], frame_coord[2], split_y]
        fc_2 = [frame_coord[0], frame_coord[1], split_y, frame_coord[3] ] 

    return Node(split_x, split_y, d, split_label, 
                kd_tree(d_sorted[:split_ind,:], depth+1, fc_1),
                kd_tree(d_sorted[split_ind+1:,:], depth+1, fc_2),
                        r_1, r_2)

def read_file(file_name): 
    # read data as 3D array of data type 'object'
    data = np.loadtxt(file_name, dtype=np.object, comments='#', delimiter=None)
        
    # read first and second column data and labels into 3D array 
    data = data.astype(np.float)
    data[:,-1] = data[:,-1].astype(np.int32) 
    
    return data

def generate_kdtree(data): 
    global k    
    k = len(data[0])-1
    
    # construct tree
    min_x = min(data[:,0]) - 5
    max_x = max(data[:,0]) + 5
    min_y = min(data[:,1]) - 5
    max_y = max(data[:,1]) + 5
    
    return kd_tree(data, 0, [min_x, max_x, min_y, max_y])
 
# traverses the tree and draws plots 
#   root : root node
#   axs: plot axis
#   depth: level to be plotted     
def plot_tree(root, axs, depth):
    if (depth > 0):
        # plot left/bottom cell rectangle
        axs.add_patch(
            patches.Rectangle(
                (root.r_1[0], root.r_1[1]),   # (x,y)
                root.r_1[2],          # width
                root.r_1[3],          # height
                fill = False,
                alpha=1
            )
        )
        # plot right/top cell rectangle
        axs.add_patch(
            patches.Rectangle(
                (root.r_2[0], root.r_2[1]),   # (x,y)
                root.r_2[2],          # width
                root.r_2[3],          # height
                fill = False,
                alpha=1
            )
        )    
    
    if (root.l_child) and (depth > 0):
        plot_tree(root.l_child, axs, depth-1)
    if root.r_child and (depth > 0) :
        plot_tree(root.r_child, axs, depth-1)    
               
# traverses and plots the tree
# root: root of the constructed tree
def print_kdtree(root, data, scatter=True, level=range(1,5), returnPlt=False, 
                 save=True):
        
    # construct tree
    min_x = min(data[:,0]) - 5
    max_x = max(data[:,0]) + 5
    min_y = min(data[:,1]) - 5
    max_y = max(data[:,1]) + 5
    
    for i in level:
        # plot tree structure by level
        fig = plt.figure()
        axs = fig.add_subplot(111)
        axs.set_aspect('equal')
        # scatter data points on plot
        if scatter:
            axs.scatter(data[:,0], data[:,1], s=20, c=data[:,-1], cmap="bwr")
            
        # set x and y limits of the plotting area
        axs.set_xlim(min_x, max_x)
        axs.set_ylim(min_y, max_y)
        plt.xlabel('x')
        plt.ylabel('y')
        
        plot_tree(root, axs, i)
        
        # either show figure on screen or write it to disk
        if returnPlt:
            return axs
        if save:
            filename = 'chart/kdtree_%s_%s_level_%d.pdf'%(split_method,sel_method,i)
            plt.savefig(filename, facecolor='w', edgecolor='w',
                        papertype=None, format='pdf', transparent=False,
                        bbox_inches='tight', pad_inches=0.1)
        plt.close()
    
# traverses the tree and pushes visited nodes into a stack 
#   root : root node
def traverse_tree(root, data, stack):
    
    if root != None:
        stack.append(root)
    else:
        return None
    
    if root.split_dim == 0:
        if root.x > data[0]:
            traverse_tree(root.l_child, data, stack)   
        elif root.x <= data[0]:
            traverse_tree(root.r_child, data, stack)   
    elif root.split_dim == 1:
        if root.y > data[1]:
            traverse_tree(root.l_child, data, stack)   
        elif root.y <= data[1]:
            traverse_tree(root.r_child, data, stack)         
    
# infer labels on the generated kd_tree
def kd_tree_inference(root, test_data, save=False):
    node_stack = []
    bench_m = np.zeros(len(test_data))
    
    for i in range(1,len(test_data)):
        start = time.time()
        s = test_data[i]
        traverse_tree(root, s, node_stack)
        b_node = node_stack.pop()
        b_dist = (b_node.x-s[0])**2 + (b_node.y-s[1])**2
        
        while len(node_stack) > 0:
            c_node = node_stack.pop()
            # distance to the parent node/head node on the stack
            c_dist = (b_node.x-s[0])**2 + (b_node.y-s[1])**2
            
            # if distance to the parent node/head node on the stack is less
            # than distance to the current best point
            if c_dist < b_dist:
                b_node = c_node
                b_dist = c_dist
  
            # distance to split plane
            if c_node.split_dim == 0: # vertical plane
                c_dist = (c_node.x-s[0])**2
            else: # horizontal plane
                c_dist = (c_node.y-s[1])**2
            
            # if distance to split plane is less than distance to the 
            # current best point
            if c_dist < b_dist:
                if c_node.split_dim == 0:
                    if s[0] < c_node.x: # traverse right child
                        traverse_tree(c_node.r_child, s, node_stack)
                    else: # traverse left child
                        traverse_tree(c_node.l_child, s, node_stack)
                else:
                    if s[1] < c_node.y: # traverse right child
                        traverse_tree(c_node.r_child, s, node_stack)
                    else: # traverse left child
                        traverse_tree(c_node.l_child, s, node_stack)
        done = time.time()
        bench_m[i] = bench_m[i-1] + done - start
         
        if save:
            # save tree and points
            axs = print_kdtree(root, test_data, False, range(5,6), True, False)
            x = b_node.x
            y = b_node.y
            # draw point
            axs.plot([x], [y], marker='o', markersize=3, color="red"
                 if b_node.label==1 else "blue" )
            axs.plot([s[0]], [s[1]], marker='+', markersize=5, color="red" 
                 if b_node.label==1 else "blue")
            
            filename = 'chart/NN_point_%d.pdf'%(i)
            plt.savefig(filename, facecolor='w', edgecolor='w',
                        papertype=None, format='pdf', transparent=False,
                        bbox_inches='tight', pad_inches=0.1)
            plt.close()
    if save:
        fig = plt.figure()
        axs = fig.add_subplot(111)
        x = np.linspace(0, len(bench_m), len(test_data))
        axs.plot(x, bench_m*1000, label='benchmark(msec)')
        plt.xlabel('samples')
        plt.ylabel('msec')
        axs.legend(loc='upper left', shadow=True, fancybox=True, numpoints=1)
        filename = 'chart/benchmark_%s_%s.pdf'%(split_method, sel_method)
        plt.savefig(filename, facecolor='w', edgecolor='w',
                    papertype=None, format='pdf', transparent=False,
                    bbox_inches='tight', pad_inches=0.1)
        plt.close()
            
if __name__ == "__main__":   
    train_data = read_file(train_f)
    root = generate_kdtree(train_data)
    print_kdtree(root, train_data, range(1,5), returnPlt=False, save=True)
    test_data = read_file(test_f)
    kd_tree_inference(root, test_data, save=True)
    
    