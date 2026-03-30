using System;
using System.Collections.Generic;

namespace ExpressionLayerEditorSkeleton;

public enum FaceLayer
{
    Eyes,
    Brows,
    Mouth,
    Jaw,
    NoseCheek,
    Other
}

public sealed class BlendshapeParam
{
    public string Key { get; set; } = string.Empty;
    public FaceLayer Layer { get; set; } = FaceLayer.Other;
    public float Value { get; set; }
    public float Min { get; set; } = -1f;
    public float Max { get; set; } = 1f;
}

public sealed class CharacterContext
{
    public string CharacterId { get; set; } = string.Empty;
    public string CharacterName { get; set; } = string.Empty;
    public bool IsValid => !string.IsNullOrWhiteSpace(CharacterId);
}

public sealed class ExpressionState
{
    public string CharacterId { get; set; } = string.Empty;
    public float GlobalIntensity { get; set; } = 1f;
    public Dictionary<string, float> Values { get; set; } = new(StringComparer.OrdinalIgnoreCase);

    public ExpressionState Clone()
    {
        return new ExpressionState
        {
            CharacterId = CharacterId,
            GlobalIntensity = GlobalIntensity,
            Values = new Dictionary<string, float>(Values, StringComparer.OrdinalIgnoreCase)
        };
    }
}

public sealed class ExpressionPreset
{
    public string SchemaVersion { get; set; } = "0.2";
    public string Name { get; set; } = string.Empty;
    public List<string> Tags { get; set; } = new();
    public float RecommendedIntensity { get; set; } = 1f;
    public Dictionary<string, float> Values { get; set; } = new(StringComparer.OrdinalIgnoreCase);
}

public sealed class BlendshapeConstraint
{
    public string Key { get; set; } = string.Empty;
    public float Min { get; set; } = -1f;
    public float Max { get; set; } = 1f;
}

public sealed class MacroDefinition
{
    public string Name { get; set; } = string.Empty;
    public Dictionary<string, float> Weights { get; set; } = new(StringComparer.OrdinalIgnoreCase);
}

public sealed class AutoKeyOptions
{
    public float DeltaThreshold { get; set; } = 0.01f;
    public int KeyEveryNFrames { get; set; } = 1;
}

public sealed class PluginOptions
{
    public string PresetDirectory { get; set; } = "UserData/ELE/presets";
    public float DefaultGlobalIntensity { get; set; } = 1f;
    public bool StrictClamp { get; set; } = true;
}
