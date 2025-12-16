#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Impostor Viewer GPU Browser - Isometric Enhanced Edition
======================================================

A high-performance molecular visualizer utilizing modern OpenGL techniques
(Texture Buffer Objects, Instanced Rendering, and Raycasted Impostors).
This version features a dual-mode camera system (Perspective and Orthographic/Isometric)
and real-time data analysis via ImGui.

Technical Overview:
-------------------
1. Rendering: Spheres are rendered as 2D quads (billboards). The actual sphere geometry
   is mathematically calculated per-pixel in the Fragment Shader (Raycasting/Impostors).
   This allows rendering millions of atoms with perfect curvature.
2. Data Management: Atom data (position, radius, color) is stored in TBOs (Texture Buffer Objects)
   accessed via `texelFetch` in the vertex shader, avoiding VBO updates for static topology.
3. Projections: Supports standard Perspective and Orthographic projections. The shader
   logic adapts the ray generation strategy based on the projection mode.

Dependencies:
    - glfw
    - PyOpenGL
    - numpy
    - imgui[glfw]
    - scipy (Optional, for KDTree acceleration)

Author: Gemini (Refactored & Enhanced)
License: MIT
"""

from __future__ import annotations
import math
import sys
from dataclasses import dataclass, field
from typing import Optional, Sequence, Tuple, List, Protocol, Any, Dict
import itertools
from collections import Counter

import numpy as np
import glfw
from OpenGL.GL import *
import imgui
from imgui.integrations.glfw import GlfwRenderer

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Try importing Scipy for optimized neighbor searching (Radial Distribution Function)
try:
    from scipy.spatial import cKDTree
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# ==========================================
# Constants & Configuration
# ==========================================

# Standard CPK coloring (Element: (R, G, B))
# Standard CPK coloring (Element: (R, G, B))
CPK_COLORS = {
    'H': (1.0, 1.0, 1.0), 'He': (0.85, 1.0, 1.0),
    'Li': (0.8, 0.5, 1.0), 'Be': (0.76, 1.0, 0.0), 'B': (1.0, 0.7, 0.7), 'C': (0.56, 0.56, 0.56), 'N': (0.19, 0.31, 0.97), 'O': (1.0, 0.05, 0.05), 'F': (0.56, 0.88, 0.31), 'Ne': (0.7, 0.89, 0.96),
    'Na': (0.67, 0.36, 0.95), 'Mg': (0.54, 1.0, 0.0), 'Al': (0.75, 0.65, 0.65), 'Si': (0.94, 0.78, 0.63), 'P': (1.0, 0.5, 0.0), 'S': (1.0, 1.0, 0.19), 'Cl': (0.12, 0.94, 0.12), 'Ar': (0.5, 0.82, 0.89),
    'K': (0.56, 0.25, 0.83), 'Ca': (0.24, 1.0, 0.0), 'Sc': (0.9, 0.9, 0.9), 'Ti': (0.75, 0.76, 0.78), 'V': (0.65, 0.65, 0.67), 'Cr': (0.54, 0.6, 0.78), 'Mn': (0.61, 0.48, 0.78), 'Fe': (0.88, 0.4, 0.2), 'Co': (0.94, 0.56, 0.63), 'Ni': (0.31, 0.82, 0.31), 'Cu': (0.78, 0.5, 0.2), 'Zn': (0.49, 0.5, 0.69), 'Ga': (0.76, 0.56, 0.56), 'Ge': (0.4, 0.56, 0.56), 'As': (0.74, 0.5, 0.89), 'Se': (1.0, 0.63, 0.0), 'Br': (0.65, 0.16, 0.16), 'Kr': (0.36, 0.72, 0.82),
    'Rb': (0.44, 0.18, 0.69), 'Sr': (0.0, 1.0, 0.0), 'Y': (0.58, 1.0, 1.0), 'Zr': (0.58, 0.88, 0.88), 'Nb': (0.45, 0.76, 0.79), 'Mo': (0.33, 0.71, 0.71), 'Tc': (0.23, 0.62, 0.62), 'Ru': (0.14, 0.56, 0.56), 'Rh': (0.04, 0.49, 0.55), 'Pd': (0.0, 0.41, 0.52), 'Ag': (0.75, 0.75, 0.75), 'Cd': (1.0, 0.85, 0.56), 'In': (0.65, 0.46, 0.45), 'Sn': (0.4, 0.5, 0.5), 'Sb': (0.62, 0.39, 0.71), 'Te': (0.83, 0.48, 0.0), 'I': (0.58, 0.0, 0.58), 'Xe': (0.26, 0.62, 0.69),
    'Cs': (0.34, 0.09, 0.56), 'Ba': (0.0, 0.79, 0.0), 'La': (0.44, 0.83, 1.0), 'Ce': (1.0, 1.0, 0.78), 'Pr': (0.85, 1.0, 0.78), 'Nd': (0.78, 1.0, 0.78), 'Pm': (0.64, 1.0, 0.78), 'Sm': (0.56, 1.0, 0.78), 'Eu': (0.38, 1.0, 0.78), 'Gd': (0.27, 1.0, 0.78), 'Tb': (0.19, 1.0, 0.78), 'Dy': (0.12, 1.0, 0.78), 'Ho': (0.0, 1.0, 0.61), 'Er': (0.0, 0.9, 0.46), 'Tm': (0.0, 0.83, 0.32), 'Yb': (0.0, 0.75, 0.22), 'Lu': (0.0, 0.67, 0.14), 'Hf': (0.3, 0.76, 1.0), 'Ta': (0.3, 0.65, 1.0), 'W': (0.13, 0.58, 0.84), 'Re': (0.15, 0.49, 0.67), 'Os': (0.15, 0.4, 0.59), 'Ir': (0.09, 0.33, 0.53), 'Pt': (0.82, 0.82, 0.88), 'Au': (1.0, 0.82, 0.14), 'Hg': (0.72, 0.72, 0.82), 'Tl': (0.65, 0.33, 0.3), 'Pb': (0.34, 0.35, 0.38), 'Bi': (0.62, 0.31, 0.71), 'Po': (0.67, 0.36, 0.0), 'At': (0.46, 0.31, 0.27), 'Rn': (0.26, 0.51, 0.59),
    'Fr': (0.26, 0.0, 0.4), 'Ra': (0.0, 0.49, 0.0), 'Ac': (0.44, 0.67, 1.0), 'Th': (0.0, 0.73, 1.0), 'Pa': (0.0, 0.63, 1.0), 'U': (0.0, 0.56, 1.0), 'Np': (0.0, 0.5, 1.0), 'Pu': (0.0, 0.42, 1.0), 'Am': (0.33, 0.36, 0.95), 'Cm': (0.47, 0.36, 0.89), 'Bk': (0.54, 0.31, 0.89), 'Cf': (0.63, 0.21, 0.83), 'Es': (0.7, 0.12, 0.83), 'Fm': (0.7, 0.12, 0.73), 'Md': (0.7, 0.05, 0.65), 'No': (0.74, 0.05, 0.53), 'Lr': (0.78, 0.0, 0.4),
    'Rf': (0.8, 0.0, 0.35), 'Db': (0.82, 0.0, 0.31), 'Sg': (0.85, 0.0, 0.27), 'Bh': (0.88, 0.0, 0.22), 'Hs': (0.9, 0.0, 0.18), 'Mt': (0.92, 0.0, 0.15), 'Ds': (0.92, 0.0, 0.15), 'Rg': (0.92, 0.0, 0.15), 'Cn': (0.92, 0.0, 0.15), 'Nh': (0.92, 0.0, 0.15), 'Fl': (0.92, 0.0, 0.15), 'Mc': (0.92, 0.0, 0.15), 'Lv': (0.92, 0.0, 0.15), 'Ts': (0.92, 0.0, 0.15), 'Og': (0.92, 0.0, 0.15)
}

# Atomic Radii (Covalent Radii, in Angstroms)
ATOMIC_RADII = {
    'H': 0.31, 'He': 0.28,
    'Li': 1.28, 'Be': 0.96, 'B': 0.84, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'F': 0.57, 'Ne': 0.58,
    'Na': 1.66, 'Mg': 1.41, 'Al': 1.21, 'Si': 1.11, 'P': 1.07, 'S': 1.05, 'Cl': 1.02, 'Ar': 1.06,
    'K': 2.03, 'Ca': 1.76, 'Sc': 1.70, 'Ti': 1.60, 'V': 1.53, 'Cr': 1.39, 'Mn': 1.39, 'Fe': 1.32, 'Co': 1.26, 'Ni': 1.24, 'Cu': 1.32, 'Zn': 1.22, 'Ga': 1.22, 'Ge': 1.20, 'As': 1.19, 'Se': 1.20, 'Br': 1.20, 'Kr': 1.16,
    'Rb': 2.20, 'Sr': 1.95, 'Y': 1.90, 'Zr': 1.75, 'Nb': 1.64, 'Mo': 1.54, 'Tc': 1.47, 'Ru': 1.46, 'Rh': 1.42, 'Pd': 1.39, 'Ag': 1.45, 'Cd': 1.44, 'In': 1.42, 'Sn': 1.39, 'Sb': 1.39, 'Te': 1.38, 'I': 1.39, 'Xe': 1.40,
    'Cs': 2.44, 'Ba': 2.15, 'La': 2.07, 'Ce': 2.04, 'Pr': 2.03, 'Nd': 2.01, 'Pm': 1.99, 'Sm': 1.98, 'Eu': 1.98, 'Gd': 1.96, 'Tb': 1.94, 'Dy': 1.92, 'Ho': 1.92, 'Er': 1.89, 'Tm': 1.90, 'Yb': 1.87, 'Lu': 1.87, 'Hf': 1.75, 'Ta': 1.70, 'W': 1.62, 'Re': 1.51, 'Os': 1.44, 'Ir': 1.41, 'Pt': 1.36, 'Au': 1.36, 'Hg': 1.32, 'Tl': 1.45, 'Pb': 1.46, 'Bi': 1.48, 'Po': 1.40, 'At': 1.50, 'Rn': 1.50,
    'Fr': 2.60, 'Ra': 2.21, 'Ac': 2.15, 'Th': 2.06, 'Pa': 2.00, 'U': 1.96, 'Np': 1.90, 'Pu': 1.87, 'Am': 1.80, 'Cm': 1.69
}

# Plotting Colors for RDF (distinct from CPK to avoid confusion, or reused)
PLOT_COLORS = [
    (1.0, 1.0, 1.0, 1.0), # White
    (1.0, 0.2, 0.2, 1.0), # Red
    (0.2, 1.0, 0.2, 1.0), # Green
    (0.2, 0.5, 1.0, 1.0), # Blue
    (1.0, 1.0, 0.0, 1.0), # Yellow
    (0.0, 1.0, 1.0, 1.0), # Cyan
    (1.0, 0.0, 1.0, 1.0), # Magenta
]

DEFAULT_COLOR = (0.78, 0.78, 0.78)
DEFAULT_RADIUS = 1.2
WORLD_UP = np.array([0, 0, 1], dtype=np.float32)

# Topology for drawing the unit cell (Indices of corners)
CELL_EDGES = np.array([
    [0, 1], [0, 2], [0, 3], [1, 4], [1, 5], 
    [2, 4], [2, 6], [3, 5], [3, 6], [4, 7], 
    [5, 7], [6, 7]
], dtype=np.int32)

# ==========================================
# Math & Geometry Helpers
# ==========================================

def normalize(v: np.ndarray) -> np.ndarray:
    """Returns the normalized vector v."""
    n = float(np.linalg.norm(v))
    return v / (n if n > 1e-12 else 1.0)

def rodrigues(v: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    """Rotates vector v around axis by angle (radians) using Rodrigues' formula."""
    k = normalize(axis)
    c = math.cos(angle)
    s = math.sin(angle)
    return v * c + np.cross(k, v) * s + k * np.dot(k, v) * (1.0 - c)

def compute_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Calculates the angle (in degrees) defined by points p1-p2-p3."""
    v1 = p1 - p2
    v2 = p3 - p2
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 < 1e-6 or norm2 < 1e-6:
        return 0.0
    cosine = np.dot(v1, v2) / (norm1 * norm2)
    return float(np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))))

def compute_dihedral(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, p4: np.ndarray) -> float:
    """Calculates the dihedral angle (in degrees) defined by points p1-p2-p3-p4."""
    b1 = p2 - p1
    b2 = p3 - p2
    b3 = p4 - p3
    
    # Normalize b2
    b2 /= np.linalg.norm(b2)
    
    # Vector rejections
    # v = b1 - <b1, b2>*b2
    v = b1 - np.dot(b1, b2) * b2
    w = b3 - np.dot(b3, b2) * b2
    
    x = np.dot(v, w)
    y = np.dot(np.cross(b2, v), w)
    
    return float(np.degrees(np.arctan2(y, x)))

def compute_bounds(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Returns the AABB (min, max) of the point cloud."""
    return points.min(axis=0), points.max(axis=0)

def cell_corners(lattice: np.ndarray) -> np.ndarray:
    """Generates the 8 corners of a triclinic unit cell matrix."""
    a, b, c = lattice[0], lattice[1], lattice[2]
    O = np.zeros(3, dtype=np.float32)
    return np.array([O, a, b, c, a+b, a+c, b+c, a+b+c], dtype=np.float32)

# --- Matrix Generators ---

def perspective(fovy_deg: float, aspect: float, znear: float, zfar: float) -> np.ndarray:
    """Generates a standard perspective projection matrix."""
    f = 1.0 / math.tan(math.radians(fovy_deg) / 2.0)
    M = np.zeros((4, 4), dtype=np.float32)
    M[0, 0] = f / aspect
    M[1, 1] = f
    M[2, 2] = (zfar + znear) / (znear - zfar)
    M[2, 3] = (2 * zfar * znear) / (znear - zfar)
    M[3, 2] = -1.0
    return M

def ortho(left: float, right: float, bottom: float, top: float, znear: float, zfar: float) -> np.ndarray:
    """Generates an orthographic projection matrix."""
    M = np.identity(4, dtype=np.float32)
    M[0, 0] = 2.0 / (right - left)
    M[1, 1] = 2.0 / (top - bottom)
    M[2, 2] = -2.0 / (zfar - znear)
    M[3, 0] = -(right + left) / (right - left)
    M[3, 1] = -(top + bottom) / (top - bottom)
    M[3, 2] = -(zfar + znear) / (zfar - znear)
    return M

def look_at(eye: np.ndarray, center: np.ndarray, up: np.ndarray) -> np.ndarray:
    """Generates a LookAt view matrix."""
    f = normalize(center - eye)
    u = normalize(up)
    s = normalize(np.cross(f, u))
    u = np.cross(s, f)
    M = np.eye(4, dtype=np.float32)
    M[0, :3] = s
    M[1, :3] = u
    M[2, :3] = -f
    T = np.eye(4, dtype=np.float32)
    T[:3, 3] = -eye
    return M @ T

def compute_rdf(pos_ref: np.ndarray, pos_target: np.ndarray, lattice: np.ndarray, r_max: float = 10.0, bins: int = 50) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculates Radial Distribution Function (Approximated).
    If pos_ref == pos_target, calculates standard RDF.
    If different, calculates partial RDF (distribution of target around ref).
    """
    if pos_ref.shape[0] == 0 or pos_target.shape[0] == 0:
        return np.linspace(0, r_max, bins), np.zeros(bins)
    
    # Use KDTree if scipy is available, otherwise use simplistic dist calc
    distances = np.array([])
    if HAS_SCIPY:
        tree_target = cKDTree(pos_target)
        # query_ball_point returns indices of target points within r_max of each ref point
        indices = tree_target.query_ball_point(pos_ref, r_max)
        
        all_dists = []
        for i, idx_list in enumerate(indices):
            if not idx_list: continue
            
            if idx_list:
                d = np.linalg.norm(pos_target[idx_list] - pos_ref[i], axis=1)
                all_dists.extend(d)
        
        distances = np.array(all_dists)
        # Filter out self-interactions (distance ~ 0)
        distances = distances[distances > 1e-3]

    else:
        # Fallback: Distances from center of mass (Very Simplified)
        print("Warning: Scipy not found. RDF calculation might be inaccurate or slow.")
        center = np.mean(pos_target, axis=0)
        distances = np.linalg.norm(pos_ref - center, axis=1)
        distances = distances[distances > 1e-3]

    hist, edges = np.histogram(distances, bins=bins, range=(0, r_max))
    radii = (edges[:-1] + edges[1:]) / 2
    dr = edges[1] - edges[0]
    volume_shell = 4 * np.pi * (radii**2) * dr
    
    # Density of target atoms
    rho = len(pos_target) / (np.linalg.det(lattice) + 1e-12)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        g_r = hist / (volume_shell * rho * len(pos_ref)) 
        
    return radii, np.nan_to_num(g_r)

def compute_cn(positions: np.ndarray, lattice: np.ndarray, r_cut: float = 3.0) -> Tuple[float, np.ndarray]:
    """Calculates average Coordination Number (CN) and returns counts per atom."""
    if positions.shape[0] < 2: return 0.0, np.array([])
    
    if HAS_SCIPY:
        tree = cKDTree(positions)
        # query_ball_point returns list of neighbors for each point
        indices = tree.query_ball_point(positions, r_cut)
        # Subtract 1 because query includes self
        counts = np.array([len(idx_list) - 1 for idx_list in indices], dtype=np.int32)
        return float(np.mean(counts)), counts
    else:
        # Fallback (slow)
        counts = []
        for i in range(len(positions)):
            d = np.linalg.norm(positions - positions[i], axis=1)
            cnt = np.sum((d > 0) & (d < r_cut))
            counts.append(cnt)
        counts = np.array(counts, dtype=np.int32)
        return float(np.mean(counts)), counts

def compute_rmsd(pos: np.ndarray, pos_ref: np.ndarray) -> float:
    """Calculates Root Mean Square Deviation (RMSD) between two structures."""
    if pos.shape != pos_ref.shape: return 0.0
    diff = pos - pos_ref
    return float(np.sqrt(np.mean(np.sum(diff**2, axis=1))))

def compute_hbonds(positions: np.ndarray, elements: List[str], lattice: np.ndarray, 
                   d_ha_cut: float = 2.5, angle_cut: float = 120.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Detects Hydrogen Bonds and returns (distances, pairs).
    Pairs are (H_index, A_index).
    Criteria: D, A in {N, O, F}; H in {H}; dist(D,H)<1.3; dist(H,A)<d_ha_cut; angle(D-H...A)>angle_cut.
    """
    if not elements or len(elements) != len(positions): return np.array([]), np.array([])
    
    # Indices
    donors_acceptors = [i for i, e in enumerate(elements) if e in ('N', 'O', 'F')]
    hydrogens = [i for i, e in enumerate(elements) if e == 'H']
    
    if not donors_acceptors or not hydrogens: return np.array([]), np.array([])
    
    hb_dists = []
    hb_pairs = []
    
    # Box size for PBC (assume orthorhombic for simplicity)
    box = np.diag(lattice) if lattice is not None else None
    
    # Helper for MIC vector
    def get_vec_mic(v, box):
        if box is None: return v
        return v - np.round(v / box) * box

    # Using cKDTree for speed if available
    if HAS_SCIPY:
        # Pass boxsize if available to handle PBC in neighbor search
        # Note: boxsize argument requires scipy >= 1.6.0
        # cKDTree with boxsize requires data to be in [0, boxsize]
        
        # Prepare data for Tree
        pos_data = positions[donors_acceptors]
        if box is not None:
            pos_data = pos_data % box
            
        try:
            tree_da = cKDTree(pos_data, boxsize=box)
        except TypeError:
            # Fallback for older scipy
            tree_da = cKDTree(positions[donors_acceptors])
            # If we can't use boxsize in tree, we might miss PBC bonds in search, 
            # but we can still apply MIC in angle check. 
            pass
        
        for h_idx in hydrogens:
            h_pos = positions[h_idx]
            h_pos_query = h_pos % box if box is not None else h_pos
            
            # 1. Find covalently bonded Donor (D)
            # Query nearest D within 1.3A. 
            # D-H bond is short, usually within cell, but check PBC anyway if possible.
            try:
                d_dists, d_indices = tree_da.query(h_pos_query, k=1, distance_upper_bound=1.3)
            except TypeError:
                 d_dists, d_indices = tree_da.query(h_pos, k=1, distance_upper_bound=1.3)

            if d_dists == float('inf'): continue
            
            d_real_idx = donors_acceptors[d_indices]
            d_pos = positions[d_real_idx]
            
            # 2. Find Acceptors (A) within d_ha_cut
            try:
                a_indices_local = tree_da.query_ball_point(h_pos_query, d_ha_cut)
            except TypeError:
                a_indices_local = tree_da.query_ball_point(h_pos, d_ha_cut)
            
            for a_idx_local in a_indices_local:
                a_real_idx = donors_acceptors[a_idx_local]
                if a_real_idx == d_real_idx: continue # D and A cannot be same atom
                
                a_pos = positions[a_real_idx]
                
                # Check Angle D-H...A using MIC vectors
                # Vector H->D
                v_hd = get_vec_mic(d_pos - h_pos, box)
                # Vector H->A
                v_ha = get_vec_mic(a_pos - h_pos, box)
                
                l_hd = np.linalg.norm(v_hd)
                l_ha = np.linalg.norm(v_ha)
                
                if l_hd < 1e-3 or l_ha < 1e-3: continue
                
                dot = np.dot(v_hd, v_ha)
                cos_theta = dot / (l_hd * l_ha)
                
                angle_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))
                angle_deg = np.degrees(angle_rad)
                
                if angle_deg > angle_cut:
                    hb_dists.append(l_ha)
                    hb_pairs.append((h_idx, a_real_idx))
                    
    else:
        # Fallback (slow)
        for h_idx in hydrogens:
            h_pos = positions[h_idx]
            # Find D
            best_d = -1
            best_d_dist = 1.3
            for d_idx in donors_acceptors:
                v = get_vec_mic(positions[d_idx] - h_pos, box)
                dist = np.linalg.norm(v)
                if dist < best_d_dist:
                    best_d_dist = dist
                    best_d = d_idx
            
            if best_d == -1: continue
            d_pos = positions[best_d]
            
            # Find A
            for a_idx in donors_acceptors:
                if a_idx == best_d: continue
                a_pos = positions[a_idx]
                v_ha = get_vec_mic(a_pos - h_pos, box)
                dist_ha = np.linalg.norm(v_ha)
                
                if dist_ha < d_ha_cut:
                    # Angle
                    v_hd = get_vec_mic(d_pos - h_pos, box)
                    
                    l_hd = np.linalg.norm(v_hd)
                    l_ha = np.linalg.norm(v_ha)
                    
                    angle = np.degrees(np.arccos(np.clip(np.dot(v_hd, v_ha) / (l_hd * l_ha), -1, 1)))
                    if angle > angle_cut:
                        hb_dists.append(dist_ha)
                        hb_pairs.append((h_idx, a_idx))

    return np.array(hb_dists), np.array(hb_pairs)

def compute_coordination_sphere(positions: np.ndarray, elements: List[str], lattice: np.ndarray, factor: float = 1.2) -> Tuple[float, np.ndarray, float]:
    """
    Calculates Coordination Number based on overlapping coordination spheres.
    Criterion: d_ij < factor * (r_i + r_j)
    Returns: (avg_cn, counts, avg_bond_len)
    """
    if not elements or len(elements) != len(positions): return 0.0, np.array([]), 0.0
    
    N = len(positions)
    # Get radii, default to 1.5 if unknown
    radii = np.array([ATOMIC_RADII.get(e, 1.5) for e in elements])
    
    # Max possible cutoff to limit search
    max_r = np.max(radii)
    max_cutoff = factor * (max_r + max_r)
    
    counts = np.zeros(N, dtype=np.int32)
    total_bond_len = 0.0
    n_bonds = 0
    
    # Box for PBC
    box = np.diag(lattice) if lattice is not None else None
    
    if HAS_SCIPY:
        # Wrap positions for cKDTree
        pos_data = positions
        if box is not None:
            pos_data = positions % box
            
        try:
            tree = cKDTree(pos_data, boxsize=box)
        except TypeError:
            tree = cKDTree(positions)
            
        # Query pairs within max_cutoff
        try:
            pairs = tree.query_pairs(max_cutoff)
        except:
            pairs = []
        
        for i, j in pairs:
            # Re-calculate distance with MIC
            v = positions[j] - positions[i]
            if box is not None:
                v = v - np.round(v / box) * box
            dist = np.linalg.norm(v)
            
            cutoff = factor * (radii[i] + radii[j])
            
            if dist < cutoff:
                counts[i] += 1
                counts[j] += 1
                total_bond_len += dist
                n_bonds += 1
                
    else:
        # Fallback O(N^2)
        for i in range(N):
            for j in range(i + 1, N):
                v = positions[j] - positions[i]
                if box is not None:
                    v = v - np.round(v / box) * box
                dist = np.linalg.norm(v)
                
                cutoff = factor * (radii[i] + radii[j])
                
                if dist < cutoff:
                    counts[i] += 1
                    counts[j] += 1
                    total_bond_len += dist
                    n_bonds += 1
                    
    avg_bond_len = total_bond_len / n_bonds if n_bonds > 0 else 0.0
    return float(np.mean(counts)), counts, avg_bond_len



# ...

def compute_bad(positions: np.ndarray, lattice: np.ndarray, r_cut: float = 3.0, bins: int = 180) -> Tuple[np.ndarray, np.ndarray]:
    """Calculates Bond Angle Distribution (BAD) histogram."""
    angles = []
    if HAS_SCIPY:
        tree = cKDTree(positions)
        # Find all pairs within r_cut
        pairs = tree.query_pairs(r_cut)
        
        # Build adjacency list
        adj = {i: [] for i in range(len(positions))}
        for i, j in pairs:
            adj[i].append(j)
            adj[j].append(i)
            
        # Iterate over central atoms (j)
        for j, neighbors in adj.items():
            if len(neighbors) < 2: continue
            # Iterate over unique pairs of neighbors (i, k)
            for i_idx in range(len(neighbors)):
                for k_idx in range(i_idx + 1, len(neighbors)):
                    i, k = neighbors[i_idx], neighbors[k_idx]
                    p1, p2, p3 = positions[i], positions[j], positions[k]
                    angles.append(compute_angle(p1, p2, p3))
    else:
        # Fallback: Brute Force (Slow but functional for small N)
        # Build adjacency list by checking all pairs
        adj = {i: [] for i in range(len(positions))}
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                d = np.linalg.norm(positions[i] - positions[j])
                if d < r_cut:
                    adj[i].append(j)
                    adj[j].append(i)
        
        for j, neighbors in adj.items():
            if len(neighbors) < 2: continue
            for i_idx in range(len(neighbors)):
                for k_idx in range(i_idx + 1, len(neighbors)):
                    i, k = neighbors[i_idx], neighbors[k_idx]
                    p1, p2, p3 = positions[i], positions[j], positions[k]
                    angles.append(compute_angle(p1, p2, p3))
    
    if not angles:
        return np.linspace(0, 180, bins), np.zeros(bins)
        
    hist, edges = np.histogram(angles, bins=bins, range=(0, 180))
    centers = (edges[:-1] + edges[1:]) / 2
    # Normalize PDF
    hist = hist / np.sum(hist)
    return centers, hist

# ==========================================
# Shader Sources
# ==========================================

# -- Sphere Vertex Shader --
SPHERE_VS = r"""#version 330 core
layout(location=0) in vec2 aQuad;
uniform mat4 uView; uniform mat4 uProj;
uniform samplerBuffer uAtomPosRad; uniform samplerBuffer uAtomColor;
uniform samplerBuffer uReplicaOffsets; uniform int uAtomCount;
uniform bool uIsOrtho;
uniform float uAtomScale;
out VS_OUT { vec3 centerVS; float radiusVS; vec3 color; vec3 posVS; } v;
void main(){
    int inst = gl_InstanceID;
    int atomIdx = inst % uAtomCount;
    int repIdx = inst / uAtomCount;
    vec4 posRad = texelFetch(uAtomPosRad, atomIdx);
    vec3 color = texelFetch(uAtomColor, atomIdx).rgb;
    vec3 offset = texelFetch(uReplicaOffsets, repIdx).xyz;
    vec3 centerWorld = posRad.xyz + offset;
    float radius = posRad.w * uAtomScale;
    vec4 centerView4 = uView * vec4(centerWorld, 1.0);
    vec3 centerView = centerView4.xyz;
    vec3 posVS = centerView + vec3(aQuad * radius, 0.0);
    v.centerVS = centerView; v.radiusVS = radius; v.color = color; v.posVS = posVS;
    gl_Position = uProj * vec4(posVS, 1.0);
}
"""

# -- Sphere Fragment Shader --
SPHERE_FS = r"""#version 330 core
in VS_OUT { vec3 centerVS; float radiusVS; vec3 color; vec3 posVS; } v;
uniform mat4 uProj; uniform vec3 uLightDirVS; uniform bool uIsOrtho;
out vec4 FragColor;
void main(){
    vec2 coord = v.posVS.xy - v.centerVS.xy;
    float distSq = dot(coord, coord);
    float rSq = v.radiusVS * v.radiusVS;
    if (distSq > rSq) discard;
    float zOffset = sqrt(rSq - distSq);
    vec3 surfacePointVS = vec3(v.posVS.xy, v.centerVS.z + zOffset);
    vec3 normal = normalize(surfacePointVS - v.centerVS);
    float diff = max(dot(normal, normalize(uLightDirVS)), 0.1);
    vec4 clipPos = uProj * vec4(surfacePointVS, 1.0);
    gl_FragDepth = (clipPos.z / clipPos.w) * 0.5 + 0.5;
    FragColor = vec4(v.color * diff, 1.0);
}
"""

# -- Line Shaders --
LINE_VS = r"""#version 330 core
layout(location=0) in vec3 aPos;
uniform mat4 uView; uniform mat4 uProj; uniform samplerBuffer uReplicaOffsets;
void main(){
    int inst = gl_InstanceID;
    vec3 offset = texelFetch(uReplicaOffsets, inst).xyz;
    gl_Position = uProj * uView * vec4(aPos + offset, 1.0);
}
"""
LINE_FS = r"""#version 330 core
uniform vec4 uRGBA;
out vec4 FragColor;
void main(){
    FragColor = uRGBA;
}
"""

# -- Cylinder Shader (Instanced) --
CYLINDER_VS = r"""#version 330 core
layout(location=0) in vec3 aPos;     // Cylinder Unit Mesh (y-axis aligned 0 to 1, radius 1)
layout(location=1) in vec3 aNormal;
layout(location=2) in vec3 iStart;   // Instance: Start Point
layout(location=3) in vec3 iEnd;     // Instance: End Point
layout(location=4) in vec3 iColor;   // Instance: Color

uniform mat4 uView; uniform mat4 uProj;
uniform samplerBuffer uReplicaOffsets;
uniform float uBondScale;   // Global scale for radius
uniform int uReplicaCount;  // Total Replicas (unused here if we duplicate instances, but we'll use loop in Geometry or just duplicate data?)
// Actually simpler: We'll draw instanced bonds *only* for primary cell? 
// Or better: pass replica offset in a loop or geometry shader?
// Simplest: Draw bonds for N atoms. For replicas, we need to replicate bond instances or use offset uniform.
// Let's use uReplicaOffsets logic:
// We'll draw total_bonds * total_replicas instances? 
// Or just draw primary bonds and handle replicas in loop?
// Let's assume input instances are just for primary cell.
// We can use gl_InstanceID to figure out replica index if we draw (bonds * replicas).

uniform int uBondCount; // Number of bonds in primary cell

out vec3 vNormal; out vec3 vColor; out vec3 vPos;
void main(){
    int totalInst = gl_InstanceID;
    int bondIdx = totalInst % uBondCount;
    int repIdx = totalInst / uBondCount;
    
    vec3 offset = texelFetch(uReplicaOffsets, repIdx).xyz;
    
    // Geometry Construction
    // Vector from Start to End
    vec3 p0 = iStart + offset;
    vec3 p1 = iEnd + offset;
    vec3 dir = p1 - p0;
    float len = length(dir);
    if(len < 0.0001) { gl_Position = vec4(0,0,0,1); return; }
    
    vec3 yAxis = normalize(dir);
    
    // Rotation Matrix to align Y (0,1,0) to dir
    // Basic construction
    vec3 up = vec3(0, 1, 0);
    vec3 axis = cross(up, yAxis);
    float c = dot(up, yAxis);
    
    mat3 rot;
    if (abs(c + 1.0) < 0.0001) {
        // 180 degree turn
        rot = mat3(-1, 0, 0,  0, -1, 0,  0, 0, 1);
    } else if (abs(c - 1.0) < 0.0001) {
        rot = mat3(1,0,0, 0,1,0, 0,0,1);     
    } else {
        float s = length(axis);
        mat3 K = mat3(0, axis.z, -axis.y,  -axis.z, 0, axis.x,  axis.y, -axis.x, 0);
        rot = mat3(1,0,0, 0,1,0, 0,0,1) + K + K*K * (1.0/(1.0+c));
    }
    
    // Scale Radius (aPos.x, aPos.z) -> uBondScale
    // Scale Length (aPos.y) -> len
    vec3 localPos = aPos;
    localPos.x *= uBondScale;
    localPos.z *= uBondScale;
    localPos.y *= len; 
    
    vec3 worldPos = p0 + rot * localPos;
    vec3 worldNormal = rot * aNormal;
    
    vNormal = worldNormal;
    vColor = iColor;
    vPos = worldPos;
    
    gl_Position = uProj * uView * vec4(worldPos, 1.0);
}
"""

CYLINDER_FS = r"""#version 330 core
in vec3 vNormal; in vec3 vColor; in vec3 vPos;
uniform vec3 uLightDirVS; // Should be World Light Dir actually if normal is World
// Let's assume simple headlamp: Light is at camera? Or fixed?
// In sphere shader uLightDirVS implies View Space.
// We computed world pos and world normal in VS. We need View Normal.
uniform mat4 uView;
out vec4 FragColor;
void main(){
    vec3 normalView = mat3(uView) * normalize(vNormal); // Transform world normal to view
    vec3 lightDir = normalize(vec3(0.5, 0.5, 1.0)); // Fixed View Space Light
    
    float diff = max(dot(normalView, lightDir), 0.2);
    FragColor = vec4(vColor * diff, 1.0);
}
"""

# -- Picking Shaders --
PICK_VS = r"""#version 330 core
layout(location=0) in vec2 aQuad;
uniform mat4 uView; uniform mat4 uProj;
uniform samplerBuffer uAtomPosRad; uniform samplerBuffer uReplicaOffsets;
uniform int uAtomCount; uniform bool uIsOrtho;
out vec4 vColor;
void main(){
    int inst = gl_InstanceID;
    int atomIdx = inst % uAtomCount;
    int repIdx = inst / uAtomCount;
    vec4 posRad = texelFetch(uAtomPosRad, atomIdx);
    vec3 offset = texelFetch(uReplicaOffsets, repIdx).xyz;
    vec3 center = posRad.xyz + offset;
    float r = posRad.w;
    vec4 centerView = uView * vec4(center, 1.0);
    vec3 posVS = centerView.xyz + vec3(aQuad * r, 0.0);
    gl_Position = uProj * vec4(posVS, 1.0);
    int id = atomIdx;
    float R = float(id & 0xFF) / 255.0;
    float G = float((id >> 8) & 0xFF) / 255.0;
    float B = float((id >> 16) & 0xFF) / 255.0;
    vColor = vec4(R, G, B, 1.0);
}
"""
PICK_FS = r"""#version 330 core
in vec4 vColor; out vec4 FragColor;
void main(){ FragColor = vColor; }
"""

# ==========================================
# Camera System
# ==========================================

@dataclass
class OrbitCamera:
    center: np.ndarray
    offset: np.ndarray # Vector from center to eye
    fov: float = 45.0
    ortho_scale: float = 20.0
    
    # Physics/Momentum
    yaw_v: float = 0.0
    pitch_v: float = 0.0
    
    # Camera Shift (Pan)
    pan: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=np.float32))

    def get_pan_vector(self) -> np.ndarray:
        # Convert 2D pan (X, Y) to 3D vector in camera basis
        right = self.right()
        # Up vector relative to camera view (Screen Up)
        up = np.cross(right, self.forward())
        return right * self.pan[0] + up * self.pan[1]

    def eye(self) -> np.ndarray:
        # Eye is center + offset + pan (in camera plane)
        return self.center + self.offset + self.get_pan_vector()

    def target(self) -> np.ndarray:
        # Target is center + pan
        return self.center + self.get_pan_vector()

    def forward(self) -> np.ndarray:
        return normalize(-self.offset)

    def right(self) -> np.ndarray:
        return normalize(np.cross(self.forward(), WORLD_UP))

    def rotate_yaw(self, angle: float):
        self.offset = rodrigues(self.offset, WORLD_UP, angle)

    def rotate_pitch(self, angle: float):
        forward = normalize(-self.offset)
        right = normalize(np.cross(forward, WORLD_UP))
        
        # Calculate current pitch (angle between forward and Up)
        # Dot product: cos(theta) = dot(forward, Up)
        # theta = 0 -> Looking Up, theta = pi -> Looking Down, theta = pi/2 -> Horizon
        current_dot = np.dot(forward, WORLD_UP)
        
        # Limit pitch to avoid gimbal lock (singularity at poles)
        # We want to keep angle between forward and Up in range (epsilon, pi-epsilon)
        # Or simply clamp the rotation if it would push us past the limit
        
        # Angle to rotate
        new_angle = angle
        
        # Check bounds
        # If current_dot is close to 1 (looking up) and we try to look up more (positive pitch usually means looking up/down depending on convention)
        # Let's use a simpler approach: track elevation or clamp dot product
        
        # Simpler approach: Predict new forward
        # But rodrigues rotates offset. 
        
        # Let's use the method from the original code I deleted/replaced which had clamping
        # Re-implementing robust clamping:
        
        up_dot = np.dot(forward, WORLD_UP)
        # Current elevation angle from horizon (0) to pole (pi/2)
        # sin(elev) = up_dot
        
        # We want to clamp elevation to e.g. [-89, 89] degrees
        max_elev = math.radians(89.0)
        
        # Current elevation
        cur_elev = math.asin(np.clip(up_dot, -1.0, 1.0))
        
        # New elevation if we apply angle
        # Note: angle sign convention depends on mouse input. 
        # Usually dy > 0 -> pitch down -> angle < 0? 
        # In _on_mouse_move: pitch_v -= 0.005 * dy. 
        # If dy > 0 (mouse down), pitch_v < 0. 
        # If pitch_v < 0, we rotate around Right. 
        # Right = Cross(Forward, Up). 
        # If Forward=(1,0,0), Up=(0,1,0), Right=(0,0,1). 
        # Rotate -angle around Z -> moves Forward towards -Y (Down).
        # So negative angle = Look Down.
        
        new_elev = cur_elev + angle
        
        # Clamp delta angle
        if new_elev > max_elev:
            angle = max_elev - cur_elev
        elif new_elev < -max_elev:
            angle = -max_elev - cur_elev
            
        self.offset = rodrigues(self.offset, right, angle)

    def snap_isometric(self):
        dist = np.linalg.norm(self.offset)
        iso_pitch = math.radians(35.264)
        c, s = math.cos(iso_pitch), math.sin(iso_pitch)
        v = np.array([0, -dist*c, dist*s], dtype=np.float32)
        rot_z = math.radians(-45.0)
        v = rodrigues(v, np.array([0, 0, 1], dtype=np.float32), rot_z)
        self.offset = v


class StructureProvider(Protocol):
    def __len__(self) -> int: ...
    def get(self, idx: int) -> Tuple[np.ndarray, np.ndarray, float, Optional[Sequence[str]], Optional[np.ndarray], Optional[np.ndarray]]: ...
    def get_all_Ef(self) -> np.ndarray: ...
    def get_all_E(self) -> np.ndarray: ...


class Viewer:
    def __init__(self, provider: StructureProvider, 
                 start_index: int = 0, 
                 replicas: Tuple[int,int,int] = (0,0,0), 
                 keep_view: bool = False,
                 win_size=(1280, 800)):
        
        self.provider = provider
        self.index = start_index
        self.keep_view = True # Default to True as requested
        self.replicas = tuple(replicas)
        
        # Rendering Stats Defaults
        self.N = 0
        self.pos = np.array([], dtype=np.float32)
        self.elements = []
        self.replica_offsets = [(0,0,0)]
        self.cell_count = 0
        self.lat = np.eye(3, dtype=np.float32)
        self.composition_str = "N/A"
        self.energy = 0.0
        
        # Selection State
        self.selected_atoms: List[int] = []
        self.box_selecting = False
        self.box_start = None
        self.box_end = None
        
        # View State
        self.is_ortho = False  # Start in Perspective
        self.show_gui = True
        self.show_rdf = False
        self.bg_color = [0.05, 0.07, 0.09]
        self.atom_scale = 1.0
        
        # Wrapping State
        self.auto_wrap = False
        
        # Bond Config
        self.show_bonds = False
        self.bond_scale = 0.2
        self.bond_cutoff_factor = 1.15
        self.bonds = [] # List of (i, j) pairs
        self.bond_count = 0
        self.bond_data = np.array([]) # For cylinder instancing (start, end, color)

        # Playback State
        self.playing = False
        self.playback_speed = 30.0 # Steps per second (when playing)
        self.target_fps = 100.0 # Max FPS for rendering
        self.time_acc = 0.0

        self.bad_x = []
        self.bad_y = []
        self.avg_cn = 0.0
        self.cn_counts = np.array([])
        self.rmsd = 0.0
        self.rdf_results = {}
        self.hb_dists = np.array([])
        self.hb_pairs = np.array([])
        self.show_hbonds = False
        self.hb_dist_cut = 2.5
        self.hb_angle_cut = 120.0
        self.coord_factor = 1.2
        self.coord_counts = np.array([])
        self.coord_avg_bond_len = 0.0
        self.show_coord_sphere = False
        self.color_by_cn = False
        
        self.rdf_rmax = 5.0

        self.rdf_bins = 200
        
        # Energy Analysis State
        self.show_formation_energy = False # Toggle (False=Total E, True=Formation Ef)
        self.hist_range = [None, None] # Selection range (min, max)
        self.hist_dragging = False
        self.hist_start_x = 0.0

        # Export State
        self.export_filename = "export"
        self.export_status_msg = ""
        self.export_status_time = 0.0
        
        # Error State
        self.last_error = None

        # Input State
        self.last_x = self.last_y = None
        self.orbiting = self.panning = False
        self.show_help = False

        self._init_gl(win_size)
        self._init_resources()
        
        # Cache Energies
        self.energy_ef = np.array(provider.get_all_Ef(), dtype=np.float32)
        if hasattr(provider, 'get_all_E'):
            self.energy_total = np.array(provider.get_all_E(), dtype=np.float32)
        else:
            self.energy_total = self.energy_ef.copy() # Fallback
            
        self._load_index(self.index)
        self.pos_0 = self.pos.copy()
        self.last_time = glfw.get_time()

    def save_screenshot(self, filename="screenshot.ppm"):
        """Saves the current framebuffer to a PPM file."""
        w, h = glfw.get_framebuffer_size(self.win)
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE)
        
        # Flip Y (OpenGL is bottom-left, Image is top-left)
        # Simple manual flip or just write it out and let user flip. 
        # For raw PPM, we can just write rows in reverse order if needed, 
        # but numpy is easier if available.
        image = np.frombuffer(data, dtype=np.uint8).reshape(h, w, 3)
        image = np.flipud(image)
        
        with open(filename, 'wb') as f:
            f.write(f"P6\n{w} {h}\n255\n".encode('ascii'))
            f.write(image.tobytes())
        print(f"Screenshot saved to {filename}")

    def _export_current_xyz(self, filename):
        """Exports the current structure to an Extended XYZ file."""
        if not filename.endswith(".extxyz") and not filename.endswith(".xyz"): 
            filename += ".extxyz"
        try:
            with open(filename, "w") as f:
                f.write(f"{self.N}\n")
                # Construct Lattice String: "ax ay az bx by bz cx cy cz"
                # self.lat is 3x3. Flatten row-wise.
                # Actually ASE expects "ax ay az bx by bz cx cy cz" (vectors as rows? columns? ASE uses vectors as rows in cell matrix)
                # Let's assume self.lat rows are vectors.
                L = self.lat.flatten()
                lat_str = " ".join([f"{v:.8f}" for v in L])
                
                # Properties line: species:S:1:pos:R:3
                # Add Energy info
                ef = self.energy_ef[self.index] if len(self.energy_ef) > self.index else 0.0
                et = self.energy_total[self.index] if hasattr(self, 'energy_total') and len(self.energy_total) > self.index else 0.0
                
                # Header Line
                header = f'Lattice="{lat_str}" Properties=species:S:1:pos:R:3 energy={et:.6f} formation_energy={ef:.6f} pbc="T T T"'
                f.write(f"{header}\n")
                
                elements = self.elements if self.elements else ["X"] * self.N
                for i in range(self.N):
                    e = elements[i] if i < len(elements) else "X"
                    x, y, z = self.pos[i]
                    f.write(f"{e} {x:.8f} {y:.8f} {z:.8f}\n")
            
            print(f"Exported current frame to {filename}")
            self.export_status_msg = f"Exported: {filename}"
            self.export_status_time = glfw.get_time() + 3.0 # Show for 3 seconds
            
        except Exception as e:
            print(f"Export failed: {e}")
            self.export_status_msg = f"Export Failed: {e}"
            self.export_status_time = glfw.get_time() + 5.0

    def _init_gl(self, win_size):
        if not glfw.init(): raise RuntimeError("GLFW failed")
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.SAMPLES, 4)
        self.win = glfw.create_window(win_size[0], win_size[1], "Impostor Viewer - Isometric", None, None)
        glfw.make_context_current(self.win)
        glfw.swap_interval(1)
        imgui.create_context()
        self.impl = GlfwRenderer(self.win)
        glEnable(GL_DEPTH_TEST); glEnable(GL_MULTISAMPLE)
        glfw.set_scroll_callback(self.win, self._on_scroll)
        glfw.set_cursor_pos_callback(self.win, self._on_mouse_move)
        glfw.set_mouse_button_callback(self.win, self._on_mouse_button)
        glfw.set_key_callback(self.win, self._on_key)

    def _init_resources(self):
        self.sphere_prog = link_program(SPHERE_VS, SPHERE_FS)
        self.line_prog = link_program(LINE_VS, LINE_FS)
        self.pick_prog = link_program(PICK_VS, PICK_FS)
        self.cylinder_prog = link_program(CYLINDER_VS, CYLINDER_FS) # New Shader
        
        # --- Sphere Quad ---
        quad = np.array([[-1,-1],[1,-1],[-1,1],[1,1]], dtype=np.float32)
        self.quad_vao = glGenVertexArrays(1)
        glBindVertexArray(self.quad_vao)
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, quad.nbytes, quad, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
        glBindVertexArray(0)
        self.pr_bo, self.pr_tbo = glGenBuffers(1), glGenTextures(1)
        self.col_bo, self.col_tbo = glGenBuffers(1), glGenTextures(1)
        self.rep_bo, self.rep_tbo = glGenBuffers(1), glGenTextures(1)
        self.cell_vao = glGenVertexArrays(1)
        self.cell_vbo = glGenBuffers(1)

        # --- Cylinder Mesh (Unit Height 0->1, Radius 1) ---
        self._init_cylinder_mesh() # Helper for verbosity
        
        # --- Bond Instance Buffers ---
        self.bond_vao = glGenVertexArrays(1)
        # Re-use cyl vbo for geometry binding later
        self.bond_inst_vbo = glGenBuffers(1)

    def _init_cylinder_mesh(self):
        # 8-sided prism is enough for thin sticks? Let's do 12.
        segments = 12
        verts = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x, z = math.cos(angle), math.sin(angle)
            # Bottom (y=0)
            verts.extend([x, 0.0, z, x, 0.0, z]) # Pos, Normal (approx normal is pos xz)
            # Top (y=1)
            verts.extend([x, 1.0, z, x, 0.0, z])
            
        # Triangles
        indices = []
        for i in range(segments):
            next_i = (i + 1) % segments
            # Two triangles forming quad
            # 2*i, 2*i+1 (top)
            b0 = 2*i
            t0 = 2*i + 1
            b1 = 2*next_i
            t1 = 2*next_i + 1
            
            # Triangle 1: b0, t0, b1
            indices.extend([b0, t0, b1])
            # Triangle 2: t0, t1, b1
            indices.extend([t0, t1, b1])
            
        val = np.array(verts, dtype=np.float32)
        idx = np.array(indices, dtype=np.uint32)
        
        self.cyl_vbo = glGenBuffers(1)
        self.cyl_ebo = glGenBuffers(1)
        self.cyl_idx_count = len(idx)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.cyl_vbo)
        glBufferData(GL_ARRAY_BUFFER, val.nbytes, val, GL_STATIC_DRAW)
        
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.cyl_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx.nbytes, idx, GL_STATIC_DRAW)

    def _ingest_structure(self, positions, lattice, energy, elements, colors, radii):
        self.pos = np.asarray(positions, dtype=np.float32).reshape(-1, 3)
        self.lat = np.asarray(lattice, dtype=np.float32).reshape(3, 3)
        self.energy = energy
        self.N = self.pos.shape[0]
        self.elements = elements if elements else []
        
        # Calculate Composition
        from collections import Counter # Added import here
        if self.elements:
            counts = Counter(self.elements)
            self.composition_str = " ".join([f"{k}{v}" for k, v in sorted(counts.items())])
        else:
            self.composition_str = "Unknown"

        if radii is None:
            if elements: radii = np.array([ATOMIC_RADII.get(e, DEFAULT_RADIUS) for e in elements], dtype=np.float32)
            else: radii = np.full(self.N, DEFAULT_RADIUS, dtype=np.float32)
        if colors is None:
            if elements: colors = np.array([CPK_COLORS.get(e, DEFAULT_COLOR) for e in elements], dtype=np.float32)
            else: colors = np.tile(DEFAULT_COLOR, (self.N, 1)).astype(np.float32)
            
        self.radii = np.asarray(radii, dtype=np.float32)
        self.colors = np.asarray(colors, dtype=np.float32)

        mn, mx = compute_bounds(np.vstack([self.pos, cell_corners(self.lat)]))
        center = (mn + mx) * 0.5
        diag = np.linalg.norm(mx - mn)
        
        # Persist View if requested
        if not self.keep_view or not hasattr(self, 'cam'):
            self.cam = OrbitCamera(center.astype(np.float32), np.array([1.5*diag, 1.5*diag, diag], dtype=np.float32))
            self.cam.ortho_scale = diag * 1.2
        else:
            # Optionally update center to follow structure if desired, or keep absolute?
            # User expectation for "Keep View" usually means "don't reset my zoom/angle".
            # but center might shift. For now, keep camera as is.
            pass

    def _get_filtered_indices(self):
        """Returns list of indices that satisfy the current energy histogram filter."""
        s_min, s_max = self.hist_range
        if s_min is None:
            return list(range(len(self.provider)))
        
        energies = self.energy_ef if self.show_formation_energy else self.energy_total
        indices = [i for i, e in enumerate(energies) if s_min <= e <= s_max]
        return indices

    def _load_index(self, idx: int):
        idx = int(idx) % len(self.provider)
        self.index = idx
        
        try:
            # Auto-Wrap Logic
            if self.auto_wrap:
                if hasattr(self.provider, 'wrap'):
                    self.provider.wrap(idx)
            
            p, l, e, els, c, r = self.provider.get(idx)
            self._ingest_structure(p, l, e, els, c, r)
            self._upload_atom_tbos()
            self._build_cell_buffers()
            self._rebuild_replica_offsets()
            self.selected_atoms = []
            if self.show_rdf: self._calc_rdf_current()
            
            # Clear error if success
            self.last_error = None
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.last_error = f"Error loading frame {idx}:\n{str(e)}"
            print(f"Warning: {self.last_error}")
            
            # Fallback for critical state if first load fails
            if not hasattr(self, 'cam'):
                # Initialize default camera if missing
                self.cam = OrbitCamera(np.zeros(3, dtype=np.float32), np.array([10.0, 10.0, 10.0], dtype=np.float32))
                self.cam.ortho_scale = 20.0
            
            # Ensure arrays exist for rendering (even if empty)
            if not hasattr(self, 'radii'): self.radii = np.array([], dtype=np.float32)
            if not hasattr(self, 'colors'): self.colors = np.array([], dtype=np.float32)

    def _upload_atom_tbos(self):
        posrad = np.hstack([self.pos, self.radii[:, None]]).astype(np.float32)
        col = np.hstack([self.colors, np.ones((self.N, 1))]).astype(np.float32)
        for i in self.selected_atoms: col[i, :3] = [1.0, 1.0, 0.2]
        glBindBuffer(GL_TEXTURE_BUFFER, self.pr_bo)
        glBufferData(GL_TEXTURE_BUFFER, posrad.nbytes, posrad, GL_DYNAMIC_DRAW)
        glBindTexture(GL_TEXTURE_BUFFER, self.pr_tbo)
        glTexBuffer(GL_TEXTURE_BUFFER, GL_RGBA32F, self.pr_bo)
        glBindBuffer(GL_TEXTURE_BUFFER, self.col_bo)
        glBufferData(GL_TEXTURE_BUFFER, col.nbytes, col, GL_DYNAMIC_DRAW)
        glBindTexture(GL_TEXTURE_BUFFER, self.col_tbo)
        glTexBuffer(GL_TEXTURE_BUFFER, GL_RGBA32F, self.col_bo)

    def _rebuild_replica_offsets(self):
        rx, ry, rz = self.replicas
        a, b, c = self.lat[0], self.lat[1], self.lat[2]
        offs = [i*a + j*b + k*c for i in range(-rx, rx+1) for j in range(-ry, ry+1) for k in range(-rz, rz+1)]
        self.replica_offsets = np.array(offs, dtype=np.float32)
        data = np.hstack([self.replica_offsets, np.zeros((len(offs), 1))]).astype(np.float32)
        glBindBuffer(GL_TEXTURE_BUFFER, self.rep_bo)
        glBufferData(GL_TEXTURE_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        glBindTexture(GL_TEXTURE_BUFFER, self.rep_tbo)
        glTexBuffer(GL_TEXTURE_BUFFER, GL_RGBA32F, self.rep_bo)

    def _build_cell_buffers(self):
        corners = cell_corners(self.lat)
        lines = np.empty((CELL_EDGES.shape[0] * 2, 3), dtype=np.float32)
        lines[0::2] = corners[CELL_EDGES[:, 0]]
        lines[1::2] = corners[CELL_EDGES[:, 1]]
        self.cell_count = len(lines)
        glBindVertexArray(self.cell_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.cell_vbo)
        glBufferData(GL_ARRAY_BUFFER, lines.nbytes, lines, GL_DYNAMIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glBindVertexArray(0)

    def _calc_rdf_current(self):
        self.rdf_results = {}
        # 1. Global
        r, g = compute_rdf(self.pos, self.pos, self.lat, r_max=self.rdf_rmax, bins=self.rdf_bins)
        self.rdf_results["Global"] = (r, g)
        # 2. Partials
        if self.elements and len(self.elements) == self.N:
            unique_elements = sorted(list(set(self.elements)))
            indices_by_el = {el: [] for el in unique_elements}
            for i, el in enumerate(self.elements): indices_by_el[el].append(i)
            for el1, el2 in itertools.combinations_with_replacement(unique_elements, 2):
                idx1, idx2 = indices_by_el[el1], indices_by_el[el2]
                if not idx1 or not idx2: continue
                pos1, pos2 = self.pos[idx1], self.pos[idx2]
                r, g = compute_rdf(pos1, pos2, self.lat, r_max=self.rdf_rmax, bins=self.rdf_bins)
                self.rdf_results[f"{el1}-{el2}"] = (r, g)

    def _draw_rdf_plot(self):
        """Draws the RDF graph using ImGui DrawList over the previously reserved item."""
        draw_list = imgui.get_window_draw_list()
        
        # Get bounds of the invisible button we just drew
        p_min = imgui.get_item_rect_min()
        p_max = imgui.get_item_rect_max()
        
        x0, y0 = p_min[0], p_min[1]
        w = p_max[0] - p_min[0]
        h = p_max[1] - p_min[1]
        
        # Background
        draw_list.add_rect_filled(x0, y0, x0 + w, y0 + h, imgui.get_color_u32_rgba(0, 0, 0, 0.5))
        draw_list.add_rect(x0, y0, x0 + w, y0 + h, imgui.get_color_u32_rgba(1, 1, 1, 0.3))

        if not self.rdf_results:
            return

        # Determine Scales
        max_r = self.rdf_rmax
        max_g = 0.0
        for r, g in self.rdf_results.values():
            if len(r) > 0:
                # max_r = max(max_r, np.max(r)) # Disabled auto-scaling for X
                max_g = max(max_g, np.max(g))
        
        if max_g == 0: return

        # Margins
        pad = 5
        plot_x, plot_y = x0 + pad, y0 + pad
        plot_w, plot_h = w - 2*pad, h - 2*pad

        # Helper to map data to screen
        def map_pt(r_val, g_val):
            sx = plot_x + (r_val / max_r) * plot_w
            sy = plot_y + plot_h - (g_val / max_g) * plot_h
            return sx, sy

        # Draw Grid
        draw_list.add_line(plot_x, plot_y + plot_h, plot_x + plot_w, plot_y + plot_h, imgui.get_color_u32_rgba(1, 1, 1, 0.5)) # X Axis
        draw_list.add_line(plot_x, plot_y, plot_x, plot_y + plot_h, imgui.get_color_u32_rgba(1, 1, 1, 0.5)) # Y Axis

        # Draw Lines
        color_idx = 0
        
        # Draw Global first (White/Grey)
        if "Global" in self.rdf_results:
            r, g = self.rdf_results["Global"]
            points = [map_pt(r[i], g[i]) for i in range(len(r))]
            draw_list.add_polyline(points, imgui.get_color_u32_rgba(1, 1, 1, 0.4), thickness=2.0)
        
        # Draw Partials
        legend_y = y0 + 5
        legend_x_start = x0 + w - 10
        
        for label, (r, g) in self.rdf_results.items():
            if label == "Global": continue
            
            # Pick Color
            c = PLOT_COLORS[(color_idx % (len(PLOT_COLORS) - 1)) + 1] # Skip white
            col_u32 = imgui.get_color_u32_rgba(*c)
            color_idx += 1
            
            points = [map_pt(r[i], g[i]) for i in range(len(r))]
            draw_list.add_polyline(points, col_u32, thickness=1.5)
            
            # Compact Legend (Right aligned)
            text_w = imgui.calc_text_size(label)[0]
            draw_list.add_rect_filled(legend_x_start - text_w - 15, legend_y, legend_x_start - text_w - 5, legend_y + 10, col_u32)
            draw_list.add_text(legend_x_start - text_w, legend_y, imgui.get_color_u32_rgba(1,1,1,1), label)
            legend_y += 12

    def _draw_energy_histogram(self, w, h):
        """Draws histogram of energy values with sub-selection functionality."""
        # Reserve Layout Space
        imgui.invisible_button("hist_canvas", w, h)
        x0, y0 = imgui.get_item_rect_min()
        
        draw_list = imgui.get_window_draw_list()
        
        energies = self.energy_ef if self.show_formation_energy else self.energy_total
        if len(energies) == 0: return

        # Define bins first
        bins = 50

        # Filter NaNs for histogram
        valid_energies = energies[~np.isnan(energies)]
        if len(valid_energies) == 0:
             min_e, max_e = 0.0, 1.0
             hist = np.zeros(bins, dtype=int)
             edges = np.linspace(0, 1, bins+1)
        else:
            min_e, max_e = np.min(valid_energies), np.max(valid_energies)
            hist, edges = np.histogram(valid_energies, bins=bins, range=(min_e, max_e))

        range_e = max_e - min_e
        if range_e == 0: range_e = 1.0

        # Histogram
        max_h = np.max(hist) if np.max(hist) > 0 else 1.0
        
        # Draw Bars
        pad_bottom = 20
        pad_left = 30
        pad_top = 5
        pad_right = 5
        
        plot_x = x0 + pad_left
        plot_y = y0 + pad_top
        plot_w = w - pad_left - pad_right
        plot_h = h - pad_top - pad_bottom
        
        bin_w = plot_w / bins

        # Draw Axes Lines
        draw_list.add_line(plot_x, plot_y + plot_h, plot_x + plot_w, plot_y + plot_h, imgui.get_color_u32_rgba(1, 1, 1, 1)) # X-Axis
        draw_list.add_line(plot_x, plot_y, plot_x, plot_y + plot_h, imgui.get_color_u32_rgba(1, 1, 1, 1)) # Y-Axis
        
        # Draw Labels
        # X-Axis Min/Max
        draw_list.add_text(plot_x, plot_y + plot_h + 2, imgui.get_color_u32_rgba(1,1,1,1), f"{min_e:.1f}")
        max_label = f"{max_e:.1f}"
        max_ts = imgui.calc_text_size(max_label)[0]
        draw_list.add_text(plot_x + plot_w - max_ts, plot_y + plot_h + 2, imgui.get_color_u32_rgba(1,1,1,1), max_label)
        
        # Y-Axis Max Count
        count_label = f"{int(max_h)}"
        count_ts = imgui.calc_text_size(count_label)[0]
        draw_list.add_text(plot_x - count_ts - 5, plot_y, imgui.get_color_u32_rgba(1,1,1,1), count_label)
        draw_list.add_text(plot_x - 10, plot_y + plot_h - 10, imgui.get_color_u32_rgba(1,1,1,1), "0")

        for i, count in enumerate(hist):
            if count == 0: continue
            
            bx0 = plot_x + i * bin_w
            bx1 = bx0 + bin_w
            
            bh = (count / max_h) * plot_h
            by0 = plot_y + plot_h
            by1 = by0 - bh
            
            # Highlight if selected
            e_start = edges[i]
            e_end = edges[i+1]
            if self.hist_range[0] is not None:
                # Simple intersection check
                # If bin range overlaps selection
                s_min, s_max = self.hist_range
                is_selected = not (e_end < s_min or e_start > s_max)
                col = imgui.get_color_u32_rgba(0.2, 0.8, 1.0, 1.0) if is_selected else imgui.get_color_u32_rgba(0.2, 0.8, 1.0, 0.3)
            else:
                 col = imgui.get_color_u32_rgba(0.2, 0.8, 1.0, 1.0) # Default full color
            
            draw_list.add_rect_filled(bx0, by1, bx1, by0, col)
            
        # Draw Selection Overlay
        if self.hist_range[0] is not None:
            s_min, s_max = self.hist_range
            
            # Map E to X
            sx0 = plot_x + ((s_min - min_e) / range_e) * plot_w
            sx1 = plot_x + ((s_max - min_e) / range_e) * plot_w
            
            sx0 = max(plot_x, min(plot_x + plot_w, sx0))
            sx1 = max(plot_x, min(plot_x + plot_w, sx1))
            
            draw_list.add_rect_filled(sx0, plot_y, sx1, plot_y + plot_h, imgui.get_color_u32_rgba(1.0, 1.0, 0.2, 0.2))
            draw_list.add_line(sx0, plot_y, sx0, plot_y + plot_h, imgui.get_color_u32_rgba(1.0, 1.0, 0.2, 0.8))
            draw_list.add_line(sx1, plot_y, sx1, plot_y + plot_h, imgui.get_color_u32_rgba(1.0, 1.0, 0.2, 0.8))

        # Input Handling (Drag to select)
        if imgui.is_item_active() or imgui.is_item_hovered():
            mx, my = imgui.get_mouse_pos()
            
            # Check if within plot area (optional, but good for UX)
            if plot_x <= mx <= plot_x + plot_w and plot_y <= my <= plot_y + plot_h:
                rel_x = (mx - plot_x) / plot_w
                val_e = min_e + rel_x * range_e
                
                if imgui.is_mouse_clicked(0):
                    self.hist_start_x = val_e
                    self.hist_range = [val_e, val_e]
                    self.hist_dragging = True
                
        if self.hist_dragging:
            if imgui.is_mouse_down(0):
                mx, my = imgui.get_mouse_pos()
                # Clamp to plot
                mx = max(plot_x, min(plot_x + plot_w, mx))
                rel_x = (mx - plot_x) / plot_w
                val_e = min_e + rel_x * range_e
                
                r_min = min(self.hist_start_x, val_e)
                r_max = max(self.hist_start_x, val_e)
                self.hist_range = [r_min, r_max]
            else:
                self.hist_dragging = False

        # Clear on double click
        if imgui.is_item_hovered() and imgui.is_mouse_double_clicked(0):
             self.hist_range = [None, None]

    def _draw_energy_plot(self):
        """Draws the Energy profile graph."""
        draw_list = imgui.get_window_draw_list()
        
        # Get bounds
        p_min = imgui.get_item_rect_min()
        p_max = imgui.get_item_rect_max()
        
        # Fix: p_min/p_max can be objects in some bindings
        x0, y0 = p_min[0], p_min[1]
        w = p_max[0] - p_min[0]
        h = p_max[1] - p_min[1]
        
        # Background
        draw_list.add_rect_filled(x0, y0, x0 + w, y0 + h, imgui.get_color_u32_rgba(0, 0, 0, 0.5))
        draw_list.add_rect(x0, y0, x0 + w, y0 + h, imgui.get_color_u32_rgba(1, 1, 1, 0.3))

        energies = self.energy_ef if self.show_formation_energy else self.energy_total
        if energies is None or len(energies) == 0: return

        # Use nanmin/nanmax to handle missing energies
        if np.all(np.isnan(energies)):
            min_e, max_e = 0.0, 1.0
        else:
            min_e, max_e = np.nanmin(energies), np.nanmax(energies)
            
        range_e = max_e - min_e
        if range_e == 0: range_e = 1.0

        pad = 5
        plot_x, plot_y = x0 + pad, y0 + pad
        plot_w, plot_h = w - 2*pad, h - 2*pad

        # Map function
        def map_pt(idx, val):
            sx = plot_x + (idx / (len(energies) - 1)) * plot_w
            sy = plot_y + plot_h - ((val - min_e) / range_e) * plot_h
            return sx, sy

        # Draw Line
        # Split into segments based on selection to dim/highlight
        points = [map_pt(i, e) for i, e in enumerate(energies)]
        
        # Simple approach: Draw full line dimmed, then draw selected segment bright
        # Or just draw full line bright
        
        # Base line (dim if selection active, else bright)
        base_col = imgui.get_color_u32_rgba(0.2, 0.8, 1.0, 0.3) if self.hist_range[0] is not None else imgui.get_color_u32_rgba(0.2, 0.8, 1.0, 1.0)
        draw_list.add_polyline(points, base_col, thickness=2.0)
        
        # Highlighted points
        if self.hist_range[0] is not None:
             s_min, s_max = self.hist_range
             # Filter indices
             indices = [i for i, e in enumerate(energies) if s_min <= e <= s_max]
             
             # Draw points individually or segments? 
             # Individual circles for highlighted structures is clearer for discrete data
             for i in indices:
                 cx, cy = map_pt(i, energies[i])
                 draw_list.add_circle_filled(cx, cy, 2.0, imgui.get_color_u32_rgba(0.2, 0.8, 1.0, 1.0))

        # Draw Current Frame Marker
        e_val = energies[self.index]
        
        if not np.isnan(e_val):
            cx, cy = map_pt(self.index, e_val)
            draw_list.add_circle_filled(cx, cy, 4.0, imgui.get_color_u32_rgba(1.0, 1.0, 0.2, 1.0))
            draw_list.add_line(cx, plot_y, cx, plot_y + plot_h, imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 0.5))
            
            # Draw Energy Value Text
            text = f"E: {e_val:.4f}"
            text_w = imgui.calc_text_size(text)[0]
            
            # Position text above marker, clamp to plot bounds
            tx = cx - text_w / 2
            ty = cy - 15
            if tx < x0: tx = x0
            if tx + text_w > x0 + w: tx = x0 + w - text_w
            if ty < y0: ty = cy + 10 # If too high, flip to below
            
            draw_list.add_text(tx, ty, imgui.get_color_u32_rgba(1, 1, 0.2, 1), text)
        else:
             # Draw vertical line only? Or "N/A" text?
             # Just draw "E: N/A" at top left or similar
             draw_list.add_text(plot_x + 5, plot_y + 5, imgui.get_color_u32_rgba(1, 0.5, 0.5, 1), f"Frame {self.index}: E = N/A")


    def _render_help(self):
        if not self.show_help: return
        imgui.begin("Help & Shortcuts", True)
        imgui.text("Navigation:")
        imgui.bullet_text("Left Click + Drag: Orbit Camera")
        imgui.bullet_text("Scroll: Zoom In/Out")
        imgui.bullet_text("H: Toggle Control Panel")
        imgui.bullet_text("Esc: Quit Application")
        
        imgui.separator()
        imgui.text("Selection:")
        imgui.bullet_text("Shift + Click: Select/Deselect Atom")
        imgui.bullet_text("Checkbox 'Selection Mode': Click without Shift")
        
        imgui.separator()
        imgui.text("Playback:")
        imgui.bullet_text("Play/Pause: Toggle Animation")
        imgui.bullet_text("Speed: Adjust Frames Per Second")
        
        if imgui.button("Close"):
            self.show_help = False
        imgui.end()

    def _calc_analysis(self):
        self.avg_cn, self.cn_counts = compute_cn(self.pos, self.lat, r_cut=3.0) # Hardcoded 3.0A for now
        self.bad_x, self.bad_y = compute_bad(self.pos, self.lat, r_cut=3.0)
        self.rmsd = compute_rmsd(self.pos, self.pos_0)
        print(f"Analysis: CN={self.avg_cn:.2f}, RMSD={self.rmsd:.4f}, BAD_len={len(self.bad_x)}")
        self.show_analysis = True
        
    def _draw_cnd_plot(self):
        draw_list = imgui.get_window_draw_list()
        p_min = imgui.get_item_rect_min()
        p_max = imgui.get_item_rect_max()
        w = p_max.x - p_min.x
        h = p_max.y - p_min.y
        
        if len(self.cn_counts) == 0:
            draw_list.add_text(p_min.x + 10, p_min.y + h/2, 0xFFFFFFFF, "No Data")
            return

        # Calculate Histogram
        max_cn = int(np.max(self.cn_counts)) if len(self.cn_counts) > 0 else 0
        bins = np.arange(0, max_cn + 2) - 0.5
        hist, edges = np.histogram(self.cn_counts, bins=bins)
        
        max_val = np.max(hist) if len(hist) > 0 else 1.0
        
        # Draw Bars
        bar_width = w / len(hist)
        for i, count in enumerate(hist):
            x0 = p_min.x + i * bar_width
            x1 = x0 + bar_width - 2 # Gap
            normalized_h = count / max_val
            y0 = p_max.y
            y1 = p_max.y - normalized_h * h
            
            color = 0xFFE0E0E0 # Light Gray
            draw_list.add_rect_filled(x0, y1, x1, y0, color)
            
            # Label (CN value)
            cn_val = int(edges[i] + 0.5)
            draw_list.add_text(x0 + 2, p_max.y - 15, 0xFF000000, str(cn_val))

        # Axis Labels
        draw_list.add_text(p_min.x + w/2 - 20, p_max.y + 5, 0xFFFFFFFF, "Coordination Number")

    def _draw_bad_plot(self):
        draw_list = imgui.get_window_draw_list()
        p_min = imgui.get_item_rect_min()
        p_max = imgui.get_item_rect_max()
        x0, y0 = p_min[0], p_min[1]
        w, h = p_max[0] - p_min[0], p_max[1] - p_min[1]
        
        draw_list.add_rect_filled(x0, y0, x0 + w, y0 + h, imgui.get_color_u32_rgba(0, 0, 0, 0.5))
        draw_list.add_rect(x0, y0, x0 + w, y0 + h, imgui.get_color_u32_rgba(1, 1, 1, 0.3))
        
        if len(self.bad_x) == 0: return
        
        max_y = np.max(self.bad_y) if np.max(self.bad_y) > 0 else 1.0
        
        pad = 5
        plot_x, plot_y = x0 + pad, y0 + pad
        plot_w, plot_h = w - 2*pad, h - 2*pad
        
        points = []
        for i in range(len(self.bad_x)):
            sx = plot_x + (self.bad_x[i] / 180.0) * plot_w
            sy = plot_y + plot_h - (self.bad_y[i] / max_y) * plot_h
            points.append((sx, sy))
            
    def _draw_geometry_lines(self, view, proj):
        # Existing cell lines
        pass

    def _render_hbonds_gl(self, view, proj):
        if not self.show_hbonds or len(self.hb_pairs) == 0: return
        
        # Prepare lines data
        # We need to draw lines between pos[h] and pos[a]
        # This is dynamic, so we can use immediate mode or a dynamic VBO.
        # Given Python overhead, let's try a simple VBO approach if we can, 
        # or just simple glBegin/glEnd for now as it's easiest to implement and likely fast enough for <1000 bonds.
        # Actually, core profile doesn't support glBegin/glEnd. We MUST use VBOs.
        
        # Let's create a temporary VBO or reuse one.
        # We can reuse self.cell_vbo if we are careful, or just create a new one in init.
        # Let's create `self.hb_vao` and `self.hb_vbo` in init resources.
        
        # For now, let's just assume we have them. I'll add them to _init_resources in a separate step if needed.
        # Wait, I can't easily add to _init_resources without scrolling up.
        # I'll check if I can use a temporary buffer or just `glDrawArrays` with client memory (deprecated/slow/not core).
        # Best way: Create a VBO on the fly or update a persistent one.
        
        lines = []
        for h_idx, a_idx in self.hb_pairs:
            lines.append(self.pos[h_idx])
            lines.append(self.pos[a_idx])
        
        if not lines: return
        lines_data = np.array(lines, dtype=np.float32)
        
        if not hasattr(self, 'hb_vao'):
            self.hb_vao = glGenVertexArrays(1)
            self.hb_vbo = glGenBuffers(1)
            
        glBindVertexArray(self.hb_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.hb_vbo)
        glBufferData(GL_ARRAY_BUFFER, lines_data.nbytes, lines_data, GL_DYNAMIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        glUseProgram(self.line_prog)
        glUniformMatrix4fv(glGetUniformLocation(self.line_prog, "uView"), 1, GL_FALSE, view.T)
        glUniformMatrix4fv(glGetUniformLocation(self.line_prog, "uProj"), 1, GL_FALSE, proj.T)
        glUniform4f(glGetUniformLocation(self.line_prog, "uRGBA"), 1, 1, 0, 0.8) # Yellow
        
        # Identity for model matrix (lines are in world space)
        # But wait, line_prog uses uReplicaOffsets?
        # If I use line_prog, I need to handle uReplicaOffsets.
        # If I pass 0 for uReplicaOffsets, it might work if the shader handles it.
        # Let's check line shader. It likely adds offset.
        # I should bind a zero-offset buffer or just disable instancing.
        # Actually, H-bonds should probably be replicated too? 
        # If I want them replicated, I use the same instancing.
        # If not, I draw once. Let's draw once for now (primary cell).
        
        # Bind a zero buffer for replicas or just use a different shader?
        # Re-using line_prog is risky if it expects instancing.
        # Let's look at line shader.
        # It probably does: pos = pos + offset.
        # So I can just bind the existing replica buffer and draw instanced!
        # That way H-bonds appear in all replicas. Cool.
        
        glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_BUFFER, self.rep_tbo)
        glUniform1i(glGetUniformLocation(self.line_prog, "uReplicaOffsets"), 0)
        
        glDrawArraysInstanced(GL_LINES, 0, len(lines), len(self.replica_offsets))
        
        glBindVertexArray(0)

    def _calc_hbonds(self):
        self.hb_dists, self.hb_pairs = compute_hbonds(self.pos, self.elements, self.lat, 
                                                      d_ha_cut=self.hb_dist_cut, 
                                                      angle_cut=self.hb_angle_cut)
        print(f"H-Bonds found: {len(self.hb_dists)}")
        self.show_hbonds = True

    def _draw_hbond_plot(self):
        if not self.show_hbonds: return
        
        imgui.begin("Hydrogen Bond Distribution", True)
        if len(self.hb_dists) == 0:
            imgui.text("No Hydrogen Bonds detected.")
        else:
            imgui.text(f"Count: {len(self.hb_dists)}")
            imgui.text(f"Mean Dist: {np.mean(self.hb_dists):.3f} A")
            
            # Histogram
            hist, edges = np.histogram(self.hb_dists, bins=20, range=(1.5, 3.0))
            
            # Plot Histogram
            imgui.plot_histogram("##hb_hist", hist.astype(np.float32), graph_size=(300, 150), 
                                 scale_min=0, scale_max=np.max(hist)*1.1, 
                                 overlay_text=f"Min: {edges[0]:.1f} A, Max: {edges[-1]:.1f} A")
            
            # X-Axis Labels (Manual)
            p_min = imgui.get_item_rect_min()
            p_max = imgui.get_item_rect_max()
            w = p_max.x - p_min.x
            draw_list = imgui.get_window_draw_list()
            
            # Draw labels at start, middle, end
            draw_list.add_text(p_min.x, p_max.y + 2, 0xFFFFFFFF, "1.5")
            draw_list.add_text(p_min.x + w/2 - 10, p_max.y + 2, 0xFFFFFFFF, "2.25")
            draw_list.add_text(p_max.x - 20, p_max.y + 2, 0xFFFFFFFF, "3.0")
            
            imgui.dummy(0, 20) # Spacing for labels
            imgui.text("X: H...A Distance (Angstroms)")
            
            # Interactive Hover
            if imgui.is_item_hovered():
                m_x, m_y = imgui.get_mouse_pos()
                rel_x = (m_x - p_min.x) / w
                if 0 <= rel_x <= 1:
                    bin_idx = int(rel_x * len(hist))
                    if 0 <= bin_idx < len(hist):
                        imgui.set_tooltip(f"Range: {edges[bin_idx]:.2f}-{edges[bin_idx+1]:.2f} A\nCount: {hist[bin_idx]}")

        imgui.end()

    def _update_color_by_cn(self):
        if len(self.coord_counts) == 0: return
        
        # Map CN to Color (Blue -> Red)
        # Normalize CN
        max_cn = np.max(self.coord_counts)
        min_cn = np.min(self.coord_counts)
        rng = max_cn - min_cn if max_cn > min_cn else 1.0
        
        colors = []
        for cn in self.coord_counts:
            t = (cn - min_cn) / rng
            # Simple Blue (0,0,1) to Red (1,0,0) interpolation
            # Or Viridis-like: Blue -> Green -> Yellow -> Red
            # Let's do Blue -> Red for simplicity
            r = t
            g = 0.0
            b = 1.0 - t
            colors.append((r, g, b, 1.0))
            
        # Update TBO
        data = np.array(colors, dtype=np.float32).flatten()
        glBindBuffer(GL_TEXTURE_BUFFER, self.col_bo)
        glBufferSubData(GL_TEXTURE_BUFFER, 0, data.nbytes, data)
        glBindBuffer(GL_TEXTURE_BUFFER, 0)

    def _calc_coord_sphere(self):
        avg, self.coord_counts, self.coord_avg_bond_len = compute_coordination_sphere(self.pos, self.elements, self.lat, factor=self.coord_factor)
        print(f"Avg Coord Sphere CN: {avg:.2f}")
        self.show_coord_sphere = True
        
        if self.color_by_cn:
            self._update_color_by_cn()
        else:
            # Revert to CPK if needed, but we don't store original CPK in a separate array easily accessible here 
            # without re-generating it.
            # Ideally we should store cpk_colors in self.cpk_data and upload it.
            # For now, let's just call _upload_atom_tbos() which re-generates everything (pos and color).
            # But wait, _upload_atom_tbos uses self.pos and self.elements.
            self._upload_atom_tbos()

    def _draw_coord_sphere_plot(self):
        if not self.show_coord_sphere or len(self.coord_counts) == 0: return
        
        imgui.begin("Coordination Sphere Distribution", True)
        imgui.text(f"Factor: {self.coord_factor:.2f}")
        imgui.text(f"Avg CN: {np.mean(self.coord_counts):.2f}")
        imgui.text(f"Avg Bond Len: {self.coord_avg_bond_len:.3f} A")
        
        imgui.separator()
        
        # Statistics Table
        imgui.columns(3, "##cn_stats")
        imgui.separator()
        imgui.text("CN"); imgui.next_column()
        imgui.text("Count"); imgui.next_column()
        imgui.text("Percent"); imgui.next_column()
        imgui.separator()
        
        counts = np.bincount(self.coord_counts)
        total = len(self.coord_counts)
        
        for cn, count in enumerate(counts):
            if count > 0:
                imgui.text(str(cn)); imgui.next_column()
                imgui.text(str(count)); imgui.next_column()
                imgui.text(f"{count/total*100:.1f}%"); imgui.next_column()
        
        imgui.columns(1)
        imgui.separator()
        
        # Histogram of counts (integers)
        if len(self.coord_counts) > 0:
            max_c = int(np.max(self.coord_counts))
            min_c = int(np.min(self.coord_counts))
            bins = max_c - min_c + 1
            if bins < 1: bins = 1
            
            hist, edges = np.histogram(self.coord_counts, bins=bins, range=(min_c, max_c + 1))
            
            imgui.plot_histogram("##cs_hist", hist.astype(np.float32), graph_size=(300, 150),
                                 scale_min=0, scale_max=np.max(hist)*1.1,
                                 overlay_text=f"Min: {min_c}, Max: {max_c}")
                                 
            # X-Axis Labels
            p_min = imgui.get_item_rect_min()
            p_max = imgui.get_item_rect_max()
            w = p_max.x - p_min.x
            draw_list = imgui.get_window_draw_list()
            
            draw_list.add_text(p_min.x, p_max.y + 2, 0xFFFFFFFF, str(min_c))
            draw_list.add_text(p_max.x - 20, p_max.y + 2, 0xFFFFFFFF, str(max_c))
            
            imgui.dummy(0, 20)
            imgui.text("X: Coordination Number")
            
            # Tooltip
            if imgui.is_item_hovered():
                m_x, m_y = imgui.get_mouse_pos()
                rel_x = (m_x - p_min.x) / w
                if 0 <= rel_x <= 1:
                    bin_idx = int(rel_x * len(hist))
                    if 0 <= bin_idx < len(hist):
                        val = min_c + bin_idx
                        imgui.set_tooltip(f"CN: {val}\nCount: {hist[bin_idx]}")
                    
        imgui.end()

    def _center_camera(self):
        """Centers the camera on the geometric center of atoms."""
        if self.N > 0:
            center = np.mean(self.pos, axis=0)
            self.cam.center = center.astype(np.float32)
            self.cam.pan = np.zeros(2, dtype=np.float32) # Reset pan

            self.bonds = []
            
        # Re-calc bonds if enabled (or always?) 
        # Better to do it lazily or on demand? For now, do it here if enabled, or just always for valid cache?
        # Doing it always for small N is cheap.
        if self.show_bonds:
            self._calc_bonds()

    def _calc_bonds(self):
        """Calculates bonds based on atomic radii heuristics using cKDTree."""
        if self.N == 0: 
            self.bonds = []
            self.bond_count = 0
            return

        # Prepare Data
        # Heuristic: Bond if dist < (r1 + r2) * 1.15
        # Since r varies, we can't use fixed radius query easily without a max bound.
        # Max atomic radius is ~2.5 Å? Max bond len maybe 4.0 Å?
        max_bond_dist = 4.0 
        
        # Build Tree
        # Handle PBC? self.lat is available.
        box = np.diag(self.lat) if self.lat is not None else None
        # Check if orthogonal box for cKDTree
        # cKDTree boxsize argument supports orthogonal only.
        # If triclinic, we should map to orthogonal or use supercell query.
        # For simple visualizer, we might ignore PBC bonds for now or use naive N^2 if N is small.
        # If N > 1000, N^2 is slow.
        # Let's assume non-PBC for visualization or simple cut.
        
        if HAS_SCIPY:
            tree = cKDTree(self.pos)
            # Query pairs within max_bond_dist
            pairs = tree.query_pairs(max_bond_dist)
            
            valid_bonds = []
            for i, j in pairs:
                p1 = self.pos[i]
                p2 = self.pos[j]
                d = np.linalg.norm(p1 - p2)
                
                r1 = self.radii[i]
                r2 = self.radii[j]
                cutoff = (r1 + r2) * self.bond_cutoff_factor
                
                if d < cutoff:
                    valid_bonds.append((i, j))
            self.bonds = valid_bonds
            self.bond_count = len(self.bonds)
        else:
            # Fallback N^2
            self.bonds = []
            for i in range(self.N):
                for j in range(i + 1, self.N):
                    d = np.linalg.norm(self.pos[i] - self.pos[j])
                    if d < (self.radii[i] + self.radii[j]) * self.bond_cutoff_factor:
                        self.bonds.append((i, j))
            self.bond_count = len(self.bonds)

    def _draw_bonds(self, view, proj):
        if not self.bonds or self.bond_count == 0: return
        
        # Prepare Instance Buffer
        # Each bond (i, j) becomes TWO cylinder instances
        # 1. i -> mid, color i
        # 2. j -> mid, color j
        
        # Structure of instance data: [Start(3), End(3), Color(3)] = 9 floats
        
        # We can construct this numpy array each frame or cache it?
        # Construct once per calc_bonds is better.
        # So we should update _calc_bonds to also produce this buffer or do it here.
        # Doing it here allows dynamic color updates logic (if we changed colors dynamically).
        # Let's do it here for simplicity.
        
        # Data size: N_bonds * 2 instances * 9 floats * 4 bytes
        # 1000 bonds -> 72KB per frame. OK.
        
        data = np.zeros((self.bond_count * 2, 9), dtype=np.float32)
        
        # Vectorize?
        # bond_indices = np.array(self.bonds) # (M, 2)
        # i_idxs = bond_indices[:, 0]
        # j_idxs = bond_indices[:, 1]
        
        # P_i = self.pos[i_idxs]
        # P_j = self.pos[j_idxs]
        # C_i = self.colors[i_idxs]
        # C_j = self.colors[j_idxs]
        
        # Mid = (P_i + P_j) * 0.5
        
        # Inst 1: P_i -> Mid, C_i
        # Inst 2: P_j -> Mid, C_j
        
        # Optimization
        if self.bond_count > 0:
            b_idxs = np.array(self.bonds)
            i_s = b_idxs[:, 0]
            j_s = b_idxs[:, 1]
            
            pos_i = self.pos[i_s]
            pos_j = self.pos[j_s]
            col_i = self.colors[i_s]
            col_j = self.colors[j_s]
            
            mids = (pos_i + pos_j) * 0.5
            
            # Fill Data
            # First half: i -> mid
            n = self.bond_count
            data[:n, 0:3] = pos_i
            data[:n, 3:6] = mids
            data[:n, 6:9] = col_i
            
            # Second half: j -> mid
            data[n:, 0:3] = pos_j
            data[n:, 3:6] = mids
            data[n:, 6:9] = col_j

        glBindBuffer(GL_ARRAY_BUFFER, self.bond_inst_vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STREAM_DRAW)
        
        glUseProgram(self.cylinder_prog)
        glUniformMatrix4fv(glGetUniformLocation(self.cylinder_prog, "uView"), 1, GL_FALSE, view.T)
        glUniformMatrix4fv(glGetUniformLocation(self.cylinder_prog, "uProj"), 1, GL_FALSE, proj.T)
        glUniform1f(glGetUniformLocation(self.cylinder_prog, "uBondScale"), self.bond_scale * self.atom_scale) # Scale relative to atoms? Or absolute? User slider.
        glUniform1i(glGetUniformLocation(self.cylinder_prog, "uReplicaOffsets"), 2) 
        glUniform1i(glGetUniformLocation(self.cylinder_prog, "uBondCount"), self.bond_count * 2) 
        
        # Bind Instance Attributes
        glBindVertexArray(self.bond_vao)
        
        # Bind Mesh VBO/EBO
        glBindBuffer(GL_ARRAY_BUFFER, self.cyl_vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.cyl_ebo)
        
        # Mesh Attribs (0: Pos, 1: Normal)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6*4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6*4, ctypes.c_void_p(3*4))
        
        # Instance Attribs (2: Start, 3: End, 4: Color)
        glBindBuffer(GL_ARRAY_BUFFER, self.bond_inst_vbo)
        
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9*4, ctypes.c_void_p(0))
        glVertexAttribDivisor(2, 1)
        
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 9*4, ctypes.c_void_p(3*4))
        glVertexAttribDivisor(3, 1)
        
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 9*4, ctypes.c_void_p(6*4))
        glVertexAttribDivisor(4, 1)
        
        # Draw
        # We are drawing (bond_count * 2) instances.
        glDrawElementsInstanced(GL_TRIANGLES, self.cyl_idx_count, GL_UNSIGNED_INT, None, self.bond_count * 2)
        
        # Cleanup
        glVertexAttribDivisor(2, 0)
        glVertexAttribDivisor(3, 0)
        glVertexAttribDivisor(4, 0)
        glBindVertexArray(0)

    def _select_atoms_in_box(self, start, end):

        """Selects atoms whose screen projection falls within the box defined by start and end."""
        # Use Window Size for coordinate mapping (matches cursor pos), NOT framebuffer size
        w, h = glfw.get_window_size(self.win)
        view, proj = self._get_matrices(w, h)
        
        # Determine Box Bounds
        x_min, x_max = min(start[0], end[0]), max(start[0], end[0])
        y_min, y_max = min(start[1], end[1]), max(start[1], end[1])
        
        # Project all atoms
        # Vectorized projection
        # P_world: (N, 4)
        ones = np.ones((self.N, 1), dtype=np.float32)
        P_world = np.hstack([self.pos, ones])
        
        # P_eye = P_world @ View.T
        P_eye = P_world @ view.T
        
        # P_clip = P_eye @ Proj.T
        P_clip = P_eye @ proj.T
        
        # NDC = P_clip / w
        # Handle w=0 case (shouldn't happen for points in frustum)
        w_coord = P_clip[:, 3:4]
        # Avoid division by zero
        mask_valid = np.abs(w_coord) > 1e-6
        # Start with all false
        mask_in_box = np.zeros(self.N, dtype=bool)
        
        # Only process valid points
        valid_indices = np.where(mask_valid.flatten())[0]
        if len(valid_indices) > 0:
            ndc = P_clip[valid_indices] / w_coord[valid_indices]
            
            # Map to Screen
            # x_screen = (ndc.x + 1) * 0.5 * w
            # y_screen = (1 - ndc.y) * 0.5 * h  <-- Flip Y for Screen Coords (Top-Left 0,0)
            
            x_screen = (ndc[:, 0] + 1.0) * 0.5 * w
            y_screen = (1.0 - ndc[:, 1]) * 0.5 * h
            
            # Check Bounds
            in_x = (x_screen >= x_min) & (x_screen <= x_max)
            in_y = (y_screen >= y_min) & (y_screen <= y_max)
            in_d = (ndc[:, 2] >= -1.0) & (ndc[:, 2] <= 1.0) # Within Frustum depth
            
            mask_in_box[valid_indices] = in_x & in_y & in_d
        
        # Update Selection
        # If Shift is held, we are adding/toggling? Usually box select is additive or replaces.
        # Let's make it additive for now since it's Shift.
        # Or better: Add unique items.
        
        new_selection = list(np.where(mask_in_box)[0])
        
        # Add to existing selection, avoid duplicates
        current_set = set(self.selected_atoms)
        for idx in new_selection:
            if idx not in current_set:
                self.selected_atoms.append(int(idx))

    def _render_gui(self):
        self.impl.process_inputs()
        imgui.new_frame()
        
        
        # Draw Selection Box Overlay
        if self.box_selecting and self.box_start and self.box_end:
            fg_dl = imgui.get_foreground_draw_list()
            # Normalize min/max
            x1, y1 = self.box_start
            x2, y2 = self.box_end
            fg_dl.add_rect_filled(min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2), imgui.get_color_u32_rgba(0.2, 0.8, 1.0, 0.3))
            fg_dl.add_rect(min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2), imgui.get_color_u32_rgba(0.2, 0.8, 1.0, 0.8))
        
        if self.show_gui:
            imgui.begin("Control Panel", True)
            
            # Show Permanent Error Message if present
            if self.last_error:
                imgui.text_colored("ERROR LOADING FRAME:", 1.0, 0.4, 0.4, 1.0)
                imgui.text_colored(self.last_error, 1.0, 0.6, 0.6, 1.0)
                imgui.separator()
            
            imgui.text(f"Struct: {self.index} | Atoms: {self.N}")
            imgui.same_line()
            imgui.text(f"| FPS: {imgui.get_io().framerate:.1f}")
            imgui.same_line()
            imgui.text(f"| Comp: {self.composition_str}")
            imgui.same_line()
            if imgui.button("?"): self.show_help = not self.show_help
            
            # Playback Controls
            if imgui.button("Pause" if self.playing else "Play"):
                self.playing = not self.playing
            imgui.same_line()
            if imgui.button(">>"): self._load_index(self.index + 1)
            
            changed, new_index = imgui.slider_int("Frame", self.index, 0, len(self.provider) - 1)
            if changed:
                self._load_index(new_index)
            
            changed, self.playback_speed = imgui.drag_float("Speed (fps)", self.playback_speed, 0.1, 0.1, 60.0)
            
            if imgui.button("Take Screenshot"):
                import time
                ts = int(time.time())
                self.save_screenshot(f"screenshot_{ts}.ppm")
            
            imgui.same_line()
            if imgui.button("Save GIF"):
                self.save_gif("animation.gif")

            changed, self.replicas = imgui.drag_int3("Replicas", *self.replicas, 0.1, 0, 10)

            if changed: self._rebuild_replica_offsets()
            
            # Wrap Feature
            changed, self.auto_wrap = imgui.checkbox("Auto Wrap", self.auto_wrap)
            if changed and self.auto_wrap:
                 # Apply immediately to current frame
                 self._load_index(self.index)
            
            # Energy Controls
            if imgui.collapsing_header("Energy Analysis", visible=True)[0]:
                if imgui.button(f"Mode: {'Formation Energy (Ef)' if self.show_formation_energy else 'Total Energy (E)'}"):
                    self.show_formation_energy = not self.show_formation_energy
                    # Reset histogram selection on mode switch
                    self.hist_range = [None, None]
                
                imgui.same_line()
                if imgui.button("Recalc"):
                    # Recalculate Formation Energy
                    self.energy_ef = np.array(self.provider.get_all_Ef(), dtype=np.float32)
                    if hasattr(self.provider, 'get_all_E'):
                        self.energy_total = np.array(self.provider.get_all_E(), dtype=np.float32)
                    else:
                        self.energy_total = self.energy_ef.copy()
                
                avail_w = imgui.get_content_region_available_width()
                imgui.invisible_button("energy_plot", avail_w, 60)
                self._draw_energy_plot()
                
                
                # Histogram
                # Self-contained histogram widget
                self._draw_energy_histogram(avail_w, 100)
                
                # Filtered Navigation
                
                # Filtered Navigation
                if self.hist_range[0] is not None:
                    filtered_indices = self._get_filtered_indices()
                    if filtered_indices:
                        current_idx = self.index
                        # Find position in filtered list
                        try:
                           f_ptr = filtered_indices.index(current_idx)
                        except ValueError:
                           f_ptr = 0
                           
                        changed, new_f_ptr = imgui.slider_int(f"Filtered Frame ({len(filtered_indices)})", f_ptr, 0, len(filtered_indices)-1)
                        if changed:
                            self._load_index(filtered_indices[new_f_ptr])
                        
                        if imgui.button("< Filtered"):
                            new_f_ptr = (f_ptr - 1) % len(filtered_indices)
                            self._load_index(filtered_indices[new_f_ptr])
                        imgui.same_line()
                        if imgui.button("Filtered >"):
                            new_f_ptr = (f_ptr + 1) % len(filtered_indices)
                            self._load_index(filtered_indices[new_f_ptr])
            
            # Camera Controls
            if imgui.collapsing_header("Camera & Projection")[0]:
                
                # Appearance Config (moved here or separate?)
                imgui.text("Appearance")
                changed, self.atom_scale = imgui.slider_float("Atom Scale", self.atom_scale, 0.1, 3.0)
                
                changed_b, self.show_bonds = imgui.checkbox("Show Bonds", self.show_bonds)
                if changed_b and self.show_bonds:
                     self._calc_bonds() # Calc on enable
                     
                if self.show_bonds:
                    imgui.indent()
                    changed, self.bond_scale = imgui.slider_float("Bond Thickness", self.bond_scale, 0.05, 1.0)
                    changed_f, self.bond_cutoff_factor = imgui.slider_float("Connection Factor", self.bond_cutoff_factor, 0.5, 2.0)
                    if changed_f:
                        self._calc_bonds()
                    imgui.unindent()
                
                # Add Keep View checkbox here
                clicked, self.is_ortho = imgui.checkbox("Orthographic Mode", self.is_ortho)
                clicked_kv, self.keep_view = imgui.checkbox("Keep View", self.keep_view)
                
                if self.is_ortho:
                    if imgui.button("Snap Isometric (Standard)"):
                        self.cam.snap_isometric()
                    changed, self.cam.ortho_scale = imgui.drag_float("Ortho Zoom", self.cam.ortho_scale, 0.5, 1.0, 500.0)
                else:
                    imgui.text("Standard Perspective (Scroll to Zoom)")

                # Center Camera
                if imgui.button("Center Camera (COM)"):
                    self._center_camera()

            imgui.separator()
            
            imgui.separator()
            if imgui.collapsing_header("Radial Distribution Function (RDF)")[0]:
                # RDF Parameters
                imgui.text("Parameters:")
                changed_r, self.rdf_rmax = imgui.slider_float("R Max (A)", self.rdf_rmax, 2.0, 15.0)
                changed_b, self.rdf_bins = imgui.slider_int("Bins", self.rdf_bins, 50, 500)
                
                if (changed_r or changed_b) and self.show_rdf:
                    self._calc_rdf_current()

                if imgui.button("Calculate RDF"):
                    self.show_rdf = True
                    self._calc_rdf_current()
                    
                if self.show_rdf:
                    imgui.separator()
                    avail_w = imgui.get_content_region_available_width()
                    plot_h = 150 # More compact height
                    
                    # Reserve space and draw
                    imgui.invisible_button("canvas", avail_w, plot_h)
                    self._draw_rdf_plot()
            
            imgui.separator()
            imgui.separator()
            if imgui.collapsing_header("Other Analysis Tools")[0]:
                if imgui.tree_node("Structure Analysis (CN & BAD)"):
                    if imgui.button("Run Analysis"):
                        self._calc_analysis()
                    
                    if hasattr(self, 'show_analysis') and self.show_analysis:
                        imgui.text(f"Avg CN (r<3.0A): {self.avg_cn:.2f}")
                        imgui.text("Coordination Number Distribution:")
                        avail_w = imgui.get_content_region_available_width()
                        imgui.invisible_button("cnd_plot", avail_w, 100)
                        self._draw_cnd_plot()
                        
                        imgui.text("Bond Angle Distribution:")
                        avail_w = imgui.get_content_region_available_width()
                        imgui.invisible_button("bad_plot", avail_w, 100)
                        self._draw_bad_plot()
                    imgui.tree_pop()
                
                if imgui.tree_node("Hydrogen Bonds"):
                    imgui.text("Cutoffs:")
                    changed_d, self.hb_dist_cut = imgui.slider_float("Dist (A)", self.hb_dist_cut, 1.5, 4.0)
                    changed_a, self.hb_angle_cut = imgui.slider_float("Angle (deg)", self.hb_angle_cut, 90.0, 180.0)
                    
                    if (changed_d or changed_a) and self.show_hbonds:
                        self._calc_hbonds()

                    if imgui.button("Run H-Bond Analysis"):
                        self._calc_hbonds()
                    
                    self._draw_hbond_plot()
                    imgui.tree_pop()
                
                
                if imgui.tree_node("Coordination Sphere"):
                    changed_c, self.coord_factor = imgui.slider_float("Coord Factor", self.coord_factor, 0.5, 2.0)
                    
                    changed_col, self.color_by_cn = imgui.checkbox("Color by CN", self.color_by_cn)
                    
                    if (changed_c or changed_col) and self.show_coord_sphere:
                        self._calc_coord_sphere()
                        
                    if imgui.button("Run Coord. Sphere Analysis"):
                        self._calc_coord_sphere()
                        
                    self._draw_coord_sphere_plot()
                    imgui.tree_pop()
            
            imgui.separator()
            if imgui.collapsing_header("Export")[0]:
                changed, self.export_filename = imgui.input_text("Filename", self.export_filename, 512)
                
                if imgui.button("Export Current (XYZ)"):
                    self._export_current_xyz(f"{self.export_filename}_{self.index}.xyz")
                    
                imgui.same_line()
                if imgui.button("Export All (Partition)"):
                    if hasattr(self.provider, 'p') and hasattr(self.provider.p, 'export_files'):
                        self.provider.p.export_files(self.export_filename)
                        print(f"Exported all files with prefix: {self.export_filename}")
                        self.export_status_msg = f"Exported ALL: {self.export_filename}*"
                        self.export_status_time = glfw.get_time() + 3.0
                    else:
                        print("Export All not supported: Provider has no underlying partition with export_files()")
                        self.export_status_msg = "Export All Not Supported"
                        self.export_status_time = glfw.get_time() + 3.0
                
                # Show Status Message
                if glfw.get_time() < self.export_status_time:
                    imgui.text_colored(self.export_status_msg, 0.2, 1.0, 0.2, 1.0)

            imgui.end()
            
            self._render_help()

            # Selection Info
            if self.selected_atoms:
                imgui.begin("Selection Info")
                imgui.text(f"Selected: {len(self.selected_atoms)}")
                
                # Selected Composition
                from collections import Counter
                s_elements = [self.elements[i] for i in self.selected_atoms if i < len(self.elements)]
                if s_elements:
                    s_counts = Counter(s_elements)
                    s_comp = " ".join([f"{k}{v}" for k, v in sorted(s_counts.items())])
                    imgui.text(f"Sel Comp: {s_comp}")
                
                if len(self.selected_atoms) >= 2:
                    d = np.linalg.norm(self.pos[self.selected_atoms[-1]] - self.pos[self.selected_atoms[-2]])
                    imgui.text(f"Distance: {d:.4f} A")
                if len(self.selected_atoms) >= 3:
                    p3, p2, p1 = [self.pos[i] for i in self.selected_atoms[-3:]]
                    ang = compute_angle(p1, p2, p3)
                    imgui.text(f"Angle: {ang:.2f} deg")
                if len(self.selected_atoms) >= 4:
                    p4, p3, p2, p1 = [self.pos[i] for i in self.selected_atoms[-4:]]
                    dih = compute_dihedral(p1, p2, p3, p4)
                    imgui.text(f"Dihedral (Last 4): {dih:.2f} deg")
                    
                if imgui.button("Clear Selection"):
                    self.selected_atoms = []
                    self._upload_atom_tbos()
                
                imgui.separator()
                imgui.text("Selected Atoms Table:")
                
                # Table configuration
                if imgui.begin_table("SelectionTable", 6, imgui.TABLE_SCROLL_Y | imgui.TABLE_BORDERS_OUTER, outer_size_height=200):
                    imgui.table_setup_scroll_freeze(0, 1) # Make top row always visible
                    imgui.table_setup_column("Idx", imgui.TABLE_COLUMN_WIDTH_FIXED, 30)
                    imgui.table_setup_column("ID", imgui.TABLE_COLUMN_WIDTH_FIXED, 40)
                    imgui.table_setup_column("El", imgui.TABLE_COLUMN_WIDTH_FIXED, 30)
                    imgui.table_setup_column("X", imgui.TABLE_COLUMN_WIDTH_STRETCH)
                    imgui.table_setup_column("Y", imgui.TABLE_COLUMN_WIDTH_STRETCH)
                    imgui.table_setup_column("Z", imgui.TABLE_COLUMN_WIDTH_STRETCH)
                    imgui.table_headers_row()
                    
                    for i, atom_idx in enumerate(self.selected_atoms):
                        imgui.table_next_row()
                        imgui.table_set_column_index(0)
                        imgui.text(str(i + 1))
                        
                        imgui.table_set_column_index(1)
                        imgui.text(str(atom_idx))
                        
                        imgui.table_set_column_index(2)
                        el = self.elements[atom_idx] if atom_idx < len(self.elements) else "?"
                        imgui.text(el)
                        
                        pos = self.pos[atom_idx]
                        imgui.table_set_column_index(3)
                        imgui.text(f"{pos[0]:.3f}")
                        
                        imgui.table_set_column_index(4)
                        imgui.text(f"{pos[1]:.3f}")
                        
                        imgui.table_set_column_index(5)
                        imgui.text(f"{pos[2]:.3f}")
                        
                    imgui.end_table()

                imgui.separator()
                imgui.text("Measurements:")
                if len(self.selected_atoms) >= 2:
                    idx1, idx2 = self.selected_atoms[-2], self.selected_atoms[-1]
                    d = np.linalg.norm(self.pos[idx1] - self.pos[idx2])
                    imgui.bullet_text(f"Dist ({idx1}-{idx2}): {d:.4f} A")
                    
                if len(self.selected_atoms) >= 3:
                    idx1, idx2, idx3 = self.selected_atoms[-3], self.selected_atoms[-2], self.selected_atoms[-1]
                    p1, p2, p3 = self.pos[idx1], self.pos[idx2], self.pos[idx3]
                    ang = compute_angle(p1, p2, p3)
                    imgui.bullet_text(f"Angle ({idx1}-{idx2}-{idx3}): {ang:.2f} deg")
                    
                if len(self.selected_atoms) >= 4:
                    idx1, idx2, idx3, idx4 = self.selected_atoms[-4], self.selected_atoms[-3], self.selected_atoms[-2], self.selected_atoms[-1]
                    p1, p2, p3, p4 = self.pos[idx1], self.pos[idx2], self.pos[idx3], self.pos[idx4]
                    dih = compute_dihedral(p1, p2, p3, p4)
                    imgui.bullet_text(f"Dihedral ({idx1}-{idx2}-{idx3}-{idx4}): {dih:.2f} deg")

                imgui.end()
        
        # Draw 3D Selection Labels (Indices)
        if self.selected_atoms:
             # We need view/proj matrices. We can re-calculate or store them. 
             # _get_matrices is cheap.
             w, h = glfw.get_framebuffer_size(self.win)
             win_w, win_h = glfw.get_window_size(self.win)
             view, proj = self._get_matrices(w, h)
             self._draw_selection_labels(view, proj, win_w, win_h)
        
        imgui.render()
        self.impl.render(imgui.get_draw_data())

    def _draw_selection_labels(self, view, proj, w, h):
        """Draws selection indices (1, 2, 3...) on top of selected atoms."""
        # Use foreground draw list to ensure it's on top of everything
        draw_list = imgui.get_foreground_draw_list()
        
        vp_mat = np.matmul(proj, view)

        
        for i, atom_idx in enumerate(self.selected_atoms):
            pos = self.pos[atom_idx]
            # Add radius to z (up) to float label slightly above atom? 
            # Or just center. Center is better for tracking.
            # pos_w = pos + np.array([0, 0, self.radii[atom_idx]], dtype=np.float32)
            
            # Project to Clip Space
            p4 = np.matmul(vp_mat, np.append(pos, 1.0))
            
            if p4[3] > 0: # In front of camera
                ndc_x = p4[0] / p4[3]
                ndc_y = p4[1] / p4[3]
                
                # Viewport Transform (OpenGL: (-1,-1) bottom-left to (1,1) top-right)
                # ImGui: (0,0) top-left
                screen_x = (ndc_x * 0.5 + 0.5) * w
                screen_y = (1.0 - (ndc_y * 0.5 + 0.5)) * h
                
                # Check bounds roughly (though ImGui clips)
                # if 0 <= screen_x <= w and 0 <= screen_y <= h:
                
                label = f"{i + 1}: {atom_idx}"
                text_w = imgui.calc_text_size(label)[0]
                
                # Draw black background text shadow for contrast
                draw_list.add_text(screen_x - text_w/2 + 1, screen_y - 7 + 1, imgui.get_color_u32_rgba(0, 0, 0, 1), label)
                # Center text
                draw_list.add_text(screen_x - text_w/2, screen_y - 7, imgui.get_color_u32_rgba(1, 1, 1, 1), label)

    def _pick_atom(self, x, y):
        w, h = glfw.get_framebuffer_size(self.win)
        win_w, win_h = glfw.get_window_size(self.win)
        
        # Handle Retina / High-DPI scaling
        pixel_ratio = w / win_w if win_w > 0 else 1.0
        x *= pixel_ratio
        y *= pixel_ratio
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        view, proj = self._get_matrices(w, h)
        glUseProgram(self.pick_prog)
        glUniformMatrix4fv(glGetUniformLocation(self.pick_prog, "uView"), 1, GL_FALSE, view.T)
        glUniformMatrix4fv(glGetUniformLocation(self.pick_prog, "uProj"), 1, GL_FALSE, proj.T)
        glUniform1i(glGetUniformLocation(self.pick_prog, "uAtomCount"), self.N)
        glUniform1i(glGetUniformLocation(self.pick_prog, "uIsOrtho"), 1 if self.is_ortho else 0)
        glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_BUFFER, self.pr_tbo)
        glActiveTexture(GL_TEXTURE1); glBindTexture(GL_TEXTURE_BUFFER, self.rep_tbo)
        glUniform1i(glGetUniformLocation(self.pick_prog, "uAtomPosRad"), 0)
        glUniform1i(glGetUniformLocation(self.pick_prog, "uReplicaOffsets"), 1)
        glBindVertexArray(self.quad_vao)
        glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, 4, self.N * len(self.replica_offsets))
        
        px = glReadPixels(int(x), int(h - y), 1, 1, GL_RGB, GL_UNSIGNED_BYTE)
        id_px = np.frombuffer(px, dtype=np.uint8)
        if id_px.size == 3:
            idx = int(id_px[0]) + (int(id_px[1]) << 8) + (int(id_px[2]) << 16)
            return idx if idx < self.N else None
        return None

    def _on_scroll(self, win, dx, dy):
        if imgui.get_io().want_capture_mouse: return
        factor = 0.9 if dy > 0 else 1.1
        if self.is_ortho: self.cam.ortho_scale *= factor
        else: self.cam.offset *= factor

    def _on_mouse_button(self, win, btn, act, mods):
        if imgui.get_io().want_capture_mouse: return
        if btn == glfw.MOUSE_BUTTON_LEFT:
            if act == glfw.PRESS:
                # Panning: Ctrl + Click
                if (mods & glfw.MOD_CONTROL):
                    self.panning = True
                # Selection: Shift + Click (Box or Single)
                elif (mods & glfw.MOD_SHIFT):
                    x, y = glfw.get_cursor_pos(win)
                    self.box_selecting = True
                    self.box_start = (x, y)
                    self.box_end = (x, y)
                # Orbit: Normal Click
                else:
                    self.orbiting = True
            elif act == glfw.RELEASE:
                if self.box_selecting:
                    # Finish Box Select
                    x, y = glfw.get_cursor_pos(win)
                    self.box_end = (x, y)
                    self.box_selecting = False
                    
                    # Check drag distance
                    dist = np.linalg.norm(np.array(self.box_end) - np.array(self.box_start))
                    if dist < 5.0:
                        # Treating as Single Click
                        idx = self._pick_atom(int(x), int(y))
                        if idx is not None:
                            if idx in self.selected_atoms: self.selected_atoms.remove(idx)
                            else: self.selected_atoms.append(idx)
                    else:
                        # Treating as Box Select
                        self._select_atoms_in_box(self.box_start, self.box_end)
                    
                    self._upload_atom_tbos()
                    
                self.orbiting = False
                self.panning = False

    def _on_mouse_move(self, win, x, y):
        if imgui.get_io().want_capture_mouse: return
        if self.last_x is None: self.last_x, self.last_y = x, y; return
        dx, dy = x - self.last_x, y - self.last_y
        self.last_x, self.last_y = x, y
        
        if self.box_selecting:
            self.box_end = (x, y)

        if self.orbiting:
            self.cam.yaw_v += 0.005 * dx
            self.cam.pitch_v -= 0.005 * dy
            
        if self.panning:
            # Scale pan speed by distance/ortho scale
            scale = 0.0
            if self.is_ortho:
                scale = self.cam.ortho_scale / 800.0 # Approximate pixel to unit ratio
            else:
                dist = np.linalg.norm(self.cam.offset)
                scale = dist * 0.001
            
            # Pan X moves right vector, Pan Y moves up vector
            # Note: Mouse Y is down, World Up is up, so invert dy
            self.cam.pan[0] -= dx * scale
            self.cam.pan[1] += dy * scale

    def _on_key(self, win, key, sc, act, mods):
        if imgui.get_io().want_capture_keyboard: return
        if act == glfw.PRESS:
            if key == glfw.KEY_ESCAPE: glfw.set_window_should_close(win, True)
            if key == glfw.KEY_H: self.show_gui = not self.show_gui

    def _get_matrices(self, w, h) -> Tuple[np.ndarray, np.ndarray]:
        aspect = w / h if h > 0 else 1.0
        view = look_at(self.cam.eye(), self.cam.target(), WORLD_UP)
        if self.is_ortho:
            height = self.cam.ortho_scale
            width = height * aspect
            dist = np.linalg.norm(self.cam.offset)
            proj = ortho(-width/2, width/2, -height/2, height/2, -dist*4.0, dist*4.0)
        else:
            proj = perspective(self.cam.fov, aspect, 0.1, 1000.0)
        return view, proj

    def _draw_geometry_lines(self, view, proj):
        if len(self.selected_atoms) >= 2:
            points = []
            for i in range(len(self.selected_atoms)-1):
                points.append(self.pos[self.selected_atoms[i]])
                points.append(self.pos[self.selected_atoms[i+1]])
            data = np.array(points, dtype=np.float32)
            glUseProgram(self.line_prog)
            glUniformMatrix4fv(glGetUniformLocation(self.line_prog, "uView"), 1, GL_FALSE, view.T)
            glUniformMatrix4fv(glGetUniformLocation(self.line_prog, "uProj"), 1, GL_FALSE, proj.T)
            glUniform4f(glGetUniformLocation(self.line_prog, "uRGBA"), 1.0, 0.2, 1.0, 1.0)
            vao, vbo = glGenVertexArrays(1), glGenBuffers(1)
            glBindVertexArray(vao); glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STREAM_DRAW)
            glEnableVertexAttribArray(0); glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
            glUniform1i(glGetUniformLocation(self.line_prog, "uReplicaOffsets"), 0) 
            glDrawArrays(GL_LINES, 0, len(data))
            glDeleteBuffers(1, [vbo]); glDeleteVertexArrays(1, [vao])

    def save_screenshot(self, filename):
        w, h = glfw.get_framebuffer_size(self.win)
        # Read pixels from the default framebuffer
        pixels = glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE)
        
        # Convert to numpy array and flip vertically (OpenGL origin is bottom-left)
        image = np.frombuffer(pixels, dtype=np.uint8).reshape(h, w, 3)
        image = np.flipud(image)
        
        # Save as PPM (Portable PixMap) format
        with open(filename, 'wb') as f:
            f.write(f'P6\n{w} {h}\n255\n'.encode())
            f.write(image.tobytes())
        print(f"Screenshot saved to {filename}")

    def save_gif(self, filename="animation.gif"):
        try:
            if not HAS_PIL:
                print("Error: PIL (Pillow) not found. Cannot save GIF.")
                return

            print("Generating GIF... This may take a moment.")
            frames = []
            n_frames = len(self.provider)
            
            # Save current state
            original_index = self.index
            
            w, h = glfw.get_framebuffer_size(self.win)
            
            for i in range(n_frames):
                self._load_index(i)
                
                # Force render
                glClearColor(*self.bg_color, 1.0)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                glViewport(0, 0, w, h)
                
                view, proj = self._get_matrices(w, h)
                
                # Render Spheres
                glUseProgram(self.sphere_prog)
                glUniformMatrix4fv(glGetUniformLocation(self.sphere_prog, "uView"), 1, GL_FALSE, view.T)
                glUniformMatrix4fv(glGetUniformLocation(self.sphere_prog, "uProj"), 1, GL_FALSE, proj.T)
                glUniform3f(glGetUniformLocation(self.sphere_prog, "uLightDirVS"), 0.5, 0.5, 1.0)
                glUniform1i(glGetUniformLocation(self.sphere_prog, "uAtomCount"), self.N)
                glUniform1i(glGetUniformLocation(self.sphere_prog, "uColorMode"), 0)
                glUniform1i(glGetUniformLocation(self.sphere_prog, "uIsOrtho"), 1 if self.is_ortho else 0)

                glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_BUFFER, self.pr_tbo)
                glActiveTexture(GL_TEXTURE1); glBindTexture(GL_TEXTURE_BUFFER, self.col_tbo)
                glActiveTexture(GL_TEXTURE2); glBindTexture(GL_TEXTURE_BUFFER, self.rep_tbo)
                
                glUniform1i(glGetUniformLocation(self.sphere_prog, "uAtomPosRad"), 0)
                glUniform1i(glGetUniformLocation(self.sphere_prog, "uAtomColor"), 1)
                glUniform1i(glGetUniformLocation(self.sphere_prog, "uReplicaOffsets"), 2)
                
                glBindVertexArray(self.quad_vao)
                glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, 4, self.N * len(self.replica_offsets))

                # Render Cell Lines
                glUseProgram(self.line_prog)
                glUniformMatrix4fv(glGetUniformLocation(self.line_prog, "uView"), 1, GL_FALSE, view.T)
                glUniformMatrix4fv(glGetUniformLocation(self.line_prog, "uProj"), 1, GL_FALSE, proj.T)
                glUniform4f(glGetUniformLocation(self.line_prog, "uRGBA"), 1, 1, 1, 0.5)
                glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_BUFFER, self.rep_tbo)
                glUniform1i(glGetUniformLocation(self.line_prog, "uReplicaOffsets"), 0)
                self._draw_geometry_lines(view, proj) 
                self._render_hbonds_gl(view, proj)
                
                # Draw Unit Cell Box
                if hasattr(self, 'cell_count') and self.cell_count > 0:
                    glBindVertexArray(self.cell_vao)
                    glDrawArrays(GL_LINES, 0, self.cell_count)
                
                # Read Pixels
                pixels = glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE)
                image = Image.frombytes("RGB", (w, h), pixels)
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
                frames.append(image)
                
                # Swap buffers to show progress
                glfw.swap_buffers(self.win)
                glfw.poll_events()
            
            # Save GIF
            if frames:
                # User requested 100 FPS = 10ms per frame
                duration = 10 
                frames[0].save(filename, save_all=True, append_images=frames[1:], duration=duration, loop=0)
                print(f"GIF saved to {filename} at 100 FPS (10ms/frame)")
            
            # Restore state
            self._load_index(original_index)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to save GIF: {e}")

    def loop(self):
        while not glfw.window_should_close(self.win):
            # Time Update
            curr_time = glfw.get_time()
            dt = curr_time - self.last_time
            self.last_time = curr_time
            
            if self.playing:
                self.time_acc += dt
                step_time = 1.0 / self.playback_speed
                if self.time_acc >= step_time:
                    steps = int(self.time_acc / step_time)
                    self.time_acc -= steps * step_time
                    self._load_index(self.index + steps)

            glfw.poll_events()
            glClearColor(*self.bg_color, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            w, h = glfw.get_framebuffer_size(self.win)
            glViewport(0, 0, w, h)
            
            view, proj = self._get_matrices(w, h)
            
            # 1. Render Spheres
            glUseProgram(self.sphere_prog)
            glUniformMatrix4fv(glGetUniformLocation(self.sphere_prog, "uView"), 1, GL_FALSE, view.T)
            glUniformMatrix4fv(glGetUniformLocation(self.sphere_prog, "uProj"), 1, GL_FALSE, proj.T)
            glUniform3f(glGetUniformLocation(self.sphere_prog, "uLightDirVS"), 0.5, 0.5, 1.0)
            glUniform1i(glGetUniformLocation(self.sphere_prog, "uColorMode"), 0)
            # Pass Ortho Flag to Shader
            glUniform1i(glGetUniformLocation(self.sphere_prog, "uIsOrtho"), int(self.is_ortho))

            glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_BUFFER, self.pr_tbo)
            glActiveTexture(GL_TEXTURE1); glBindTexture(GL_TEXTURE_BUFFER, self.col_tbo)
            glActiveTexture(GL_TEXTURE2); glBindTexture(GL_TEXTURE_BUFFER, self.rep_tbo)
            
            glUniform1i(glGetUniformLocation(self.sphere_prog, "uAtomPosRad"), 0)
            glUniform1i(glGetUniformLocation(self.sphere_prog, "uAtomColor"), 1)
            glUniform1i(glGetUniformLocation(self.sphere_prog, "uReplicaOffsets"), 2)
            glUniform1i(glGetUniformLocation(self.sphere_prog, "uAtomCount"), self.N)
            glUniform1i(glGetUniformLocation(self.sphere_prog, "uIsOrtho"), int(self.is_ortho))
            glUniform1f(glGetUniformLocation(self.sphere_prog, "uAtomScale"), self.atom_scale)
            
            glBindVertexArray(self.quad_vao)
            glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, 4, self.N * len(self.replica_offsets))

            # 2. Render Cell Lines
            glUseProgram(self.line_prog)
            glUniformMatrix4fv(glGetUniformLocation(self.line_prog, "uView"), 1, GL_FALSE, view.T)
            glUniformMatrix4fv(glGetUniformLocation(self.line_prog, "uProj"), 1, GL_FALSE, proj.T)
            glUniform4f(glGetUniformLocation(self.line_prog, "uRGBA"), 1, 1, 1, 0.5)
            glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_BUFFER, self.rep_tbo)
            glUniform1i(glGetUniformLocation(self.line_prog, "uReplicaOffsets"), 0)
            
            glBindVertexArray(self.cell_vao)
            glDrawArraysInstanced(GL_LINES, 0, self.cell_count, len(self.replica_offsets))

            # 3. Render Geometry Selections (Simple Lines)
            # 2. Render Bonds (if enabled)
            if self.show_bonds:
                self._draw_bonds(view, proj)
            
            # 3. Render Selection Lines
            self._draw_geometry_lines(view, proj)
            self._render_hbonds_gl(view, proj)

            self._render_gui()
            glfw.swap_buffers(self.win)
            self.cam.rotate_yaw(self.cam.yaw_v)
            self.cam.rotate_pitch(self.cam.pitch_v)
            self.cam.yaw_v *= 0.9
            self.cam.pitch_v *= 0.9

            # FPS Limiter
            target_dt = 1.0 / self.target_fps
            actual_dt = glfw.get_time() - curr_time
            if actual_dt < target_dt:
                import time
                time.sleep(target_dt - actual_dt)

        self.impl.shutdown()
        glfw.terminate()

def link_program(vertex_source, fragment_source):
    vs = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vs, vertex_source)
    glCompileShader(vs)
    if not glGetShaderiv(vs, GL_COMPILE_STATUS): raise RuntimeError(glGetShaderInfoLog(vs))
    fs = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fs, fragment_source)
    glCompileShader(fs)
    if not glGetShaderiv(fs, GL_COMPILE_STATUS): raise RuntimeError(glGetShaderInfoLog(fs))
    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)
    if not glGetProgramiv(prog, GL_LINK_STATUS): raise RuntimeError(glGetProgramInfoLog(prog))
    glDeleteShader(vs); glDeleteShader(fs)
    return prog

class DemoProvider:
    def __init__(self):
        self.wrapped_indices = set()

    def __len__(self): return 50
    def get_all_Ef(self): 
        # Generate a sine wave energy profile for demo (Formation Energy)
        return np.sin(np.linspace(0, 4*np.pi, 50)) * 5.0 # Lower magnitude
    
    def get_all_E(self):
        # Generate a different sine wave for Total Energy
        return np.sin(np.linspace(0, 4*np.pi, 50)) * 10.0 - 100.0 # Higher magnitude and offset
        
    def get(self, idx):
        N = 300
        np.random.seed(idx)
        # Random positions in [-10, 10]
        pos = (np.random.rand(N, 3) - 0.5) * 20.0
        lat = np.eye(3) * 25.0
        
        if idx in self.wrapped_indices:
            # Simulate wrapping to [0, 25]
            # Simple periodic boundary condition
            pos = pos % 25.0
            
        elements = ['H'] * (N//2) + ['O'] * (N - N//2)
        return pos, lat, 0.0, elements, None, None

    def wrap(self, idx):
        self.wrapped_indices.add(idx)

if __name__ == "__main__":
    provider = DemoProvider()
    viewer = Viewer(provider)
    viewer.loop()
