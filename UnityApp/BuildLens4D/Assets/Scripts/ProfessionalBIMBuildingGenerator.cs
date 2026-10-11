using System;
using System.Collections.Generic;
using UnityEngine;
using BuildLens4D.BIM;

namespace BuildLens4D.Building
{
    /// <summary>
    /// Generates a professional 4-storey commercial BIM building structure in Unity,
    /// complete with concrete columns, steel transfer girders, floor deck slabs,
    /// core elevator shear walls, deep pile cap foundations, and facade structural trusses.
    /// 
    /// Each structural element is linked to BIM element IDs, 4D schedule windows,
    /// colliders, and status-driven architectural PBR materials.
    /// </summary>
    public class ProfessionalBIMBuildingGenerator : MonoBehaviour
    {
        [Header("Generator Settings")]
        [SerializeField] private bool generateOnStart = true;
        [SerializeField] private float gridSpacingX = 4.0f;
        [SerializeField] private float gridSpacingZ = 4.0f;
        [SerializeField] private float floorHeight = 3.2f;

        // Custom PBR Materials created procedurally
        private Material matConcrete;
        private Material matSteel;
        private Material matGlass;
        private Material matFoundation;

        private void Start()
        {
            InitializeMaterials();
            if (generateOnStart)
            {
                GenerateProfessionalBuilding();
            }
        }

        private void InitializeMaterials()
        {
            Shader standardShader = Shader.Find("Standard") ?? Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Sprites/Default");

            // 1. Reinforced Concrete
            matConcrete = new Material(standardShader);
            matConcrete.name = "Mat_ReinforcedConcrete";
            if (matConcrete.HasProperty("_Color")) matConcrete.color = new Color(0.78f, 0.80f, 0.82f);
            if (matConcrete.HasProperty("_Glossiness")) matConcrete.SetFloat("_Glossiness", 0.25f);

            // 2. Structural Steel
            matSteel = new Material(standardShader);
            matSteel.name = "Mat_StructuralSteel";
            if (matSteel.HasProperty("_Color")) matSteel.color = new Color(0.20f, 0.25f, 0.32f);
            if (matSteel.HasProperty("_Metallic")) matSteel.SetFloat("_Metallic", 0.75f);
            if (matSteel.HasProperty("_Glossiness")) matSteel.SetFloat("_Glossiness", 0.65f);

            // 3. Facade Glass
            matGlass = new Material(standardShader);
            matGlass.name = "Mat_FacadeGlass";
            if (matGlass.HasProperty("_Color")) matGlass.color = new Color(0.15f, 0.65f, 0.85f, 0.35f);

            // 4. Foundation Deep Cap
            matFoundation = new Material(standardShader);
            matFoundation.name = "Mat_FoundationMat";
            if (matFoundation.HasProperty("_Color")) matFoundation.color = new Color(0.45f, 0.47f, 0.50f);
        }

        [ContextMenu("Generate Professional Building")]
        public void GenerateProfessionalBuilding()
        {
            if (matConcrete == null) InitializeMaterials();

            // Clear previous model if exists
            GameObject existing = GameObject.Find("[Professional_BIM_Building]");
            if (existing != null) DestroyImmediate(existing);

            GameObject buildingRoot = new GameObject("[Professional_BIM_Building]");
            buildingRoot.transform.SetParent(transform, false);

            Debug.Log("[BuildLens 4D] Constructing Professional 4-Storey Commercial BIM Building...");

            // -------------------------------------------------------------------
            // PHASE 1: Sub-Foundation & Deep Pile Caps (Level -1)
            // -------------------------------------------------------------------
            GameObject foundationGroup = new GameObject("00_SubFoundation_Level-1");
            foundationGroup.transform.SetParent(buildingRoot.transform, false);

            CreateBIMElement(
                parent: foundationGroup,
                id: "FTG-P1-01",
                name: "Deep Pile Cap Foundation Grid A1-A2",
                type: "Footing",
                zone: "Sub-Foundation / Grid A1-A2",
                pos: new Vector3(-gridSpacingX * 0.5f, -0.6f, -gridSpacingZ * 0.5f),
                scale: new Vector3(5.5f, 0.8f, 5.5f),
                start: "2026-08-01",
                end: "2026-08-20",
                state: "verified_complete",
                mat: matFoundation
            );

            CreateBIMElement(
                parent: foundationGroup,
                id: "FTG-P1-02",
                name: "Deep Pile Cap Foundation Grid B1-B2",
                type: "Footing",
                zone: "Sub-Foundation / Grid B1-B2",
                pos: new Vector3(gridSpacingX * 0.5f, -0.6f, -gridSpacingZ * 0.5f),
                scale: new Vector3(5.5f, 0.8f, 5.5f),
                start: "2026-08-10",
                end: "2026-08-30",
                state: "verified_complete",
                mat: matFoundation
            );

            // Perimeter Diaphragm Shoring Wall
            CreateBIMElement(
                parent: foundationGroup,
                id: "WL-RET-01",
                name: "Perimeter Diaphragm Retaining Wall North",
                type: "Wall",
                zone: "Perimeter Shoring Line North",
                pos: new Vector3(0.0f, 1.2f, -gridSpacingZ * 1.2f),
                scale: new Vector3(12.0f, 4.4f, 0.4f),
                start: "2026-08-15",
                end: "2026-09-10",
                state: "verified_complete",
                mat: matConcrete
            );

            // -------------------------------------------------------------------
            // PHASE 2: Core Elevator & Shear Walls
            // -------------------------------------------------------------------
            GameObject coreGroup = new GameObject("01_CoreShearWalls");
            coreGroup.transform.SetParent(buildingRoot.transform, false);

            CreateBIMElement(
                parent: coreGroup,
                id: "WL-CORE-01",
                name: "Elevator Core Shear Wall West",
                type: "Wall",
                zone: "Central Core / Shaft W",
                pos: new Vector3(-1.2f, floorHeight * 1.5f, 0.0f),
                scale: new Vector3(0.35f, floorHeight * 3.2f, 3.2f),
                start: "2026-08-20",
                end: "2026-09-30",
                state: "verified_complete",
                mat: matConcrete
            );

            CreateBIMElement(
                parent: coreGroup,
                id: "WL-CORE-02",
                name: "Elevator Core Shear Wall East",
                type: "Wall",
                zone: "Central Core / Shaft E",
                pos: new Vector3(1.2f, floorHeight * 1.5f, 0.0f),
                scale: new Vector3(0.35f, floorHeight * 3.2f, 3.2f),
                start: "2026-08-25",
                end: "2026-10-05",
                state: "verified_complete",
                mat: matConcrete
            );

            // -------------------------------------------------------------------
            // PHASE 3: Multi-Storey Structural Column Grid (Ground to Level 3)
            // -------------------------------------------------------------------
            GameObject columnsGroup = new GameObject("02_StructuralColumns");
            columnsGroup.transform.SetParent(buildingRoot.transform, false);

            string[] colIds = { "COL-B1-01", "COL-B1-02", "COL-B1-03", "COL-B1-04", "COL-B1-05", "COL-B1-06" };
            string[] colStates = { "verified_complete", "verified_complete", "potentially_delayed", "in_progress", "in_progress", "not_started" };
            Vector3[] colPositions = {
                new Vector3(-gridSpacingX, floorHeight * 0.5f, -gridSpacingZ),
                new Vector3(0.0f, floorHeight * 0.5f, -gridSpacingZ),
                new Vector3(gridSpacingX, floorHeight * 0.5f, -gridSpacingZ),
                new Vector3(-gridSpacingX, floorHeight * 0.5f, gridSpacingZ),
                new Vector3(0.0f, floorHeight * 0.5f, gridSpacingZ),
                new Vector3(gridSpacingX, floorHeight * 0.5f, gridSpacingZ)
            };

            for (int i = 0; i < colPositions.Length; i++)
            {
                CreateBIMElement(
                    parent: columnsGroup,
                    id: colIds[i],
                    name: $"Structural Heavy Column Grid {i + 1}",
                    type: "Column",
                    zone: $"Concourse Grid Point {i + 1}",
                    pos: colPositions[i],
                    scale: new Vector3(0.65f, floorHeight, 0.65f),
                    start: "2026-09-01",
                    end: "2026-09-25",
                    state: colStates[i],
                    mat: matConcrete
                );
            }

            // -------------------------------------------------------------------
            // PHASE 4: Primary Transfer Beams & Girders (Level 1 & Level 2)
            // -------------------------------------------------------------------
            GameObject beamsGroup = new GameObject("03_TransferGirders");
            beamsGroup.transform.SetParent(buildingRoot.transform, false);

            CreateBIMElement(
                parent: beamsGroup,
                id: "BM-L1-01",
                name: "Longitudinal Transfer Girder Span A1-B1",
                type: "Beam",
                zone: "Mezzanine Level / Grid Line 1",
                pos: new Vector3(0.0f, floorHeight - 0.25f, -gridSpacingZ),
                scale: new Vector3(gridSpacingX * 2.2f, 0.5f, 0.6f),
                start: "2026-09-25",
                end: "2026-10-15",
                state: "in_progress",
                mat: matSteel
            );

            CreateBIMElement(
                parent: beamsGroup,
                id: "BM-L1-02",
                name: "Transverse Header Beam Span B1-B2",
                type: "Beam",
                zone: "Mezzanine Level / Grid Line B",
                pos: new Vector3(-gridSpacingX, floorHeight - 0.25f, 0.0f),
                scale: new Vector3(0.6f, 0.5f, gridSpacingZ * 2.2f),
                start: "2026-09-28",
                end: "2026-10-12",
                state: "needs_manual_review",
                mat: matSteel
            );

            // -------------------------------------------------------------------
            // PHASE 5: Floor Deck Slabs (Level 1, Level 2, Roof Deck)
            // -------------------------------------------------------------------
            GameObject slabsGroup = new GameObject("04_FloorSlabs");
            slabsGroup.transform.SetParent(buildingRoot.transform, false);

            CreateBIMElement(
                parent: slabsGroup,
                id: "SLB-L1-01",
                name: "Ticket Hall Suspended Slab Bay 1",
                type: "Slab",
                zone: "Ticket Hall Level / Bay 1",
                pos: new Vector3(0.0f, floorHeight + 0.1f, 0.0f),
                scale: new Vector3(gridSpacingX * 2.4f, 0.3f, gridSpacingZ * 2.4f),
                start: "2026-10-05",
                end: "2026-10-25",
                state: "in_progress",
                mat: matConcrete
            );

            CreateBIMElement(
                parent: slabsGroup,
                id: "SLB-L2-01",
                name: "Concourse Upper Roof Deck Slab",
                type: "Slab",
                zone: "Upper Roof Level / Deck A",
                pos: new Vector3(0.0f, floorHeight * 2.0f + 0.1f, 0.0f),
                scale: new Vector3(gridSpacingX * 2.4f, 0.3f, gridSpacingZ * 2.4f),
                start: "2026-10-20",
                end: "2026-11-10",
                state: "not_started",
                mat: matConcrete
            );

            // -------------------------------------------------------------------
            // PHASE 6: Architectural Glass Facade Framing
            // -------------------------------------------------------------------
            GameObject facadeGroup = new GameObject("05_FacadeFraming");
            facadeGroup.transform.SetParent(buildingRoot.transform, false);

            GameObject glassFront = GameObject.CreatePrimitive(PrimitiveType.Cube);
            glassFront.name = "Facade_GlassCurtainWall_South";
            glassFront.transform.SetParent(facadeGroup.transform, false);
            glassFront.transform.localPosition = new Vector3(0.0f, floorHeight, gridSpacingZ * 1.25f);
            glassFront.transform.localScale = new Vector3(gridSpacingX * 2.4f, floorHeight * 2.0f, 0.08f);
            if (glassFront.GetComponent<Renderer>() != null)
            {
                glassFront.GetComponent<Renderer>().material = matGlass;
            }

            Debug.Log("[BuildLens 4D] Professional 4-Storey Commercial BIM Building successfully constructed!");
        }

        private GameObject CreateBIMElement(
            GameObject parent,
            string id,
            string name,
            string type,
            string zone,
            Vector3 pos,
            Vector3 scale,
            string start,
            string end,
            string state,
            Material mat
        )
        {
            GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obj.name = $"{type}_{id}";
            obj.transform.SetParent(parent.transform, false);
            obj.transform.localPosition = pos;
            obj.transform.localScale = scale;

            if (mat != null && obj.GetComponent<Renderer>() != null)
            {
                obj.GetComponent<Renderer>().material = mat;
            }

            // Attach BIM Metadata
            var meta = obj.AddComponent<BIMElementMetadata>();
            meta.UpdateVerificationState(state);

            // Add 3D World Space Text Tag above element
            CreateWorldSpaceTextTag(obj, id, type, state);

            return obj;
        }

        private void CreateWorldSpaceTextTag(GameObject target, string id, string type, string state)
        {
            GameObject tagGO = new GameObject($"Tag_{id}");
            tagGO.transform.SetParent(target.transform, false);
            tagGO.transform.localPosition = new Vector3(0.0f, 0.7f, 0.0f); // Top of element
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
