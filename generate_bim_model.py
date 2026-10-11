import os
import math

def build_bim_obj(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    obj_path = os.path.join(output_dir, "BIM_Building_Model.obj")
    mtl_path = os.path.join(output_dir, "BIM_Building_Model.mtl")

    # 1. Write Material Library (.mtl)
    with open(mtl_path, "w", encoding="utf-8") as mtl:
        mtl.write("# BuildLens 4D BIM Architectural Materials\n\n")
        
        materials = {
            "Mat_Concrete": {"Kd": "0.80 0.82 0.84", "Ks": "0.15 0.15 0.15", "Ns": "20.0", "d": "1.0"},
            "Mat_DarkSteel": {"Kd": "0.22 0.26 0.32", "Ks": "0.60 0.60 0.65", "Ns": "80.0", "d": "1.0"},
            "Mat_Glass": {"Kd": "0.20 0.70 0.90", "Ks": "0.85 0.85 0.90", "Ns": "95.0", "d": "0.45"},
            "Mat_WoodTimber": {"Kd": "0.72 0.46 0.24", "Ks": "0.10 0.10 0.10", "Ns": "15.0", "d": "1.0"},
            "Mat_GreenTurf": {"Kd": "0.22 0.58 0.26", "Ks": "0.05 0.05 0.05", "Ns": "10.0", "d": "1.0"},
            "Mat_SolarPanel": {"Kd": "0.08 0.14 0.38", "Ks": "0.75 0.75 0.85", "Ns": "90.0", "d": "1.0"},
            "Mat_Pavement": {"Kd": "0.68 0.70 0.72", "Ks": "0.10 0.10 0.10", "Ns": "15.0", "d": "1.0"},
            "Mat_Foundation": {"Kd": "0.48 0.50 0.52", "Ks": "0.10 0.10 0.10", "Ns": "10.0", "d": "1.0"},
            "Mat_StatusComplete": {"Kd": "0.10 0.85 0.45", "Ks": "0.30 0.30 0.30", "Ns": "40.0", "d": "0.9"},
            "Mat_StatusDelayed": {"Kd": "0.90 0.22 0.20", "Ks": "0.30 0.30 0.30", "Ns": "40.0", "d": "0.9"},
            "Mat_StatusReview": {"Kd": "0.68 0.35 0.95", "Ks": "0.30 0.30 0.30", "Ns": "40.0", "d": "0.9"},
        }
        
        for name, props in materials.items():
            mtl.write(f"newmtl {name}\n")
            mtl.write(f"Kd {props['Kd']}\n")
            mtl.write(f"Ks {props['Ks']}\n")
            mtl.write(f"Ns {props['Ns']}\n")
            mtl.write(f"d {props['d']}\n")
            mtl.write("illum 2\n\n")

    # 2. Geometry Builder
    vertices = []
    normals = []
    faces = [] # list of (material, [(v_idx, n_idx), ...])

    def add_normal(nx, ny, nz):
        l = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
        normals.append((nx/l, ny/l, nz/l))
        return len(normals)

    n_up = add_normal(0, 1, 0)
    n_down = add_normal(0, -1, 0)
    n_north = add_normal(0, 0, -1)
    n_south = add_normal(0, 0, 1)
    n_east = add_normal(1, 0, 0)
    n_west = add_normal(-1, 0, 0)

    def add_box(cx, cy, cz, sx, sy, sz, mat_name):
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        base = len(vertices) + 1
        
        # 8 corners
        corners = [
            (cx - hx, cy - hy, cz - hz), # 1
            (cx + hx, cy - hy, cz - hz), # 2
            (cx + hx, cy + hy, cz - hz), # 3
            (cx - hx, cy + hy, cz - hz), # 4
            (cx - hx, cy - hy, cz + hz), # 5
            (cx + hx, cy - hy, cz + hz), # 6
            (cx + hx, cy + hy, cz + hz), # 7
            (cx - hx, cy + hy, cz + hz), # 8
        ]
        vertices.extend(corners)

        # 6 faces: (v1, v2, v3, v4, norm_idx)
        quads = [
            # North face (z-)
            (base+0, base+3, base+2, base+1, n_north),
            # South face (z+)
            (base+4, base+5, base+6, base+7, n_south),
            # Top face (y+)
            (base+3, base+7, base+6, base+2, n_up),
            # Bottom face (y-)
            (base+0, base+1, base+5, base+4, n_down),
            # West face (x-)
            (base+0, base+4, base+7, base+3, n_west),
            # East face (x+)
            (base+1, base+2, base+6, base+5, n_east),
        ]
        
        for v1, v2, v3, v4, n in quads:
            faces.append((mat_name, [v1, v2, v3], n))
            faces.append((mat_name, [v1, v3, v4], n))

    print("Generating 3D architectural geometry...")

    # A. SITE & LANDSCAPE
    # Base green lawn
    add_box(0, -0.2, 0, 42.0, 0.4, 36.0, "Mat_GreenTurf")
    # Paved entrance plaza
    add_box(0, 0.05, 5.0, 26.0, 0.1, 14.0, "Mat_Pavement")
    # Entrance walkway path
    add_box(0, 0.05, 14.0, 8.0, 0.1, 8.0, "Mat_Pavement")

    # B. FOUNDATION & PILE CAPS (Level -1)
    # 8 Pile Cap Footings
    for x in [-9.0, -3.0, 3.0, 9.0]:
        for z in [-6.0, 2.0]:
            add_box(x, -0.6, z, 2.4, 0.8, 2.4, "Mat_Foundation")
    
    # Perimeter North Retaining Wall (Verified complete)
    add_box(0, 1.2, -8.2, 25.0, 3.6, 0.5, "Mat_StatusComplete")

    # C. STRUCTURAL COLUMNS (Ground to Roof, 3 storeys)
    # Grid X: -9, -3, 3, 9  |  Grid Z: -6, -1, 4
    col_x_coords = [-9.0, -3.0, 3.0, 9.0]
    col_z_coords = [-6.0, -1.0, 4.0]
    floor_height = 3.6
    
    for level in range(3):
        cy = level * floor_height + (floor_height * 0.5)
        for i, x in enumerate(col_x_coords):
            for j, z in enumerate(col_z_coords):
                # Apply sample status colors to specific elements
                if level == 0 and i == 0 and j == 0:
                    mat = "Mat_StatusComplete" # COL-B1-01
                elif level == 0 and i == 1 and j == 0:
                    mat = "Mat_StatusDelayed" # COL-B1-03
                elif level == 0 and i == 2 and j == 1:
                    mat = "Mat_StatusReview"  # COL-B1-04
                else:
                    mat = "Mat_Concrete"
                
                # Column shaft
                add_box(x, cy, z, 0.7, floor_height, 0.7, mat)
                # Column capital / head plate
                add_box(x, cy + (floor_height * 0.45), z, 1.0, 0.2, 1.0, "Mat_DarkSteel")

    # D. ELEVATOR & SHEAR CORE (Central Core Shaft)
    # Concrete core rising through all floors
    total_h = floor_height * 3.5
    add_box(0, total_h * 0.5, -3.5, 4.8, total_h, 3.6, "Mat_Concrete")
    # Lift door openings / accents on each floor
    for level in range(3):
        dy = level * floor_height + 1.2
        add_box(0, dy, -1.65, 1.8, 2.2, 0.1, "Mat_DarkSteel")

    # E. TRANSFER GIRDERS & STEEL BEAMS
    # Longitudinal beams (along X) on each floor
    for level in [1, 2, 3]:
        by = level * floor_height - 0.2
        for z in col_z_coords:
            mat = "Mat_StatusComplete" if (level == 1 and z == -6.0) else "Mat_DarkSteel"
            add_box(0, by, z, 22.0, 0.45, 0.4, mat)
    
    # Transverse beams (along Z) on each floor
    for level in [1, 2, 3]:
        by = level * floor_height - 0.2
        for x in col_x_coords:
            mat = "Mat_StatusReview" if (level == 1 and x == 3.0) else "Mat_DarkSteel"
            add_box(x, by, -1.0, 0.4, 0.45, 11.0, mat)

    # F. FLOOR SLABS
    # Ground Floor Concourse (Level 0)
    add_box(0, 0.15, -1.0, 23.0, 0.3, 13.0, "Mat_Concrete")
    
    # Level 1 Floor Slab with Atrium Opening (Atrium from X -3 to 3, Z 0 to 4)
    # South half
    add_box(0, floor_height + 0.15, -3.5, 23.0, 0.3, 7.0, "Mat_Concrete")
    # East wing
    add_box(6.5, floor_height + 0.15, 2.0, 10.0, 0.3, 4.0, "Mat_Concrete")
    # West wing
    add_box(-6.5, floor_height + 0.15, 2.0, 10.0, 0.3, 4.0, "Mat_Concrete")

    # Level 2 Floor Slab (Full coverage)
    add_box(0, floor_height * 2.0 + 0.15, -1.0, 23.0, 0.3, 13.0, "Mat_Concrete")

    # Level 3 Roof Deck Slab
    add_box(0, floor_height * 3.0 + 0.15, -1.0, 23.0, 0.3, 13.0, "Mat_Concrete")

    # G. ARCHITECTURAL GLASS CURTAIN WALL FACADE
    # Front South Entrance Facade (Level 0 & 1)
    facade_h = floor_height * 2.0
    add_box(0, facade_h * 0.5, 4.4, 22.0, facade_h - 0.2, 0.08, "Mat_Glass")
    # Facade Steel Mullions (vertical bars)
    for x in [-9.0, -6.0, -3.0, 0.0, 3.0, 6.0, 9.0]:
        add_box(x, facade_h * 0.5, 4.45, 0.15, facade_h, 0.15, "Mat_DarkSteel")
    
    # Entrance Portal Canopy
    add_box(0, 3.2, 6.0, 6.0, 0.2, 3.5, "Mat_DarkSteel")
    # Canopy Support Columns
    add_box(-2.8, 1.6, 7.5, 0.18, 3.2, 0.18, "Mat_DarkSteel")
    add_box(2.8, 1.6, 7.5, 0.18, 3.2, 0.18, "Mat_DarkSteel")

    # Upper Level 2 Glass Windows
    add_box(0, floor_height * 2.5, 4.4, 22.0, floor_height - 0.4, 0.08, "Mat_Glass")

    # H. SUSTAINABLE TIMBER SHADING LOUVERS (West Facade)
    for i in range(12):
        lz = -6.0 + i * 0.9
        add_box(-9.5, floor_height * 1.5, lz, 0.12, floor_height * 2.2, 0.45, "Mat_WoodTimber")

    # I. ROOFTOP ECO-GARDEN & SOLAR PAVILION (Level 3 Roof)
    roof_y = floor_height * 3.0 + 0.3
    # Rooftop Parapet Wall (Safety railing)
    add_box(0, roof_y + 0.55, -7.5, 23.0, 1.1, 0.2, "Mat_Concrete") # North
    add_box(0, roof_y + 0.55, 5.5, 23.0, 1.1, 0.2, "Mat_Glass")     # South Glass Parapet
    add_box(-11.5, roof_y + 0.55, -1.0, 0.2, 1.1, 13.0, "Mat_Concrete") # West
    add_box(11.5, roof_y + 0.55, -1.0, 0.2, 1.1, 13.0, "Mat_Concrete")  # East

    # Rooftop Eco-Garden Turf Beds (2 lush green zones)
    add_box(-5.5, roof_y + 0.2, 0.0, 7.0, 0.3, 8.0, "Mat_GreenTurf")
    add_box(-5.5, roof_y + 0.15, 0.0, 7.4, 0.2, 8.4, "Mat_WoodTimber") # Timber border

    # Photovoltaic Solar Panel Array (8 Solar Racks angled on steel pergola)
    # Solar Pergola Structure
    add_box(5.5, roof_y + 1.2, 0.0, 0.2, 2.4, 0.2, "Mat_DarkSteel")
    add_box(5.5, roof_y + 1.2, -4.0, 0.2, 2.4, 0.2, "Mat_DarkSteel")
    add_box(9.5, roof_y + 1.2, 0.0, 0.2, 2.4, 0.2, "Mat_DarkSteel")
    add_box(9.5, roof_y + 1.2, -4.0, 0.2, 2.4, 0.2, "Mat_DarkSteel")
    
    # 8 Photovoltaic Solar Panels
    for px in [4.5, 6.5, 8.5, 10.5]:
        for pz in [-3.0, -1.0]:
            add_box(px, roof_y + 2.2, pz, 1.6, 0.08, 1.4, "Mat_SolarPanel")

    # J. SURROUNDING GREEN TREES
    tree_locs = [
        (-14.0, -8.0), (14.0, -8.0),
        (-14.0, 8.0),  (14.0, 8.0),
        (-15.0, 0.0),  (15.0, 0.0),
        (-6.0, 12.0),  (6.0, 12.0)
    ]
    for tx, tz in tree_locs:
        # Trunk
        add_box(tx, 1.2, tz, 0.5, 2.4, 0.5, "Mat_WoodTimber")
        # Foliage lower
        add_box(tx, 3.2, tz, 3.2, 2.0, 3.2, "Mat_GreenTurf")
        # Foliage upper
        add_box(tx, 4.6, tz, 2.2, 1.4, 2.2, "Mat_GreenTurf")

    # K. ATRIUM OPEN-TREAD STAIRCASE (Ground to Level 1)
    for st in range(12):
        sy = 0.25 + st * (floor_height / 12.0)
        sz = 3.5 - st * 0.4
        add_box(0, sy, sz, 2.4, 0.15, 0.45, "Mat_DarkSteel")

    # 3. Write Wavefront OBJ file
    with open(obj_path, "w", encoding="utf-8") as obj:
        obj.write("# BuildLens 4D Architectural BIM Model\n")
        obj.write(f"mtllib BIM_Building_Model.mtl\n\n")

        for v in vertices:
            obj.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        obj.write("\n")

        for n in normals:
            obj.write(f"vn {n[0]:.4f} {n[1]:.4f} {n[2]:.4f}\n")
        obj.write("\n")

        current_mat = None
        for mat_name, (v1, v2, v3), n in faces:
            if mat_name != current_mat:
                obj.write(f"\nusemtl {mat_name}\n")
                current_mat = mat_name
            obj.write(f"f {v1}//{n} {v2}//{n} {v3}//{n}\n")

    print(f"Successfully generated {obj_path} ({len(vertices)} vertices, {len(faces)} polygons)")

if __name__ == "__main__":
    out_dir = r"C:\BuildLens4D\UnityApp\BuildLens4D\Assets\Models"
    build_bim_obj(out_dir)
