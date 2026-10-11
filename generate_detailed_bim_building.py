import os
import math

def generate_obj():
    out_dir = r"C:\BuildLens4D\UnityApp\BuildLens4D\Assets\Models"
    os.makedirs(out_dir, exist_ok=True)
    obj_path = os.path.join(out_dir, "BIM_Building_Detailed.obj")
    mtl_path = os.path.join(out_dir, "BIM_Building_Detailed.mtl")

    # 1. Write Material Definitions (.mtl)
    materials = {
        "Mat_PlazaPaving": {"Kd": "0.88 0.90 0.92", "Ks": "0.15 0.15 0.15", "Ns": "25.0", "d": "1.0"},
        "Mat_GreenTurf": {"Kd": "0.18 0.55 0.22", "Ks": "0.05 0.05 0.05", "Ns": "10.0", "d": "1.0"},
        "Mat_TreeTrunk": {"Kd": "0.38 0.25 0.15", "Ks": "0.05 0.05 0.05", "Ns": "10.0", "d": "1.0"},
        "Mat_TreeFoliage": {"Kd": "0.12 0.44 0.18", "Ks": "0.08 0.08 0.08", "Ns": "15.0", "d": "1.0"},
        "Mat_PrecastConcrete": {"Kd": "0.82 0.84 0.86", "Ks": "0.12 0.12 0.12", "Ns": "20.0", "d": "1.0"},
        "Mat_CoreConcrete": {"Kd": "0.62 0.65 0.68", "Ks": "0.10 0.10 0.10", "Ns": "20.0", "d": "1.0"},
        "Mat_StructuralSteel": {"Kd": "0.18 0.22 0.28", "Ks": "0.70 0.70 0.75", "Ns": "75.0", "d": "1.0"},
        "Mat_MetalMullion": {"Kd": "0.12 0.14 0.16", "Ks": "0.55 0.55 0.60", "Ns": "60.0", "d": "1.0"},
        "Mat_StainlessRail": {"Kd": "0.75 0.78 0.82", "Ks": "0.85 0.85 0.90", "Ns": "95.0", "d": "1.0"},
        "Mat_CurtainGlass": {"Kd": "0.22 0.68 0.85", "Ks": "0.90 0.90 0.95", "Ns": "95.0", "d": "0.45"},
        "Mat_SpandrelGlass": {"Kd": "0.14 0.20 0.28", "Ks": "0.80 0.80 0.85", "Ns": "90.0", "d": "0.95"},
        "Mat_TimberLouvers": {"Kd": "0.72 0.48 0.26", "Ks": "0.10 0.10 0.10", "Ns": "15.0", "d": "1.0"},
        "Mat_SolarPV": {"Kd": "0.06 0.12 0.28", "Ks": "0.85 0.85 0.90", "Ns": "90.0", "d": "1.0"},
        "Mat_SolarFrame": {"Kd": "0.65 0.68 0.72", "Ks": "0.60 0.60 0.65", "Ns": "70.0", "d": "1.0"},
        "Mat_HVACMetal": {"Kd": "0.45 0.48 0.52", "Ks": "0.50 0.50 0.55", "Ns": "60.0", "d": "1.0"},
        "Mat_StatusComplete": {"Kd": "0.08 0.85 0.42", "Ks": "0.35 0.35 0.35", "Ns": "50.0", "d": "0.95"},
        "Mat_StatusDelayed": {"Kd": "0.92 0.15 0.12", "Ks": "0.35 0.35 0.35", "Ns": "50.0", "d": "0.95"},
        "Mat_StatusReview": {"Kd": "0.70 0.22 0.95", "Ks": "0.35 0.35 0.35", "Ns": "50.0", "d": "0.95"},
        "Mat_StatusInProgress": {"Kd": "0.98 0.72 0.10", "Ks": "0.35 0.35 0.35", "Ns": "50.0", "d": "0.95"},
    }

    with open(mtl_path, "w", encoding="utf-8") as f:
        f.write("# BuildLens 4D Architectural Materials\n\n")
        for name, p in materials.items():
            f.write(f"newmtl {name}\n")
            f.write(f"Kd {p['Kd']}\n")
            f.write(f"Ks {p['Ks']}\n")
            f.write(f"Ns {p['Ns']}\n")
            f.write(f"d {p['d']}\n")
            f.write("illum 2\n\n")

    # 2. Build 3D Geometric Primitives
    verts = []
    normals = []
    groups = {} # mat_name -> list of face vertex tuples

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
        if mat_name not in groups:
            groups[mat_name] = []
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        b = len(verts) + 1
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
        verts.extend(corners)

        # 6 faces (quads converted to 2 triangles each)
        box_faces = [
            # South (+Z)
            (n_south, [(b+4, n_south), (b+5, n_south), (b+6, n_south), (b+7, n_south)]),
            # North (-Z)
            (n_north, [(b+1, n_north), (b+0, n_north), (b+3, n_north), (b+2, n_north)]),
            # Top (+Y)
            (n_up, [(b+3, n_up), (b+7, n_up), (b+6, n_up), (b+2, n_up)]),
            # Bottom (-Y)
            (n_down, [(b+0, n_down), (b+1, n_down), (b+5, n_down), (b+4, n_down)]),
            # East (+X)
            (n_east, [(b+1, n_east), (b+2, n_east), (b+6, n_east), (b+5, n_east)]),
            # West (-X)
            (n_west, [(b+4, n_west), (b+7, n_west), (b+3, n_west), (b+0, n_west)]),
        ]
        for _, face_verts in box_faces:
            # Triangulate quad: (0, 1, 2) and (0, 2, 3)
            groups[mat_name].append((face_verts[0], face_verts[1], face_verts[2]))
            groups[mat_name].append((face_verts[0], face_verts[2], face_verts[3]))

    def add_cylinder(cx, cy, cz, radius, height, mat_name, segments=12):
        if mat_name not in groups:
            groups[mat_name] = []
        b = len(verts) + 1
        half_h = height * 0.5
        top_verts = []
        bot_verts = []

        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            x = cx + radius * math.cos(angle)
            z = cz + radius * math.sin(angle)
            verts.append((x, cy - half_h, z))
            bot_verts.append(len(verts))
            verts.append((x, cy + half_h, z))
            top_verts.append(len(verts))

        # Wall faces
        for i in range(segments):
            next_i = (i + 1) % segments
            b1 = bot_verts[i]
            t1 = top_verts[i]
            b2 = bot_verts[next_i]
            t2 = top_verts[next_i]
            # Normals approx
            n1 = add_normal(math.cos(2*math.pi*i/segments), 0, math.sin(2*math.pi*i/segments))
            n2 = add_normal(math.cos(2*math.pi*next_i/segments), 0, math.sin(2*math.pi*next_i/segments))
            groups[mat_name].append(((b1, n1), (b2, n2), (t2, n2)))
            groups[mat_name].append(((b1, n1), (t2, n2), (t1, n1)))

    print("Synthesizing High-Detail Architectural Geometry...")

    # -------------------------------------------------------------------------
    # A. SITE & PLAZA INFRASTRUCTURE
    # -------------------------------------------------------------------------
    # Plaza Ground Base
    add_box(0, -0.25, 0, 36.0, 0.5, 30.0, "Mat_PlazaPaving")
    # Manicured Lawns flanking the building
    add_box(-14.5, -0.05, 0, 6.0, 0.15, 26.0, "Mat_GreenTurf")
    add_box(14.5, -0.05, 0, 6.0, 0.15, 26.0, "Mat_GreenTurf")
    add_box(0, -0.05, 12.0, 22.0, 0.15, 4.0, "Mat_GreenTurf")

    # Entrance Stepped Podium
    add_box(0, 0.15, -6.5, 12.0, 0.3, 3.0, "Mat_PrecastConcrete")
    add_box(0, 0.35, -5.5, 10.0, 0.3, 2.0, "Mat_PrecastConcrete")

    # Landscaping Trees (8 perimeter trees)
    tree_spots = [
        (-14.0, -10.0), (-14.0, -3.0), (-14.0, 4.0), (-14.0, 10.0),
        (14.0, -10.0),  (14.0, -3.0),  (14.0, 4.0),  (14.0, 10.0)
    ]
    for tx, tz in tree_spots:
        # Trunk
        add_cylinder(tx, 1.2, tz, 0.25, 2.4, "Mat_TreeTrunk", 8)
        # Foliage Tiers
        add_cylinder(tx, 2.8, tz, 1.8, 1.6, "Mat_TreeFoliage", 8)
        add_cylinder(tx, 4.0, tz, 1.3, 1.4, "Mat_TreeFoliage", 8)
        add_cylinder(tx, 4.8, tz, 0.8, 1.0, "Mat_TreeFoliage", 8)

    # Decorative Planter Boxes
    planter_spots = [(-6.5, -7.5), (6.5, -7.5), (-10.5, -7.5), (10.5, -7.5)]
    for px, pz in planter_spots:
        add_box(px, 0.4, pz, 1.6, 0.8, 1.6, "Mat_PrecastConcrete")
        add_box(px, 0.85, pz, 1.3, 0.3, 1.3, "Mat_GreenTurf")
        add_cylinder(px, 1.2, pz, 0.6, 0.7, "Mat_TreeFoliage", 6)

    # -------------------------------------------------------------------------
    # B. SUBSTRUCTURE & FOUNDATION
    # -------------------------------------------------------------------------
    # Raised Concrete Plinth
    add_box(0, 0.25, 0, 21.0, 0.5, 15.0, "Mat_PrecastConcrete")

    # Perimeter Diaphragm Shoring Walls (Basement/Ground Edge)
    add_box(0, 0.8, 7.6, 21.0, 1.6, 0.4, "Mat_CoreConcrete")
    add_box(-10.6, 0.8, 0, 0.4, 1.6, 15.0, "Mat_CoreConcrete")
    add_box(10.6, 0.8, 0, 0.4, 1.6, 15.0, "Mat_CoreConcrete")

    # -------------------------------------------------------------------------
    # C. 4-STOREY STRUCTURAL COLUMN & GIRDER FRAMEWORK
    # -------------------------------------------------------------------------
    col_x = [-9.0, -3.0, 3.0, 9.0]
    col_z = [-6.5, 0.0, 6.5]
    floor_heights = [0.5, 4.2, 7.8, 11.4, 15.0]

    # Columns with Pedestals & Capitals
    col_counter = 0
    for x in col_x:
        for z in col_z:
            col_counter += 1
            # Base Pedestal
            add_box(x, 0.6, z, 1.1, 0.4, 1.1, "Mat_CoreConcrete")

            # Column Stems per floor
            for fl in range(4):
                y_bot = floor_heights[fl]
                y_top = floor_heights[fl+1]
                h = y_top - y_bot
                y_mid = (y_bot + y_top) * 0.5

                # Assign specific BIM status to key columns
                mat = "Mat_PrecastConcrete"
                if col_counter == 1 and fl == 0:
                    mat = "Mat_StatusComplete"  # COL-B1-01
                elif col_counter == 2 and fl == 0:
                    mat = "Mat_StatusComplete"  # COL-B1-02
                elif col_counter == 3 and fl == 0:
                    mat = "Mat_StatusDelayed"   # COL-B1-03 (Delayed Alert!)
                elif col_counter == 4 and fl == 0:
                    mat = "Mat_StatusInProgress" # COL-B1-04
                elif fl == 3:
                    mat = "Mat_StructuralSteel" # Top floor exposed steel columns

                add_box(x, y_mid, z, 0.65, h, 0.65, mat)
                # Capital bracket
                add_box(x, y_top - 0.15, z, 0.85, 0.3, 0.85, "Mat_PrecastConcrete")

    # Primary Horizontal Steel I-Beams (Flanges & Web)
    for fl in range(1, 5):
        y_beam = floor_heights[fl] - 0.25

        # Longitudinal Beams (along X)
        for z in col_z:
            for i in range(len(col_x) - 1):
                x1, x2 = col_x[i], col_x[i+1]
                xm = (x1 + x2) * 0.5
                span = x2 - x1

                mat = "Mat_StructuralSteel"
                if fl == 1 and z == col_z[0] and i == 1:
                    mat = "Mat_StatusReview" # BM-L1-02 (Needs Review Alert!)
                elif fl == 1 and z == col_z[0] and i == 0:
                    mat = "Mat_StatusInProgress" # BM-L1-01

                # Top flange
                add_box(xm, y_beam + 0.22, z, span - 0.7, 0.06, 0.45, mat)
                # Web
                add_box(xm, y_beam, z, span - 0.7, 0.38, 0.08, mat)
                # Bottom flange
                add_box(xm, y_beam - 0.22, z, span - 0.7, 0.06, 0.45, mat)

        # Transverse Beams (along Z)
        for x in col_x:
            for j in range(len(col_z) - 1):
                z1, z2 = col_z[j], col_z[j+1]
                zm = (z1 + z2) * 0.5
                span = z2 - z1
                # Top flange
                add_box(x, y_beam + 0.22, zm, 0.45, 0.06, span - 0.7, "Mat_StructuralSteel")
                # Web
                add_box(x, y_beam, zm, 0.08, 0.38, span - 0.7, "Mat_StructuralSteel")
                # Bottom flange
                add_box(x, y_beam - 0.22, zm, 0.45, 0.06, span - 0.7, "Mat_StructuralSteel")

    # -------------------------------------------------------------------------
    # D. CONCRETE FLOOR SLABS & BALCONIES
    # -------------------------------------------------------------------------
    for fl in range(1, 5):
        y_slab = floor_heights[fl]
        # Main suspended floor slab
        add_box(0, y_slab + 0.15, 0, 20.0, 0.3, 14.5, "Mat_PrecastConcrete")

        # 3rd & 4th floor front cantilevered balconies
        if fl in [2, 3]:
            # Balcony slab
            add_box(0, y_slab + 0.15, -7.5, 10.0, 0.25, 1.8, "Mat_PrecastConcrete")
            # Glass Balustrade
            add_box(0, y_slab + 0.75, -8.3, 9.8, 0.9, 0.06, "Mat_CurtainGlass")
            # Stainless Steel Handrail
            add_box(0, y_slab + 1.22, -8.3, 10.0, 0.08, 0.10, "Mat_StainlessRail")
            # Side railings
            add_box(-4.9, y_slab + 0.75, -7.5, 0.06, 0.9, 1.7, "Mat_CurtainGlass")
            add_box(4.9, y_slab + 0.75, -7.5, 0.06, 0.9, 1.7, "Mat_CurtainGlass")

    # -------------------------------------------------------------------------
    # E. ARCHITECTURAL CURTAIN WALL FACADE & MULLIONS
    # -------------------------------------------------------------------------
    # Generate multi-bay extruded mullions and double-glazed vision glass
    for fl in range(4):
        y_bot = floor_heights[fl] + 0.3
        y_top = floor_heights[fl+1] - 0.1
        h_bay = y_top - y_bot
        y_mid = (y_bot + y_top) * 0.5

        # Front Facade (South, Z = -6.8)
        # Vertical Mullions (every 2.0 meters)
        for mx in range(-9, 10, 2):
            add_box(mx, y_mid, -6.85, 0.12, h_bay, 0.16, "Mat_MetalMullion")
        # Horizontal Transoms
        add_box(0, y_mid - h_bay * 0.25, -6.85, 18.2, 0.10, 0.14, "Mat_MetalMullion")
        add_box(0, y_mid + h_bay * 0.25, -6.85, 18.2, 0.10, 0.14, "Mat_MetalMullion")
        # Vision Glass Panes
        add_box(0, y_mid, -6.85, 18.0, h_bay - 0.1, 0.06, "Mat_CurtainGlass")
        # Insulated Spandrel Panel at slab edge
        add_box(0, floor_heights[fl+1], -6.86, 18.2, 0.5, 0.12, "Mat_SpandrelGlass")

        # Rear Facade (North, Z = 6.8)
        for mx in range(-9, 10, 3):
            add_box(mx, y_mid, 6.85, 0.12, h_bay, 0.16, "Mat_MetalMullion")
        add_box(0, y_mid, 6.85, 18.0, h_bay - 0.1, 0.06, "Mat_CurtainGlass")

    # Entrance Double-Height Canopy Marquee
    add_box(0, 4.4, -8.2, 8.0, 0.2, 3.2, "Mat_StructuralSteel")
    add_box(0, 4.52, -8.2, 7.8, 0.05, 3.0, "Mat_CurtainGlass")
    # Canopy support diagonal tie-rods
    add_cylinder(-3.8, 5.8, -8.0, 0.04, 3.0, "Mat_StainlessRail", 6)
    add_cylinder(3.8, 5.8, -8.0, 0.04, 3.0, "Mat_StainlessRail", 6)

    # -------------------------------------------------------------------------
    # F. SUSTAINABLE GREEN TIMBER LOUVERS & SHADING SYSTEM
    # -------------------------------------------------------------------------
    # Angled Cedar Timber Blades (West Facade Brise-Soleil)
    for fl in range(1, 4):
        for ly in range(6):
            y_louver = floor_heights[fl] + 0.6 + ly * 0.45
            for lz in range(-5, 6, 2):
                add_box(-9.8, y_louver, lz, 0.08, 0.22, 1.6, "Mat_TimberLouvers")

    # -------------------------------------------------------------------------
    # G. ROOFTOP ECO-GARDEN, MECHANICAL PENTHOUSE & SOLAR PLANT
    # -------------------------------------------------------------------------
    roof_y = floor_heights[4] + 0.3 # 15.3m

    # Perimeter Safety Parapet Wall with Metal Coping
    add_box(0, roof_y + 0.6, -7.0, 20.2, 1.2, 0.3, "Mat_PrecastConcrete")
    add_box(0, roof_y + 1.22, -7.0, 20.4, 0.08, 0.36, "Mat_MetalMullion") # Coping cap
    add_box(0, roof_y + 0.6, 7.0, 20.2, 1.2, 0.3, "Mat_PrecastConcrete")
    add_box(0, roof_y + 1.22, 7.0, 20.4, 0.08, 0.36, "Mat_MetalMullion")
    add_box(-9.9, roof_y + 0.6, 0, 0.3, 1.2, 14.2, "Mat_PrecastConcrete")
    add_box(-9.9, roof_y + 1.22, 0, 0.36, 0.08, 14.4, "Mat_MetalMullion")
    add_box(9.9, roof_y + 0.6, 0, 0.3, 1.2, 14.2, "Mat_PrecastConcrete")
    add_box(9.9, roof_y + 1.22, 0, 0.36, 0.08, 14.4, "Mat_MetalMullion")

    # Central Elevator & Stair Core Penthouse (Height 3.5m)
    add_box(0, roof_y + 1.75, 1.5, 6.0, 3.5, 5.0, "Mat_CoreConcrete")
    add_box(0, roof_y + 3.6, 1.5, 6.4, 0.3, 5.4, "Mat_PrecastConcrete")
    # Penthouse Louvered Ventilation Grille
    add_box(0, roof_y + 2.4, -1.05, 3.2, 1.6, 0.1, "Mat_MetalMullion")

    # Rooftop Eco-Garden Turf & Paver Zones (West Side)
    add_box(-5.2, roof_y + 0.1, -1.5, 7.0, 0.2, 8.5, "Mat_GreenTurf")
    # Timber Boardwalk Walkways
    add_box(-5.2, roof_y + 0.22, -1.5, 1.4, 0.06, 8.2, "Mat_TimberLouvers")
    # Eco Garden Planters
    add_box(-7.8, roof_y + 0.45, -3.5, 1.2, 0.6, 2.4, "Mat_PrecastConcrete")
    add_box(-7.8, roof_y + 0.8, -3.5, 1.0, 0.4, 2.2, "Mat_TreeFoliage")
    add_box(-7.8, roof_y + 0.45, 0.5, 1.2, 0.6, 2.4, "Mat_PrecastConcrete")
    add_box(-7.8, roof_y + 0.8, 0.5, 1.0, 0.4, 2.2, "Mat_TreeFoliage")

    # 2 Commercial HVAC Rooftop Chiller Units
    for hx in [4.5, 7.5]:
        # Body
        add_box(hx, roof_y + 0.9, 3.5, 2.2, 1.8, 3.4, "Mat_HVACMetal")
        # Compressor housing
        add_box(hx, roof_y + 0.6, 1.5, 1.6, 1.2, 1.2, "Mat_HVACMetal")
        # Top Exhaust Fan Cowls
        add_cylinder(hx, roof_y + 1.9, 2.6, 0.7, 0.3, "Mat_StructuralSteel", 10)
        add_cylinder(hx, roof_y + 1.9, 4.4, 0.7, 0.3, "Mat_StructuralSteel", 10)

    # Photovoltaic Solar Power Plant (East Side - 2 Tilted Arrays)
    for array_z in [-4.0, -1.0]:
        # Racking Frame Leg Posts
        add_cylinder(4.2, roof_y + 0.4, array_z - 0.8, 0.05, 0.8, "Mat_SolarFrame", 6)
        add_cylinder(8.2, roof_y + 0.4, array_z - 0.8, 0.05, 0.8, "Mat_SolarFrame", 6)
        add_cylinder(4.2, roof_y + 0.8, array_z + 0.8, 0.05, 1.6, "Mat_SolarFrame", 6)
        add_cylinder(8.2, roof_y + 0.8, array_z + 0.8, 0.05, 1.6, "Mat_SolarFrame", 6)
        # Tilted Mounting Rails
        add_box(6.2, roof_y + 0.9, array_z, 4.8, 0.08, 2.2, "Mat_SolarFrame")
        # High-Efficiency Monocrystalline PV Panels
        add_box(6.2, roof_y + 0.96, array_z, 4.6, 0.05, 2.0, "Mat_SolarPV")

    # 3. Write Wavefront OBJ File
    print(f"Total Vertices: {len(verts)}, Faces Count: {sum(len(f) for f in groups.values())}")
    with open(obj_path, "w", encoding="utf-8") as f:
        f.write("# BuildLens 4D Architectural BIM Building Model\n")
        f.write(f"mtllib BIM_Building_Detailed.mtl\n\n")

        for vx, vy, vz in verts:
            f.write(f"v {vx:.4f} {vy:.4f} {vz:.4f}\n")

        f.write("\n")
        for nx, ny, nz in normals:
            f.write(f"vn {nx:.4f} {ny:.4f} {nz:.4f}\n")

        for mat_name, face_list in groups.items():
            f.write(f"\nusemtl {mat_name}\n")
            f.write(f"g Group_{mat_name}\n")
            for f_tri in face_list:
                # 3 vertices per triangle
                f.write(f"f {f_tri[0][0]}//{f_tri[0][1]} {f_tri[1][0]}//{f_tri[1][1]} {f_tri[2][0]}//{f_tri[2][1]}\n")

    print(f"Successfully generated detailed BIM OBJ at: {obj_path}")

if __name__ == "__main__":
    generate_obj()
