
import numpy as np
import re

class GAUSSIAN:
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        self.file_location = file_location
        self.name = name
        
        # Attributes expected by AtomPositionLoader/Manager
        self.atomLabelsList = None
        self.atomPositions = None
        self.E = None
        self.forces = None
        self.charge = None
        self.magnetization = None


    def read_GAUSSIAN(self, file_location:str=None, **kwargs):
        """
        Reads a Gaussian log file (.log or .out).
        Extracts the LAST frame found in the file.
        """
        all_frames = self.read_all_frames(file_location, **kwargs)
        if not all_frames:
            return False
            
        last_frame = all_frames[-1]
        self.atomLabelsList = last_frame['atomLabelsList']
        self.atomPositions = last_frame['atomPositions']
        self.E = last_frame['E']
        self.forces = last_frame['forces']
        
        return True

    def read_all_frames(self, file_location:str=None, **kwargs):
        """
        Reads all frames from a Gaussian log file.
        Returns a list of dictionaries, each containing:
            - atomLabelsList
            - atomPositions
            - E
            - total_force (optional)
        """
        file_location = file_location or self.file_location
        if not file_location:
            raise ValueError("File location must be provided.")

        try:
            with open(file_location, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_location}")

        frames = []
        
        # State variables for a single frame
        current_atoms = []
        current_coords = []
        current_energy = None
        current_forces = []
        
        # Flags
        in_geometry = False
        in_forces = False
        
        # Helper to push a completed frame
        def push_frame():
            nonlocal current_atoms, current_coords, current_energy, current_forces
            if current_coords:
                frame_data = {
                    'atomLabelsList': np.array(current_atoms, dtype=object),
                    'atomPositions': np.array(current_coords, dtype=float),
                    'E': current_energy,
                    'forces': np.array(current_forces, dtype=float) if current_forces else None
                }
                frames.append(frame_data)
            
            # Reset strictly, but we might carry over Energy if the print order varies?
            # Usually Gaussian prints Geometry -> Energy. 
            # If we find a new Geometry, the previous frame is definitely done.
            current_atoms = []
            current_coords = []
            # current_energy = None # Energy usually follows, so we reset.
            current_forces = []

        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # --- Geometry ---
            if "Standard orientation:" in line or "Input orientation:" in line:
                # If we already have coordinates collected, this means we are starting a NEW frame.
                # Push the previous one.
                if current_coords:
                    push_frame()
                    current_energy = None # Reset energy for the new frame
                
                # Start parsing geometry
                start_idx = i + 5
                j = start_idx
                temp_atoms = []
                temp_coords = []
                while j < len(lines):
                    gline = lines[j].strip()
                    if gline.startswith("---"):
                        break
                    parts = gline.split()
                    if len(parts) >= 6:
                        try:
                            atomic_number = int(parts[1])
                            x = float(parts[3])
                            y = float(parts[4])
                            z = float(parts[5])
                            temp_atoms.append(self._get_symbol_from_Z(atomic_number))
                            temp_coords.append([x, y, z])
                        except ValueError:
                            pass
                    j += 1
                current_atoms = temp_atoms
                current_coords = temp_coords
                i = j # fast forward
                continue

            # --- Energy ---
            if "SCF Done:" in line:
                # If we already have an energy and coords, push previous frame
                if current_energy is not None and current_coords:
                    push_frame()

                match = re.search(r"SCF Done:\s+E\(\w+\)\s+=\s+([-+]?\d*\.\d+)", line)
                if match:
                    e_au = float(match.group(1))
                    current_energy = e_au * 27.211386245988  # convert to eV

            # --- Forces ---
            # Only parse real force tables (not the optimization summary)
            if "Forces (Hartrees/Bohr)" in line:
                j = i + 3  # the table starts 3 lines below
                temp_forces = []
                while j < len(lines):
                    fline = lines[j].strip()
                    if fline.startswith("---"):
                        break
                    parts = fline.split()
                    if len(parts) >= 5:
                        try:
                            fx, fy, fz = map(float, parts[2:5])
                            conv = 51.42208619083232  # Ha/Bohr → eV/Å
                            temp_forces.append([fx*conv, fy*conv, fz*conv])
                        except:
                            pass
                    j += 1
                current_forces = temp_forces
                i = j
                continue

            # IMPORTANT: Do NOT parse this — Gaussian optimization prints no force table here
            if "Cartesian Forces:" in line:
                i += 1
                continue

            i += 1
            
        # Push the last frame if it exists
        if current_coords and (current_energy is not None or current_forces):
            push_frame()
            
        return frames

    def export_as_GAUSSIAN(self, file_location:str=None, **kwargs):
        """
        Export functionality is not strictly required yet, but valid to define.
        """
        print("Export to Gaussian input not yet implemented.")
        return False

    def _get_symbol_from_Z(self, Z):
        # Simple lookup
        periodic_table = {
            1: "H", 2: "He", 3: "Li", 4: "Be", 5: "B", 6: "C", 7: "N", 8: "O", 9: "F", 10: "Ne",
            11: "Na", 12: "Mg", 13: "Al", 14: "Si", 15: "P", 16: "S", 17: "Cl", 18: "Ar", 19: "K", 20: "Ca",
            21: "Sc", 22: "Ti", 23: "V", 24: "Cr", 25: "Mn", 26: "Fe", 27: "Co", 28: "Ni", 29: "Cu", 30: "Zn",
            31: "Ga", 32: "Ge", 33: "As", 34: "Se", 35: "Br", 36: "Kr", 37: "Rb", 38: "Sr", 39: "Y", 40: "Zr",
            41: "Nb", 42: "Mo", 43: "Tc", 44: "Ru", 45: "Rh", 46: "Pd", 47: "Ag", 48: "Cd", 49: "In", 50: "Sn",
            51: "Sb", 52: "Te", 53: "I", 54: "Xe", 55: "Cs", 56: "Ba", 57: "La", 58: "Ce", 59: "Pr", 60: "Nd",
            61: "Pm", 62: "Sm", 63: "Eu", 64: "Gd", 65: "Tb", 66: "Dy", 67: "Ho", 68: "Er", 69: "Tm", 70: "Yb",
            71: "Lu", 72: "Hf", 73: "Ta", 74: "W", 75: "Re", 76: "Os", 77: "Ir", 78: "Pt", 79: "Au", 80: "Hg",
            81: "Tl", 82: "Pb", 83: "Bi", 84: "Po", 85: "At", 86: "Rn", 87: "Fr", 88: "Ra", 89: "Ac", 90: "Th",
            91: "Pa", 92: "U", 93: "Np", 94: "Pu", 95: "Am", 96: "Cm", 97: "Bk", 98: "Cf", 99: "Es", 100: "Fm",
        }
        return periodic_table.get(Z, "X")
