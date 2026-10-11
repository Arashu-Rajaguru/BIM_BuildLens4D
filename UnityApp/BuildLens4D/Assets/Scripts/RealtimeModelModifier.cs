using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using BuildLens4D.BIM;
using BuildLens4D.Network;

namespace BuildLens4D.Realtime
{
    /// <summary>
    /// Handles real-time 3D BIM model synchronization, spatial positioning,
    /// dynamic progress scaling, 4D schedule timeline scrubbing, and floor-level isolation.
    /// </summary>
    public class RealtimeModelModifier : MonoBehaviour
    {
        [Header("System References")]
        [SerializeField] private BuildLensApiClient apiClient;
        [SerializeField] private Transform bimContainerTransform;

        [Header("Realtime Polling Configuration")]
        [SerializeField] private string activeProjectId = "proj-terminal-04";
        [SerializeField] private float pollIntervalSeconds = 1.8f;
        [SerializeField] private bool enableRealtimeSync = true;
        [SerializeField] private bool showOnScreenHUD = true;

        [Header("4D Time Scrubber & Floor Isolator")]
        [SerializeField] private bool isSimulationMode = false;
        [SerializeField] private string simulationDateStr = "2026-10-11";
        [SerializeField] private string activeFloorFilter = "ALL";

        // Registry of live 3D BIM Element objects indexed by stable Element ID
        private readonly Dictionary<string, BIMElementMetadata> liveElements = new Dictionary<string, BIMElementMetadata>();
        private Coroutine syncCoroutine;
        private string lastSyncTime = "Pending...";
        private string statusMessage = "Initializing Realtime Link...";
        private string recentNotification = "";
        private float notificationTimer = 0f;
        private bool isConnected = false;
        private DateTime currentSimDate = new DateTime(2026, 10, 11);

        public static RealtimeModelModifier Instance { get; private set; }

        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
                return;
            }
        }

        private void Start()
        {
            if (apiClient == null) apiClient = BuildLensApiClient.Instance;
            if (apiClient == null)
            {
                GameObject netGO = new GameObject("[BuildLens_API_Client]");
                apiClient = netGO.AddComponent<BuildLensApiClient>();
            }

            // Register initial scene elements across the entire scene
            RegisterExistingSceneElements();

            if (enableRealtimeSync)
            {
                syncCoroutine = StartCoroutine(RealtimeSyncLoop());
            }
        }

        private void Update()
        {
            if (notificationTimer > 0f)
            {
                notificationTimer -= Time.deltaTime;
                if (notificationTimer <= 0f) recentNotification = "";
            }

            // Keyboard Shortcuts: [ and ] for 4D Scrubber, H for HUD toggle
            if (Input.GetKeyDown(KeyCode.LeftBracket))
            {
                StepSimulationDate(-1);
            }
            else if (Input.GetKeyDown(KeyCode.RightBracket))
            {
                StepSimulationDate(1);
            }
            else if (Input.GetKeyDown(KeyCode.H))
            {
                showOnScreenHUD = !showOnScreenHUD;
            }
        }

        public void RegisterExistingSceneElements()
        {
            var elements = UnityEngine.Object.FindObjectsByType<BIMElementMetadata>(FindObjectsSortMode.None);
            foreach (var meta in elements)
            {
                if (!string.IsNullOrEmpty(meta.ElementId))
                {
                    liveElements[meta.ElementId] = meta;
                }
            }
            Debug.Log($"[BuildLens Realtime] Registered {liveElements.Count} 3D BIM elements in scene.");
        }

        private IEnumerator RealtimeSyncLoop()
        {
            while (enableRealtimeSync)
            {
                if (!isSimulationMode)
                {
                    FetchLatestProgress();
                }
                yield return new WaitForSeconds(pollIntervalSeconds);
            }
        }

        public void FetchLatestProgress()
        {
            if (apiClient == null) apiClient = BuildLensApiClient.Instance;
            if (apiClient == null) return;

            apiClient.GetProjectElements(activeProjectId, (success, jsonResponse) =>
            {
                if (success)
                {
                    isConnected = true;
                    lastSyncTime = DateTime.Now.ToString("HH:mm:ss");
                    statusMessage = $"Live Connected ({liveElements.Count} elements tracked)";
                    ProcessElementUpdatesJson(jsonResponse);
                }
                else
                {
                    isConnected = false;
                    statusMessage = "Connecting to http://localhost:8000/api...";
                }
            });
        }

        public void ProcessElementUpdatesJson(string json)
        {
            try
            {
                var elementList = SimpleJsonArrayParser(json);
                foreach (var el in elementList)
                {
                    string id = GetDictValue(el, "id");
                    string state = GetDictValue(el, "verification_state");
                    string type = GetDictValue(el, "element_type");
                    string label = GetDictValue(el, "label");
                    string start = GetDictValue(el, "planned_start");
                    string end = GetDictValue(el, "planned_end");

                    if (string.IsNullOrEmpty(id)) continue;

                    if (liveElements.TryGetValue(id, out BIMElementMetadata meta))
                    {
                        if (meta.VerificationState != state)
                        {
                            string previousState = meta.VerificationState;
                            meta.UpdateVerificationState(state, DateTime.UtcNow.ToString("o"));
                            AnimateElementStateChange(meta.gameObject, state);

                            recentNotification = $"⚡ LIVE UPDATE: [{id}] -> {state.ToUpper()}!";
                            notificationTimer = 5.0f;
                            Debug.Log($"[BuildLens Realtime] {recentNotification}");
                        }
                    }
                    else
                    {
                        CreateNew3DElement(id, type, label, start, end, state);
                    }
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[BuildLens Realtime] Error processing realtime JSON: {ex.Message}");
            }
        }

        // 4D Time-Lapse Schedule Scrubber Simulation
        public void StepSimulationDate(int daysDelta)
        {
            isSimulationMode = true;
            currentSimDate = currentSimDate.AddDays(daysDelta);
            simulationDateStr = currentSimDate.ToString("yyyy-MM-dd");
            ApplySimulationDate(currentSimDate);
        }

        public void ApplySimulationDate(DateTime targetDate)
        {
            recentNotification = $"⏳ 4D SIMULATION: Scrubbed to {targetDate:yyyy-MM-dd}";
            notificationTimer = 3.0f;

            foreach (var kvp in liveElements)
            {
                var meta = kvp.Value;
                if (DateTime.TryParse(meta.PlannedStartDate, out DateTime startD) &&
                    DateTime.TryParse(meta.PlannedEndDate, out DateTime endD))
                {
                    string simState;
                    if (targetDate < startD) simState = "not_started";
                    else if (targetDate <= endD) simState = "in_progress";
                    else simState = "verified_complete";

                    meta.UpdateVerificationState(simState);
                }
            }
        }

        public void ResetToLiveBackend()
        {
            isSimulationMode = false;
            statusMessage = "Resetting to Live Backend...";
            FetchLatestProgress();
        }

        // Floor-by-Floor & Zone Spatial Isolator
        public void SetFloorFilter(string floor)
        {
            activeFloorFilter = floor;
            foreach (var kvp in liveElements)
            {
                var meta = kvp.Value;
                bool shouldShow = true;

                if (floor == "Foundation")
                {
                    shouldShow = meta.ElementType.Equals("Footing", StringComparison.OrdinalIgnoreCase) ||
                                 meta.ElementType.Equals("Wall", StringComparison.OrdinalIgnoreCase);
                }
                else if (floor == "Ground")
                {
                    shouldShow = meta.SpatialZone.Contains("Ground") || meta.ElementType.Equals("Column", StringComparison.OrdinalIgnoreCase);
                }
                else if (floor == "Mezzanine")
                {
                    shouldShow = meta.SpatialZone.Contains("Mezzanine") || meta.ElementType.Equals("Beam", StringComparison.OrdinalIgnoreCase);
                }

                if (meta.gameObject != null)
                {
                    var ren = meta.GetComponent<Renderer>();
                    if (ren != null) ren.enabled = shouldShow;
                    var tm = meta.GetComponentInChildren<TextMesh>();
                    if (tm != null) tm.gameObject.SetActive(shouldShow);
                }
            }
            recentNotification = $"🏢 FLOOR ISOLATOR: Filtered to [{floor}]";
            notificationTimer = 3.0f;
        }

        public GameObject CreateNew3DElement(string id, string type, string label, string plannedStart, string plannedEnd, string state)
        {
            GameObject newObj = null;

            if (type.Equals("Column", StringComparison.OrdinalIgnoreCase))
            {
                newObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
                newObj.transform.localScale = new Vector3(0.8f, 3.2f, 0.8f);
            }
            else if (type.Equals("Beam", StringComparison.OrdinalIgnoreCase))
            {
                newObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
                newObj.transform.localScale = new Vector3(4.0f, 0.45f, 0.6f);
            }
            else if (type.Equals("Slab", StringComparison.OrdinalIgnoreCase))
            {
                newObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
                newObj.transform.localScale = new Vector3(5.0f, 0.25f, 5.0f);
            }
            else
            {
                newObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
                newObj.transform.localScale = Vector3.one * 1.2f;
            }

            newObj.name = $"{type}_{id}";
            var col = newObj.GetComponent<Collider>();
            if (col != null) Destroy(col);

            int index = liveElements.Count;
            newObj.transform.position = new Vector3((index % 4) * 2.5f - 4.0f, 1.6f, -12.0f + (index / 4) * 3.0f);

            var meta = newObj.AddComponent<BIMElementMetadata>();
            meta.SetElementData(id, type, label, "Spatial Grid", plannedStart, plannedEnd, state);

            CreateWorldSpaceBadge(newObj, id, state);

            liveElements[id] = meta;
            return newObj;
        }

        private void CreateWorldSpaceBadge(GameObject target, string id, string state)
        {
            GameObject tagGO = new GameObject($"Tag_{id}");
            tagGO.transform.SetParent(target.transform, false);
            tagGO.transform.localPosition = new Vector3(0.0f, 1.1f, 0.0f);
            tagGO.transform.localScale = new Vector3(0.12f, 0.12f, 0.12f);

            TextMesh textMesh = tagGO.AddComponent<TextMesh>();
            textMesh.text = $"[{id}]\n{state.Replace("_", " ").ToUpper()}";
            textMesh.fontSize = 24;
            textMesh.alignment = TextAlignment.Center;
            textMesh.anchor = TextAnchor.MiddleCenter;
            textMesh.characterSize = 0.5f;
            textMesh.color = BIMElementMetadata.GetStatusColor(state, 1.0f);
        }

        private void AnimateElementStateChange(GameObject target, string state)
        {
            if (target == null) return;
            var meta = target.GetComponent<BIMElementMetadata>();
            if (meta != null) meta.TriggerVisualHighlight();
        }

        // OnGUI Realtime HUD Overlay with Scrubber & Isolator
        private void OnGUI()
        {
            if (!showOnScreenHUD) return;

            GUI.color = Color.white;
            GUIStyle boxStyle = new GUIStyle(GUI.skin.box)
            {
                fontSize = 11,
                alignment = TextAnchor.UpperLeft
            };

            GUILayout.BeginArea(new Rect(15, 15, 360, 220), boxStyle);
            GUILayout.Label($"<b>BuildLens 4D Realtime Monitor & 4D Scrubber</b>", GUILayout.ExpandWidth(true));
            
            GUI.color = isConnected ? new Color(0.2f, 1f, 0.5f) : new Color(1f, 0.4f, 0.4f);
            GUILayout.Label($"Status: {statusMessage}");
            
            GUI.color = Color.white;
            GUILayout.Label($"Project: {activeProjectId} | Tracked: {liveElements.Count}");

            if (isSimulationMode)
            {
                GUI.color = new Color(0.3f, 0.8f, 1f);
                GUILayout.Label($"<b>Simulated 4D Date: {simulationDateStr}</b> (Keys [ / ])");
            }
            else
            {
                GUILayout.Label($"Mode: Live Backend Sync (Interval {pollIntervalSeconds}s)");
            }

            if (!string.IsNullOrEmpty(recentNotification))
            {
                GUI.color = new Color(1f, 0.85f, 0.2f);
                GUILayout.Label($"<b>{recentNotification}</b>");
            }

            GUI.color = Color.white;

            // 4D Scrubber Buttons
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("◄ -1 Day")) StepSimulationDate(-1);
            if (GUILayout.Button("+1 Day ►")) StepSimulationDate(1);
            if (GUILayout.Button("Live Reset")) ResetToLiveBackend();
            GUILayout.EndHorizontal();

            // Floor Isolator Buttons
            GUILayout.Label("Floor Isolator:");
            GUILayout.BeginHorizontal();
            if (GUILayout.Button(activeFloorFilter == "ALL" ? "<b>[All]</b>" : "All")) SetFloorFilter("ALL");
            if (GUILayout.Button(activeFloorFilter == "Foundation" ? "<b>[Found]</b>" : "Found")) SetFloorFilter("Foundation");
            if (GUILayout.Button(activeFloorFilter == "Ground" ? "<b>[Ground]</b>" : "Ground")) SetFloorFilter("Ground");
            if (GUILayout.Button(activeFloorFilter == "Mezzanine" ? "<b>[Mezz]</b>" : "Mezz")) SetFloorFilter("Mezzanine");
            GUILayout.EndHorizontal();

            GUILayout.EndArea();
        }

        private List<Dictionary<string, string>> SimpleJsonArrayParser(string json)
        {
            var result = new List<Dictionary<string, string>>();
            if (string.IsNullOrEmpty(json) || !json.Trim().StartsWith("[")) return result;

            string inner = json.Trim().Trim('[', ']');
            string[] objects = inner.Split(new string[] { "}," }, StringSplitOptions.RemoveEmptyEntries);

            foreach (var rawObj in objects)
            {
                var dict = new Dictionary<string, string>();
                string cleaned = rawObj.Replace("{", "").Replace("}", "").Replace("\"", "");
                string[] pairs = cleaned.Split(',');
                foreach (var pair in pairs)
                {
                    string[] kv = pair.Split(new char[] { ':' }, 2);
                    if (kv.Length == 2)
                    {
                        dict[kv[0].Trim()] = kv[1].Trim();
                    }
                }
                result.Add(dict);
            }
            return result;
        }

        private string GetDictValue(Dictionary<string, string> dict, string key)
        {
            if (dict != null && dict.TryGetValue(key, out var val))
            {
                return val;
            }
            return string.Empty;
        }
    }
}
