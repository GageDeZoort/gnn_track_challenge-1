#!/usr/bin/env python

""" plot_functions.py: suite of visualizations and kinematic studies for TrackML events """ 

__author__  = "Gage DeZoort"
__version__ = "1.0.0"
__status__  = "Development"

import os
import math
import trackml
import numpy as np
import pandas as pd
from cycler import cycler
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from trackml.dataset import load_event
from trackml.dataset import load_dataset


def plotSingleHist(data, x_label, y_label, bins, weights=None, title='', color='blue'):
    """ plotSingleHist(): generic function for histogramming a data array
    """
    bin_heights, bin_borders, _ = plt.hist(data, bins=bins, color=color, weights=weights)
    bin_centers = bin_borders[:-1] + np.diff(bin_borders)/2.
    print bin_heights
    print bin_centers
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.title(title,    fontsize=16)
    plt.show()

def plotXY(x, y, x_label, y_label, title='', color='blue'):
    plt.scatter(x, y, c=color)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()
    
def plotBinnedHist(x, y, x_label, y_label, nbins, title='', color='blue'):
    """ plotBinnedHist(): generic function for plotting a binned y vs. x scatter plot
    					  similar to a TProfile
    """
    n, _ = np.histogram(x, bins=nbins)
    sy, _ = np.histogram(x, bins=nbins, weights=y)
    sy2, _ = np.histogram(x, bins=nbins, weights=y*y)
    mean = sy / n
    std = np.sqrt(sy2/n - mean*mean)/np.sqrt(n)
    plt.errorbar((_[1:] + _[:-1])/2, mean, yerr=std, color=color, marker='.', ls='')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()

def plotHeatMap(x, y, x_label, y_label, x_bins, y_bins, weights=None, title=''):
    """ plotHeatMap(): generic function for plotting a heatmap of y vs. x with 
                       pre-specified weights
    """
    plt.hist2d(x, y, bins=(x_bins,y_bins), weights=weights, cmap=plt.cm.jet)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Normalized $P_T$')
    plt.title(title)
    plt.show()

def plotTrack(track):
	""" plotTrack(): plot a track in a simple 3D grid 
	"""
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.plot(track['tx'], track['ty'], track['tz'], lw=0.5, c='skyblue')
        ax.scatter3D(track['tx'], track['ty'], track['tz'], 
                     c=track['tR'], cmap ='viridis', marker='h', s=30)
        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y [mm]')
        ax.set_zlabel('z [mm]')
        plt.show()

def getModuleCoords(v_id, l_id, m_id):
    detectors = pd.read_csv('../data/detectors.csv')
    coords = detectors[(detectors['volume_id'] == v_id) & (detectors['layer_id'] == l_id) 
                       & (detectors['module_id'] == m_id)]
    
    c_vec = [coords.iloc[0]['cx'], coords.iloc[0]['cy'], coords.iloc[0]['cz']]
    hu = coords.iloc[0]['module_maxhu']
    hv = coords.iloc[0]['module_hv']
    
    def rotateCoords(vec):
        rotation_matrix = np.array([[coords.iloc[0]['rot_xu'],coords.iloc[0]['rot_xv'],coords.iloc[0]['rot_xw']],
                           [coords.iloc[0]['rot_yu'],coords.iloc[0]['rot_yv'],coords.iloc[0]['rot_yw']],
                           [coords.iloc[0]['rot_zu'],coords.iloc[0]['rot_zv'],coords.iloc[0]['rot_zw']]])
        return rotation_matrix.dot(vec)


    v1 = rotateCoords(np.array([-hu,-hv,0]))
    v2 = rotateCoords(np.array([hu,-hv,0]))
    v3 = rotateCoords(np.array([hu,hv,0]))
    v4 = rotateCoords(np.array([-hu,hv,0]))
    
    x = np.array([v1[0],v2[0],v3[0],v4[0]]) + c_vec[0]
    y = np.array([v1[1],v2[1],v3[1],v4[1]]) + c_vec[1]
    z = np.array([v1[2],v2[2],v3[2],v4[2]]) + c_vec[2]
    
    verts = [list(zip(x,y,z))]
    return verts

def plotTrackOverLayers(track, hits, plotModules):
    """ plotTrackOverLayers(): plot a track and the detector layers
                               it hits
    """
    
    volume_ids = [7,8,9]
    detectors = pd.read_csv('../data/detectors.csv')
    detectors['xyz'] = detectors[['cx', 'cy', 'cz']].values.tolist()
    
    volumes = detectors.groupby('volume_id')['xyz'].apply(list).to_frame()	
    accept_volumes = detectors[detectors.volume_id.isin(volume_ids)]
    
    x_min, x_max = accept_volumes['cx'].min(), accept_volumes['cx'].max()
    y_min, y_max = accept_volumes['cy'].min(), accept_volumes['cy'].max()
    z_min, z_max = accept_volumes['cz'].min(), accept_volumes['cz'].max()
    
    volumes_layers = accept_volumes.groupby(['volume_id','layer_id'])['xyz'].apply(list).to_frame()
    fig = plt.figure(figsize=plt.figaspect(0.9))
    
    ax = plt.axes(projection='3d')
    ax.set_aspect('equal')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)
    #ax.set_prop_cycle(cycler('color', ['forestgreen', 'firebrick', 'royalblue', 'indigo']))
    
    ax.plot(track['tx'], track['ty'], track['tz'], lw=0.5, c='skyblue')
    ax.scatter3D(track['tx'], track['ty'], track['tz'],
                 c=track['tR'], cmap='viridis', marker='h', s=30)
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    ax.set_zlabel('z [mm]')
    
    if plotModules:
        for index, row in hits.iterrows():
            verts = getModuleCoords(row['volume_id'], row['layer_id'], row['module_id'])
            ax.add_collection3d(Poly3DCollection(verts, facecolors='silver', linewidths=1, edgecolors='black'), zs='z')
    
    num_regions = volumes_layers.shape[0]
    for (i, row) in volumes_layers.iloc[:num_regions+1].iterrows():
        xyz = np.array(row['xyz'])
        x, y, z = xyz[:,0], xyz[:,1], xyz[:,2]
        ax.plot(x,y,z, linestyle='', marker='h', markersize='0.5', color='mediumslateblue', alpha=0.5)
        ax.text(x[0], y[0], z[0], str(i), None, size=5)
    plt.show()
        

def plotWholeDetector():
    volume_ids = [7,8,9]
    detectors = pd.read_csv('../data/detectors.csv')
    detectors['xyz'] = detectors[['cx', 'cy', 'cz']].values.tolist()

    volumes = detectors.groupby('volume_id')['xyz'].apply(list).to_frame()
    accept_volumes = detectors[detectors.volume_id.isin(volume_ids)]

    x_min, x_max = accept_volumes['cx'].min(), accept_volumes['cx'].max()
    y_min, y_max = accept_volumes['cy'].min(), accept_volumes['cy'].max()
    z_min, z_max = accept_volumes['cz'].min(), accept_volumes['cz'].max()

    volumes_layers = accept_volumes.groupby(['volume_id','layer_id'])['xyz'].apply(list).to_frame()
    fig = plt.figure(figsize=plt.figaspect(0.9))

    ax = plt.axes(projection='3d')
    ax.set_aspect('equal')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)

    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    ax.set_zlabel('z [mm]')

    
    pixel_detector = detectors[detectors.volume_id.isin([7,8,9])]
    #pixel_detector = pixel_detector[pixel_detector.layer_id.isin([8])]
    for index, row in pixel_detector.iterrows():
        print "looking at", index
        verts = getModuleCoords(row['volume_id'], row['layer_id'], row['module_id'])
        ax.add_collection3d(Poly3DCollection(verts, facecolors='silver', linewidths=1, edgecolor='black'), zs='z')

    plt.show()



