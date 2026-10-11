import os
import math

def build_urban_building():
    out_dir = r"C:\BuildLens4D\UnityApp\BuildLens4D\Assets\Models"
    os.makedirs(out_dir, exist_ok=True)
    obj_path = os.path.join(out_dir, "Urban_Building_Model.obj")
    mtl_path = os.path.join(out_dir, "Urban_Building_Model.mtl")

    # 1. Rich, Authentic Real-World Material Library (.mtl)
    materials = {
        # Facade Body & Stone Trim
        "Mat_RedBrick":        {"Kd": "0.72 0.32 0.22", "Ks": "0.08 0.08 0.08", "Ns": "10.0", "d": "1.0"}, # Warm Red Brick
        "Mat_LimestoneTrim":   {"Kd": "0.94 0.92 0.86", "Ks": "0.15 0.15 0.15", "Ns": "25.0", "d": "1.0"}, # Crisp Cream Limestone
        "Mat_GroundBaseStone": {"Kd": "0.45 0.48 0.52", "Ks": "0.15 0.15 0.15", "Ns": "20.0", "d": "1.0"}, # Carved Granite Base
        
        # Windows & Glazing
        "Mat_WindowFrameWhite":{"Kd": "0.96 0.96 0.94", "Ks": "0.25 0.25 0.25", "Ns": "35.0", "d": "1.0"}, # Crisp White Sashes
        "Mat_WindowGlassSky":  {"Kd": "0.22 0.60 0.82", "Ks": "0.90 0.90 0.95", "Ns": "95.0", "d": "0.85"}, # Reflective Sky Cyan
        
        # Storefronts & Colorful Awnings
        "Mat_StorefrontWood":  {"Kd": "0.12 0.26 0.18", "Ks": "0.35 0.35 0.35", "Ns": "45.0", "d": "1.0"}, # Dark Emerald Storeframe
        "Mat_AwningBurgundy":  {"Kd": "0.72 0.12 0.18", "Ks": "0.10 0.10 0.10", "Ns": "15.0", "d": "1.0"}, # Wine Red Canvas
        "Mat_AwningNavy":      {"Kd": "0.08 0.26 0.52", "Ks": "0.10 0.10 0.10", "Ns": "15.0", "d": "1.0"}, # Royal Navy Canvas
        "Mat_AwningForest":    {"Kd": "0.12 0.45 0.22", "Ks": "0.10 0.10 0.10", "Ns": "15.0", "d": "1.0"}, # British Racing Green
        "Mat_AwningAmber":     {"Kd": "0.88 0.58 0.12", "Ks": "0.10 0.10 0.10", "Ns": "15.0", "d": "1.0"}, # Mustard Gold Canvas
        
        # Store Signboards
        "Mat_SignBakery":      {"Kd": "0.92 0.82 0.35", "Ks": "0.40 0.40 0.40", "Ns": "50.0", "d": "1.0"}, # Warm Gold Sign
        "Mat_SignPharmacy":    {"Kd": "0.15 0.65 0.85", "Ks": "0.40 0.40 0.40", "Ns": "50.0", "d": "1.0"}, # Cyan Glow Sign
        
        # Accents & Details
        "Mat_FireEscapeBlack": {"Kd": "0.16 0.18 0.20", "Ks": "0.70 0.70 0.75", "Ns": "75.0", "d": "1.0"}, # Satin Black Cast Iron
        "Mat_ACMetalBody":     {"Kd": "0.82 0.84 0.86", "Ks": "0.45 0.45 0.50", "Ns": "55.0", "d": "1.0"}, # Pale Metallic AC
        "Mat_ACGrilleDark":    {"Kd": "0.22 0.24 0.26", "Ks": "0.25 0.25 0.25", "Ns": "30.0", "d": "1.0"}, # Dark Front Grille
        "Mat_WindowAwningWarm":{"Kd": "0.85 0.48 0.18", "Ks": "0.15 0.15 0.15", "Ns": "20.0", "d": "1.0"}, # Terracotta Window Shade
        "Mat_FlowerPetals":    {"Kd": "0.92 0.18 0.35", "Ks": "0.10 0.10 0.10", "Ns": "15.0", "d": "1.0"}, # Blooming Pink/Red Flowers
        "Mat_FlowerFoliage":   {"Kd": "0.18 0.68 0.24", "Ks": "0.08 0.08 0.08", "Ns": "12.0", "d": "1.0"}, # Lush Green Leaves
        
        # Roof & Water Tank
        "Mat_WaterTankWood":   {"Kd": "0.58 0.36 0.20", "Ks": "0.08 0.08 0.08", "Ns": "10.0", "d": "1.0"}, # Cedar Staves
        "Mat_RoofGravel":      {"Kd": "0.38 0.40 0.42", "Ks": "0.08 0.08 0.08", "Ns": "10.0", "d": "1.0"}, # Dark Roof Tar
        
        # Street Infrastructure
        "Mat_SidewalkPaver":   {"Kd": "0.78 0.80 0.82", "Ks": "0.10 0.10 0.10", "Ns": "15.0", "d": "1.0"}, # Sidewalk Concrete
        "Mat_StreetAsphalt":   {"Kd": "0.20 0.22 0.25", "Ks": "0.10 0.10 0.10", "Ns": "15.0", "d": "1.0"}, # Dark Asphalt
        "Mat_RoadMarking":     {"Kd": "0.95 0.95 0.95", "Ks": "0.20 0.20 0.20", "Ns": "25.0", "d": "1.0"}, # White Road Lines
        "Mat_FireHydrantRed":  {"Kd": "0.88 0.10 0.12", "Ks": "0.60 0.60 0.60", "Ns": "65.0", "d": "1.0"}, # Fire Hydrant Red
        "Mat_LamppostBlack":   {"Kd": "0.14 0.16 0.18", "Ks": "0.65 0.65 0.70", "Ns": "70.0", "d": "1.0"}, # Cast Iron Lamp
        "Mat_LampGlowYellow":  {"Kd": "1.00 0.88 0.40", "Ks": "0.85 0.85 0.90", "Ns": "90.0", "d": "1.0"}, # Warm Glowing Lamp
        "Mat_TreeTrunkBrown":  {"Kd": "0.38 0.25 0.15", "Ks": "0.05 0.05 0.05", "Ns": "10.0", "d": "1.0"}, # Tree Trunk
        "Mat_TreeLeafGreen":   {"Kd": "0.16 0.58 0.22", "Ks": "0.08 0.08 0.08", "Ns": "15.0", "d": "1.0"}, # Vibrant Foliage
        
        # BIM Monitoring materials
        "Mat_StatusComplete":  {"Kd": "0.08 0.85 0.40", "Ks": "0.35 0.35 0.35", "Ns": "50.0", "d": "1.0"},
        "Mat_StatusDelayed":   {"Kd": "0.92 0.15 0.12", "Ks": "0.35 0.35 0.35", "Ns": "50.0", "d": "1.0"},
        "Mat_StatusReview":    {"Kd": "0.70 0.22 0.95", "Ks": "0.35 0.35 0.35", "Ns": "50.0", "d": "1.0"},
        "Mat_StatusProgress":  {"Kd": "0.98 0.72 0.10", "Ks": "0.35 0.35 0.35", "Ns": "50.0", "d": "1.0"},
    }

    with open(mtl_path, "w", encoding="utf-8") as f:
        f.write("# Real-World Urban Building Material Library\n\n")
        for name, p in materials.items():
            f.write(f"newmtl {name}\n")
            f.write(f"Kd {p['Kd']}\n")
            f.write(f"Ks {p['Ks']}\n")
            f.write(f"Ns {p['Ns']}\n")
            f.write(f"d {p['d']}\n")
            f.write("illum 2\n\n")

    verts = []
    normals = []
    groups = {}

    def add_normal(nx, ny, nz):
        l = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
        normals.append((nx/l, ny/l, nz/l))
        return len(normals)

    n_up    = add_normal(0, 1, 0)
    n_down  = add_normal(0, -1, 0)
    n_north = add_normal(0, 0, -1)
    n_south = add_normal(0, 0, 1)
    n_east  = add_normal(1, 0, 0)
    n_west  = add_normal(-1, 0, 0)

    def add_box(cx, cy, cz, sx, sy, sz, mat_name):
        if mat_name not in groups:
            groups[mat_name] = []
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        b = len(verts) + 1
        corners = [
            (cx - hx, cy - hy, cz - hz),
            (cx + hx, cy - hy, cz - hz),
            (cx + hx, cy + hy, cz - hz),
            (cx - hx, cy + hy, cz - hz),
            (cx - hx, cy - hy, cz + hz),
            (cx + hx, cy - hy, cz + hz),
            (cx + hx, cy + hy, cz + hz),
            (cx - hx, cy + hy, cz + hz),
        ]
        verts.extend(corners)

        box_faces = [
            (n_south, [b+4, b+5, b+6, b+7]),
            (n_north, [b+1, b+0, b+3, b+2]),
            (n_up,    [b+3, b+7, b+6, b+2]),
            (n_down,  [b+0, b+1, b+5, b+4]),
            (n_east,  [b+1, b+2, b+6, b+5]),
            (n_west,  [b+4, b+7, b+3, b+0]),
        ]
        for _, fv in box_faces:
            groups[mat_name].append(((fv[0], n_south), (fv[1], n_south), (fv[2], n_south)))
            groups[mat_name].append(((fv[0], n_south), (fv[2], n_south), (fv[3], n_south)))

    def add_slanted_awning(cx, cy, cz, sx, sy, sz, mat_name):
        if mat_name not in groups:
            groups[mat_name] = []
        hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
        b = len(verts) + 1
        corners = [
            (cx - hx, cy + hy, cz - hz),
            (cx + hx, cy + hy, cz - hz),
            (cx + hx, cy - hy, cz + hz),
            (cx - hx, cy - hy, cz + hz),
        ]
        verts.extend(corners)
        n_slant = add_normal(0, 0.6, 0.8)
        groups[mat_name].append(((b+0, n_slant), (b+1, n_slant), (b+2, n_slant)))
        groups[mat_name].append(((b+0, n_slant), (b+2, n_slant), (b+3, n_slant)))

    def add_cylinder(cx, cy, cz, radius, height, mat_name, segments=10):
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

        for i in range(segments):
            next_i = (i + 1) % segments
            b1 = bot_verts[i]
            t1 = top_verts[i]
            b2 = bot_verts[next_i]
            t2 = top_verts[next_i]
            n1 = add_normal(math.cos(2*math.pi*i/segments), 0, math.sin(2*math.pi*i/segments))
            n2 = add_normal(math.cos(2*math.pi*next_i/segments), 0, math.sin(2*math.pi*next_i/segments))
            groups[mat_name].append(((b1, n1), (b2, n2), (t2, n2)))
            groups[mat_name].append(((b1, n1), (t2, n2), (t1, n1)))

    print("Synthesizing Colorful Real-World Urban Building...")

    b_w = 16.0
    b_d = 14.0
    h_ground = 3.6
    h_floor = 2.8
    num_upper_floors = 7
    total_roof_y = h_ground + num_upper_floors * h_floor  # 23.2m
    parapet_top = total_roof_y + 1.2
    front_z = -b_d * 0.5
    east_x = b_w * 0.5

    # -------------------------------------------------------------------------
    # 1. STREET & SIDEWALK ENVIRONMENT
    # -------------------------------------------------------------------------
    # Dark Asphalt Street Lane
    add_box(0, -0.25, -12.0, 32.0, 0.2, 10.0, "Mat_StreetAsphalt")
    # White Painted Road Markings (Stripes)
    for rx in range(-12, 14, 4):
        add_box(rx, -0.14, -12.0, 2.4, 0.02, 0.35, "Mat_RoadMarking")

    # Concrete Sidewalk & Curbs
    add_box(0, -0.10, -2.5, 26.0, 0.3, 11.0, "Mat_SidewalkPaver")
    add_box(0, -0.05, -7.9, 26.0, 0.2, 0.25, "Mat_LimestoneTrim") # Curb stone

    # 4 Sidewalk Street Trees
    tree_x_positions = [-11.0, -5.0, 4.0, 11.0]
    for tx in tree_x_positions:
        add_cylinder(tx, 1.4, -9.2, 0.22, 2.8, "Mat_TreeTrunkBrown", 8)
        add_cylinder(tx, 3.2, -9.2, 1.6, 1.8, "Mat_TreeLeafGreen", 8)
        add_cylinder(tx, 4.4, -9.2, 1.2, 1.4, "Mat_TreeLeafGreen", 8)

    # Classic Red Fire Hydrant
    add_cylinder(-8.0, 0.35, -8.6, 0.18, 0.7, "Mat_FireHydrantRed", 8)
    add_box(-8.0, 0.5, -8.6, 0.5, 0.12, 0.18, "Mat_FireHydrantRed")

    # 2 Cast Iron Street Lampposts
    for lx in [-2.0, 8.5]:
        add_cylinder(lx, 2.2, -8.8, 0.09, 4.4, "Mat_LamppostBlack", 8)
        add_box(lx, 4.4, -8.8, 0.45, 0.25, 0.45, "Mat_LamppostBlack")
        add_box(lx, 4.3, -8.8, 0.35, 0.35, 0.35, "Mat_LampGlowYellow") # Glowing lantern

    # -------------------------------------------------------------------------
    # 2. BUILDING BASE & RED BRICK FACADE
    # -------------------------------------------------------------------------
    # Ground Floor Heavy Masonry Plinth
    add_box(0, h_ground * 0.5, 0, b_w, h_ground, b_d, "Mat_GroundBaseStone")

    # Upper 7 Floors: Warm Red Brick Body
    upper_h = num_upper_floors * h_floor
    upper_mid_y = h_ground + upper_h * 0.5
    add_box(0, upper_mid_y, 0, b_w, upper_h, b_d, "Mat_RedBrick")

    # Classical Cream Limestone Belt Cornices
    add_box(0, h_ground + 0.15, front_z - 0.1, b_w + 0.4, 0.32, 0.35, "Mat_LimestoneTrim")
    add_box(0, h_ground + 0.15, -front_z + 0.1, b_w + 0.4, 0.32, 0.35, "Mat_LimestoneTrim")
    add_box(-east_x - 0.1, h_ground + 0.15, 0, 0.35, 0.32, b_d + 0.4, "Mat_LimestoneTrim")
    add_box( east_x + 0.1, h_ground + 0.15, 0, 0.35, 0.32, b_d + 0.4, "Mat_LimestoneTrim")

    # Mid-height Accent Limestone Band (above 4th floor)
    mid_belt_y = h_ground + 3 * h_floor
    add_box(0, mid_belt_y, front_z - 0.05, b_w + 0.2, 0.2, 0.25, "Mat_LimestoneTrim")
    add_box(east_x + 0.05, mid_belt_y, 0, 0.25, 0.2, b_d + 0.2, "Mat_LimestoneTrim")

    # Roof Parapet & Classical Decorative Cornice
    add_box(0, total_roof_y - 0.05, 0, b_w - 0.8, 0.1, b_d - 0.8, "Mat_RoofGravel")
    # Red Brick Parapet Walls
    add_box(0, total_roof_y + 0.6, front_z + 0.2, b_w, 1.2, 0.4, "Mat_RedBrick")
    add_box(0, total_roof_y + 0.6, -front_z - 0.2, b_w, 1.2, 0.4, "Mat_RedBrick")
    add_box(-east_x + 0.2, total_roof_y + 0.6, 0, 0.4, 1.2, b_d, "Mat_RedBrick")
    add_box( east_x - 0.2, total_roof_y + 0.6, 0, 0.4, 1.2, b_d, "Mat_RedBrick")
    # Classical Cream Parapet Coping Trim
    add_box(0, parapet_top + 0.06, front_z + 0.2, b_w + 0.3, 0.12, 0.55, "Mat_LimestoneTrim")
    add_box(0, parapet_top + 0.06, -front_z - 0.2, b_w + 0.3, 0.12, 0.55, "Mat_LimestoneTrim")
    add_box(-east_x + 0.2, parapet_top + 0.06, 0, 0.55, 0.12, b_d + 0.3, "Mat_LimestoneTrim")
    add_box( east_x - 0.2, parapet_top + 0.06, 0, 0.55, 0.12, b_d + 0.3, "Mat_LimestoneTrim")

    # Iconic Rooftop Wooden Water Tank Tower
    wt_x, wt_y, wt_z = -4.0, total_roof_y + 0.5, 2.0
    # Steel Stanchion Legs
    add_cylinder(wt_x - 1.2, wt_y + 1.2, wt_z - 1.2, 0.08, 2.4, "Mat_FireEscapeBlack", 6)
    add_cylinder(wt_x + 1.2, wt_y + 1.2, wt_z - 1.2, 0.08, 2.4, "Mat_FireEscapeBlack", 6)
    add_cylinder(wt_x - 1.2, wt_y + 1.2, wt_z + 1.2, 0.08, 2.4, "Mat_FireEscapeBlack", 6)
    add_cylinder(wt_x + 1.2, wt_y + 1.2, wt_z + 1.2, 0.08, 2.4, "Mat_FireEscapeBlack", 6)
    # Wooden Barrel Body
    add_cylinder(wt_x, wt_y + 3.6, wt_z, 1.6, 2.6, "Mat_WaterTankWood", 12)
    # Steel Hoops
    add_cylinder(wt_x, wt_y + 3.0, wt_z, 1.63, 0.1, "Mat_FireEscapeBlack", 12)
    add_cylinder(wt_x, wt_y + 4.2, wt_z, 1.63, 0.1, "Mat_FireEscapeBlack", 12)
    # Conical Roof Cap
    add_cylinder(wt_x, wt_y + 5.2, wt_z, 1.7, 0.6, "Mat_WaterTankWood", 12)

    # -------------------------------------------------------------------------
    # 3. COLORFUL GROUND FLOOR STOREFRONTS & AWNINGS
    # -------------------------------------------------------------------------
    shop_x = [-5.4, -1.8, 1.8, 5.4]
    awnings = ["Mat_AwningBurgundy", "Mat_AwningNavy", "Mat_AwningForest", "Mat_AwningAmber"]
    signs   = ["Mat_SignBakery", "Mat_SignPharmacy", "Mat_LimestoneTrim", "Mat_LimestoneTrim"]

    for i in range(4):
        bx = shop_x[i]
        # Dark Wooden Frame & Large Glass
        add_box(bx, 1.6, front_z + 0.05, 3.1, 2.4, 0.15, "Mat_StorefrontWood")
        add_box(bx, 1.6, front_z + 0.02, 2.9, 2.2, 0.08, "Mat_WindowGlassSky")
        # Store Signboard
        add_box(bx, 3.1, front_z - 0.15, 3.2, 0.55, 0.2, signs[i])
        # Vibrant Slanted Fabric Awning
        add_slanted_awning(bx, 2.4, front_z - 0.65, 3.3, 0.6, 1.1, awnings[i])

    # Side Storefronts wrapping around East facade
    side_bays_z = [-4.5, -1.5, 1.5, 4.5]
    side_awnings = ["Mat_AwningNavy", "Mat_AwningBurgundy", "Mat_AwningForest", "Mat_AwningAmber"]
    for i in range(4):
        sz = side_bays_z[i]
        add_box(east_x - 0.05, 1.6, sz, 0.15, 2.4, 2.5, "Mat_StorefrontWood")
        add_box(east_x - 0.02, 1.6, sz, 0.08, 2.2, 2.3, "Mat_WindowGlassSky")
        add_box(east_x + 0.15, 3.1, sz, 0.2, 0.55, 2.6, "Mat_LimestoneTrim")
        add_slanted_awning(east_x + 0.65, 2.4, sz, 1.1, 0.6, 2.6, side_awnings[i])

    # -------------------------------------------------------------------------
    # 4. UPPER WINDOWS: 49 WINDOWS WITH WHITE SASHES, BLUE GLASS & FLOWERS
    # -------------------------------------------------------------------------
    col_x_front = [-5.7, -3.8, -1.9, 0.0, 1.9, 3.8, 5.7]
    win_w = 1.05
    win_h = 1.45

    ac_spots_front = {
        (1, 0), (2, 3), (2, 5), (3, 1), (4, 2), (4, 6), (5, 1), (5, 4), (6, 5)
    }
    awning_spots_front = {
        (2, 4), (3, 2), (5, 3), (6, 6)
    }
    # Flower box spots for cheerful residential color
    flower_spots = {
        (1, 2), (1, 4), (3, 0), (3, 5), (4, 3), (5, 6)
    }

    for fl in range(num_upper_floors):
        fl_y = h_ground + fl * h_floor + 1.4

        for c_idx, cx in enumerate(col_x_front):
            # 1. White Window Outer Frame / Lintel
            add_box(cx, fl_y, front_z + 0.04, win_w + 0.15, win_h + 0.15, 0.14, "Mat_WindowFrameWhite")
            # 2. Reflective Sky Glass Pane
            add_box(cx, fl_y, front_z + 0.02, win_w - 0.1, win_h - 0.1, 0.06, "Mat_WindowGlassSky")
            # 3. Limestone Window Sill Ledge
            add_box(cx, fl_y - win_h*0.5 - 0.05, front_z - 0.08, win_w + 0.25, 0.12, 0.22, "Mat_LimestoneTrim")

            # 4. Realistic Window AC Units (Pale Metallic Body + Dark Grille)
            if (fl, c_idx) in ac_spots_front:
                ac_y = fl_y - win_h * 0.25
                add_box(cx, ac_y, front_z - 0.35, 0.65, 0.45, 0.55, "Mat_ACMetalBody")
                add_box(cx, ac_y, front_z - 0.63, 0.55, 0.38, 0.03, "Mat_ACGrilleDark") # Grille face
                add_box(cx - 0.22, ac_y - 0.26, front_z - 0.25, 0.05, 0.15, 0.35, "Mat_FireEscapeBlack")
                add_box(cx + 0.22, ac_y - 0.26, front_z - 0.25, 0.05, 0.15, 0.35, "Mat_FireEscapeBlack")

            # 5. Terracotta Window Awnings
            if (fl, c_idx) in awning_spots_front:
                add_slanted_awning(cx, fl_y + win_h * 0.45, front_z - 0.3, win_w + 0.15, 0.35, 0.55, "Mat_WindowAwningWarm")

            # 6. Charming Flower Boxes with Colorful Blossoms
            if (fl, c_idx) in flower_spots:
                box_y = fl_y - win_h * 0.5 + 0.08
                add_box(cx, box_y, front_z - 0.22, win_w, 0.22, 0.28, "Mat_WaterTankWood") # Planter box
                add_box(cx, box_y + 0.12, front_z - 0.22, win_w - 0.1, 0.15, 0.24, "Mat_FlowerFoliage") # Green leaves
                # Red/Pink Flower blossoms
                add_box(cx - 0.25, box_y + 0.20, front_z - 0.22, 0.2, 0.08, 0.18, "Mat_FlowerPetals")
                add_box(cx + 0.25, box_y + 0.20, front_z - 0.22, 0.2, 0.08, 0.18, "Mat_FlowerPetals")

    # Attic Vents (7 Square Openings with White Trim)
    vent_y = total_roof_y - 0.8
    for cx in col_x_front:
        add_box(cx, vent_y, front_z + 0.04, 0.5, 0.5, 0.1, "Mat_LimestoneTrim")

    # -------------------------------------------------------------------------
    # 5. SIDE FACADE WINDOWS (EAST, X = 8.0)
    # -------------------------------------------------------------------------
    side_col_z = [-5.0, -2.5, 0.0, 2.5, 5.0]
    for fl in range(num_upper_floors):
        fl_y = h_ground + fl * h_floor + 1.4
        for cz in side_col_z:
            add_box(east_x - 0.04, fl_y, cz, 0.14, win_h + 0.15, win_w + 0.15, "Mat_WindowFrameWhite")
            add_box(east_x - 0.02, fl_y, cz, 0.06, win_h - 0.1, win_w - 0.1, "Mat_WindowGlassSky")
            add_box(east_x + 0.08, fl_y - win_h*0.5 - 0.05, cz, 0.22, 0.12, win_w + 0.25, "Mat_LimestoneTrim")

            if (fl == 2 and cz == 0.0) or (fl == 5 and cz == 2.5):
                add_box(east_x + 0.35, fl_y - win_h*0.25, cz, 0.55, 0.45, 0.65, "Mat_ACMetalBody")
                add_box(east_x + 0.63, fl_y - win_h*0.25, cz, 0.03, 0.38, 0.55, "Mat_ACGrilleDark")

    # -------------------------------------------------------------------------
    # 6. EXTERNAL BLACK CAST-IRON FIRE ESCAPE STAIRCASE (FRONT-RIGHT CORNER)
    # -------------------------------------------------------------------------
    fe_x = 7.1
    fe_z = front_z - 0.7

    for fl in range(num_upper_floors):
        plat_y = h_ground + fl * h_floor + 0.1
        plat_w = 1.3
        plat_d = 1.0

        # Metal Floor Grating Platform (Satin Black Cast Iron)
        add_box(fe_x, plat_y, fe_z, plat_w, 0.06, plat_d, "Mat_FireEscapeBlack")

        # Platform Safety Railings (0.9m height)
        add_box(fe_x, plat_y + 0.45, fe_z - plat_d*0.5, plat_w, 0.9, 0.04, "Mat_FireEscapeBlack")
        add_box(fe_x + plat_w*0.5, plat_y + 0.45, fe_z, 0.04, 0.9, plat_d, "Mat_FireEscapeBlack")
        add_box(fe_x - plat_w*0.5, plat_y + 0.45, fe_z, 0.04, 0.9, plat_d, "Mat_FireEscapeBlack")

        # Alternating Zig-Zag Diagonal Stair Flights
        if fl < num_upper_floors - 1:
            stair_y_mid = plat_y + h_floor * 0.5
            dir_sign = 1 if (fl % 2 == 0) else -1
            stair_x_mid = fe_x - 0.7 * dir_sign

            add_box(stair_x_mid, stair_y_mid, fe_z, 1.2, h_floor - 0.2, 0.5, "Mat_FireEscapeBlack")
            add_box(stair_x_mid, stair_y_mid + 0.5, fe_z - 0.25, 1.2, h_floor - 0.2, 0.04, "Mat_FireEscapeBlack")

    # Top Roof Access Ladder
    top_fe_y = h_ground + (num_upper_floors - 1) * h_floor + 0.1
    add_box(fe_x, top_fe_y + 1.8, fe_z, 0.5, 2.6, 0.08, "Mat_FireEscapeBlack")

    # -------------------------------------------------------------------------
    # 7. WRITE TO WAVEFRONT OBJ
    # -------------------------------------------------------------------------
    print(f"Total Vertices: {len(verts)}, Faces Count: {sum(len(f) for f in groups.values())}")
    with open(obj_path, "w", encoding="utf-8") as f:
        f.write("# BuildLens 4D - Colorful Real-World Urban Building\n")
        f.write("mtllib Urban_Building_Model.mtl\n\n")

        for vx, vy, vz in verts:
            f.write(f"v {vx:.4f} {vy:.4f} {vz:.4f}\n")
        f.write("\n")

        for nx, ny, nz in normals:
            f.write(f"vn {nx:.4f} {ny:.4f} {nz:.4f}\n")

        for mat_name, face_list in groups.items():
            f.write(f"\nusemtl {mat_name}\n")
            f.write(f"g Group_{mat_name}\n")
            for f_tri in face_list:
                f.write(f"f {f_tri[0][0]}//{f_tri[0][1]} {f_tri[1][0]}//{f_tri[1][1]} {f_tri[2][0]}//{f_tri[2][1]}\n")

    print(f"Successfully generated colorful urban model at: {obj_path}")

if __name__ == "__main__":
    build_urban_building()
