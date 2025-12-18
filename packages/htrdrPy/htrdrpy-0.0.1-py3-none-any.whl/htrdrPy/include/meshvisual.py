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
import math
import vtk
import pyvista as pv

def write_obj(vertices, faces,file_path):
    with open(file_path, 'w') as obj_file:
        for vertex in vertices:
            obj_file.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")

        for face in faces:
            # OBJ format uses 1-based indexing
            face_str = " ".join(str(idx + 1) for idx in face)
            obj_file.write(f"f {face_str}\n")

def write_vtk(vertices, cells,file_path):
    num_points = vertices.shape[0]
    num_cells = cells.shape[0]
    
    with open(file_path, 'w') as vtk_file:
        vtk_file.write("# vtk DataFile Version 3.0\n")
        vtk_file.write("Cube Example\n")
        vtk_file.write("ASCII\n")
        vtk_file.write("DATASET UNSTRUCTURED_GRID\n")
        
        # Write the points
        vtk_file.write(f"POINTS {num_points} float\n")
        for i in range(num_points):
            vtk_file.write(f"{vertices[i][0]} {vertices[i][1]} {vertices[i][2]}\n")
        
        # Write the cell connectivity
        vtk_file.write(f"CELLS {num_cells} {num_cells * 4}\n")
        for i in range(num_cells):
            vtk_file.write("3 " + " ".join(str(cell) for cell in cells[i]) + "\n")
        
        # Write the cell types
        vtk_file.write("CELL_TYPES " + str(num_cells) + "\n")
        for _ in range(num_cells):
            vtk_file.write("5\n")  # Assuming the cells are triangles (VTK_TRIANGLE)

def write_vtk_tetr(node_coord, cell_ids, output_file):
    # Create the points
    points = vtk.vtkPoints()
    for coord in node_coord:
        points.InsertNextPoint(coord)

    # Create the cells
    cells = vtk.vtkCellArray()
    for cell in cell_ids:
        tetra = vtk.vtkTetra()
        for i, point_id in enumerate(cell):
            tetra.GetPointIds().SetId(i, point_id)
        cells.InsertNextCell(tetra)

    # Create the unstructured grid
    ugrid = vtk.vtkUnstructuredGrid()
    ugrid.SetPoints(points)
    ugrid.SetCells(vtk.VTK_TETRA, cells)

    # Write the file
    writer = vtk.vtkUnstructuredGridWriter()
    writer.SetFileName(output_file)
    if vtk.VTK_MAJOR_VERSION <= 5:
        writer.SetInput(ugrid)
    else:
        writer.SetInputData(ugrid)
    writer.Write()

def attach_values_to_nodes(file_name, values,output_name):
    """
    Function to open a vtk file and attach values to each node.

    Args:
        file_name (str): Path to the vtk file.
        values (list): List of values to be attached.

    Returns:
        None.
    """

    # Load the vtk file
    mesh = pv.read(file_name)

    # Check if the number of values matches the number of nodes
    if len(values) != mesh.n_points:
        raise ValueError('The length of values does not match the number of nodes.')

    # Attach values to nodes
    mesh.point_data['values'] = values

    # Save the modified vtk file
    mesh.save(output_name)

def attach_values_to_cells(file_name, values,output_name):
    """
    Function to open a vtk file and attach values to each node.

    Args:
        file_name (str): Path to the vtk file.
        values (list): List of values to be attached.

    Returns:
        None.
    """

    # Load the vtk file
    mesh = pv.read(file_name)

    # Check if the number of values matches the number of nodes
    if len(values) != mesh.n_cells:
        raise ValueError('The length of values does not match the number of cells.')

    # Attach values to nodes
    mesh.cell_data['values'] = values

    # Save the modified vtk file
    mesh.save(output_name)
