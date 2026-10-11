using System;
using UnityEngine;
using BuildLens4D.BIM;

namespace BuildLens4D.Building
{
    /// <summary>
    /// Generates a realistic 3D multi-storey BIM building model in Unity,
    /// complete with columns, transfer beams, floor slabs, perimeter walls,
    /// and deep pile foundations linked to 4D schedule metadata.
    /// </summary>
    public class SampleBIMBuildingGenerator : MonoBehaviour
    {
        [Header("Building Configuration")]
        [SerializeField] private Material defaultConcreteMaterial;
        [SerializeField] private bool generateOnStart = true;

        private void Start()
        {
            if (generateOnStart)
            {
                GenerateSampleBuildingModel();
            }
        }

        [ContextMenu("Generate Sample Building Model")]
        public void GenerateSampleBuildingModel()
        {
            // Create root container
            GameObject buildingRoot = GameObject.Find("[BIM_Building_Model]");
            if (buildingRoot != null)
            {
                DestroyImmediate(buildingRoot);
            }

            buildingRoot = new GameObject("[BIM_Building_Model]");
            buildingRoot.transform.SetParent(transform, false);

            Debug.Log("[BuildLens 4D] Generating sample 3D BIM building structure...");

            // -------------------------------------------------------------------
            // Level -1: Foundation & Retaining Wall
            // -------------------------------------------------------------------
            CreateBIMElement(
                parent: buildingRoot,
                id: "FTG-P1-01",
                name: "Deep Pile Cap Foundation P1",
                type: "Footing",
                zone: "Sub-foundation Level / Pier 1",
                pos: new Vector3(-2.0f, -0.4f, 0.0f),
                scale: new Vector3(1.2f, 0.5f, 1.2f),
                start: "2026-10-18",
                end: "2026-11-05",
                state: "not_started"
            );

            CreateBIMElement(
                parent: buildingRoot,
                id: "WL-RET-01",
                name: "Perimeter Diaphragm Retaining Wall North",
                type: "Wall",
                zone: "Perimeter North / Shoring Line",
                pos: new Vector3(0.0f, 0.8f, -2.2f),
                scale: new Vector3(6.5f, 2.6f, 0.3f),
                start: "2026-08-15",
                end: "2026-09-10",
                state: "verified_complete"
            );

            // -------------------------------------------------------------------
            // Level 0: Concourse Columns
            // -------------------------------------------------------------------
            CreateBIMElement(
                parent: buildingRoot,
                id: "COL-B1-01",
                name: "Track Level Heavy Column Grid A1",
                type: "Column",
                zone: "Concourse Level / Grid A-1",
                pos: new Vector3(-2.0f, 1.2f, -1.0f),
                scale: new Vector3(0.5f, 2.2f, 0.5f),
                start: "2026-09-01",
                end: "2026-09-20",
                state: "verified_complete"
            );

            CreateBIMElement(
                parent: buildingRoot,
                id: "COL-B1-02",
                name: "Track Level Heavy Column Grid A2",
                type: "Column",
                zone: "Concourse Level / Grid A-2",
                pos: new Vector3(2.0f, 1.2f, -1.0f),
                scale: new Vector3(0.5f, 2.2f, 0.5f),
                start: "2026-09-05",
                end: "2026-09-25",
                state: "verified_complete"
            );

            CreateBIMElement(
                parent: buildingRoot,
                id: "COL-B1-03",
                name: "Concourse Central Pillar Grid B1",
                type: "Column",
                zone: "Concourse Level / Grid B-1",
                pos: new Vector3(-2.0f, 1.2f, 1.5f),
                scale: new Vector3(0.5f, 2.2f, 0.5f),
                start: "2026-09-15",
                end: "2026-10-02",
                state: "potentially_delayed"
            );

            // -------------------------------------------------------------------
            // Level 1: Transfer Beams & Spans
            // -------------------------------------------------------------------
            CreateBIMElement(
                parent: buildingRoot,
                id: "BM-L1-01",
                name: "Longitudinal Transfer Beam Grid A1-A2",
                type: "Beam",
                zone: "Mezzanine Level / Spans A1-A2",
                pos: new Vector3(0.0f, 2.45f, -1.0f),
                scale: new Vector3(4.5f, 0.4f, 0.6f),
                start: "2026-09-25",
                end: "2026-10-15",
                state: "in_progress"
            );

            CreateBIMElement(
                parent: buildingRoot,
                id: "BM-L1-02",
                name: "Transverse Header Beam Grid B1-B2",
                type: "Beam",
                zone: "Mezzanine Level / Spans B1-B2",
                pos: new Vector3(-2.0f, 2.45f, 0.25f),
                scale: new Vector3(0.6f, 0.4f, 3.0f),
                start: "2026-09-28",
                end: "2026-10-12",
                state: "needs_manual_review"
            );

            // -------------------------------------------------------------------
            // Level 2: Suspended Floor Slab
            // -------------------------------------------------------------------
            CreateBIMElement(
                parent: buildingRoot,
                id: "SLB-L1-01",
                name: "Ticket Hall Suspended Slab Bay 1",
                type: "Slab",
                zone: "Ticket Hall Level / Bay 1",
                pos: new Vector3(0.0f, 2.7f, 0.25f),
                scale: new Vector3(5.0f, 0.25f, 3.5f),
                start: "2026-10-05",
                end: "2026-10-25",
                state: "in_progress"
            );

            Debug.Log("[BuildLens 4D] 3D Sample BIM building model successfully generated!");
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
            string state
        )
        {
            GameObject obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obj.name = $"{type}_{id}";
            obj.transform.SetParent(parent.transform, false);
            obj.transform.localPosition = pos;
            obj.transform.localScale = scale;

            // Attach BIM Metadata
            var meta = obj.AddComponent<BIMElementMetadata>();
            meta.UpdateVerificationState(state);

            return obj;
        }
    }
}
