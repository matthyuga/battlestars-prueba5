using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace ExpressionLayerEditorSkeleton;

public sealed class ConsoleLogger : ILogger
{
    public void Info(string message) => Console.WriteLine($"[INFO] {message}");
    public void Warn(string message) => Console.WriteLine($"[WARN] {message}");
    public void Error(string message) => Console.WriteLine($"[ERROR] {message}");
}

public sealed class ExpressionComposer : IExpressionComposer
{
    public ExpressionState Compose(ExpressionState baseState, ExpressionState layerState, float layerIntensity, float globalIntensity)
    {
        var output = baseState.Clone();
        output.GlobalIntensity = globalIntensity;

        foreach (var kv in layerState.Values)
        {
            var baseValue = output.Values.TryGetValue(kv.Key, out var b) ? b : 0f;
            output.Values[kv.Key] = baseValue + (kv.Value * layerIntensity * globalIntensity);
        }

        return output;
    }
}

public sealed class ConstraintEngine : IConstraintEngine
{
    private readonly List<string> _warnings = new();

    public ExpressionState ValidateAndFix(ExpressionState state, IEnumerable<BlendshapeConstraint> constraints)
    {
        _warnings.Clear();
        var fixedState = state.Clone();

        foreach (var c in constraints)
        {
            if (!fixedState.Values.TryGetValue(c.Key, out var value))
                continue;

            var clamped = Math.Clamp(value, c.Min, c.Max);
            if (Math.Abs(clamped - value) > 0.0001f)
            {
                fixedState.Values[c.Key] = clamped;
                _warnings.Add($"Clamped '{c.Key}' from {value:F3} to {clamped:F3}.");
            }
        }

        return fixedState;
    }

    public IReadOnlyList<string> GetWarnings() => _warnings;
}

public sealed class JsonFilePresetRepository : IPresetRepository
{
    private readonly string _presetDirectory;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        WriteIndented = true
    };

    public JsonFilePresetRepository(string presetDirectory)
    {
        _presetDirectory = presetDirectory;
    }

    public void Save(ExpressionPreset preset)
    {
        if (preset is null)
            throw new ArgumentNullException(nameof(preset));
        EnsureValidPresetName(preset.Name);

        Directory.CreateDirectory(_presetDirectory);
        var safeName = ToFileSafeName(preset.Name);
        var path = Path.Combine(_presetDirectory, $"{safeName}.json");
        var json = JsonSerializer.Serialize(preset, JsonOptions);
        File.WriteAllText(path, json);
    }

    public ExpressionPreset Load(string presetName)
    {
        EnsureValidPresetName(presetName);
        var path = GetPresetPath(presetName);
        var json = File.ReadAllText(path);

        return JsonSerializer.Deserialize<ExpressionPreset>(json, JsonOptions)
               ?? throw new InvalidDataException($"Preset at '{path}' is invalid.");
    }

    public IReadOnlyCollection<string> ListPresetNames()
    {
        if (!Directory.Exists(_presetDirectory))
            return Array.Empty<string>();

        return Directory
            .EnumerateFiles(_presetDirectory, "*.json", SearchOption.TopDirectoryOnly)
            .Select(Path.GetFileNameWithoutExtension)
            .Where(x => !string.IsNullOrWhiteSpace(x))
            .Cast<string>()
            .OrderBy(x => x, StringComparer.OrdinalIgnoreCase)
            .ToArray();
    }

    public bool Exists(string presetName)
    {
        EnsureValidPresetName(presetName);
        var path = GetPresetPath(presetName);
        return File.Exists(path);
    }

    public void Delete(string presetName)
    {
        EnsureValidPresetName(presetName);
        var path = GetPresetPath(presetName);
        if (File.Exists(path))
            File.Delete(path);
    }

    public void Rename(string oldName, string newName, bool overwrite = false)
    {
        EnsureValidPresetName(oldName);
        EnsureValidPresetName(newName);

        if (string.Equals(oldName.Trim(), newName.Trim(), StringComparison.OrdinalIgnoreCase))
            return;

        var oldPath = GetPresetPath(oldName);
        var newPath = GetPresetPath(newName);

        if (!File.Exists(oldPath))
            throw new FileNotFoundException($"Preset '{oldName}' not found.", oldPath);

        if (File.Exists(newPath))
        {
            if (!overwrite)
                throw new IOException($"Target preset '{newName}' already exists.");

            File.Delete(newPath);
        }

        File.Move(oldPath, newPath);
    }

    private string GetPresetPath(string presetName)
    {
        var safeName = ToFileSafeName(presetName);
        return Path.Combine(_presetDirectory, $"{safeName}.json");
    }

    private static string ToFileSafeName(string value)
    {
        var invalid = Path.GetInvalidFileNameChars();
        var chars = value.Select(ch => invalid.Contains(ch) ? '_' : ch).ToArray();
        var safe = new string(chars).Trim();
        return string.IsNullOrWhiteSpace(safe) ? "preset" : safe;
    }

    private static void EnsureValidPresetName(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException("Preset name cannot be empty.", nameof(value));
    }
}

public sealed class SnapshotService : ISnapshotService
{
    private ExpressionState? _a;
    private ExpressionState? _b;

    public void SaveA(ExpressionState state) => _a = state.Clone();
    public void SaveB(ExpressionState state) => _b = state.Clone();

    public ExpressionState Interpolate(float t, bool smoothStep = false)
    {
        if (_a is null || _b is null)
            throw new InvalidOperationException("Snapshots A and B must be initialized.");

        var normalizedT = Math.Clamp(t, 0f, 1f);
        if (smoothStep)
            normalizedT = normalizedT * normalizedT * (3f - (2f * normalizedT));

        var result = new ExpressionState
        {
            CharacterId = _a.CharacterId,
            GlobalIntensity = Lerp(_a.GlobalIntensity, _b.GlobalIntensity, normalizedT)
        };

        var keys = _a.Values.Keys.Union(_b.Values.Keys, StringComparer.OrdinalIgnoreCase);
        foreach (var key in keys)
        {
            var av = _a.Values.TryGetValue(key, out var aVal) ? aVal : 0f;
            var bv = _b.Values.TryGetValue(key, out var bVal) ? bVal : 0f;
            result.Values[key] = Lerp(av, bv, normalizedT);
        }

        return result;
    }

    private static float Lerp(float a, float b, float t) => a + ((b - a) * t);
}

public sealed class NullTimelineBridge : ITimelineBridge
{
    public bool IsAvailable => false;
    public int GetCurrentFrame() => 0;
    public void SetCurrentFrame(int frame) { }
    public void SetKey(string paramKey, float value, int frame) { }
    public void SetKeysForRange(Dictionary<string, float> fromValues, Dictionary<string, float> toValues, int frameStart, int frameEnd) { }
}

public sealed class InMemoryTimelineBridge : ITimelineBridge
{
    private readonly Dictionary<int, Dictionary<string, float>> _keysByFrame = new();
    private int _currentFrame;

    public bool IsAvailable => true;

    public int GetCurrentFrame() => _currentFrame;

    public void SetCurrentFrame(int frame)
    {
        _currentFrame = Math.Max(0, frame);
    }

    public void SetKey(string paramKey, float value, int frame)
    {
        if (!_keysByFrame.TryGetValue(frame, out var frameKeys))
        {
            frameKeys = new Dictionary<string, float>(StringComparer.OrdinalIgnoreCase);
            _keysByFrame[frame] = frameKeys;
        }

        frameKeys[paramKey] = value;
    }

    public void SetKeysForRange(Dictionary<string, float> fromValues, Dictionary<string, float> toValues, int frameStart, int frameEnd)
    {
        if (frameEnd < frameStart)
            throw new ArgumentException("frameEnd must be >= frameStart");

        var total = Math.Max(1, frameEnd - frameStart);
        var keys = fromValues.Keys.Union(toValues.Keys, StringComparer.OrdinalIgnoreCase);

        for (var frame = frameStart; frame <= frameEnd; frame++)
        {
            var t = (frame - frameStart) / (float)total;
            foreach (var key in keys)
            {
                var from = fromValues.TryGetValue(key, out var fv) ? fv : 0f;
                var to = toValues.TryGetValue(key, out var tv) ? tv : 0f;
                var v = from + ((to - from) * t);
                SetKey(key, v, frame);
            }
        }
    }

    public IReadOnlyDictionary<int, IReadOnlyDictionary<string, float>> SnapshotKeys()
    {
        return _keysByFrame.ToDictionary(
            kv => kv.Key,
            kv => (IReadOnlyDictionary<string, float>)new Dictionary<string, float>(kv.Value, StringComparer.OrdinalIgnoreCase));
    }
}

public sealed class InMemoryCharacterRuntimeAdapter : ICharacterRuntimeAdapter
{
    private readonly CharacterContext _ctx = new()
    {
        CharacterId = "demo-char",
        CharacterName = "Demo Character"
    };

    private readonly List<BlendshapeParam> _registry = new()
    {
        new BlendshapeParam { Key = "eye_face.f00_def_cl", Layer = FaceLayer.Eyes, Min = -1f, Max = 1f },
        new BlendshapeParam { Key = "eye_face.f00_egao_op", Layer = FaceLayer.Eyes, Min = -1f, Max = 1f },
        new BlendshapeParam { Key = "kuti_face.f00_doki_ss_op", Layer = FaceLayer.Mouth, Min = -1f, Max = 1f },
        new BlendshapeParam { Key = "kuti_face.f00_ikari_cl", Layer = FaceLayer.Mouth, Min = -1f, Max = 1f }
    };

    private readonly ExpressionState _state = new() { CharacterId = "demo-char" };

    public CharacterContext GetActiveCharacter() => _ctx;
    public IReadOnlyCollection<BlendshapeParam> GetBlendshapeRegistry(CharacterContext context) => _registry;
    public ExpressionState ReadCurrentState(CharacterContext context) => _state.Clone();

    public void ApplyState(CharacterContext context, ExpressionState state)
    {
        _state.CharacterId = state.CharacterId;
        _state.GlobalIntensity = state.GlobalIntensity;
        _state.Values = new Dictionary<string, float>(state.Values, StringComparer.OrdinalIgnoreCase);
    }
}
