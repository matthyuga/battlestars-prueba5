using System;
using System.Collections.Generic;

namespace ExpressionLayerEditorSkeleton;

/// <summary>
/// Phase 0 adapters prepared for host wiring via delegates.
/// They avoid hard dependency on BepInEx/KKAPI types in this skeleton project.
/// </summary>
public sealed class BepInExLogger : ILogger
{
    private readonly Action<string> _info;
    private readonly Action<string> _warn;
    private readonly Action<string> _error;

    public BepInExLogger(Action<string>? info = null, Action<string>? warn = null, Action<string>? error = null)
    {
        _info = info ?? Console.WriteLine;
        _warn = warn ?? Console.WriteLine;
        _error = error ?? Console.WriteLine;
    }

    public void Info(string message) => _info(message);
    public void Warn(string message) => _warn(message);
    public void Error(string message) => _error(message);
}

public sealed class BepInExCharacterRuntimeAdapter : ICharacterRuntimeAdapter
{
    private readonly Func<CharacterContext> _getActiveCharacter;
    private readonly Func<CharacterContext, IReadOnlyCollection<BlendshapeParam>> _getBlendshapeRegistry;
    private readonly Func<CharacterContext, ExpressionState> _readCurrentState;
    private readonly Action<CharacterContext, ExpressionState> _applyState;

    public BepInExCharacterRuntimeAdapter(
        Func<CharacterContext> getActiveCharacter,
        Func<CharacterContext, IReadOnlyCollection<BlendshapeParam>> getBlendshapeRegistry,
        Func<CharacterContext, ExpressionState> readCurrentState,
        Action<CharacterContext, ExpressionState> applyState)
    {
        _getActiveCharacter = getActiveCharacter;
        _getBlendshapeRegistry = getBlendshapeRegistry;
        _readCurrentState = readCurrentState;
        _applyState = applyState;
    }

    public CharacterContext GetActiveCharacter() => _getActiveCharacter();

    public IReadOnlyCollection<BlendshapeParam> GetBlendshapeRegistry(CharacterContext context)
        => _getBlendshapeRegistry(context);

    public ExpressionState ReadCurrentState(CharacterContext context)
        => _readCurrentState(context);

    public void ApplyState(CharacterContext context, ExpressionState state)
        => _applyState(context, state);
}

public sealed class TimelinePluginBridge : ITimelineBridge
{
    private readonly Func<bool> _isAvailable;
    private readonly Func<int> _getCurrentFrame;
    private readonly Action<int> _setCurrentFrame;
    private readonly Action<string, float, int> _setKey;
    private readonly Action<Dictionary<string, float>, Dictionary<string, float>, int, int> _setKeysForRange;

    public TimelinePluginBridge(
        Func<bool> isAvailable,
        Func<int> getCurrentFrame,
        Action<int> setCurrentFrame,
        Action<string, float, int> setKey,
        Action<Dictionary<string, float>, Dictionary<string, float>, int, int> setKeysForRange)
    {
        _isAvailable = isAvailable;
        _getCurrentFrame = getCurrentFrame;
        _setCurrentFrame = setCurrentFrame;
        _setKey = setKey;
        _setKeysForRange = setKeysForRange;
    }

    public bool IsAvailable => _isAvailable();
    public int GetCurrentFrame() => _getCurrentFrame();
    public void SetCurrentFrame(int frame) => _setCurrentFrame(frame);
    public void SetKey(string paramKey, float value, int frame) => _setKey(paramKey, value, frame);

    public void SetKeysForRange(Dictionary<string, float> fromValues, Dictionary<string, float> toValues, int frameStart, int frameEnd)
        => _setKeysForRange(fromValues, toValues, frameStart, frameEnd);
}
