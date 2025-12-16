import numpy as np
from typing import List
from itertools import product

class Triangle:
    def __init__(self, p1, p2, p3):
        self.P1 = p1
        self.P2 = p2
        self.P3 = p3

def create_triangle_mesh_from_voxel(voxel, ID_to_material):
    mesh = []

    dx = [-1, 1, 0, 0, 0, 0]
    dy = [0, 0, -1, 1, 0, 0]
    dz = [0, 0, 0, 0, -1, 1]

    voxel_size = -1.0 / max(voxel.shape)

    def is_surface_voxel(idx):
        for i in range(6):
            nx = idx[0] + dx[i]
            ny = idx[1] + dy[i]
            nz = idx[2] + dz[i]

            if (0 <= nx < voxel.shape[0] and
                0 <= ny < voxel.shape[1] and
                0 <= nz < voxel.shape[2] and
                voxel[nx, ny, nz] != ID_to_material):
                return True
        return False

    for idx in product(*map(range, voxel.shape)):
        if voxel[idx] == ID_to_material:
            if is_surface_voxel(idx):
                p1 = np.array(idx) * voxel_size
                p2 = (np.array(idx) + np.array([1, 0, 0])) * voxel_size
                p3 = (np.array(idx) + np.array([0, 1, 0])) * voxel_size
                p4 = (np.array(idx) + np.array([1, 1, 0])) * voxel_size
                p5 = (np.array(idx) + np.array([0, 0, 1])) * voxel_size
                p6 = (np.array(idx) + np.array([1, 0, 1])) * voxel_size
                p7 = (np.array(idx) + np.array([0, 1, 1])) * voxel_size
                p8 = (np.array(idx) + np.array([1, 1, 1])) * voxel_size

                if voxel[idx[0] - 1, idx[1], idx[2]] != ID_to_material:
                    mesh.append(Triangle(p1, p5, p7))
                    mesh.append(Triangle(p1, p7, p3))

                if voxel[idx[0] + 1, idx[1], idx[2]] != ID_to_material:
                    mesh.append(Triangle(p2, p6, p8))
                    mesh.append(Triangle(p2, p8, p4))

                if voxel[idx[0], idx[1] - 1, idx[2]] != ID_to_material:
                    mesh.append(Triangle(p1, p2, p5))
                    mesh.append(Triangle(p2, p6, p5))

                if voxel[idx[0], idx[1] + 1, idx[2]] != ID_to_material:
                    mesh.append(Triangle(p3, p4, p7))
                    mesh.append(Triangle(p4, p8, p7))

                if voxel[idx[0], idx[1], idx[2] - 1] != ID_to_material:
                    mesh.append(Triangle(p1, p2, p3))
                    mesh.append(Triangle(p2, p4, p3))

                if voxel[idx[0], idx[1], idx[2] + 1] != ID_to_material:
                    mesh.append(Triangle(p5, p6, p7))
                    mesh.append(Triangle(p6, p8, p7))
    return mesh

def save_triangles_as_ply(mesh, filename):
    with open(filename, 'w') as outputFile:
        print(f"Saving {len(mesh)} Triangles")
        outputFile.write("ply\n")
        outputFile.write("format ascii 1.0\n")
        outputFile.write(f"element vertex {len(mesh) * 3}\n")
        outputFile.write("property float x\n")
        outputFile.write("property float y\n")
        outputFile.write("property float z\n")
        outputFile.write(f"element face {len(mesh)}\n")
        outputFile.write("property list uchar int vertex_indices\n")
        outputFile.write("end_header\n")

        for triangle in mesh:
            outputFile.write(f"{triangle.P1[0]} {triangle.P1[1]} {triangle.P1[2]}\n")
            outputFile.write(f"{triangle.P2[0]} {triangle.P2[1]} {triangle.P2[2]}\n")
            outputFile.write(f"{triangle.P3[0]} {triangle.P3[1]} {triangle.P3[2]}\n")

        vertex_index = 0
        for i in range(len(mesh)):
            outputFile.write(f"3 {vertex_index} {vertex_index + 1} {vertex_index + 2}\n")
            vertex_index += 3
