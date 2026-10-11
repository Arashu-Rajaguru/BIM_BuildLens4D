using UnityEngine;

namespace BuildLens4D.Navigation
{
    /// <summary>
    /// Free 6-DOF Fly-Camera Navigation Controller.
    /// Operates with immediate WASD movement without requiring key holding locks or right click for position.
    /// Allows 100% free movement throughout the 3D building and surrounding landscape.
    /// </summary>
    public class BuildLensFlyCam : MonoBehaviour
    {
        [Header("Movement Settings")]
        [SerializeField] private float moveSpeed = 10.0f;
        [SerializeField] private float boostMultiplier = 2.5f;
        [SerializeField] private float mouseSensitivity = 2.5f;

        private float rotationX = 18.0f;
        private float rotationY = 0.0f;

        private void Start()
        {
            // Remove any physics components on camera
            var col = GetComponent<Collider>();
            if (col != null) Destroy(col);

            var rb = GetComponent<Rigidbody>();
            if (rb != null) Destroy(rb);

#if UNITY_EDITOR
            // Detach camera from XR Origin hierarchy so world flycam movements are never overridden
            transform.SetParent(null, true);

            // Disable and destroy TrackedPoseDriver to prevent XR simulation from overriding camera position
            var monobehaviours = GetComponents<MonoBehaviour>();
            foreach (var mb in monobehaviours)
            {
                if (mb != null && mb != this && mb.GetType().Name.Contains("TrackedPoseDriver"))
                {
                    mb.enabled = false;
                    Destroy(mb);
                }
            }
#endif

            Vector3 angles = transform.eulerAngles;
            rotationX = angles.x;
            rotationY = angles.y;
        }

        private void Update()
        {
            // Mouse Look (Right-Click Drag or Left-Click Drag)
            if (Input.GetMouseButton(1) || Input.GetMouseButton(0))
            {
                rotationY += Input.GetAxis("Mouse X") * mouseSensitivity;
                rotationX -= Input.GetAxis("Mouse Y") * mouseSensitivity;
                rotationX = Mathf.Clamp(rotationX, -88.0f, 88.0f);

                transform.rotation = Quaternion.Euler(rotationX, rotationY, 0.0f);
            }

            // Keyboard Movement (WASD + QE) — Active immediately on key press
            float speed = moveSpeed;
            if (Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift))
            {
                speed *= boostMultiplier;
            }

            Vector3 direction = Vector3.zero;

            if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow)) direction += transform.forward;
            if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow)) direction -= transform.forward;
            if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) direction -= transform.right;
            if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) direction += transform.right;
            if (Input.GetKey(KeyCode.E) || Input.GetKey(KeyCode.Space)) direction += Vector3.up;
            if (Input.GetKey(KeyCode.Q) || Input.GetKey(KeyCode.C) || Input.GetKey(KeyCode.LeftControl)) direction -= Vector3.up;

            // Press 'R' to reset camera to standard overview
            if (Input.GetKeyDown(KeyCode.R))
            {
                transform.position = new Vector3(8.5f, 11.5f, -25.5f);
                transform.rotation = Quaternion.Euler(8.0f, -20.0f, 0.0f);
                rotationX = 8.0f;
                rotationY = -20.0f;
            }

            // Direct position update
            transform.position += direction * speed * Time.deltaTime;
        }

        private void OnGUI()
        {
            // Navigation hint overlay
            GUI.Box(new Rect(10, 10, 420, 115), "🚀 BuildLens 4D — Free Fly Navigation");
            GUI.Label(new Rect(20, 32, 400, 20), "• Fly: W / A / S / D or Arrow Keys");
            GUI.Label(new Rect(20, 52, 400, 20), "• Look: Drag Mouse (Left or Right Click)");
            GUI.Label(new Rect(20, 72, 400, 20), "• Up / Down: Space / E (Up), C / Ctrl / Q (Down)");
            GUI.Label(new Rect(20, 92, 400, 20), "• Shift: Speed Boost | R: Reset View to Overview");
        }
    }
}
