"""
Mesh Optimization - Decimation, vertex merging, LOD generation
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple
import numpy as np

if TYPE_CHECKING:
    from assetpipe.core.asset import MeshData


class MeshOptimizer:
    """
    Mesh optimization utilities.
    """
    
    def decimate(
        self,
        mesh: "MeshData",
        ratio: float,
        preserve_boundaries: bool = True,
    ) -> None:
        """
        Reduce mesh triangle count by ratio.
        
        Uses quadric error metrics for quality decimation.
        Modifies mesh in place.
        
        Args:
            mesh: MeshData to decimate
            ratio: Target ratio (0.5 = reduce to 50% of triangles)
            preserve_boundaries: Whether to preserve mesh boundaries
        """
        if mesh.faces is None or len(mesh.faces) == 0:
            return
        
        target_faces = int(len(mesh.faces) * ratio)
        if target_faces >= len(mesh.faces):
            return
        
        try:
            # Try to use trimesh for decimation
            import trimesh
            
            # Create trimesh object
            tm = trimesh.Trimesh(
                vertices=mesh.vertices,
                faces=mesh.faces,
                process=False,
            )
            
            # Simplify
            simplified = tm.simplify_quadric_decimation(target_faces)
            
            # Update mesh data
            mesh.vertices = np.array(simplified.vertices, dtype=np.float32)
            mesh.faces = np.array(simplified.faces, dtype=np.int32)
            
            # Recompute normals
            mesh.compute_normals()
            
            # Note: UVs are lost during decimation with trimesh
            # A more sophisticated implementation would preserve UVs
            
        except ImportError:
            # Fallback: simple random face removal (not recommended)
            indices = np.random.choice(
                len(mesh.faces),
                size=target_faces,
                replace=False
            )
            mesh.faces = mesh.faces[indices]
    
    def merge_vertices(
        self,
        mesh: "MeshData",
        tolerance: float = 1e-6,
    ) -> int:
        """
        Merge duplicate vertices within tolerance.
        
        Args:
            mesh: MeshData to process
            tolerance: Distance threshold for merging
            
        Returns:
            Number of vertices removed
        """
        if mesh.vertices is None or len(mesh.vertices) == 0:
            return 0
        
        original_count = len(mesh.vertices)
        
        # Round vertices to tolerance
        rounded = np.round(mesh.vertices / tolerance) * tolerance
        
        # Find unique vertices
        unique_verts, inverse_indices = np.unique(
            rounded, axis=0, return_inverse=True
        )
        
        # Update faces to use new indices
        if mesh.faces is not None:
            mesh.faces = inverse_indices[mesh.faces]
        
        # Update vertices
        mesh.vertices = unique_verts.astype(np.float32)
        
        # Update normals if present
        if mesh.normals is not None and len(mesh.normals) == original_count:
            # Average normals for merged vertices
            new_normals = np.zeros((len(unique_verts), 3), dtype=np.float32)
            counts = np.zeros(len(unique_verts), dtype=np.int32)
            
            for i, new_idx in enumerate(inverse_indices):
                new_normals[new_idx] += mesh.normals[i]
                counts[new_idx] += 1
            
            # Normalize
            counts[counts == 0] = 1
            new_normals /= counts[:, np.newaxis]
            norms = np.linalg.norm(new_normals, axis=1, keepdims=True)
            norms[norms == 0] = 1
            mesh.normals = new_normals / norms
        
        return original_count - len(unique_verts)
    
    def remove_degenerate_triangles(
        self,
        mesh: "MeshData",
        area_threshold: float = 1e-10,
    ) -> int:
        """
        Remove triangles with zero or near-zero area.
        
        Args:
            mesh: MeshData to process
            area_threshold: Minimum triangle area
            
        Returns:
            Number of triangles removed
        """
        if mesh.faces is None or len(mesh.faces) == 0:
            return 0
        
        original_count = len(mesh.faces)
        valid_faces = []
        
        for face in mesh.faces:
            if len(face) < 3:
                continue
            
            # Check for duplicate indices
            if len(set(face)) < 3:
                continue
            
            v0 = mesh.vertices[face[0]]
            v1 = mesh.vertices[face[1]]
            v2 = mesh.vertices[face[2]]
            
            # Calculate area
            edge1 = v1 - v0
            edge2 = v2 - v0
            cross = np.cross(edge1, edge2)
            area = np.linalg.norm(cross) / 2
            
            if area >= area_threshold:
                valid_faces.append(face)
        
        mesh.faces = np.array(valid_faces, dtype=np.int32)
        
        return original_count - len(valid_faces)
    
    def generate_lod_levels(
        self,
        mesh: "MeshData",
        levels: List[float] = [1.0, 0.5, 0.25, 0.125],
    ) -> List["MeshData"]:
        """
        Generate LOD (Level of Detail) versions of mesh.
        
        Args:
            mesh: Source MeshData
            levels: List of decimation ratios for each LOD
            
        Returns:
            List of MeshData objects, one per LOD level
        """
        from assetpipe.core.asset import MeshData
        
        lods = []
        
        for ratio in levels:
            if ratio >= 1.0:
                # LOD 0 is the original
                lods.append(mesh)
            else:
                # Create copy and decimate
                lod_mesh = MeshData(
                    vertices=mesh.vertices.copy(),
                    faces=mesh.faces.copy(),
                    normals=mesh.normals.copy() if mesh.normals is not None else None,
                    uvs=mesh.uvs.copy() if mesh.uvs is not None else None,
                )
                self.decimate(lod_mesh, ratio)
                lods.append(lod_mesh)
        
        return lods
    
    def compute_vertex_normals(self, mesh: "MeshData") -> None:
        """Compute smooth vertex normals from face geometry"""
        mesh.compute_normals()
    
    def flip_normals(self, mesh: "MeshData") -> None:
        """Flip all normals (for inside-out meshes)"""
        if mesh.normals is not None:
            mesh.normals = -mesh.normals
        
        # Also flip face winding
        if mesh.faces is not None:
            mesh.faces = mesh.faces[:, ::-1]
    
    def center_mesh(self, mesh: "MeshData") -> np.ndarray:
        """
        Center mesh at origin.
        
        Returns:
            The offset that was applied
        """
        if mesh.vertices is None or len(mesh.vertices) == 0:
            return np.zeros(3)
        
        center = mesh.vertices.mean(axis=0)
        mesh.vertices -= center
        
        return center
    
    def normalize_scale(
        self,
        mesh: "MeshData",
        target_size: float = 1.0,
    ) -> float:
        """
        Scale mesh to fit within target size.
        
        Returns:
            The scale factor that was applied
        """
        if mesh.vertices is None or len(mesh.vertices) == 0:
            return 1.0
        
        # Get current size
        min_v = mesh.vertices.min(axis=0)
        max_v = mesh.vertices.max(axis=0)
        current_size = np.max(max_v - min_v)
        
        if current_size == 0:
            return 1.0
        
        scale = target_size / current_size
        mesh.vertices *= scale
        
        return scale


# Convenience functions
def decimate_mesh(mesh: "MeshData", ratio: float) -> None:
    """Decimate mesh to target ratio"""
    MeshOptimizer().decimate(mesh, ratio)


def merge_vertices(mesh: "MeshData", tolerance: float = 1e-6) -> int:
    """Merge duplicate vertices"""
    return MeshOptimizer().merge_vertices(mesh, tolerance)


def remove_degenerate_triangles(mesh: "MeshData") -> int:
    """Remove degenerate triangles"""
    return MeshOptimizer().remove_degenerate_triangles(mesh)


def generate_lods(
    mesh: "MeshData",
    levels: List[float] = [1.0, 0.5, 0.25],
) -> List["MeshData"]:
    """Generate LOD levels"""
    return MeshOptimizer().generate_lod_levels(mesh, levels)
