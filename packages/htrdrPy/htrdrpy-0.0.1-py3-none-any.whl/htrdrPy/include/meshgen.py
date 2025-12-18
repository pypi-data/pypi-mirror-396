#####################################################################
# Copyright (C) Observatoire de Paris - PSL
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>. 
#####################################################################

import numpy as np 
import matplotlib.pyplot as plt
import math

'''
helper functions
'''
def spher2cart(theta,phi,r):
    x = r * math.cos(theta) * math.cos(phi)
    y = r * math.cos(theta) * math.sin(phi)
    z = r * math.sin(theta)
    return [x, y, z]

'''
DEBUG 
'''
def plot_points(node_coord,r):
    # Create a new figure
    fig = plt.figure()
    
    # Add 3d subplot
    ax = fig.add_subplot(111, projection='3d')

    # Convert node_coord list into a numpy array
    node_coord_np = np.array(node_coord)
    
    # Separate x, y, z coordinates for plotting
    xs = node_coord_np[:, 0]
    ys = node_coord_np[:, 1]
    zs = node_coord_np[:, 2]
    
    # Plot points
    ax.scatter(xs, ys, zs)

    # Plot sphere
    # Create u, v parameters for the sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    
    # Convert the u, v parameters to x, y, z coordinates
    x = r * np.outer(np.cos(u), np.sin(v))
    y = r * np.outer(np.sin(u), np.sin(v))
    z = r * np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Plot the sphere
    ax.plot_surface(x, y, z, color='b',alpha=0.2)

    # Set labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim3d(-2,2)
    ax.set_ylim3d(-2,2)
    ax.set_zlim3d(-2,2)

    # Show the plot
    plt.show()

'''
Mesh generation
'''
def spherical_mesh_control_cell(Ntheta,Nphi,Alt_level):
    """
    Write homogeneous spherical atmosphere mesh.
    control_cell -> the optical properties of each GCM cell are controlled and homogeneous.
    Optical properties are homogeneous within each GCM cell. 
    The mesh is drew from spherical coordinates (r,theta,phi) as inputs.
    The outputs are in Cartesian coordinates and the sphere center is located at (0,0,0)
    
    Parameters:
    Ntheta: Mesh Resolution on theta
    Nphi: Mesh Resolution on phi
    Alt_level (Array): Precise an array of r of each level of the mesh.

    * The name Alt_level is confusing. In fact, they needed to be the sum of the altitudes of each level and the radius of Titan.
    
    Returns:
    noed_coord (Array of shape (N_noed,3) ): N_noed is the number of noeds, 3 -> (x,y,z) in Cartesian coordinates.
    cell_ids (Array of shape (N_tetrahedrons,4)): N_tetrahedrons is the number of tetrahedrons. 4 -> the indices of the four points of each tetrahedrons (indices in noed_corrd). 

    * All the meshes have the same data format of node_coord and cell_ids, so that the function write_binary_file_grid() (in write.py) can be called to read these format and generate the mesh file input for htrdr.
    * For the meshes of gas and hazes (clouds), cell_ids has a shape of (N_tetrahedrons,4), since the cells are tetrahedrons.
    * For the meshes of the surface (ground), cell_ids has a shape of (N_triangle,3), since the cells are triangles.
    
    """
    # Computing the real spherical coordinates (theta, phi, z_grids) from the function input
    theta_grid = np.linspace(-math.pi/2, math.pi/2, Ntheta)
    phi_grid = np.linspace(0, math.pi*2, Nphi)
    z_grid = Alt_level 
    Nz = len(z_grid)
    r_min = z_grid[0]
    r_max = z_grid[-1]

    '''
    points generation: convert spherical coordinates to Cartesian coordinates

    '''
    print('Mesh generator. Ntheta = {}, Nphi = {}, Nz = {}, r_min = {}, r_max = {}'.format(Ntheta,Nphi,Nz,r_min,r_max))
    print('Generating points...')
    # nodes coord initialization
    point_coord = []
    
    # record the south pole
    itheta = 0
    for iz in range(Nz):
        iphi = 0
        coord = spher2cart(theta_grid[itheta],phi_grid[iphi],z_grid[iz])
        point_coord.append(coord)
    
    # record others 
    for itheta in range(1,Ntheta-1):
        for iphi in range(Nphi-1):
            for iz in range(Nz):
                coord = spher2cart(theta_grid[itheta],phi_grid[iphi],z_grid[iz])
                point_coord.append(coord)
    
    # record the north pole
    itheta = Ntheta-1
    for iz in range(Nz):
        iphi = 0
        coord = spher2cart(theta_grid[itheta],phi_grid[iphi],z_grid[iz])
        point_coord.append(coord)
    
    # convert to numpy
    point_coord = np.array(point_coord)
    
    '''
    nodes generations: 
    From the points, we identify the nodes for each GCM cells.
    The GCM cells around the north pole and the south pole are Hexahedron.
    Therefore, 6 nodes are identified for each Hexahedron ((x,y,z) for 6 points are stocked in node_S_mesh and node_N_mesh).
    Other GCM cells are Octahedron.
    Therefore, 8 nodes are identified for each Octahedron ((x,y,z) for 8 points stocked in node_M_mesh).
    * node_S_mesh has a shape of (N_Hexahedron,6,3)
    * node_N_mesh has a shape of (N_Hexahedron,6,3)
    * node_M_mesh has a shape of (N_Octahedron,8,3)
    '''
    print('Generating nodes...')
    # cells ids initialization
    node_S_mesh = []
    node_N_mesh = []
    node_M_mesh = []
    
    # record the south pole
    for iphi in range(Nphi-1):
        if (iphi < Nphi-2):
            for iz in range(Nz-1):
                ids = -1*np.ones((6),dtype=int)
                ids[0] = iz
                ids[1] = iz+1
                ids[2] = ids[0]+Nz*(iphi+1) # next phi
                ids[3] = ids[1]+Nz*(iphi+1) # next phi
                ids[4] = ids[0]+Nz*(iphi+2) # next 2 phi
                ids[5] = ids[1]+Nz*(iphi+2) # next 2 phi
                noeds = point_coord[ids]
                node_S_mesh.append(noeds)
    
        if (iphi == Nphi-2):
            for iz in range(Nz-1):
                ids = -1*np.ones((6),dtype=int)
                ids[0] = iz
                ids[1] = iz+1
                ids[2] = ids[0]+Nz+Nz*(iphi) # next phi
                ids[3] = ids[1]+Nz+Nz*(iphi) # next phi
                ids[4] = ids[0]+Nz
                ids[5] = ids[1]+Nz
                noeds = point_coord[ids]
                node_S_mesh.append(noeds)
     
    ##########
    #DEBUG
    #node_S_mesh = np.array(node_S_mesh)
    #noeds = np.reshape(node_S_mesh,(len(node_S_mesh[:,0,0])*len(node_S_mesh[0,:,0]),3))
    #plot_points(noeds,r_min)
    ##########
    
    # record others
    for itheta in range(1,Ntheta-2):
        for iphi in range(Nphi-1):
            if (iphi < Nphi-2):
                for iz in range(Nz-1):
                    ids = -1*np.ones((8),dtype=int)
                    ids[0] = (itheta-1)*(Nphi-1)*Nz + Nz*iphi + Nz + iz
                    ids[1] = (itheta-1)*(Nphi-1)*Nz + Nz*iphi + Nz + iz + 1
                    ids[2] = (itheta-1)*(Nphi-1)*Nz + Nz*(iphi+1) + Nz + iz
                    ids[3] = (itheta-1)*(Nphi-1)*Nz + Nz*(iphi+1) + Nz + iz + 1
                    ids[4] = (itheta)*(Nphi-1)*Nz + Nz*(iphi) + Nz + iz
                    ids[5] = (itheta)*(Nphi-1)*Nz + Nz*(iphi) + Nz + iz + 1
                    ids[6] = (itheta)*(Nphi-1)*Nz + Nz*(iphi+1) + Nz + iz
                    ids[7] = (itheta)*(Nphi-1)*Nz + Nz*(iphi+1) + Nz + iz + 1
                    noeds = point_coord[ids]
                    node_M_mesh.append(noeds)
            if (iphi == Nphi-2):
                for iz in range(Nz-1):
                    ids = -1*np.ones((8),dtype=int)
                    ids[0] = (itheta-1)*(Nphi-1)*Nz + Nz*iphi + Nz + iz
                    ids[1] = (itheta-1)*(Nphi-1)*Nz + Nz*iphi + Nz + iz + 1
                    ids[2] = (itheta-1)*(Nphi-1)*Nz + Nz + iz
                    ids[3] = (itheta-1)*(Nphi-1)*Nz + Nz + iz + 1
                    ids[4] = (itheta)*(Nphi-1)*Nz + Nz*(iphi) + Nz + iz
                    ids[5] = (itheta)*(Nphi-1)*Nz + Nz*(iphi) + Nz + iz + 1
                    ids[6] = (itheta)*(Nphi-1)*Nz + Nz + iz
                    ids[7] = (itheta)*(Nphi-1)*Nz + Nz + iz + 1
                    noeds = point_coord[ids]
                    node_M_mesh.append(noeds)
    ##########
    #DEBUG
    #node_M_mesh = np.array(node_M_mesh)
    #nodes = np.reshape(node_M_mesh,(len(node_M_mesh[:,0,0])*len(node_M_mesh[0,:,0]),3))
    #print(np.shape(nodes))
    #plot_points(noeds,r_min)
    ##########
    
    # record the north pole
    for iphi in range(Nphi-1):
        if (iphi < Nphi-2):
            for iz in range(Nz-1):
                ids = -1*np.ones((6),dtype=int)
                ids[0] = Nz + (Ntheta-2)*(Nphi-1)*Nz + iz
                ids[1] = Nz + (Ntheta-2)*(Nphi-1)*Nz + iz + 1
                ids[2] = Nz + (Ntheta-3)*(Nphi-1)*Nz + Nz*iphi + iz
                ids[3] = Nz + (Ntheta-3)*(Nphi-1)*Nz + Nz*iphi + iz + 1
                ids[4] = Nz + (Ntheta-3)*(Nphi-1)*Nz + Nz*(iphi+1) + iz
                ids[5] = Nz + (Ntheta-3)*(Nphi-1)*Nz + Nz*(iphi+1) + iz + 1
                noeds = point_coord[ids]
                node_N_mesh.append(noeds)
        if (iphi == Nphi-2):
            for iz in range(Nz-1):
                ids = -1*np.ones((6),dtype=int)
                ids[0] = Nz + (Ntheta-2)*(Nphi-1)*Nz +iz
                ids[1] = Nz + (Ntheta-2)*(Nphi-1)*Nz +iz+1
                ids[2] = Nz + (Ntheta-3)*(Nphi-1)*Nz +Nz*iphi + iz
                ids[3] = Nz + (Ntheta-3)*(Nphi-1)*Nz +Nz*iphi + iz + 1
                ids[4] = Nz + (Ntheta-3)*(Nphi-1)*Nz +iz
                ids[5] = Nz + (Ntheta-3)*(Nphi-1)*Nz +iz + 1
                noeds = point_coord[ids]
                node_N_mesh.append(noeds)
    
    ##########
    #DEBUG
    #node_N_mesh = np.array(node_N_mesh)
    #nodes = np.reshape(node_N_mesh,(len(node_N_mesh[:,0,0])*len(node_N_mesh[0,:,0]),3))
    #plot_points(nodes,r_min)
    ##########

    print('Hexahedron & Octahedron generation completed. N_Hexahedron = {}, N_Octahedron = {}'.format(len(node_N_mesh)+len(node_S_mesh),len(node_M_mesh)))
    '''
    Tetrahedrons generation
    Once we have all the nodes, we draw tetrahedrons within each Hexahedron and Octahedron.
    We loop every Hexahedron and Octahedron.
    Each Hexahedron is divided to 3 tetrahedrons.
    Each Octahedron is divided to 5 tetrahedrons.
    Ids are stocked in cell_ids from south, middle to north.
    '''
    print('Generating Tetrahedrons...')
    # draw Tetrahedrons
    cell_ids = []
    
    # record for south pole
    for i in range(len(node_S_mesh)):
        # nidx to be skipped
        d_idx = i * 6
        # 1st Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = 0
        ids[1] = 2
        ids[2] = 3
        ids[3] = 4
        cell_ids.append(ids + d_idx)
        # 2nd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = 0
        ids[1] = 3
        ids[2] = 4
        ids[3] = 5
        cell_ids.append(ids + d_idx)
        # 3rd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = 0
        ids[1] = 1
        ids[2] = 3
        ids[3] = 5
        cell_ids.append(ids + d_idx)
   
    #record others
    for i in range(len(node_M_mesh)):
        d_idx = i * 8 + len(node_S_mesh)*6
        # 1st Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = 0
        ids[1] = 1
        ids[2] = 2
        ids[3] = 4
        cell_ids.append(ids + d_idx)
        # 2nd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = 2
        ids[1] = 3
        ids[2] = 1
        ids[3] = 7
        cell_ids.append(ids + d_idx)
        # 3rd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = 4
        ids[1] = 5
        ids[2] = 1
        ids[3] = 7
        cell_ids.append(ids + d_idx)
        # 4th Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = 6
        ids[1] = 7
        ids[2] = 4
        ids[3] = 2
        cell_ids.append(ids + d_idx)
        # 5th Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = 2
        ids[1] = 7
        ids[2] = 4
        ids[3] = 1
        cell_ids.append(ids + d_idx)
    
    for i in range(len(node_N_mesh)):
        d_idx = i * 6 + len(node_S_mesh)*6 + len(node_M_mesh)*8
        # 1st Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = 0
        ids[1] = 1
        ids[2] = 2
        ids[3] = 5
        cell_ids.append(ids + d_idx)
        # 2nd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = 2
        ids[1] = 3
        ids[2] = 1
        ids[3] = 5
        cell_ids.append(ids + d_idx)
        # 3rd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = 4
        ids[1] = 5
        ids[2] = 0
        ids[3] = 2
        cell_ids.append(ids + d_idx)
    
    '''
    Merge the nodes stocked in south, middle and north.
    * The order S-M-N needs to be followed since the cell_ids is recorded in the same order.
    '''

    node_S_mesh = np.array(node_S_mesh)
    node_M_mesh = np.array(node_M_mesh)
    node_N_mesh = np.array(node_N_mesh)
    
    noeds_S = np.reshape(node_S_mesh,(len(node_S_mesh[:,0,0])*len(node_S_mesh[0,:,0]),3))
    noeds_M = np.reshape(node_M_mesh,(len(node_M_mesh[:,0,0])*len(node_M_mesh[0,:,0]),3))
    noeds_N = np.reshape(node_N_mesh,(len(node_N_mesh[:,0,0])*len(node_N_mesh[0,:,0]),3))
    
    noed_coord = np.append(np.append(noeds_S,noeds_M,axis=0),noeds_N,axis=0)
    cell_ids = np.array(cell_ids,dtype=int)

    return noed_coord,cell_ids

def spherical_mesh_control_pt(Ntheta,Nphi,Alt_level):
    """
    Write ordinary spherical atmosphere mesh.
    control_pt -> the optical properties of each node are controlled. 
    The optical properties in the GCM cells are interpolated by htrdr.
    
    Parameters:
    Ntheta: Mesh Resolution on theta
    Nphi: Mesh Resolution on phi
    Alt_level (Array): Precise an array of r of each level of the mesh.

    * The altitudes of layers are averagely distributed. 
    NOTE : needed to update for the next version.
    User-defined alts for each layers is better.
    
    Returns:
    noed_coord (Array of shape (N_noed,3) ): N_noed is the number of noeds, 3 -> (x,y,z) in Cartesian coordinates.
    cell_ids (Array of shape (N_tetrahedrons,4)): N_tetrahedrons is the number of tetrahedrons. 4 -> the indices of the four points of each tetrahedrons (indices in noed_corrd). 

    """
    # Computing the theta, phi, and z grids
    theta_grid = np.linspace(-math.pi/2, math.pi/2, Ntheta)
    phi_grid = np.linspace(0, math.pi*2, Nphi)
    z_grid = Alt_level
    Nz = len(Alt_level)
    r_min = Alt_level[0]
    r_max = Alt_level[-1]
    #z_grid = np.linspace(r_min, r_max, Nz)
    n_nodes = ((Ntheta-2)*(Nphi-1)+2)*Nz
    
    '''
    points generation: convert spherical coordinates to Cartesian coordinates
    Here goes the difference from homogeneous mesh !
    The points in the Cartesian coordinates are also the nodes of each GCM cells !

    '''
    print('Mesh generator. Ntheta = {}, Nphi = {}, Nz = {}, r_min = {}, r_max = {}'.format(Ntheta,Nphi,Nz,r_min,r_max))
    print('Generating Nodes...')
    # nodes coord initialization
    node_coord = []
    
    # record the south pole
    itheta = 0
    for iz in range(Nz):
        iphi = 0
        coord = spher2cart(theta_grid[itheta],phi_grid[iphi],z_grid[iz])
        node_coord.append(coord)
    
    # record others 
    for itheta in range(1,Ntheta-1):
        for iphi in range(Nphi-1):
            for iz in range(Nz):
                coord = spher2cart(theta_grid[itheta],phi_grid[iphi],z_grid[iz])
                node_coord.append(coord)
    
    # record the north pole
    itheta = Ntheta-1
    for iz in range(Nz):
        iphi = 0
        coord = spher2cart(theta_grid[itheta],phi_grid[iphi],z_grid[iz])
        node_coord.append(coord)
    
    # convert to numpy
    node_coord = np.array(node_coord)
    
    print('Nodes generation completed. Nnodes = {}'.format(len(node_coord)))
    '''
    Hexahedron & Octahedron generation
    Different from homogeneous mesh !
    The points in the Cartesian coordinates are also the nodes of each GCM cells !
    The GCM cells around the north pole and the south pole are Hexahedron.
    Therefore, 6 points are identified for each Hexahedron ((x,y,z) for 6 points are stocked in cell_S_mesh and cell_N_mesh).
    Other GCM cells are Octahedron.
    Therefore, 8 points are identified for each Octahedron ((x,y,z) for 8 points stocked in cell_M_mesh).
    * The ids of points are stoked.
    * cell_S_mesh has a shape of (N_Hexahedron,6)
    * cell_N_mesh has a shape of (N_Hexahedron,6)
    * cell_M_mesh has a shape of (N_Octahedron,8)

    '''
    print('Generating Hexahedron & Octahedron...')
    # cells ids initialization
    cell_S_ids = []
    cell_N_ids = []
    cell_M_ids = []
    
    # record the south pole
    for iphi in range(Nphi-1):
        if (iphi < Nphi-2):
            for iz in range(Nz-1):
                ids = -1*np.ones((6),dtype=int)
                ids[0] = iz
                ids[1] = iz+1
                ids[2] = ids[0]+Nz*(iphi+1) # next phi
                ids[3] = ids[1]+Nz*(iphi+1) # next phi
                ids[4] = ids[0]+Nz*(iphi+2) # next 2 phi
                ids[5] = ids[1]+Nz*(iphi+2) # next 2 phi
                cell_S_ids.append(ids)
        if (iphi == Nphi-2):
            for iz in range(Nz-1):
                ids = -1*np.ones((6),dtype=int)
                ids[0] = iz
                ids[1] = iz+1
                ids[2] = ids[0]+Nz+Nz*(iphi) # next phi
                ids[3] = ids[1]+Nz+Nz*(iphi) # next phi
                ids[4] = ids[0]+Nz
                ids[5] = ids[1]+Nz
                cell_S_ids.append(ids)
    
    # record others
    for itheta in range(1,Ntheta-2):
        for iphi in range(Nphi-1):
            if (iphi < Nphi-2):
                for iz in range(Nz-1):
                    ids = -1*np.ones((8),dtype=int)
                    ids[0] = (itheta-1)*(Nphi-1)*Nz + Nz*iphi + Nz + iz
                    ids[1] = (itheta-1)*(Nphi-1)*Nz + Nz*iphi + Nz + iz + 1
                    ids[2] = (itheta-1)*(Nphi-1)*Nz + Nz*(iphi+1) + Nz + iz
                    ids[3] = (itheta-1)*(Nphi-1)*Nz + Nz*(iphi+1) + Nz + iz + 1
                    ids[4] = (itheta)*(Nphi-1)*Nz + Nz*(iphi) + Nz + iz
                    ids[5] = (itheta)*(Nphi-1)*Nz + Nz*(iphi) + Nz + iz + 1
                    ids[6] = (itheta)*(Nphi-1)*Nz + Nz*(iphi+1) + Nz + iz
                    ids[7] = (itheta)*(Nphi-1)*Nz + Nz*(iphi+1) + Nz + iz + 1
                    cell_M_ids.append(ids)
            if (iphi == Nphi-2):
                for iz in range(Nz-1):
                    ids = -1*np.ones((8),dtype=int)
                    ids[0] = (itheta-1)*(Nphi-1)*Nz + Nz*iphi + Nz + iz
                    ids[1] = (itheta-1)*(Nphi-1)*Nz + Nz*iphi + Nz + iz + 1
                    ids[2] = (itheta-1)*(Nphi-1)*Nz + Nz + iz
                    ids[3] = (itheta-1)*(Nphi-1)*Nz + Nz + iz + 1
                    ids[4] = (itheta)*(Nphi-1)*Nz + Nz*(iphi) + Nz + iz
                    ids[5] = (itheta)*(Nphi-1)*Nz + Nz*(iphi) + Nz + iz + 1
                    ids[6] = (itheta)*(Nphi-1)*Nz + Nz + iz
                    ids[7] = (itheta)*(Nphi-1)*Nz + Nz + iz + 1
                    cell_M_ids.append(ids)
    
    # record the north pole
    for iphi in range(Nphi-1):
        if (iphi < Nphi-2):
            for iz in range(Nz-1):
                ids = -1*np.ones((6),dtype=int)
                ids[0] = Nz + (Ntheta-2)*(Nphi-1)*Nz + iz
                ids[1] = Nz + (Ntheta-2)*(Nphi-1)*Nz + iz + 1
                ids[2] = Nz + (Ntheta-3)*(Nphi-1)*Nz + Nz*iphi + iz
                ids[3] = Nz + (Ntheta-3)*(Nphi-1)*Nz + Nz*iphi + iz + 1
                ids[4] = Nz + (Ntheta-3)*(Nphi-1)*Nz + Nz*(iphi+1) + iz
                ids[5] = Nz + (Ntheta-3)*(Nphi-1)*Nz + Nz*(iphi+1) + iz + 1
                cell_N_ids.append(ids)
        if (iphi == Nphi-2):
            for iz in range(Nz-1):
                ids = -1*np.ones((6),dtype=int)
                ids[0] = Nz + (Ntheta-2)*(Nphi-1)*Nz +iz
                ids[1] = Nz + (Ntheta-2)*(Nphi-1)*Nz +iz+1
                ids[2] = Nz + (Ntheta-3)*(Nphi-1)*Nz +Nz*iphi + iz
                ids[3] = Nz + (Ntheta-3)*(Nphi-1)*Nz +Nz*iphi + iz + 1
                ids[4] = Nz + (Ntheta-3)*(Nphi-1)*Nz +iz
                ids[5] = Nz + (Ntheta-3)*(Nphi-1)*Nz +iz + 1
                cell_N_ids.append(ids)
    
    print('Hexahedron & Octahedron generation completed. N_Hexahedron = {}, N_Octahedron = {}'.format(len(cell_N_ids)+len(cell_S_ids),len(cell_M_ids)))
    '''
    Tetrahedrons generation
    Once we have all the point-ids of each Hexahedron and Octahedron, we loop each Hexahedron and Octahedron and identify the point-ids of each Tetrahedrons.
    Each Hexahedron is divided to 3 tetrahedrons.
    Each Octahedron is divided to 5 tetrahedrons.
    Ids are stocked in cell_ids from south, middle to north.
    * The order S-M-N needs to be followed since the node_coord is recorded in the same order.
    '''
    print('Generating Tetrahedrons...')
    # draw Tetrahedrons
    cell_ids = []
    
    # record for south pole
    for i in range(len(cell_S_ids)):
        # 1st Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = cell_S_ids[i][0]
        ids[1] = cell_S_ids[i][2]
        ids[2] = cell_S_ids[i][3]
        ids[3] = cell_S_ids[i][4]
        cell_ids.append(ids)
        # 2nd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = cell_S_ids[i][0]
        ids[1] = cell_S_ids[i][3]
        ids[2] = cell_S_ids[i][4]
        ids[3] = cell_S_ids[i][5]
        cell_ids.append(ids)
        # 3rd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = cell_S_ids[i][0]
        ids[1] = cell_S_ids[i][1]
        ids[2] = cell_S_ids[i][3]
        ids[3] = cell_S_ids[i][5]
        cell_ids.append(ids)
    
    #record others
    for i in range(len(cell_M_ids)):
        # 1st Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = cell_M_ids[i][0]
        ids[1] = cell_M_ids[i][1]
        ids[2] = cell_M_ids[i][2]
        ids[3] = cell_M_ids[i][4]
        cell_ids.append(ids)
        # 2nd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = cell_M_ids[i][2]
        ids[1] = cell_M_ids[i][3]
        ids[2] = cell_M_ids[i][1]
        ids[3] = cell_M_ids[i][7]
        cell_ids.append(ids)
        # 3rd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = cell_M_ids[i][4]
        ids[1] = cell_M_ids[i][5]
        ids[2] = cell_M_ids[i][1]
        ids[3] = cell_M_ids[i][7]
        cell_ids.append(ids)
        # 4th Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = cell_M_ids[i][6]
        ids[1] = cell_M_ids[i][7]
        ids[2] = cell_M_ids[i][4]
        ids[3] = cell_M_ids[i][2]
        cell_ids.append(ids)
        # 5th Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = cell_M_ids[i][2]
        ids[1] = cell_M_ids[i][7]
        ids[2] = cell_M_ids[i][4]
        ids[3] = cell_M_ids[i][1]
        cell_ids.append(ids)

    ##
    ## record for north pole
    for i in range(len(cell_N_ids)):
        # 1st Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = cell_N_ids[i][0]
        ids[1] = cell_N_ids[i][1]
        ids[2] = cell_N_ids[i][2]
        ids[3] = cell_N_ids[i][5]
        cell_ids.append(ids)
        # 2nd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = cell_N_ids[i][2]
        ids[1] = cell_N_ids[i][3]
        ids[2] = cell_N_ids[i][1]
        ids[3] = cell_N_ids[i][5]
        cell_ids.append(ids)
        # 3rd Tetr
        ids = -1*np.ones((4),dtype=int)
        ids[0] = cell_N_ids[i][4]
        ids[1] = cell_N_ids[i][5]
        ids[2] = cell_N_ids[i][0]
        ids[3] = cell_N_ids[i][2]
        cell_ids.append(ids)
    print('Tetrahedrons generation completed. N_Tetrahedrons = {}'.format(len(cell_ids)))

    return node_coord,cell_ids

def topo_ground_mesh(R,Z):
    """
    Write homogeneous ground mesh.
    The optical properties of each triangle are controlled. 
    
    Parameters:
    Ntheta: Mesh Resolution on theta
    Nphi: Mesh Resolution on phi
    R: The radius of the planet 
    R: Global elevation array

    Returns:
    noed_coord (Array of shape (N_noed,3) ): N_noed is the number of noeds, 3 -> (x,y,z) in Cartesian coordinates.
    cell_ids (Array of shape (N_triangle,3)): N_triangle is the number of triangle. 3 -> the indices of the three points of each triangle (indices in noed_corrd). 
    """
    # Computing the theta, phi
    Ntheta = len(Z[:,0])
    Nphi = len(Z[0,:])+1
    theta_grid = np.linspace(-math.pi/2, math.pi/2, Ntheta)
    phi_grid = np.linspace(0, math.pi*2, Nphi)
    n_nodes = ((Ntheta-2)*(Nphi-1)+2)

    '''
    points generation: convert spherical coordinates to Cartesian coordinates
    '''
    print('Mesh generator. Ntheta = {}, Nphi = {}, R = {}'.format(Ntheta,Nphi,R))
    print('Generating points...')
    # nodes coord initialization
    point_coord = []
    
    # record the south pole
    itheta = 0
    iphi = 0
    coord = spher2cart(theta_grid[itheta],phi_grid[iphi],R+np.mean(Z[0,:]))
    point_coord.append(coord)
    
    # record others 
    for itheta in range(1,Ntheta-1):
        for iphi in range(Nphi-1):
            coord = spher2cart(theta_grid[itheta],phi_grid[iphi],R+Z[itheta,iphi])
            point_coord.append(coord)
    
    # record the north pole
    itheta = Ntheta-1
    iphi = 0
    coord = spher2cart(theta_grid[itheta],phi_grid[iphi],R+np.mean(Z[-1,:]))
    point_coord.append(coord)
    
    # convert to numpy
    point_coord = np.array(point_coord)
    # print(point_coord.shape)
    
    '''
    noeds generations
    From the points, we identify the nodes for each cells.
    There are triangles on the north pole and south pole. 
    Between the two poles, the rectangles are first identified.
    * node_S_mesh has a shape of (N_Hexahedron,3,3)
    * node_N_mesh has a shape of (N_Hexahedron,3,3)
    * node_M_mesh has a shape of (N_Octahedron,3,3)

    '''
    print('Generating noeds...')
    # cells ids initialization
    node_S_mesh = []
    node_N_mesh = []
    node_M_mesh = []
    
    # record the south pole
    for iphi in range(Nphi-1):
        if (iphi < Nphi-2):
            ids = -1*np.ones((3),dtype=int)
            ids[0] = 0
            ids[1] = iphi + 1
            ids[2] = iphi + 2 # next phi
            noeds = point_coord[ids]
            node_S_mesh.append(noeds)
    
        if (iphi == Nphi-2):
            ids = -1*np.ones((3),dtype=int)
            ids[0] = 0
            ids[1] = iphi + 1
            ids[2] = 1 # next phi
            noeds = point_coord[ids]
            node_S_mesh.append(noeds)

    # record others
    for itheta in range(1,Ntheta-2):
        for iphi in range(Nphi-1):
            if (iphi < Nphi-2):
                ids = -1*np.ones((4),dtype=int)
                ids[0] = 1 + (itheta-1)*(Nphi-1) + iphi 
                ids[1] = 1 + (itheta-1)*(Nphi-1) + iphi + 1 
                ids[2] = 1 + (itheta-1)*(Nphi-1) + (Nphi-1) + iphi 
                ids[3] = 1 + (itheta-1)*(Nphi-1) + (Nphi-1) + iphi + 1 
                noeds = point_coord[ids]
                node_M_mesh.append(noeds)
            if (iphi == Nphi-2):
                ids = -1*np.ones((4),dtype=int)
                ids[0] = 1 + (itheta-1)*(Nphi-1) + iphi 
                ids[1] = 1 + (itheta-1)*(Nphi-1) + 0
                ids[2] = 1 + (itheta-1)*(Nphi-1) + (Nphi-1) + iphi 
                ids[3] = 1 + (itheta-1)*(Nphi-1) + (Nphi-1) + 0
                noeds = point_coord[ids]
                node_M_mesh.append(noeds)

    # record the north pole
    for iphi in range(Nphi-1):
        if (iphi < Nphi-2):
            ids = -1*np.ones((3),dtype=int)
            ids[0] = -1
            ids[1] = (Ntheta-3)*(Nphi-1)+1 + iphi
            ids[2] = (Ntheta-3)*(Nphi-1)+1 + iphi + 1
            noeds = point_coord[ids]
            node_N_mesh.append(noeds)
        if (iphi == Nphi-2):
            ids = -1*np.ones((3),dtype=int)
            ids[0] = -1
            ids[1] = (Ntheta-3)*(Nphi-1)+1 + iphi
            ids[2] = (Ntheta-3)*(Nphi-1)+1 + 0
            noeds = point_coord[ids]
            node_N_mesh.append(noeds)

    ##########
    #DEBUG
    #node_N_mesh = np.array(node_N_mesh)
    #nodes = np.reshape(node_N_mesh,(len(node_N_mesh[:,0,0])*len(node_N_mesh[0,:,0]),3))
    #plot_points(nodes,1)
    ##########

    print('triangles,rectangles generation completed. N_triangles = {}, N_rectangles = {}'.format(len(node_N_mesh)+len(node_S_mesh),len(node_M_mesh)))
    '''
    triangle generation
    Triangles of the south poles and north poles are already identified.
    Here we stokes their indices.
    The rectangles are divided into two triangles.
    '''
    print('Generating triangles...')
    # draw Tetrahedrons
    cell_ids = []
    
    # record for south pole
    for i in range(len(node_S_mesh)):
        # nidx to be skipped
        d_idx = i * 3
        # 1st Triangle
        ids = -1*np.ones((3),dtype=int)
        ids[0] = 0
        ids[1] = 1
        ids[2] = 2
        cell_ids.append(ids + d_idx)

    #record others
    for i in range(len(node_M_mesh)):
        d_idx = i * 4 + len(node_S_mesh)*3
        # 1st Triangle
        ids = -1*np.ones((3),dtype=int)
        ids[0] = 0
        ids[1] = 1
        ids[2] = 2
        cell_ids.append(ids + d_idx)
        # 2nd Triangle
        ids = -1*np.ones((3),dtype=int)
        ids[0] = 2
        ids[1] = 1
        ids[2] = 3
        cell_ids.append(ids + d_idx)
   
    for i in range(len(node_N_mesh)):
        d_idx = i * 3 + len(node_S_mesh)*3 + len(node_M_mesh)*4
        # 1st Triangle
        ids = -1*np.ones((3),dtype=int)
        ids[0] = 0
        ids[1] = 1
        ids[2] = 2
        cell_ids.append(ids + d_idx)
   
    '''
    Merge the nodes stocked in south, middle and north.
    * The order S-M-N needs to be followed since the cell_ids is recorded in the same order.
    '''
    node_S_mesh = np.array(node_S_mesh)
    node_M_mesh = np.array(node_M_mesh)
    node_N_mesh = np.array(node_N_mesh)
    
    noeds_S = np.reshape(node_S_mesh,(len(node_S_mesh[:,0,0])*len(node_S_mesh[0,:,0]),3))
    noeds_M = np.reshape(node_M_mesh,(len(node_M_mesh[:,0,0])*len(node_M_mesh[0,:,0]),3))
    noeds_N = np.reshape(node_N_mesh,(len(node_N_mesh[:,0,0])*len(node_N_mesh[0,:,0]),3))
    
    noed_coord = np.append(np.append(noeds_S,noeds_M,axis=0),noeds_N,axis=0)
    cell_ids = np.array(cell_ids,dtype=int)

    return noed_coord,cell_ids

def sphere_ground_mesh(Ntheta,Nphi,R):
    """
    Write homogeneous ground mesh.
    The optical properties of each triangle are controlled. 
    
    Parameters:
    Ntheta: Mesh Resolution on theta
    Nphi: Mesh Resolution on phi
    R: The radius of the planet 

    Returns:
    noed_coord (Array of shape (N_noed,3) ): N_noed is the number of noeds, 3 -> (x,y,z) in Cartesian coordinates.
    cell_ids (Array of shape (N_triangle,3)): N_triangle is the number of triangle. 3 -> the indices of the three points of each triangle (indices in noed_corrd). 
    """
    # Computing the theta, phi
    theta_grid = np.linspace(-math.pi/2, math.pi/2, Ntheta)
    phi_grid = np.linspace(0, math.pi*2, Nphi)
    n_nodes = ((Ntheta-2)*(Nphi-1)+2)

    '''
    points generation: convert spherical coordinates to Cartesian coordinates
    '''
    print('Mesh generator. Ntheta = {}, Nphi = {}, R = {}'.format(Ntheta,Nphi,R))
    print('Generating points...')
    # nodes coord initialization
    point_coord = []
    
    # record the south pole
    itheta = 0
    iphi = 0
    coord = spher2cart(theta_grid[itheta],phi_grid[iphi],R)
    point_coord.append(coord)
    
    # record others 
    for itheta in range(1,Ntheta-1):
        for iphi in range(Nphi-1):
            coord = spher2cart(theta_grid[itheta],phi_grid[iphi],R)
            point_coord.append(coord)
    
    # record the north pole
    itheta = Ntheta-1
    iphi = 0
    coord = spher2cart(theta_grid[itheta],phi_grid[iphi],R)
    point_coord.append(coord)
    
    # convert to numpy
    point_coord = np.array(point_coord)
    
    '''
    noeds generations
    From the points, we identify the nodes for each cells.
    There are triangles on the north pole and south pole. 
    Between the two poles, the rectangles are first identified.
    * node_S_mesh has a shape of (N_Hexahedron,3,3)
    * node_N_mesh has a shape of (N_Hexahedron,3,3)
    * node_M_mesh has a shape of (N_Octahedron,3,3)

    '''
    print('Generating noeds...')
    # cells ids initialization
    node_S_mesh = []
    node_N_mesh = []
    node_M_mesh = []
    
    # record the south pole
    for iphi in range(Nphi-1):
        if (iphi < Nphi-2):
            ids = -1*np.ones((3),dtype=int)
            ids[0] = 0
            ids[1] = iphi + 1
            ids[2] = iphi + 2 # next phi
            noeds = point_coord[ids]
            node_S_mesh.append(noeds)
    
        if (iphi == Nphi-2):
            ids = -1*np.ones((3),dtype=int)
            ids[0] = 0
            ids[1] = iphi + 1
            ids[2] = 1 # next phi
            noeds = point_coord[ids]
            node_S_mesh.append(noeds)

    # record others
    for itheta in range(1,Ntheta-2):
        for iphi in range(Nphi-1):
            if (iphi < Nphi-2):
                ids = -1*np.ones((4),dtype=int)
                ids[0] = 1 + (itheta-1)*(Nphi-1) + iphi 
                ids[1] = 1 + (itheta-1)*(Nphi-1) + iphi + 1 
                ids[2] = 1 + (itheta-1)*(Nphi-1) + (Nphi-1) + iphi 
                ids[3] = 1 + (itheta-1)*(Nphi-1) + (Nphi-1) + iphi + 1 
                noeds = point_coord[ids]
                node_M_mesh.append(noeds)
            if (iphi == Nphi-2):
                ids = -1*np.ones((4),dtype=int)
                ids[0] = 1 + (itheta-1)*(Nphi-1) + iphi 
                ids[1] = 1 + (itheta-1)*(Nphi-1) + 0
                ids[2] = 1 + (itheta-1)*(Nphi-1) + (Nphi-1) + iphi 
                ids[3] = 1 + (itheta-1)*(Nphi-1) + (Nphi-1) + 0
                noeds = point_coord[ids]
                node_M_mesh.append(noeds)

    # record the north pole
    for iphi in range(Nphi-1):
        if (iphi < Nphi-2):
            ids = -1*np.ones((3),dtype=int)
            ids[0] = -1
            ids[1] = (Ntheta-3)*(Nphi-1)+1 + iphi
            ids[2] = (Ntheta-3)*(Nphi-1)+1 + iphi + 1
            noeds = point_coord[ids]
            node_N_mesh.append(noeds)
        if (iphi == Nphi-2):
            ids = -1*np.ones((3),dtype=int)
            ids[0] = -1
            ids[1] = (Ntheta-3)*(Nphi-1)+1 + iphi
            ids[2] = (Ntheta-3)*(Nphi-1)+1 + 0
            noeds = point_coord[ids]
            node_N_mesh.append(noeds)

    ##########
    #DEBUG
    #node_N_mesh = np.array(node_N_mesh)
    #nodes = np.reshape(node_N_mesh,(len(node_N_mesh[:,0,0])*len(node_N_mesh[0,:,0]),3))
    #plot_points(nodes,1)
    ##########

    print('triangles,rectangles generation completed. N_triangles = {}, N_rectangles = {}'.format(len(node_N_mesh)+len(node_S_mesh),len(node_M_mesh)))
    '''
    triangle generation
    Triangles of the south poles and north poles are already identified.
    Here we stokes their indices.
    The rectangles are divided into two triangles.
    '''
    print('Generating triangles...')
    # draw Tetrahedrons
    cell_ids = []
    
    # record for south pole
    for i in range(len(node_S_mesh)):
        # nidx to be skipped
        d_idx = i * 3
        # 1st Triangle
        ids = -1*np.ones((3),dtype=int)
        ids[0] = 0
        ids[1] = 1
        ids[2] = 2
        cell_ids.append(ids + d_idx)

    #record others
    for i in range(len(node_M_mesh)):
        d_idx = i * 4 + len(node_S_mesh)*3
        # 1st Triangle
        ids = -1*np.ones((3),dtype=int)
        ids[0] = 0
        ids[1] = 1
        ids[2] = 2
        cell_ids.append(ids + d_idx)
        # 2nd Triangle
        ids = -1*np.ones((3),dtype=int)
        ids[0] = 2
        ids[1] = 1
        ids[2] = 3
        cell_ids.append(ids + d_idx)
   
    for i in range(len(node_N_mesh)):
        d_idx = i * 3 + len(node_S_mesh)*3 + len(node_M_mesh)*4
        # 1st Triangle
        ids = -1*np.ones((3),dtype=int)
        ids[0] = 0
        ids[1] = 1
        ids[2] = 2
        cell_ids.append(ids + d_idx)
   
    '''
    Merge the nodes stocked in south, middle and north.
    * The order S-M-N needs to be followed since the cell_ids is recorded in the same order.
    '''
    node_S_mesh = np.array(node_S_mesh)
    node_M_mesh = np.array(node_M_mesh)
    node_N_mesh = np.array(node_N_mesh)
    
    noeds_S = np.reshape(node_S_mesh,(len(node_S_mesh[:,0,0])*len(node_S_mesh[0,:,0]),3))
    noeds_M = np.reshape(node_M_mesh,(len(node_M_mesh[:,0,0])*len(node_M_mesh[0,:,0]),3))
    noeds_N = np.reshape(node_N_mesh,(len(node_N_mesh[:,0,0])*len(node_N_mesh[0,:,0]),3))
    
    noed_coord = np.append(np.append(noeds_S,noeds_M,axis=0),noeds_N,axis=0)
    cell_ids = np.array(cell_ids,dtype=int)

    #return noed_coord,cell_ids
    return noed_coord,cell_ids

def cubic_ground_mesh(a,b,c):
    """
    Homogeneous mesh
    """
    # the surface is on the y-z plan

    pts = np.array([[    0,   b/2,  c/2],
                    [   -a,   b/2,  c/2],
                    [   -a,  -b/2,  c/2],
                    [    0,  -b/2,  c/2],
                    [    0,   b/2, -c/2],
                    [   -a,   b/2, -c/2],
                    [   -a,  -b/2, -c/2],
                    [    0,  -b/2, -c/2]])
                    
    celles = np.array([[0,1,2],
                       [0,2,3],
                       [0,3,7],
                       [0,7,4],
                       [0,4,5],
                       [0,5,1],
                       [6,5,4],
                       [6,4,7],
                       [6,7,3],
                       [6,3,2],
                       [6,2,1],
                       [6,1,5]])
    return pts,celles

def cubic_atm_mesh(a,b,c):
    """
    Ordinary mesh
    """
    pts = np.array([[    a/2,   b/2,  c/2],
                    [   -a/2,   b/2,  c/2],
                    [   -a/2,  -b/2,  c/2],
                    [    a/2,  -b/2,  c/2],
                    [    a/2,   b/2, -c/2],
                    [   -a/2,   b/2, -c/2],
                    [   -a/2,  -b/2, -c/2],
                    [    a/2 , -b/2, -c/2]])
                    
    celles = np.array([[2,0,7,3],
                       [2,0,5,1],
                       [0,7,5,4],
                       [2,7,5,0],
                       [2,7,5,6]])
    return pts,celles

def cubic_cloud_mesh(a,b,c,center):
    """
    Ordinary mesh
    """
    transformation = np.array([[center[0],center[1],center[2]],
                               [center[0],center[1],center[2]],
                               [center[0],center[1],center[2]],
                               [center[0],center[1],center[2]],
                               [center[0],center[1],center[2]],
                               [center[0],center[1],center[2]],
                               [center[0],center[1],center[2]],
                               [center[0],center[1],center[2]]])

    pts = np.array([[    a/2,   b/2,  c/2],
                    [   -a/2,   b/2,  c/2],
                    [   -a/2,  -b/2,  c/2],
                    [    a/2,  -b/2,  c/2],
                    [    a/2,   b/2, -c/2],
                    [   -a/2,   b/2, -c/2],
                    [   -a/2,  -b/2, -c/2],
                    [    a/2 , -b/2, -c/2]])

    pts = pts + transformation 

    celles = np.array([[2,0,7,3],
                       [2,0,5,1],
                       [0,7,5,4],
                       [2,7,5,0],
                       [2,7,5,6]])

    return pts,celles

def plan_atm_mesh(Alt,b,c):
    """
    Homogeneous mesh
    """
    # Alt on levels
    Nlayer = len(Alt)-1
    Nlevel = len(Alt)

    # initialize pts [layer,point,coor]
    pts = np.ones((Nlayer,8,3))*-1 # 8 -> each layer has 8 nodes
    for i in range(Nlayer):

        pts[i] = np.array([[  Alt[i+1],   b/2,   c/2],
                           [    Alt[i],   b/2,   c/2],
                           [    Alt[i],  -b/2,   c/2],
                           [  Alt[i+1],  -b/2,   c/2],
                           [  Alt[i+1],   b/2,  -c/2],
                           [    Alt[i],   b/2,  -c/2],
                           [    Alt[i],  -b/2,  -c/2],
                           [  Alt[i+1],  -b/2,  -c/2]])

    # celles [layers,tredr,pts_idx]
    celles = np.ones((Nlayer,5,4))*-1 # 5-> each layer has 5 tetrahedrons.
    for i in range(Nlayer):
        # nidx to be skipped
        d_idx = i*8
        celles[i] = np.array([[2,0,7,3],
                              [2,0,5,1],
                              [0,7,5,4],
                              [2,7,5,0],
                              [2,7,5,6]]) + d_idx

    # All the meshes have the same data format of node_coord and cell_ids, so that the function write_binary_file_grid() (in write.py) can be called to read these format and generate the mesh file input for htrdr.
    pts = np.reshape(pts,(Nlayer*8,3))
    celles = np.reshape(celles,(Nlayer*5,4))
    celles = celles.astype(int)

    return pts,celles
