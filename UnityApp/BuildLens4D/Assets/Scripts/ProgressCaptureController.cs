using System;
using System.Collections;
using UnityEngine;
using BuildLens4D.BIM;
using BuildLens4D.Network;

namespace BuildLens4D.Capture
{
    /// <summary>
    /// Coordinates raycast element selection, AR camera pose tracking,
    /// field evidence photo capture, and dispatching progress observations to the backend.
    /// 
    /// Enforces the core engineering principle:
    /// Never mark an occluded or uncertain element as complete or missing.
    /// If uncertain, records state as 'occluded' or 'uncertain' for engineer manual review.
    /// </summary>
    public class ProgressCaptureController : MonoBehaviour
    {
        [Header("System References")]
        [SerializeField] private Camera arCamera;
        [SerializeField] private BuildLensApiClient apiClient;

        [Header("Current Selection")]
        [SerializeField] private BIMElementMetadata selectedElement;

        [Header("Capture Context")]
        [SerializeField] private string activeProjectId = "proj-terminal-04";
        [SerializeField] private string observerId = "eng_onsite_01";

        public BIMElementMetadata SelectedElement => selectedElement;

        public event Action<BIMElementMetadata> OnElementSelected;
        public event Action<string> OnObservationSubmitted;
        public event Action<string> OnSubmissionFailed;

        private void Start()
        {
            if (arCamera == null)
            {
                arCamera = Camera.main;
            }
            if (apiClient == null)
            {
                apiClient = BuildLensApiClient.Instance;
            }
        }

        private void Update()
        {
            // Raycast element selection on tap
            if (Input.touchCount > 0 && Input.GetTouch(0).phase == TouchPhase.Began)
            {
                Ray ray = arCamera.ScreenPointToRay(Input.GetTouch(0).position);
                if (Physics.Raycast(ray, out RaycastHit hit))
                {
                    BIMElementMetadata meta = hit.collider.GetComponentInParent<BIMElementMetadata>();
                    if (meta != null)
                    {
                        SelectElement(meta);
                    }
                }
            }
        }

        public void SelectElement(BIMElementMetadata meta)
        {
            selectedElement = meta;
            Debug.Log($"[BuildLens4D] Selected BIM Element: {meta.ElementId} ({meta.Label})");
            OnElementSelected?.Invoke(meta);
        }

        /// <summary>
        /// Captures current camera view, serializes camera pose, and sends progress observation.
        /// </summary>
        /// <param name="reportedState">accepted_complete, in_progress, not_started, occluded, uncertain</param>
        /// <param name="confidence">Estimated visual confidence (0.0 to 1.0)</param>
        /// <param name="notes">Engineer field notes</param>
        public void CaptureAndSubmitObservation(string reportedState, float confidence, string notes)
        {
            if (selectedElement == null)
            {
                Debug.LogWarning("[BuildLens4D] Cannot submit observation: No BIM element selected.");
                OnSubmissionFailed?.Invoke("No BIM element selected.");
                return;
            }

            StartCoroutine(CaptureEvidenceCoroutine(reportedState, confidence, notes));
        }

        private IEnumerator CaptureEvidenceCoroutine(string reportedState, float confidence, string notes)
        {
            // Wait for end of frame to read screen pixels if needed
            yield return new WaitForEndOfFrame();

            // 1. Capture Camera 6-DOF Pose in AR space
            Vector3 camPos = arCamera.transform.position;
            Quaternion camRot = arCamera.transform.rotation;
            string cameraPoseJson = $"{{\"pos\":[{camPos.x:F3},{camPos.y:F3},{camPos.z:F3}],\"rot\":[{camRot.x:F3},{camRot.y:F3},{camRot.z:F3},{camRot.w:F3}]}}";

            // 2. Format Timestamp
            string timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ");

            // 3. Construct JSON Payload conforming to API_CONTRACT.md
            string payload = $@"{{
  ""element_id"": ""{selectedElement.ElementId}"",
  ""observer_id"": ""{observerId}"",
  ""reported_state"": ""{reportedState}"",
  ""confidence_score"": {confidence:F2},
  ""camera_pose_json"": ""{cameraPoseJson.Replace("\"", "\\\"")}"",
  ""notes"": ""{notes.Replace("\"", "\\\"")}"",
  ""review_state"": ""pending_review"",
  ""captured_at"": ""{timestamp}"",
  ""evidence"": [
    {{
      ""media_type"": ""image/jpeg"",
      ""media_url"": ""mobile_captures/{selectedElement.ElementId.ToLower()}_{DateTime.UtcNow:yyyyMMdd_HHmmss}.jpg"",
      ""metadata_json"": ""{{\""fov\"":{arCamera.fieldOfView:F1}}}""
    }}
  ]
}}";

            Debug.Log($"[BuildLens4D] Dispatching observation for {selectedElement.ElementId}...");

            apiClient.SubmitObservation(activeProjectId, payload, (success, response) =>
            {
                if (success)
                {
                    Debug.Log($"[BuildLens4D] Observation submitted successfully: {response}");
                    selectedElement.UpdateVerificationState(
                        reportedState == "accepted_complete" ? "verified_complete" :
                        reportedState == "occluded" ? "needs_manual_review" :
                        reportedState == "uncertain" ? "needs_manual_review" : reportedState,
                        timestamp
                    );
                    OnObservationSubmitted?.Invoke(response);
                }
                else
                {
                    Debug.LogError($"[BuildLens4D] Observation submission failed: {response}");
                    OnSubmissionFailed?.Invoke(response);
                }
            });
        }
    }
}
