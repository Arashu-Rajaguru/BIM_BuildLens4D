using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

namespace BuildLens4D.AR
{
    /// <summary>
    /// Controls the detection of real-world horizontal surfaces and tap-to-place
    /// alignment for the lightweight BIM model using Unity AR Foundation and Google ARCore.
    /// 
    /// Note: This script is prepared as source code and requires AR Foundation and
    /// Google ARCore XR Plug-in to be installed in the Unity project via Package Manager.
    /// </summary>
    [RequireComponent(typeof(ARRaycastManager))]
    [RequireComponent(typeof(ARPlaneManager))]
    public class ARPlacementController : MonoBehaviour
    {
        [Header("Placement Configuration")]
        [Tooltip("Prefab of the lightweight BIM structure or root assembly to instantiate.")]
        [SerializeField] private GameObject bimModelPrefab;

        [Tooltip("Optional visual indicator / reticle showing where the model will be placed.")]
        [SerializeField] private GameObject placementIndicator;

        [Header("Placement State")]
        [SerializeField] private bool isModelPlaced = false;
        [SerializeField] private bool lockPlacementAfterFirstTap = false;

        private ARRaycastManager raycastManager;
        private ARPlaneManager planeManager;
        private GameObject spawnedBimModel;
        private static readonly List<ARRaycastHit> hits = new List<ARRaycastHit>();
        private Pose currentPlacementPose;
        private bool placementPoseIsValid = false;

        public GameObject SpawnedBIMModel => spawnedBimModel;
        public bool IsPlaced => isModelPlaced;

        private void Awake()
        {
            raycastManager = GetComponent<ARRaycastManager>();
            planeManager = GetComponent<ARPlaneManager>();
        }

        private void Update()
        {
            UpdatePlacementPose();
            UpdatePlacementIndicator();

            // Detect touch on Android mobile screen
            if (Input.touchCount > 0)
            {
                Touch touch = Input.GetTouch(0);
                if (touch.phase == TouchPhase.Began)
                {
                    OnScreenTapped(touch.position);
                }
            }
        }

        /// <summary>
        /// Raycasts from screen center against detected AR planes (TrackableType.PlaneWithinPolygon).
        /// </summary>
        private void UpdatePlacementPose()
        {
            if (isModelPlaced && lockPlacementAfterFirstTap)
            {
                placementPoseIsValid = false;
                return;
            }

            Vector2 screenCenter = new Vector2(Screen.width * 0.5f, Screen.height * 0.5f);
            if (raycastManager.Raycast(screenCenter, hits, TrackableType.PlaneWithinPolygon))
            {
                placementPoseIsValid = hits.Count > 0;
                if (placementPoseIsValid)
                {
                    currentPlacementPose = hits[0].pose;
                }
            }
            else
            {
                placementPoseIsValid = false;
            }
        }

        private void UpdatePlacementIndicator()
        {
            if (placementIndicator == null) return;

            if (placementPoseIsValid && (!isModelPlaced || !lockPlacementAfterFirstTap))
            {
                placementIndicator.SetActive(true);
                placementIndicator.transform.SetPositionAndRotation(currentPlacementPose.position, currentPlacementPose.rotation);
            }
            else
            {
                placementIndicator.SetActive(false);
            }
        }

        private void OnScreenTapped(Vector2 touchPosition)
        {
            // If already placed and locked, ignore tap
            if (isModelPlaced && lockPlacementAfterFirstTap) return;

            if (raycastManager.Raycast(touchPosition, hits, TrackableType.PlaneWithinPolygon))
            {
                Pose hitPose = hits[0].pose;
                PlaceOrRepositionModel(hitPose);
            }
        }

        /// <summary>
        /// Instantiates or repositions the BIM model onto the detected surface.
        /// </summary>
        public void PlaceOrRepositionModel(Pose targetPose)
        {
            if (spawnedBimModel == null)
            {
                if (bimModelPrefab != null)
                {
                    spawnedBimModel = Instantiate(bimModelPrefab, targetPose.position, targetPose.rotation);
                    isModelPlaced = true;
                    Debug.Log($"[BuildLens4D] BIM Model placed successfully at {targetPose.position}.");
                }
                else
                {
                    Debug.LogWarning("[BuildLens4D] Cannot place model: bimModelPrefab is not assigned in Inspector.");
                }
            }
            else
            {
                spawnedBimModel.transform.SetPositionAndRotation(targetPose.position, targetPose.rotation);
                Debug.Log($"[BuildLens4D] BIM Model repositioned to {targetPose.position}.");
            }
        }

        /// <summary>
        /// Resets model placement, allowing re-alignment.
        /// </summary>
        public void ResetPlacement()
        {
            if (spawnedBimModel != null)
            {
                Destroy(spawnedBimModel);
                spawnedBimModel = null;
            }
            isModelPlaced = false;
        }

        /// <summary>
        /// Toggles visual display of detected AR surface planes.
        /// </summary>
        public void SetPlanesActive(bool active)
        {
            foreach (var plane in planeManager.trackables)
            {
                plane.gameObject.SetActive(active);
            }
            planeManager.enabled = active;
        }
    }
}
