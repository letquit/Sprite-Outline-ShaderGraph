using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

// Renders the PixelOutline material on the sample sprite to PNG files so the
// outline behaviour can be verified without opening the Editor GUI.
// Usage: Unity.exe -batchmode -projectPath <project> -executeMethod OutlineCapture.Run
// The camera is rendered by URP in play mode; the render texture is read back
// a couple of frames after each thickness change.
public static class OutlineCapture
{
    const string ScenePath = "Assets/Scenes/SampleScene.unity";
    const string MatPath = "Assets/Shader/Shader Graphs_PixelOutline.mat";
    const string SpritePath = "Assets/Textures/sample(idle&walk)/idle.png";
    const string OutDir = "Tools";

    static readonly float[] Thicknesses = { 1.5f, 3f, 6f };
    static readonly string[] Names = { "render_t15", "render_t3", "render_t6" };

    static Camera cam;
    static Material mat;
    static int frame;
    static int shot;

    public static void Run()
    {
        Directory.CreateDirectory(OutDir);
        EditorSceneManager.OpenScene(ScenePath);

        // Keep the original scene content out of the capture frame.
        foreach (var c in Object.FindObjectsOfType<Camera>()) c.enabled = false;
        foreach (var r in Object.FindObjectsOfType<SpriteRenderer>())
            if (r.name == "idle_0") r.transform.position = new Vector3(100f, 100f, 0f);

        Sprite sprite = null;
        foreach (var o in AssetDatabase.LoadAllAssetsAtPath(SpritePath))
            if (o is Sprite s && (sprite == null || s.name.EndsWith("0"))) sprite = s;

        var go = new GameObject("CaptureSprite");
        var sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = sprite;
        mat = new Material(AssetDatabase.LoadAssetAtPath<Material>(MatPath));
        mat.SetFloat("_OutlineThickness", Thicknesses[0]);
        sr.sharedMaterial = mat;
        go.transform.position = Vector3.zero;
        go.transform.localScale = Vector3.one * 4f;

        var camGo = new GameObject("CaptureCamera");
        cam = camGo.AddComponent<Camera>();
        cam.orthographic = true;
        cam.orthographicSize = 3.2f;
        cam.transform.position = new Vector3(0f, 0f, -10f);
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = new Color(0.12f, 0.18f, 0.25f, 1f);
        cam.targetTexture = new RenderTexture(512, 512, 24, RenderTextureFormat.ARGB32);
        cam.enabled = true;

        Debug.Log($"[OutlineCapture] sprite={sprite} rect={sprite.rect} tex={sprite.texture}");

        EditorApplication.update += Tick;
        EditorApplication.EnterPlaymode();
    }

    static void Tick()
    {
        if (!EditorApplication.isPlaying) return;
        frame++;

        // 4 frames to warm up, then 3 frames per thickness (2 to settle + 1 to read).
        const int warmup = 6;
        if (frame < warmup) return;
        int local = frame - warmup;
        int index = local / 3;
        int phase = local % 3;

        if (index >= Thicknesses.Length)
        {
            EditorApplication.Exit(0);
            return;
        }

        if (phase == 0 && shot == index) mat.SetFloat("_OutlineThickness", Thicknesses[index]);
        if (phase == 2 && shot == index)
        {
            shot++;
            ReadBack(Names[index], Thicknesses[index]);
        }
    }

    static void ReadBack(string name, float thickness)
    {
        RenderTexture.active = cam.targetTexture;
        var tex = new Texture2D(cam.targetTexture.width, cam.targetTexture.height, TextureFormat.RGBA32, false);
        tex.ReadPixels(new Rect(0, 0, cam.targetTexture.width, cam.targetTexture.height), 0, 0);
        tex.Apply();
        File.WriteAllBytes(Path.Combine(OutDir, name + ".png"), tex.EncodeToPNG());
        Debug.Log($"[OutlineCapture] wrote {name} thickness={thickness}");
    }
}
