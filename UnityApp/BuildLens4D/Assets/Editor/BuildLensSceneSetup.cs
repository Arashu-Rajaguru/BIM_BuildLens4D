#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using BuildLens4D.AR;
using BuildLens4D.BIM;
using BuildLens4D.Building;
using BuildLens4D.Capture;
using BuildLens4D.Navigation;
using BuildLens4D.Network;
using BuildLens4D.Realtime;

namespace BuildLens4D.EditorScripts
{
    [InitializeOnLoad]
    public static class BuildLensSceneSetup
    {
        static BuildLensSceneSetup()
        {
            EditorApplication.delayCall += () =>
            {
                // Auto-generate if current scene is empty or has only the legacy Column_B1_01 cube
                GameObject legacyCube = GameObject.Find("Column_B1_01");
                GameObject greenBIM = GameObject.Find("[Professional_Green_BIM_Building]");
                if (legacyCube != null && greenBIM == null)
                {
                    Debug.Log("[BuildLens4D] Detected legacy placeholder scene — Auto-generating complete Green BIM scene...");
                    GenerateCompleteScene();
                }
            };
        }

        [MenuItem("BuildLens4D/Generate Complete Green BIM Building Scene")]
        public static void GenerateCompleteScene()
        {
            // 1. Create fresh new empty scene
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // 2. Add Directional Sun Light for bright architectural illumination
            GameObject lightGO = new GameObject("Directional Light");
            var light = lightGO.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.4f;
            light.color = new Color(1.0f, 0.98f, 0.92f);
            lightGO.transform.rotation = Quaternion.Euler(50.0f, -30.0f, 0.0f);

            // 3. Create AR Session & Managers (for Mobile AR build target)
            GameObject arSessionGO = new GameObject("AR Session");
            arSessionGO.AddComponent<ARSession>();
            arSessionGO.AddComponent<ARInputManager>();

            // 4. Create Main Camera with Free Fly Navigation & Open-Air Architectural View
            GameObject mainCameraGO = new GameObject("Main Camera");
            mainCameraGO.tag = "MainCamera";
            mainCameraGO.transform.position = new Vector3(0.0f, 8.5f, -22.0f);
            mainCameraGO.transform.rotation = Quaternion.Euler(18.0f, 0.0f, 0.0f);

            var camera = mainCameraGO.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.12f, 0.16f, 0.22f); // Deep Slate Sky
            camera.fieldOfView = 60.0f;
            camera.nearClipPlane = 0.1f;
            camera.farClipPlane = 1000.0f;

            // Free 6-DOF Fly Camera navigation (WASD + mouse look + Space/C)
            mainCameraGO.AddComponent<BuildLensFlyCam>();

            // AR Camera Manager for AR runtime
            mainCameraGO.AddComponent<ARCameraManager>();

            // 5. Create [BuildLensSystem] API & 4D Progress Monitoring
            GameObject systemGO = new GameObject("[BuildLensSystem]");
            var apiClient = systemGO.AddComponent<BuildLensApiClient>();
            apiClient.SetBaseUrl("http://127.0.0.1:8000/api");

            systemGO.AddComponent<ProgressCaptureController>();
            systemGO.AddComponent<RealtimeModelModifier>();

            // 6. Generate Complete Detailed Sustainable Green BIM Building
            GameObject buildingGenGO = new GameObject("[Professional_Green_BIM_Building_Generator]");
            var generator = buildingGenGO.AddComponent<ProfessionalGreenBIMBuildingGenerator>();
            generator.GenerateGreenBuildingModel();

            // 7. Save Scene to BOTH Assets/MainARScene.unity and Assets/Scenes/MainARScene.unity
            string rootScenePath = "Assets/MainARScene.unity";
            EditorSceneManager.SaveScene(scene, rootScenePath);

            string scenesDir = "Assets/Scenes";
            if (!Directory.Exists(scenesDir))
            {
                Directory.CreateDirectory(scenesDir);
            }
            string subScenePath = "Assets/Scenes/MainARScene.unity";
            EditorSceneManager.SaveScene(scene, subScenePath);

            // 8. Update EditorBuildSettings
            EditorBuildSettingsScene[] buildScenes = new EditorBuildSettingsScene[]
            {
                new EditorBuildSettingsScene(rootScenePath, true),
                new EditorBuildSettingsScene(subScenePath, true)
            };
            EditorBuildSettings.scenes = buildScenes;

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log($"[BuildLens4D] Successfully generated complete Green BIM Building AR Scene at {rootScenePath} & {subScenePath}!");
        }
    }
}
#endif
