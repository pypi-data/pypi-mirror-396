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
import struct
import math
import tqdm

def write_binary_file_grid(filename, pagesize, node_positions, cell_ids):
    # Derive the necessary variables from the inputs
    num_nodes = len(node_positions)
    num_cells = len(cell_ids)

    # Assuming that the lists are non-empty and all sublists have the same length
    dim_node = len(node_positions[0])
    dim_cell = len(cell_ids[0])
    print('Nnodes = {} Ncells = {} dim_node = {} dim_cell = {}'.format(num_nodes,num_cells,dim_node,dim_cell))
    
    with open(filename, 'wb') as f:
        # Writing <smsh>
        f.write(struct.pack('<Q', pagesize))  # UINT64
        f.write(struct.pack('<Q', num_nodes))  # UINT64
        f.write(struct.pack('<Q', num_cells))  # UINT64
        f.write(struct.pack('<I', dim_node))  # UINT32
        f.write(struct.pack('<I', dim_cell))  # UINT32

        # Calculate padding length after header to align nodes
        current_pos = f.tell()
        padding_length = (pagesize - (current_pos % pagesize)) % pagesize

        # Writing padding
        f.write(b'\x00' * padding_length)  # BYTEs

        # Writing nodes
        for pos_list in node_positions:
            for pos in pos_list:
                f.write(struct.pack('<d', pos))  # DOUBLEs

        # Calculate padding length after nodes to align cells
        current_pos = f.tell()
        padding_length = (pagesize - (current_pos % pagesize)) % pagesize

        # Writing padding
        f.write(b'\x00' * padding_length)  # BYTEs

        # Writing cells
        for id_list in cell_ids:
            for id in id_list:
                f.write(struct.pack('<Q', id))  # UINT64s

        # Calculate padding length after cells to align end of file
        current_pos = f.tell()
        padding_length = (pagesize - (current_pos % pagesize)) % pagesize

        # Writing padding
        f.write(b'\x00' * padding_length)  # BYTEs

def write_phase_function_decrete_dat(filename,arr ):
    wavelength = arr[1].copy()
    angle_deg = arr[0].copy()
    phi = arr[2].copy()
    # rad
    angle_rad = np.deg2rad(angle_deg)

    with open(filename, 'w') as f:
        f.write("wavelengths {}\n".format(len(wavelength)))
        for i in range(len(wavelength)):
            f.write("{} discrete {}\n".format(wavelength[i],len(angle_rad)))
            for j in range(len(angle_rad)):
                # TODO angles are inversed, verify the convention
                #f.write("{} {}\n".format(angle_rad[j],phi[len(angle_rad)-j-1,i]))
                f.write("{} {}\n".format(angle_rad[j],phi[j,i]))

def write_binary_file_surface_properties(file_path, page_size, celles, T, idx):
    def pad_to_align(current_pos):
        # Calculate padding based on current file position and page size
        remainder = current_pos % page_size
        if remainder != 0:
            padding = page_size - remainder
            file.write(b'\x00' * padding)

    size = len(celles)
    try:
        if len(T) != size:
            raise IndexError("error in size of surface temperature array")
        else:
            Temperature = T
    except TypeError: 
        Temperature = np.ones(size)*T
    try:
        if len(idx) != size:
            print("error in size of surface temperature array")
    except TypeError: 
        idx = np.ones(size, dtype=int)*idx

    # Open file in binary write mode
    with open(file_path, 'wb') as file:
        # Write page size, number of bands and nodes
        file.write(struct.pack('<QQQQ',page_size, size, 8, 8))

        # Pad to align
        pad_to_align(file.tell())

        #Write the id
        for i in range(size):
            file.write(struct.pack('<lf', idx[i], Temperature[i]))

        # Pad to align
        pad_to_align(file.tell())

def write_binary_file_phase_function(file_path, page_size, ka, idx):
    def pad_to_align(current_pos):
        # Calculate padding based on current file position and page size
        remainder = current_pos % page_size
        if remainder != 0:
            padding = page_size - remainder
            file.write(b'\x00' * padding)

    size = len(ka[0,:])

    # Open file in binary write mode
    with open(file_path, 'wb') as file:
        # Write page size, number of bands and nodes
        file.write(struct.pack('<QQQQ',page_size, size, 4, 4))

        # Pad to align
        pad_to_align(file.tell())

        #Write the id
        for i in range(size):
            file.write(struct.pack('<l', idx))

        # Pad to align
        pad_to_align(file.tell())

def write_binary_file_phase_function_het(file_path, page_size, idx):
    def pad_to_align(current_pos):
        # Calculate padding based on current file position and page size
        remainder = current_pos % page_size
        if remainder != 0:
            padding = page_size - remainder
            file.write(b'\x00' * padding)

    size = len(idx)

    # Open file in binary write mode
    with open(file_path, 'wb') as file:
        # Write page size, number of bands and nodes
        file.write(struct.pack('<QQQQ',page_size, size, 4, 4))

        # Pad to align
        pad_to_align(file.tell())

        #Write the id
        for i in range(size):
            file.write(struct.pack('<l', idx[i]))

        # Pad to align
        pad_to_align(file.tell())

def write_binary_file_k_haze_sphere(file_path, page_size, bands_low, bands_upp, ka, ks):
    def pad_to_align(current_pos):
        # Calculate padding based on current file position and page size
        remainder = current_pos % page_size
        if remainder != 0:
            padding = page_size - remainder
            file.write(b'\x00' * padding)

    Nband = 1 
    Nnodes = len(ka)

    # Open file in binary write mode
    with open(file_path, 'wb') as file:

        # Write page size, number of bands and nodes
        file.write(struct.pack('<QQQ', page_size, Nband, Nnodes))

        # Write bands
        file.write(struct.pack('<dd', bands_low, bands_upp))

        # Pad to align pad_to_align(file.tell())
        pad_to_align(file.tell())

        # Write ka-ks
        for inode in range(Nnodes):
            file.write(struct.pack('<ff', ka[inode], ks[inode]))
        # Pad to align
        pad_to_align(file.tell())

def write_binary_file_k_haze(file_path, page_size, bands_low, bands_upp, ka, ks):
    def pad_to_align(current_pos):
        # Calculate padding based on current file position and page size
        remainder = current_pos % page_size
        if remainder != 0:
            padding = page_size - remainder
            file.write(b'\x00' * padding)

    Nband = len(ka[:,0])
    Nnodes = len(ka[0,:])

    # Open file in binary write mode
    with open(file_path, 'wb') as file:

        # Write page size, number of bands and nodes
        file.write(struct.pack('<QQQ', page_size, Nband, Nnodes))

        # Write bands
        for i in range(Nband):
            file.write(struct.pack('<dd', bands_low[i], bands_upp[i]))

        # Pad to align pad_to_align(file.tell())
        pad_to_align(file.tell())

        # Write ka-ks
        for iband in tqdm.tqdm((range(Nband))):
            for inode in range(Nnodes):
                file.write(struct.pack('<ff', ka[iband,inode], ks[iband,inode]))
                #file.write(struct.pack('<ff',, 1))
            # Pad to align
            pad_to_align(file.tell())

def write_binary_file_k(file_path, page_size, bands_low, bands_upp, quad_pts, ka, ks):
    def pad_to_align(current_pos):
        # Calculate padding based on current file position and page size
        remainder = current_pos % page_size
        if remainder != 0:
            padding = page_size - remainder
            file.write(b'\x00' * padding)

    Nband = len(ka[:,0,0])
    Nnodes = len(ka[0,:,0])
    Nq = len(ka[0,0,:])

    # Open file in binary write mode
    with open(file_path, 'wb') as file:
        # Write page size, number of bands and nodes
        file.write(struct.pack('<QQQ', page_size, len(bands_low), Nnodes))

        # Write band low, band upp, number of quad points
        for i in range(Nband):
            file.write(struct.pack('<ddQ', bands_low[i], bands_upp[i], len(quad_pts[i,:])))
            # Write quad points
            for quad_weight in quad_pts[i,:]:
                file.write(struct.pack('<d', quad_weight))

        # Pad to align
        pad_to_align(file.tell())

        # Write ks
        for iband in tqdm.tqdm((range(Nband))):
            for inode in range(Nnodes):
                file.write(struct.pack('<f', ks[iband,inode]))
            # Pad to align
            pad_to_align(file.tell())
            for iq in range(Nq):
                for inode in range(Nnodes):
                    file.write(struct.pack('<f', ka[iband,inode,iq]))
                pad_to_align(file.tell())

def write_binary_file_k_sphere(file_path, page_size, bands_low, bands_upp, quad_pts, ka, ks):
    def pad_to_align(current_pos):
        # Calculate padding based on current file position and page size
        remainder = current_pos % page_size
        if remainder != 0:
            padding = page_size - remainder
            file.write(b'\x00' * padding)

    Nband = 1
    Nnodes = len(ka[:,0])
    Nq = len(ka[0,:])

    # Open file in binary write mode
    with open(file_path, 'wb') as file:
        # Write page size, number of bands and nodes
        file.write(struct.pack('<QQQ', page_size, Nband, Nnodes))

        # Write band low, band upp, number of quad points
        file.write(struct.pack('<ddQ', bands_low, bands_upp, Nq))
        # Write quad points
        for quad_weight in quad_pts:
            file.write(struct.pack('<d', quad_weight))

        # Pad to align
        pad_to_align(file.tell())

        # Write ks
        for inode in range(Nnodes):
            file.write(struct.pack('<f', ks[inode]))
        # Pad to align
        pad_to_align(file.tell())
        for iq in range(Nq):
            for inode in range(Nnodes):
                file.write(struct.pack('<f', ka[inode,iq]))
            pad_to_align(file.tell())

def write_binary_file_T(file_path, page_size, T):
    def pad_to_align(current_pos):
        # Calculate padding based on current file position and page size
        remainder = current_pos % page_size
        if remainder != 0:
            padding = page_size - remainder
            file.write(b'\x00' * padding)

    Nnodes = len(T)

    # Open file in binary write mode
    with open(file_path, 'wb') as file:
        # Write page size, number of bands and nodes
        file.write(struct.pack('<QQQQ',page_size, Nnodes, 4,4))

        # Pad to align
        pad_to_align(file.tell())

        #Write T
        for iT in range(len(T)):
            file.write(struct.pack('<f', T[iT]))
        # Pad to align
        pad_to_align(file.tell())

def writeSourceRadiance(file_path, wavelength, spectrum, page_size):
    def pad_to_align(current_pos):
        # Calculate padding based on current file position and page size
        remainder = current_pos % page_size
        if remainder != 0:
            padding = page_size - remainder
            file.write(b'\x00' * padding)
    
    size = len(wavelength)
    with open(file_path, 'wb') as file:

        # Write page size, number of bands and nodes
        file.write(struct.pack('<QQQQ', page_size, size, 16, 16))

        # Pad to align pad_to_align(file.tell())
        pad_to_align(file.tell())
    
        for wvl, spec in zip(wavelength, spectrum):
            file.write(struct.pack('<dd', wvl, spec))

        # Pad to align pad_to_align(file.tell())
        pad_to_align(file.tell())
    return

def write_binary_file_spectral_pdf(file_path, page_size, nCells, pdf):
    def pad_to_align(current_pos, alignSize):
        # Calculate padding based on current file position and page size
        remainder = current_pos % alignSize
        if remainder != 0:
            padding = alignSize - remainder
            file.write(b'\x00' * padding)

    size = int(nCells)
    if pdf.shape[0] != size:
        raise IndexError(f"The first dimension of the pdf is the cell list and \
                         should be equal to {size}, but is {pdf.shape[0]}")

    nSpectralItems = pdf.shape[1]
    itemSize = nSpectralItems*4 # each item is a list of nSpectralItems floats
    alignement = 1
    while alignement < itemSize:
        alignement *= 2

    # Open file in binary fwrite mode
    with open(file_path, 'wb') as file:
        # Write page size, number of bands and nodes
        file.write(struct.pack('<QQQQ',page_size, size, itemSize, alignement))

        # Pad to align
        pad_to_align(file.tell(), page_size)

        #Write the id
        for i in range(size):
            file.write(struct.pack('<'+nSpectralItems*'f', *pdf[i,:]))
            pad_to_align(file.tell(), alignement)

        # Pad to align
        pad_to_align(file.tell(), page_size)
    return

if __name__ == "__main__":
    ncells = int(1e6)
    arr = np.ones((ncells, 23*16))
    write_binary_file_spectral_pdf("test_pds.bin", 4096, ncells, arr)
