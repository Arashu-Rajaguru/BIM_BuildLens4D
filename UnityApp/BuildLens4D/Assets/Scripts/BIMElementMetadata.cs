using System;
using System.Collections;
using UnityEngine;

namespace BuildLens4D.BIM
{
    /// <summary>
    /// Attaches to individual BIM components (columns, beams, slabs, walls) in the Unity hierarchy.
    /// Stores the stable element identifier, 4D schedule milestones, and verification state.
    /// Provides visual state tinting and 3D world-space text tag updates for real-time inspection.
    /// </summary>
    [DisallowMultipleComponent]
    public class BIMElementMetadata : MonoBehaviour
    {
        [Header("BIM Element Identification")]
        [Tooltip("Stable unique identifier matching the BIM model and schedule (e.g., COL-B1-01).")]
        [SerializeField] private string elementId = "COL-B1-01";

        [Tooltip("Structural element category: Column, Beam, Slab, Wall, Footing.")]
        [SerializeField] private string elementType = "Column";

        [Tooltip("Human-readable label for on-site display.")]
        [SerializeField] private string label = "Level 1 Structural Column";

        [Tooltip("Spatial zone or grid reference (e.g., Grid A-1 / Concourse).")]
        [SerializeField] private string spatialZone = "Grid A-1";

        [Header("4D Schedule Metadata")]
        [Tooltip("Planned start date in ISO-8601 (YYYY-MM-DD).")]
        [SerializeField] private string plannedStartDate = "2026-10-01";

        [Tooltip("Planned completion date in ISO-8601 (YYYY-MM-DD).")]
        [SerializeField] private string plannedEndDate = "2026-10-20";

        [Header("Current Progress & Verification State")]
        [Tooltip("verified_complete, in_progress, potentially_delayed, ahead_of_schedule, needs_manual_review, not_started")]
        [SerializeField] private string verificationState = "not_started";

        [SerializeField] private string lastInspectionTimestamp = "";

        private Renderer cachedRenderer;
        private Color originalColor = Color.white;
        private Coroutine pulseRoutine;

        public string ElementId => elementId;
        public string ElementType => elementType;
        public string Label => label;
        public string SpatialZone => spatialZone;
        public string PlannedStartDate => plannedStartDate;
        public string PlannedEndDate => plannedEndDate;
        public string VerificationState => verificationState;
        public string LastInspectionTimestamp => lastInspectionTimestamp;

        private void Awake()
        {
            cachedRenderer = GetComponent<Renderer>();
            if (cachedRenderer != null && cachedRenderer.material.HasProperty("_Color"))
            {
                originalColor = cachedRenderer.material.color;
            }
            ApplyStatusColor();
        }

        public void SetElementData(string id, string type, string nameLabel, string zone, string start, string end, string state)
        {
            elementId = id;
            elementType = type;
            label = nameLabel;
            spatialZone = zone;
            plannedStartDate = start;
            plannedEndDate = end;
            verificationState = state;
            gameObject.name = $"{type}_{id}";
            ApplyStatusColor();
            UpdateChildTextTag();
        }

        /// <summary>
        /// Updates the verification state and refreshes the AR shader overlay color and 3D badge in real time.
        /// </summary>
        public void UpdateVerificationState(string newState, string timestamp = "")
        {
            if (verificationState != newState)
            {
                verificationState = newState;
                if (!string.IsNullOrEmpty(timestamp))
                {
                    lastInspectionTimestamp = timestamp;
                }
                ApplyStatusColor();
                UpdateChildTextTag();
                TriggerVisualHighlight();
            }
        }

        /// <summary>
        /// Updates child world-space text tag to display the updated state in real-time.
        /// </summary>
        public void UpdateChildTextTag()
        {
            var textMesh = GetComponentInChildren<TextMesh>();
            if (textMesh != null)
            {
                textMesh.text = $"[{elementId}]\n{verificationState.Replace("_", " ").ToUpper()}";
                textMesh.color = GetStatusColor(verificationState, 1.0f);
            }
        }

        /// <summary>
        /// Tints the element mesh according to its 4D status to aid rapid visual inspection.
        /// </summary>
        public void ApplyStatusColor()
        {
            if (cachedRenderer == null || !cachedRenderer.material.HasProperty("_Color")) return;
            cachedRenderer.material.color = GetStatusColor(verificationState, 0.85f);
        }

        public static Color GetStatusColor(string state, float alpha = 0.85f)
        {
            switch (state)
            {
                case "verified_complete":
                    return new Color(0.18f, 0.80f, 0.44f, alpha); // Emerald Green
                case "ahead_of_schedule":
                    return new Color(0.13f, 0.59f, 0.95f, alpha); // Cyan / Blue
                case "in_progress":
                    return new Color(0.95f, 0.77f, 0.06f, alpha); // Amber / Yellow
                case "potentially_delayed":
                    return new Color(0.91f, 0.30f, 0.24f, alpha); // Crimson / Red
                case "needs_manual_review":
                    return new Color(0.61f, 0.35f, 0.71f, alpha); // Violet / Manual Review Alert
                case "not_started":
                default:
                    return new Color(0.6f, 0.6f, 0.6f, alpha * 0.5f); // Gray
            }
        }

        public void TriggerVisualHighlight()
        {
            if (pulseRoutine != null) StopCoroutine(pulseRoutine);
            pulseRoutine = StartCoroutine(PulseAnimation());
        }

        private IEnumerator PulseAnimation()
        {
            Vector3 originalScale = transform.localScale;
            Vector3 targetScale = originalScale * 1.15f;

            for (int i = 0; i < 2; i++)
            {
                float t = 0f;
                while (t < 0.2f)
                {
                    transform.localScale = Vector3.Lerp(originalScale, targetScale, t / 0.2f);
                    t += Time.deltaTime;
                    yield return null;
                }
                t = 0f;
                while (t < 0.2f)
                {
                    transform.localScale = Vector3.Lerp(targetScale, originalScale, t / 0.2f);
                    t += Time.deltaTime;
                    yield return null;
                }
            }
            transform.localScale = originalScale;
        }

        /// <summary>
        /// Restores original unselected material color.
        /// </summary>
        public void ResetOriginalColor()
        {
            if (cachedRenderer != null && cachedRenderer.material.HasProperty("_Color"))
            {
                cachedRenderer.material.color = originalColor;
            }
        }
    }
}
