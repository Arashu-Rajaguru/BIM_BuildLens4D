using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace BuildLens4D.Network
{
    /// <summary>
    /// Asynchronous REST API client connecting the Unity 3D client
    /// to the FastAPI backend with real-time bidirectional communication.
    /// </summary>
    public class BuildLensApiClient : MonoBehaviour
    {
        [Header("Backend Connection Settings")]
        [Tooltip("The base URL of the FastAPI backend.")]
        [SerializeField] private string apiBaseUrl = "http://localhost:8000/api";

        [Tooltip("Default timeout in seconds for API network requests.")]
        [SerializeField] private int timeoutSeconds = 8;

        public static BuildLensApiClient Instance { get; private set; }

        public string ApiBaseUrl => apiBaseUrl;

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

            // Automatically use localhost when running on PC / Editor
            if (Application.isEditor || Application.platform == RuntimePlatform.WindowsPlayer || Application.platform == RuntimePlatform.WindowsEditor)
            {
                apiBaseUrl = "http://localhost:8000/api";
                Debug.Log($"[BuildLens4D API] Connected to local FastAPI backend: {apiBaseUrl}");
            }
            else if (Application.platform == RuntimePlatform.Android)
            {
                if (apiBaseUrl.Contains("localhost") || apiBaseUrl.Contains("127.0.0.1"))
                {
                    apiBaseUrl = "http://192.168.29.102:8000/api";
                }
                Debug.Log($"[BuildLens4D API] Android client targeting PC Wi-Fi IP: {apiBaseUrl}");
            }

        }

        public void SetBaseUrl(string newUrl)
        {
            apiBaseUrl = newUrl.TrimEnd('/');
        }

        /// <summary>
        /// Asynchronously checks backend operational health.
        /// </summary>
        public void CheckHealth(Action<bool, string> callback)
        {
            StartCoroutine(GetRequestCoroutine($"{apiBaseUrl}/health", callback));
        }

        /// <summary>
        /// Retrieves all BIM elements for a specified project.
        /// </summary>
        public void GetProjectElements(string projectId, Action<bool, string> callback)
        {
            StartCoroutine(GetRequestCoroutine($"{apiBaseUrl}/projects/{projectId}/elements", callback));
        }

        /// <summary>
        /// Retrieves project 4D schedule summary metrics.
        /// </summary>
        public void GetProjectSummary(string projectId, Action<bool, string> callback)
        {
            StartCoroutine(GetRequestCoroutine($"{apiBaseUrl}/projects/{projectId}/summary", callback));
        }

        /// <summary>
        /// Posts a field progress observation.
        /// </summary>
        public void SubmitObservation(string projectId, string jsonPayload, Action<bool, string> callback)
        {
            StartCoroutine(PostRequestCoroutine($"{apiBaseUrl}/projects/{projectId}/observations", jsonPayload, callback));
        }

        /// <summary>
        /// Posts a human review decision (SRS FR-024).
        /// </summary>
        public void SubmitReviewDecision(string projectId, string jsonPayload, Action<bool, string> callback)
        {
            StartCoroutine(PostRequestCoroutine($"{apiBaseUrl}/projects/{projectId}/reviews", jsonPayload, callback));
        }

        /// <summary>
        /// Retrieves project audit trail logs (SRS FR-025).
        /// </summary>
        public void GetAuditTrail(string projectId, Action<bool, string> callback)
        {
            StartCoroutine(GetRequestCoroutine($"{apiBaseUrl}/projects/{projectId}/audit-trail", callback));
        }

        private IEnumerator GetRequestCoroutine(string url, Action<bool, string> callback)
        {
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.timeout = timeoutSeconds;
                request.SetRequestHeader("Accept", "application/json");

                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    callback?.Invoke(true, request.downloadHandler.text);
                }
                else
                {
                    string errorMsg = $"[GET Error] {request.responseCode}: {request.error} | URL: {url}";
                    callback?.Invoke(false, errorMsg);
                }
            }
        }

        private IEnumerator PostRequestCoroutine(string url, string jsonBody, Action<bool, string> callback)
        {
            using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
            {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonBody);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.timeout = timeoutSeconds;
                request.SetRequestHeader("Content-Type", "application/json");
                request.SetRequestHeader("Accept", "application/json");

                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    callback?.Invoke(true, request.downloadHandler.text);
                }
                else
                {
                    string errorMsg = $"[POST Error] {request.responseCode}: {request.error} | Response: {request.downloadHandler?.text}";
                    Debug.LogWarning(errorMsg);
                    callback?.Invoke(false, errorMsg);
                }
            }
        }
    }
}
