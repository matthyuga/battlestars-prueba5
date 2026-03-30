using System;
using System.Collections.Generic;

namespace ExpressionLayerEditorSkeleton;

/// <summary>
/// Step 3 stubs for production integrations.
/// Replace internals with actual BepInEx/KKAPI/Timeline calls in the plugin project.
/// </summary>
public sealed class BepInExLogger : ILogger
{
    public void Info(string message) => throw new NotImplementedException("Wire this to BepInEx logger (LogInfo).");
    public void Warn(string message) => throw new NotImplementedException("Wire this to BepInEx logger (LogWarning).");
    public void Error(string message) => throw new NotImplementedException("Wire this to BepInEx logger (LogError).");
}

public sealed class BepInExCharacterRuntimeAdapter : ICharacterRuntimeAdapter
{
    public CharacterContext GetActiveCharacter() => throw new NotImplementedException("Resolve active character from Studio scene context.");

    public IReadOnlyCollection<BlendshapeParam> GetBlendshapeRegistry(CharacterContext context)
        => throw new NotImplementedException("Build registry from KKPE/face blendshape metadata.");

    public ExpressionState ReadCurrentState(CharacterContext context)
        => throw new NotImplementedException("Read current blendshape values from character runtime.");

    public void ApplyState(CharacterContext context, ExpressionState state)
        => throw new NotImplementedException("Apply blendshape values to character runtime.");
}

public sealed class TimelinePluginBridge : ITimelineBridge
{
    public bool IsAvailable => throw new NotImplementedException("Detect Timeline plugin availability.");

    public int GetCurrentFrame() => throw new NotImplementedException("Read current frame from Timeline plugin.");

    public void SetCurrentFrame(int frame)
        => throw new NotImplementedException("Set current frame in Timeline plugin.");

    public void SetKey(string paramKey, float value, int frame)
        => throw new NotImplementedException("Insert/update keyframe via Timeline API.");

    public void SetKeysForRange(Dictionary<string, float> fromValues, Dictionary<string, float> toValues, int frameStart, int frameEnd)
        => throw new NotImplementedException("Write interpolated keyframes using Timeline API.");
}
