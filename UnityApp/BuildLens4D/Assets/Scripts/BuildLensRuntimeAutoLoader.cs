using UnityEngine;
using UnityEngine.XR.ARFoundation;
using BuildLens4D.Building;
using BuildLens4D.Navigation;

namespace BuildLens4D.Runtime
{
    /// <summary>
    /// Runtime Auto-Loader that automatically runs whenever Play ▶ is pressed.
    /// Completely eliminates ARCameraBackground boxes, XR Simulation room box cubes,
    /// and camera collision bounds in Editor Play mode so the 3D building and green landscape
    /// render with 100% clarity and completely unrestricted 6-DOF fly navigation!
    /// </summary>
    public class BuildLensRuntimeAutoLoader : MonoBehaviour
    {
        private int checkFramesRemaining = 10;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        public static void AutoInitializeSceneOnPlay()
        {
            Debug.Log("[BuildLens4D Runtime] Play ▶ detected — Initializing free-flight open-air BIM experience...");

            // Create persistent controller to continuously ensure open space
            GameObject runner = new GameObject("[BuildLens_Runtime_Environment_Controller]");
            DontDestroyOnLoad(runner);
            runner.AddComponent<BuildLensRuntimeAutoLoader>();
        }

        private void Start()
        {
            CleanEnvironment();
        }

        private void Update()
        {
            if (checkFramesRemaining > 0)
            {
                CleanEnvironment();
                checkFramesRemaining--;
            }
        }

        private void CleanEnvironment()
        {
            // 1. Ensure Directional Sun Light exists for bright architectural illumination
            Light[] lights = Object.FindObjectsByType<Light>(FindObjectsSortMode.None);
            bool hasSun = false;
            foreach (var l in lights)
            {
                if (l.type == LightType.Directional && l.enabled)
                {
                    hasSun = true;
                    break;
                }
            }

            if (!hasSun)
            {
                GameObject lightGO = new GameObject("Directional Light");
                var light = lightGO.AddComponent<Light>();
                light.type = LightType.Directional;
                light.intensity = 1.4f;
                light.color = new Color(1.0f, 0.98f, 0.92f);
                lightGO.transform.rotation = Quaternion.Euler(50.0f, -30.0f, 0.0f);
            }

            // 2. Disable ARCameraBackground in Editor Play mode (prevents black/gray box occlusion)
#if UNITY_EDITOR
            var bgComponents = Object.FindObjectsByType<ARCameraBackground>(FindObjectsSortMode.None);
            foreach (var bg in bgComponents)
            {
                if (bg != null && bg.enabled)
                {
                    bg.enabled = false;
                }
            }
#endif

            // 3. Destroy or deactivate any simulated room boxes / environment boxes (e.g. layer 30 or room names)
            string[] roomBoxNames = {
                "XR Environment", "DefaultSimulationEnvironment", "AR Environment",
                "RoomBox", "SimulationEnvironment", "Room", "Environment", "SubSimRoot"
            };
            foreach (var boxName in roomBoxNames)
            {
                GameObject box = GameObject.Find(boxName);
                if (box != null)
                {
                    box.SetActive(false);
                    Destroy(box);
                }
            }

            // Also check all root objects on layer 30 (Unity XR Simulation layer)
            GameObject[] allObjects = Object.FindObjectsByType<GameObject>(FindObjectsSortMode.None);
            foreach (var go in allObjects)
            {
                if (go.layer == 30) // XR Simulation Environment Layer
                {
                    go.SetActive(false);
                }
            }

            // 4. Adjust Main Camera to open-air view (22m back) & attach Free Fly Navigation
            Camera mainCam = Camera.main;
            if (mainCam != null)
            {
                // Remove any colliders, rigidbodies, or character controllers on camera
                var cols = mainCam.GetComponents<Collider>();
                foreach (var c in cols) Destroy(c);

                var rbs = mainCam.GetComponents<Rigidbody>();
                foreach (var r in rbs) Destroy(r);

                var ccs = mainCam.GetComponents<CharacterController>();
                foreach (var cc in ccs) Destroy(cc);

                // If camera is still stuck at origin or inside a box, relocate to overview
                if (mainCam.transform.position == Vector3.zero || mainCam.transform.position.z > -5.0f)
                {
                    mainCam.transform.position = new Vector3(8.5f, 11.5f, -25.5f);
                    mainCam.transform.rotation = Quaternion.Euler(8.0f, -20.0f, 0.0f);
                }

                mainCam.clearFlags = CameraClearFlags.SolidColor;
                mainCam.backgroundColor = new Color(0.42f, 0.55f, 0.70f); // Atmospheric Sky like the screenshot
                mainCam.fieldOfView = 55.0f;

                // Attach Free Fly Navigation Controller
                if (mainCam.GetComponent<BuildLensFlyCam>() == null)
                {
                    mainCam.gameObject.AddComponent<BuildLensFlyCam>();
                }
            }

            // 5. Ensure Detailed Sustainable Green BIM Building Model is instantiated
            GameObject buildingRoot = GameObject.Find("[Professional_Green_BIM_Building]");
            if (buildingRoot == null)
            {
                var existingGen = Object.FindAnyObjectByType<ProfessionalGreenBIMBuildingGenerator>();
                if (existingGen != null)
                {
                    existingGen.GenerateGreenBuildingModel();
                }
                else
                {
                    GameObject genGO = new GameObject("[Professional_Green_BIM_Building_Generator]");
                    var generator = genGO.AddComponent<ProfessionalGreenBIMBuildingGenerator>();
                    generator.GenerateGreenBuildingModel();
                }
            }


            // 6. Ensure Realtime REST API Client and Model Modifier are active
            if (BuildLens4D.Network.BuildLensApiClient.Instance == null)
            {
                GameObject netGO = new GameObject("[BuildLens_API_Client]");
                netGO.AddComponent<BuildLens4D.Network.BuildLensApiClient>();
            }

            if (BuildLens4D.Realtime.RealtimeModelModifier.Instance == null)
            {
                GameObject realtimeGO = new GameObject("[BuildLens_Realtime_Model_Modifier]");
                realtimeGO.AddComponent<BuildLens4D.Realtime.RealtimeModelModifier>();
            }
        }
    }
}

