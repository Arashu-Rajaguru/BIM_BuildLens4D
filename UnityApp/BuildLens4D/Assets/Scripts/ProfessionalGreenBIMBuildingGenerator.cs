using System;
using UnityEngine;
using BuildLens4D.BIM;

namespace BuildLens4D.Building
{
    /// <summary>
    /// Authentic Colorful Urban Mid-Rise Building Generator for BuildLens 4D.
    /// Recreates the real-world architectural building from the reference image with:
    /// - Warm red brick facade with crisp cream limestone belt cornices & window lintels
    /// - Ground floor commercial storefront arcade with colorful fabric awnings (Burgundy, Navy, Forest, Amber)
    /// - 7 upper floors with 7 columns of punched rectangular windows (49 windows) with white frames & sky-blue glass
    /// - Colorful window flower boxes with blooming blossoms and leafy greens
    /// - Authentic metallic window AC units with front ventilation grilles
    /// - Exterior satin black cast-iron zig-zag fire escape staircase on the front-right corner
    /// - Iconic rooftop cedar water tank tower on steel stanchions
    /// - Streetscape: concrete paver sidewalk, dark asphalt road with white stripes, 4 street trees, red fire hydrant, lampposts
    /// - 4D BIM progress status tracking elements and 3D callouts
    /// Collision-free for 100% unrestricted 6-DOF fly navigation!
    /// </summary>
    [ExecuteAlways]
    public class ProfessionalGreenBIMBuildingGenerator : MonoBehaviour
    {
        [Header("Generator Configuration")]
        [SerializeField] private bool generateOnStart = true;

        // Rich Architectural Materials
        private Material matRedBrick;
        private Material matLimestoneTrim;
        private Material matGroundBaseStone;
        private Material matWindowFrameWhite;
        private Material matWindowGlassSky;
        private Material matStorefrontWood;

        private Material matAwningBurgundy;
        private Material matAwningNavy;
        private Material matAwningForest;
        private Material matAwningAmber;

        private Material matSignBakery;
        private Material matSignPharmacy;

        private Material matFireEscapeBlack;
        private Material matACMetalBody;
        private Material matACGrilleDark;
        private Material matWindowAwningWarm;
        private Material matFlowerPetals;
        private Material matFlowerFoliage;

        private Material matWaterTankWood;
        private Material matRoofGravel;
        private Material matSidewalkPaver;
        private Material matStreetAsphalt;
        private Material matRoadMarking;
        private Material matFireHydrantRed;
        private Material matLamppostBlack;
        private Material matLampGlowYellow;
        private Material matTreeTrunkBrown;
        private Material matTreeLeafGreen;

        // BIM Status Materials
        private Material matStatusComplete;
        private Material matStatusDelayed;
        private Material matStatusReview;
        private Material matStatusProgress;

        private void Start()
        {
            InitializeMaterials();
            if (generateOnStart && transform.childCount == 0)
            {
                GenerateGreenBuildingModel();
            }
        }

        private void OnEnable()
        {
            if (transform.childCount == 0)
            {
                InitializeMaterials();
                GenerateGreenBuildingModel();
            }
        }

        private void InitializeMaterials()
        {
            Shader shader = Shader.Find("Standard") ?? Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Sprites/Default");

            // 1. Facade & Stone Accents
            matRedBrick = CreateMat(shader, "Mat_RedBrick", new Color(0.72f, 0.32f, 0.22f), 0.05f, 0.20f);
            matLimestoneTrim = CreateMat(shader, "Mat_LimestoneTrim", new Color(0.95f, 0.93f, 0.88f), 0.10f, 0.35f);
            matGroundBaseStone = CreateMat(shader, "Mat_GroundBaseStone", new Color(0.45f, 0.48f, 0.52f), 0.15f, 0.25f);

            // 2. Windows & Glass
            matWindowFrameWhite = CreateMat(shader, "Mat_WindowFrameWhite", new Color(0.98f, 0.98f, 0.96f), 0.20f, 0.40f);
            matWindowGlassSky = CreateMat(shader, "Mat_WindowGlassSky", new Color(0.20f, 0.62f, 0.85f, 0.90f), 0.85f, 0.95f);
            matStorefrontWood = CreateMat(shader, "Mat_StorefrontWood", new Color(0.12f, 0.25f, 0.18f), 0.30f, 0.45f);

            // 3. Colorful Storefront Awnings
            matAwningBurgundy = CreateMat(shader, "Mat_AwningBurgundy", new Color(0.72f, 0.12f, 0.18f), 0.10f, 0.20f);
            matAwningNavy = CreateMat(shader, "Mat_AwningNavy", new Color(0.08f, 0.26f, 0.52f), 0.10f, 0.20f);
            matAwningForest = CreateMat(shader, "Mat_AwningForest", new Color(0.12f, 0.45f, 0.22f), 0.10f, 0.20f);
            matAwningAmber = CreateMat(shader, "Mat_AwningAmber", new Color(0.88f, 0.58f, 0.12f), 0.10f, 0.20f);

            // 4. Store Signboards
            matSignBakery = CreateMat(shader, "Mat_SignBakery", new Color(0.92f, 0.82f, 0.35f), 0.40f, 0.50f);
            matSignPharmacy = CreateMat(shader, "Mat_SignPharmacy", new Color(0.15f, 0.65f, 0.85f), 0.40f, 0.50f);

            // 5. Fire Escape, AC & Window Details
            matFireEscapeBlack = CreateMat(shader, "Mat_FireEscapeBlack", new Color(0.16f, 0.18f, 0.20f), 0.70f, 0.70f);
            matACMetalBody = CreateMat(shader, "Mat_ACMetalBody", new Color(0.82f, 0.84f, 0.86f), 0.45f, 0.55f);
            matACGrilleDark = CreateMat(shader, "Mat_ACGrilleDark", new Color(0.22f, 0.24f, 0.26f), 0.25f, 0.30f);
            matWindowAwningWarm = CreateMat(shader, "Mat_WindowAwningWarm", new Color(0.85f, 0.48f, 0.18f), 0.15f, 0.25f);
            matFlowerPetals = CreateMat(shader, "Mat_FlowerPetals", new Color(0.92f, 0.18f, 0.35f), 0.10f, 0.20f);
            matFlowerFoliage = CreateMat(shader, "Mat_FlowerFoliage", new Color(0.18f, 0.68f, 0.24f), 0.08f, 0.20f);

            // 6. Roof & Streetscape
            matWaterTankWood = CreateMat(shader, "Mat_WaterTankWood", new Color(0.58f, 0.36f, 0.20f), 0.08f, 0.20f);
            matRoofGravel = CreateMat(shader, "Mat_RoofGravel", new Color(0.38f, 0.40f, 0.42f), 0.08f, 0.15f);
            matSidewalkPaver = CreateMat(shader, "Mat_SidewalkPaver", new Color(0.80f, 0.82f, 0.84f), 0.10f, 0.20f);
            matStreetAsphalt = CreateMat(shader, "Mat_StreetAsphalt", new Color(0.20f, 0.22f, 0.25f), 0.10f, 0.15f);
            matRoadMarking = CreateMat(shader, "Mat_RoadMarking", new Color(0.96f, 0.96f, 0.96f), 0.20f, 0.30f);
            matFireHydrantRed = CreateMat(shader, "Mat_FireHydrantRed", new Color(0.88f, 0.10f, 0.12f), 0.60f, 0.65f);
            matLamppostBlack = CreateMat(shader, "Mat_LamppostBlack", new Color(0.14f, 0.16f, 0.18f), 0.65f, 0.70f);
            matLampGlowYellow = CreateMat(shader, "Mat_LampGlowYellow", new Color(1.00f, 0.88f, 0.40f), 0.85f, 0.90f);
            matTreeTrunkBrown = CreateMat(shader, "Mat_TreeTrunkBrown", new Color(0.38f, 0.25f, 0.15f), 0.05f, 0.15f);
            matTreeLeafGreen = CreateMat(shader, "Mat_TreeLeafGreen", new Color(0.16f, 0.58f, 0.22f), 0.08f, 0.20f);

            // 7. 4D BIM Status Indicators
            matStatusComplete = CreateMat(shader, "Mat_StatusComplete", new Color(0.08f, 0.85f, 0.40f), 0.35f, 0.50f);
            matStatusDelayed = CreateMat(shader, "Mat_StatusDelayed", new Color(0.92f, 0.15f, 0.12f), 0.35f, 0.50f);
            matStatusReview = CreateMat(shader, "Mat_StatusReview", new Color(0.70f, 0.22f, 0.95f), 0.35f, 0.50f);
            matStatusProgress = CreateMat(shader, "Mat_StatusProgress", new Color(0.98f, 0.72f, 0.10f), 0.35f, 0.50f);
        }

        private Material CreateMat(Shader s, string name, Color color, float metallic, float smoothness)
        {
            Material mat = new Material(s);
            mat.name = name;
            if (mat.HasProperty("_Color")) mat.color = color;
            if (mat.HasProperty("_Metallic")) mat.SetFloat("_Metallic", metallic);
            if (mat.HasProperty("_Glossiness")) mat.SetFloat("_Glossiness", smoothness);
            return mat;
        }

        [ContextMenu("Generate Authentic Colorful Urban Building")]
        public void GenerateGreenBuildingModel()
        {
            if (matRedBrick == null) InitializeMaterials();

            // Clear old children under this generator
            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                DestroyImmediate(transform.GetChild(i).gameObject);
            }

            GameObject buildingRoot = new GameObject("[Urban_Building_Complex]");
            buildingRoot.transform.SetParent(transform, false);

            Debug.Log("[BuildLens 4D] Constructing Authentic Colorful Urban Building...");

            // Building Dimensions
            float bW = 16.0f;  // Width (X: -8 to +8)
            float bD = 14.0f;  // Depth (Z: -7 to +7)
            float hGround = 3.6f;
            float hFloor = 2.8f;
            int numUpperFloors = 7;
            float totalRoofY = hGround + numUpperFloors * hFloor; // 23.2m
            float parapetTop = totalRoofY + 1.2f;                // 24.4m
            float frontZ = -bD * 0.5f;                           // -7.0m
            float eastX = bW * 0.5f;                             // +8.0m

            // -------------------------------------------------------------------------
            // 1. STREET & SIDEWALK ENVIRONMENT
            // -------------------------------------------------------------------------
            GameObject streetGroup = new GameObject("00_Street_And_Sidewalk");
            streetGroup.transform.SetParent(buildingRoot.transform, false);

            // Dark Asphalt Road
            CreateBox("Street_Asphalt", streetGroup, new Vector3(0, -0.25f, -12.0f), new Vector3(32.0f, 0.2f, 10.0f), matStreetAsphalt);

            // White Road Lane Markings
            for (int rx = -12; rx <= 12; rx += 4)
            {
                CreateBox($"Road_Stripe_{rx}", streetGroup, new Vector3(rx, -0.14f, -12.0f), new Vector3(2.4f, 0.02f, 0.35f), matRoadMarking);
            }

            // Concrete Sidewalk & Curb Stone
            CreateBox("Sidewalk_Pavers", streetGroup, new Vector3(0, -0.10f, -2.5f), new Vector3(26.0f, 0.3f, 11.0f), matSidewalkPaver);
            CreateBox("Sidewalk_Curb", streetGroup, new Vector3(0, -0.05f, -7.9f), new Vector3(26.0f, 0.2f, 0.25f), matLimestoneTrim);

            // 4 Sidewalk Street Trees
            float[] treeX = { -11.0f, -5.0f, 4.0f, 11.0f };
            foreach (var tx in treeX)
            {
                CreateCylinder($"TreeTrunk_{tx}", streetGroup, new Vector3(tx, 1.4f, -9.2f), 0.22f, 2.8f, matTreeTrunkBrown);
                CreateCylinder($"TreeLeaf_1_{tx}", streetGroup, new Vector3(tx, 3.2f, -9.2f), 1.6f, 1.8f, matTreeLeafGreen);
                CreateCylinder($"TreeLeaf_2_{tx}", streetGroup, new Vector3(tx, 4.4f, -9.2f), 1.2f, 1.4f, matTreeLeafGreen);
            }

            // Red Fire Hydrant
            CreateCylinder("Fire_Hydrant_Base", streetGroup, new Vector3(-8.0f, 0.35f, -8.6f), 0.18f, 0.7f, matFireHydrantRed);
            CreateBox("Fire_Hydrant_Top", streetGroup, new Vector3(-8.0f, 0.5f, -8.6f), new Vector3(0.5f, 0.12f, 0.18f), matFireHydrantRed);

            // 2 Street Lampposts with Glowing Lanterns
            float[] lampX = { -2.0f, 8.5f };
            foreach (var lx in lampX)
            {
                CreateCylinder($"Lamppost_Pole_{lx}", streetGroup, new Vector3(lx, 2.2f, -8.8f), 0.09f, 4.4f, matLamppostBlack);
                CreateBox($"Lamppost_Cap_{lx}", streetGroup, new Vector3(lx, 4.4f, -8.8f), new Vector3(0.45f, 0.25f, 0.45f), matLamppostBlack);
                CreateBox($"Lamppost_Glow_{lx}", streetGroup, new Vector3(lx, 4.3f, -8.8f), new Vector3(0.35f, 0.35f, 0.35f), matLampGlowYellow);
            }

            // -------------------------------------------------------------------------
            // 2. RED BRICK FACADE & CARVED LIMESTONE DETAILS
            // -------------------------------------------------------------------------
            GameObject buildingGroup = new GameObject("01_Building_Architecture");
            buildingGroup.transform.SetParent(buildingRoot.transform, false);

            // Ground Floor Heavy Granite Base
            CreateBox("Ground_Granite_Base", buildingGroup, new Vector3(0, hGround * 0.5f, 0), new Vector3(bW, hGround, bD), matGroundBaseStone);

            // Upper 7 Floors: Warm Red Brick Body
            float upperH = numUpperFloors * hFloor;
            float upperMidY = hGround + upperH * 0.5f;
            CreateBox("Upper_Red_Brick_Body", buildingGroup, new Vector3(0, upperMidY, 0), new Vector3(bW, upperH, bD), matRedBrick);

            // Classical Limestone Belt Cornices
            CreateBox("Belt_Cornice_South", buildingGroup, new Vector3(0, hGround + 0.15f, frontZ - 0.1f), new Vector3(bW + 0.4f, 0.32f, 0.35f), matLimestoneTrim);
            CreateBox("Belt_Cornice_East",  buildingGroup, new Vector3(eastX + 0.1f, hGround + 0.15f, 0), new Vector3(0.35f, 0.32f, bD + 0.4f), matLimestoneTrim);

            // Mid-Height Limestone Accent Band (Above Level 4)
            float midBeltY = hGround + 3 * hFloor;
            CreateBox("Mid_Belt_South", buildingGroup, new Vector3(0, midBeltY, frontZ - 0.05f), new Vector3(bW + 0.2f, 0.2f, 0.25f), matLimestoneTrim);
            CreateBox("Mid_Belt_East",  buildingGroup, new Vector3(eastX + 0.05f, midBeltY, 0), new Vector3(0.25f, 0.2f, bD + 0.2f), matLimestoneTrim);

            // Roof Parapet Walls & Classical Coping Trim
            CreateBox("Roof_Gravel_Deck", buildingGroup, new Vector3(0, totalRoofY - 0.05f, 0), new Vector3(bW - 0.8f, 0.1f, bD - 0.8f), matRoofGravel);
            CreateBox("Parapet_Wall_South", buildingGroup, new Vector3(0, totalRoofY + 0.6f, frontZ + 0.2f), new Vector3(bW, 1.2f, 0.4f), matRedBrick);
            CreateBox("Parapet_Wall_East",  buildingGroup, new Vector3(eastX - 0.2f, totalRoofY + 0.6f, 0), new Vector3(0.4f, 1.2f, bD), matRedBrick);

            CreateBox("Parapet_Coping_South", buildingGroup, new Vector3(0, parapetTop + 0.06f, frontZ + 0.2f), new Vector3(bW + 0.3f, 0.12f, 0.55f), matLimestoneTrim);
            CreateBox("Parapet_Coping_East",  buildingGroup, new Vector3(eastX - 0.2f, parapetTop + 0.06f, 0), new Vector3(0.55f, 0.12f, bD + 0.3f), matLimestoneTrim);

            // Iconic Rooftop Wooden Water Tank Tower
            float wtX = -4.0f, wtY = totalRoofY + 0.5f, wtZ = 2.0f;
            CreateCylinder("WT_Leg_1", buildingGroup, new Vector3(wtX - 1.2f, wtY + 1.2f, wtZ - 1.2f), 0.08f, 2.4f, matFireEscapeBlack);
            CreateCylinder("WT_Leg_2", buildingGroup, new Vector3(wtX + 1.2f, wtY + 1.2f, wtZ - 1.2f), 0.08f, 2.4f, matFireEscapeBlack);
            CreateCylinder("WT_Leg_3", buildingGroup, new Vector3(wtX - 1.2f, wtY + 1.2f, wtZ + 1.2f), 0.08f, 2.4f, matFireEscapeBlack);
            CreateCylinder("WT_Leg_4", buildingGroup, new Vector3(wtX + 1.2f, wtY + 1.2f, wtZ + 1.2f), 0.08f, 2.4f, matFireEscapeBlack);
            CreateCylinder("WT_Barrel", buildingGroup, new Vector3(wtX, wtY + 3.6f, wtZ), 1.6f, 2.6f, matWaterTankWood);
            CreateCylinder("WT_Cap", buildingGroup, new Vector3(wtX, wtY + 5.2f, wtZ), 1.7f, 0.6f, matWaterTankWood);

            // -------------------------------------------------------------------------
            // 3. COLORFUL STOREFRONTS & FABRIC AWNINGS
            // -------------------------------------------------------------------------
            GameObject storefrontGroup = new GameObject("02_Storefronts_Colorful");
            storefrontGroup.transform.SetParent(buildingRoot.transform, false);

            float[] shopX = { -5.4f, -1.8f, 1.8f, 5.4f };
            Material[] awnings = { matAwningBurgundy, matAwningNavy, matAwningForest, matAwningAmber };
            Material[] signs = { matSignBakery, matSignPharmacy, matLimestoneTrim, matLimestoneTrim };

            for (int i = 0; i < 4; i++)
            {
                float bx = shopX[i];
                // Dark Emerald Wooden Window Frame & Display Glazing
                CreateBox($"Shop_Frame_{i}", storefrontGroup, new Vector3(bx, 1.6f, frontZ + 0.05f), new Vector3(3.1f, 2.4f, 0.15f), matStorefrontWood);
                CreateBox($"Shop_Glass_{i}", storefrontGroup, new Vector3(bx, 1.6f, frontZ + 0.02f), new Vector3(2.9f, 2.2f, 0.08f), matWindowGlassSky);
                // Signboard
                CreateBox($"Shop_Sign_{i}", storefrontGroup, new Vector3(bx, 3.1f, frontZ - 0.15f), new Vector3(3.2f, 0.55f, 0.2f), signs[i]);
                // Vibrant Slanted Awning
                CreateAwning($"Shop_Awning_{i}", storefrontGroup, new Vector3(bx, 2.4f, frontZ - 0.65f), new Vector3(3.3f, 0.6f, 1.1f), awnings[i]);
            }

            // Side Storefronts wrapping around East facade
            float[] sideBaysZ = { -4.5f, -1.5f, 1.5f, 4.5f };
            Material[] sideAwnings = { matAwningNavy, matAwningBurgundy, matAwningForest, matAwningAmber };
            for (int i = 0; i < 4; i++)
            {
                float sz = sideBaysZ[i];
                CreateBox($"Side_Shop_Frame_{i}", storefrontGroup, new Vector3(eastX - 0.05f, 1.6f, sz), new Vector3(0.15f, 2.4f, 2.5f), matStorefrontWood);
                CreateBox($"Side_Shop_Glass_{i}", storefrontGroup, new Vector3(eastX - 0.02f, 1.6f, sz), new Vector3(0.08f, 2.2f, 2.3f), matWindowGlassSky);
                CreateBox($"Side_Shop_Sign_{i}", storefrontGroup, new Vector3(eastX + 0.15f, 3.1f, sz), new Vector3(0.2f, 0.55f, 2.6f), matLimestoneTrim);
                CreateAwning($"Side_Shop_Awning_{i}", storefrontGroup, new Vector3(eastX + 0.65f, 2.4f, sz), new Vector3(1.1f, 0.6f, 2.6f), sideAwnings[i]);
            }

            // -------------------------------------------------------------------------
            // 4. UPPER WINDOWS: 49 WINDOWS WITH WHITE SASHES, BLUE GLASS & FLOWERS
            // -------------------------------------------------------------------------
            GameObject windowsGroup = new GameObject("03_Upper_Windows_Grid");
            windowsGroup.transform.SetParent(buildingRoot.transform, false);

            float[] colXFront = { -5.7f, -3.8f, -1.9f, 0.0f, 1.9f, 3.8f, 5.7f };
            float winW = 1.05f;
            float winH = 1.45f;

            bool[,] hasAC = new bool[numUpperFloors, colXFront.Length];
            hasAC[1, 0] = true; hasAC[2, 3] = true; hasAC[2, 5] = true;
            hasAC[3, 1] = true; hasAC[4, 2] = true; hasAC[4, 6] = true;
            hasAC[5, 1] = true; hasAC[5, 4] = true; hasAC[6, 5] = true;

            bool[,] hasAwning = new bool[numUpperFloors, colXFront.Length];
            hasAwning[2, 4] = true; hasAwning[3, 2] = true;
            hasAwning[5, 3] = true; hasAwning[6, 6] = true;

            bool[,] hasFlowers = new bool[numUpperFloors, colXFront.Length];
            hasFlowers[1, 2] = true; hasFlowers[1, 4] = true;
            hasFlowers[3, 0] = true; hasFlowers[3, 5] = true;
            hasFlowers[4, 3] = true; hasFlowers[5, 6] = true;

            for (int fl = 0; fl < numUpperFloors; fl++)
            {
                float flY = hGround + fl * hFloor + 1.4f;

                for (int c = 0; c < colXFront.Length; c++)
                {
                    float cx = colXFront[c];

                    // Crisp White Window Frame / Lintel
                    CreateBox($"WinFrame_L{fl+2}_{c}", windowsGroup, new Vector3(cx, flY, frontZ + 0.04f), new Vector3(winW + 0.15f, winH + 0.15f, 0.14f), matWindowFrameWhite);
                    // Reflective Sky Blue Glass
                    CreateBox($"WinGlass_L{fl+2}_{c}", windowsGroup, new Vector3(cx, flY, frontZ + 0.02f), new Vector3(winW - 0.1f, winH - 0.1f, 0.06f), matWindowGlassSky);
                    // Limestone Window Sill
                    CreateBox($"WinSill_L{fl+2}_{c}", windowsGroup, new Vector3(cx, flY - winH * 0.5f - 0.05f, frontZ - 0.08f), new Vector3(winW + 0.25f, 0.12f, 0.22f), matLimestoneTrim);

                    // Metallic Window AC Units (with dark grille face)
                    if (hasAC[fl, c])
                    {
                        float acY = flY - winH * 0.25f;
                        GameObject acNode = CreateBox($"AC_Body_L{fl+2}_{c}", windowsGroup, new Vector3(cx, acY, frontZ - 0.35f), new Vector3(0.65f, 0.45f, 0.55f), matACMetalBody);
                        CreateBox("AC_Grille", acNode, new Vector3(cx, acY, frontZ - 0.63f), new Vector3(0.55f, 0.38f, 0.03f), matACGrilleDark);
                        CreateBox("Bracket_L", acNode, new Vector3(cx - 0.22f, acY - 0.26f, frontZ - 0.25f), new Vector3(0.05f, 0.15f, 0.35f), matFireEscapeBlack);
                        CreateBox("Bracket_R", acNode, new Vector3(cx + 0.22f, acY - 0.26f, frontZ - 0.25f), new Vector3(0.05f, 0.15f, 0.35f), matFireEscapeBlack);
                    }

                    // Terracotta Window Sunshade Awnings
                    if (hasAwning[fl, c])
                    {
                        CreateAwning($"WinAwning_L{fl+2}_{c}", windowsGroup, new Vector3(cx, flY + winH * 0.45f, frontZ - 0.3f), new Vector3(winW + 0.15f, 0.35f, 0.55f), matWindowAwningWarm);
                    }

                    // Colorful Window Flower Planter Boxes
                    if (hasFlowers[fl, c])
                    {
                        float boxY = flY - winH * 0.5f + 0.08f;
                        CreateBox($"FlowerBox_L{fl+2}_{c}", windowsGroup, new Vector3(cx, boxY, frontZ - 0.22f), new Vector3(winW, 0.22f, 0.28f), matWaterTankWood);
                        CreateBox($"FlowerLeaves_L{fl+2}_{c}", windowsGroup, new Vector3(cx, boxY + 0.12f, frontZ - 0.22f), new Vector3(winW - 0.1f, 0.15f, 0.24f), matFlowerFoliage);
                        CreateBox($"FlowerBlossoms_L{fl+2}_{c}", windowsGroup, new Vector3(cx, boxY + 0.20f, frontZ - 0.22f), new Vector3(winW - 0.3f, 0.08f, 0.18f), matFlowerPetals);
                    }
                }
            }

            // Attic Vents (7 Square Openings with White Trim)
            float ventY = totalRoofY - 0.8f;
            for (int c = 0; c < colXFront.Length; c++)
            {
                CreateBox($"AtticVent_{c}", windowsGroup, new Vector3(colXFront[c], ventY, frontZ + 0.04f), new Vector3(0.5f, 0.5f, 0.1f), matLimestoneTrim);
            }

            // -------------------------------------------------------------------------
            // 5. SIDE FACADE WINDOWS (EAST, X = 8.0)
            // -------------------------------------------------------------------------
            GameObject sideWinGroup = new GameObject("04_Side_Windows");
            sideWinGroup.transform.SetParent(buildingRoot.transform, false);

            float[] sideColZ = { -5.0f, -2.5f, 0.0f, 2.5f, 5.0f };
            for (int fl = 0; fl < numUpperFloors; fl++)
            {
                float flY = hGround + fl * hFloor + 1.4f;
                for (int s = 0; s < sideColZ.Length; s++)
                {
                    float cz = sideColZ[s];
                    CreateBox($"SideWinFrame_L{fl+2}_{s}", sideWinGroup, new Vector3(eastX - 0.04f, flY, cz), new Vector3(0.14f, winH + 0.15f, winW + 0.15f), matWindowFrameWhite);
                    CreateBox($"SideWinGlass_L{fl+2}_{s}", sideWinGroup, new Vector3(eastX - 0.02f, flY, cz), new Vector3(0.06f, winH - 0.1f, winW - 0.1f), matWindowGlassSky);
                    CreateBox($"SideWinSill_L{fl+2}_{s}", sideWinGroup, new Vector3(eastX + 0.08f, flY - winH * 0.5f - 0.05f, cz), new Vector3(0.22f, 0.12f, winW + 0.25f), matLimestoneTrim);

                    if ((fl == 2 && s == 2) || (fl == 5 && s == 3))
                    {
                        CreateBox($"SideAC_Body_L{fl+2}_{s}", sideWinGroup, new Vector3(eastX + 0.35f, flY - winH * 0.25f, cz), new Vector3(0.55f, 0.45f, 0.65f), matACMetalBody);
                        CreateBox($"SideAC_Grille_L{fl+2}_{s}", sideWinGroup, new Vector3(eastX + 0.63f, flY - winH * 0.25f, cz), new Vector3(0.03f, 0.38f, 0.55f), matACGrilleDark);
                    }
                }
            }

            // -------------------------------------------------------------------------
            // 6. EXTERNAL BLACK CAST-IRON FIRE ESCAPE STAIRCASE (FRONT-RIGHT CORNER)
            // -------------------------------------------------------------------------
            GameObject fireEscapeGroup = new GameObject("05_External_Fire_Escape");
            fireEscapeGroup.transform.SetParent(buildingRoot.transform, false);

            float feX = 7.1f;
            float feZ = frontZ - 0.7f;

            for (int fl = 0; fl < numUpperFloors; fl++)
            {
                float platY = hGround + fl * hFloor + 0.1f;
                float platW = 1.3f;
                float platD = 1.0f;

                // Satin Black Metal Grating Platform
                CreateBox($"FE_Plat_L{fl+2}", fireEscapeGroup, new Vector3(feX, platY, feZ), new Vector3(platW, 0.06f, platD), matFireEscapeBlack);

                // Platform Safety Railings
                CreateBox($"FE_Rail_Front_L{fl+2}", fireEscapeGroup, new Vector3(feX, platY + 0.45f, feZ - platD * 0.5f), new Vector3(platW, 0.9f, 0.04f), matFireEscapeBlack);
                CreateBox($"FE_Rail_Right_L{fl+2}", fireEscapeGroup, new Vector3(feX + platW * 0.5f, platY + 0.45f, feZ), new Vector3(0.04f, 0.9f, platD), matFireEscapeBlack);
                CreateBox($"FE_Rail_Left_L{fl+2}", fireEscapeGroup, new Vector3(feX - platW * 0.5f, platY + 0.45f, feZ), new Vector3(0.04f, 0.9f, platD), matFireEscapeBlack);

                // Alternating Zig-Zag Diagonal Stair Flights
                if (fl < numUpperFloors - 1)
                {
                    float stairYMid = platY + hFloor * 0.5f;
                    float dirSign = (fl % 2 == 0) ? 1.0f : -1.0f;
                    float stairXMid = feX - 0.7f * dirSign;

                    CreateBox($"FE_Stairs_L{fl+2}", fireEscapeGroup, new Vector3(stairXMid, stairYMid, feZ), new Vector3(1.2f, hFloor - 0.2f, 0.5f), matFireEscapeBlack);
                    CreateBox($"FE_StairRail_L{fl+2}", fireEscapeGroup, new Vector3(stairXMid, stairYMid + 0.5f, feZ - 0.25f), new Vector3(1.2f, hFloor - 0.2f, 0.04f), matFireEscapeBlack);
                }
            }

            // Roof Access Ladder
            float topFeY = hGround + (numUpperFloors - 1) * hFloor + 0.1f;
            CreateBox("FE_Roof_Ladder", fireEscapeGroup, new Vector3(feX, topFeY + 1.8f, feZ), new Vector3(0.5f, 2.6f, 0.08f), matFireEscapeBlack);

            // -------------------------------------------------------------------------
            // 7. 4D BIM TRACKING INTEGRATION
            // -------------------------------------------------------------------------
            GameObject bimGroup = new GameObject("06_BIM_Tracking_Elements");
            bimGroup.transform.SetParent(buildingRoot.transform, false);

            CreateBIMElement(bimGroup, "COL-B1-01", "Corner Structural Pier 1", "Column", "Ground Retail South-West",
                new Vector3(-7.5f, hGround * 0.5f, frontZ - 0.1f), new Vector3(0.9f, hGround, 0.8f),
                "2026-09-01", "2026-09-20", "verified_complete", matStatusComplete);

            CreateBIMElement(bimGroup, "COL-B1-02", "Entrance Pier Center", "Column", "Ground Retail Central",
                new Vector3(0.0f, hGround * 0.5f, frontZ - 0.1f), new Vector3(0.9f, hGround, 0.8f),
                "2026-09-05", "2026-09-25", "verified_complete", matStatusComplete);

            CreateBIMElement(bimGroup, "COL-B1-03", "Corner Structural Pier 3", "Column", "Ground Retail South-East",
                new Vector3(7.5f, hGround * 0.5f, frontZ - 0.1f), new Vector3(0.9f, hGround, 0.8f),
                "2026-09-15", "2026-10-02", "verified_complete", matStatusComplete);

            CreateBIMElement(bimGroup, "BM-L1-01", "Storefront Header Girder A", "Beam", "Level 1 Fascia Line",
                new Vector3(-3.8f, hGround + 0.15f, frontZ - 0.15f), new Vector3(7.2f, 0.35f, 0.45f),
                "2026-09-25", "2026-10-15", "in_progress", matStatusProgress);

            CreateBIMElement(bimGroup, "BM-L1-02", "Storefront Header Girder B", "Beam", "Level 1 Fascia Line",
                new Vector3(3.8f, hGround + 0.15f, frontZ - 0.15f), new Vector3(7.2f, 0.35f, 0.45f),
                "2026-09-28", "2026-10-12", "needs_manual_review", matStatusReview);

            CreateBIMElement(bimGroup, "WL-RET-01", "Perimeter Diaphragm Retaining Wall North", "Wall", "Perimeter North / Shoring Line",
                new Vector3(0.0f, hGround * 0.5f, bD * 0.5f + 0.1f), new Vector3(bW, hGround, 0.5f),
                "2026-08-15", "2026-09-10", "verified_complete", matStatusComplete);

            CreateBIMElement(bimGroup, "FTG-P1-01", "Deep Pile Cap Foundation P1", "Footing", "Sub-foundation Level / Pier 1",
                new Vector3(-7.5f, -0.4f, frontZ - 0.1f), new Vector3(2.2f, 0.8f, 2.2f),
                "2026-10-18", "2026-11-05", "not_started", null);

            CreateBIMElement(bimGroup, "SLB-L1-01", "Ticket Hall Suspended Slab Bay 1", "Slab", "Ticket Hall Level / Bay 1",
                new Vector3(0.0f, hGround + 0.05f, 0.0f), new Vector3(bW - 0.4f, 0.25f, bD - 0.4f),
                "2026-10-05", "2026-10-25", "in_progress", matStatusProgress);

            Debug.Log("[BuildLens 4D] Authentic Colorful Urban Building with 8 BIM tracking elements successfully constructed!");


        }

        private GameObject CreateBox(string name, GameObject parent, Vector3 localPos, Vector3 localScale, Material mat)
        {
            GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obj.name = name;
            obj.transform.SetParent(parent.transform, false);
            obj.transform.localPosition = localPos;
            obj.transform.localScale = localScale;

            var col = obj.GetComponent<Collider>();
            if (col != null) DestroyImmediate(col);

            if (mat != null && obj.GetComponent<Renderer>() != null)
            {
                obj.GetComponent<Renderer>().material = mat;
            }
            return obj;
        }

        private GameObject CreateCylinder(string name, GameObject parent, Vector3 localPos, float radius, float height, Material mat)
        {
            GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            obj.name = name;
            obj.transform.SetParent(parent.transform, false);
            obj.transform.localPosition = localPos;
            obj.transform.localScale = new Vector3(radius * 2.0f, height * 0.5f, radius * 2.0f);

            var col = obj.GetComponent<Collider>();
            if (col != null) DestroyImmediate(col);

            if (mat != null && obj.GetComponent<Renderer>() != null)
            {
                obj.GetComponent<Renderer>().material = mat;
            }
            return obj;
        }

        private GameObject CreateAwning(string name, GameObject parent, Vector3 localPos, Vector3 localScale, Material mat)
        {
            GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obj.name = name;
            obj.transform.SetParent(parent.transform, false);
            obj.transform.localPosition = localPos;
            obj.transform.localScale = localScale;
            obj.transform.localRotation = Quaternion.Euler(28.0f, 0.0f, 0.0f);

            var col = obj.GetComponent<Collider>();
            if (col != null) DestroyImmediate(col);

            if (mat != null && obj.GetComponent<Renderer>() != null)
            {
                obj.GetComponent<Renderer>().material = mat;
            }
            return obj;
        }

        private GameObject CreateBIMElement(
            GameObject parent, string id, string name, string type, string zone,
            Vector3 pos, Vector3 scale, string start, string end, string state, Material mat
        )
        {
            GameObject obj = CreateBox($"{type}_{id}", parent, pos, scale, mat);

            var meta = obj.AddComponent<BIMElementMetadata>();
            meta.SetElementData(id, type, name, zone, start, end, state);

            CreateWorldSpaceTextTag(obj, id, type, state);
            return obj;
        }


        private void CreateWorldSpaceTextTag(GameObject target, string id, string type, string state)
        {
            GameObject tagGO = new GameObject($"Tag_{id}");
            tagGO.transform.SetParent(target.transform, false);
            tagGO.transform.localPosition = new Vector3(0.0f, 0.95f, 0.0f);
            tagGO.transform.localScale = new Vector3(0.12f, 0.12f, 0.12f);

            TextMesh textMesh = tagGO.AddComponent<TextMesh>();
            textMesh.text = $"[{id}]\n{state.Replace("_", " ").ToUpper()}";
            textMesh.fontSize = 24;
            textMesh.alignment = TextAlignment.Center;
            textMesh.anchor = TextAnchor.MiddleCenter;
            textMesh.characterSize = 0.5f;

            Color tagColor = Color.white;
            switch (state)
            {
                case "verified_complete": tagColor = new Color(0.1f, 0.9f, 0.4f); break;
                case "in_progress": tagColor = new Color(1.0f, 0.75f, 0.1f); break;
                case "potentially_delayed": tagColor = new Color(1.0f, 0.25f, 0.2f); break;
                case "needs_manual_review": tagColor = new Color(0.7f, 0.4f, 1.0f); break;
                default: tagColor = new Color(0.7f, 0.7f, 0.7f); break;
            }
            textMesh.color = tagColor;
        }
    }
}
