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
    private readonly ILogger _logger;

    private CharacterContext? _lastValidCharacter;
    private IReadOnlyCollection<BlendshapeParam>? _cachedRegistry;
    private string? _cachedRegistryCharacterId;

    public BepInExCharacterRuntimeAdapter(
        Func<CharacterContext> getActiveCharacter,
        Func<CharacterContext, IReadOnlyCollection<BlendshapeParam>> getBlendshapeRegistry,
        Func<CharacterContext, ExpressionState> readCurrentState,
        Action<CharacterContext, ExpressionState> applyState,
        ILogger? logger = null)
    {
        _getActiveCharacter = getActiveCharacter;
        _getBlendshapeRegistry = getBlendshapeRegistry;
        _readCurrentState = readCurrentState;
        _applyState = applyState;
        _logger = logger ?? new BepInExLogger();
    }

    public CharacterContext GetActiveCharacter()
    {
        try
        {
            var current = _getActiveCharacter();
            if (current.IsValid)
            {
                _lastValidCharacter = current;
                return current;
            }

            if (_lastValidCharacter is not null)
            {
                _logger.Warn("Active character is invalid, reusing last valid character context.");
                return _lastValidCharacter;
            }

            return current;
        }
        catch (Exception ex)
        {
            _logger.Error($"Failed to resolve active character: {ex.Message}");
            return _lastValidCharacter ?? new CharacterContext();
        }
    }

    public IReadOnlyCollection<BlendshapeParam> GetBlendshapeRegistry(CharacterContext context)
    {
        if (!context.IsValid)
            return Array.Empty<BlendshapeParam>();

        if (_cachedRegistry is not null && string.Equals(_cachedRegistryCharacterId, context.CharacterId, StringComparison.OrdinalIgnoreCase))
            return _cachedRegistry;

        try
        {
            var registry = _getBlendshapeRegistry(context) ?? Array.Empty<BlendshapeParam>();
            _cachedRegistry = registry;
            _cachedRegistryCharacterId = context.CharacterId;
            return registry;
        }
        catch (Exception ex)
        {
            _logger.Error($"Failed to read blendshape registry for '{context.CharacterName}': {ex.Message}");
            return _cachedRegistry ?? Array.Empty<BlendshapeParam>();
        }
    }

    public ExpressionState ReadCurrentState(CharacterContext context)
    {
        if (!context.IsValid)
            return new ExpressionState();

        try
        {
            return _readCurrentState(context) ?? new ExpressionState { CharacterId = context.CharacterId };
        }
        catch (Exception ex)
        {
            _logger.Error($"Failed to read expression state for '{context.CharacterName}': {ex.Message}");
            return new ExpressionState { CharacterId = context.CharacterId };
        }
    }

    public void ApplyState(CharacterContext context, ExpressionState state)
    {
        if (!context.IsValid)
        {
            _logger.Warn("Skipping ApplyState because active character context is invalid.");
            return;
        }

        try
        {
            _applyState(context, state);
        }
        catch (Exception ex)
        {
            _logger.Error($"Failed to apply expression state for '{context.CharacterName}': {ex.Message}");
        }
    }
}

public sealed class TimelinePluginBridge : ITimelineBridge
{
    private readonly Func<bool> _isAvailable;
    private readonly Func<int> _getCurrentFrame;
    private readonly Action<int> _setCurrentFrame;
    private readonly Action<string, float, int> _setKey;
    private readonly Action<Dictionary<string, float>, Dictionary<string, float>, int, int> _setKeysForRange;
    private readonly ILogger _logger;

    public TimelinePluginBridge(
        Func<bool> isAvailable,
        Func<int> getCurrentFrame,
        Action<int> setCurrentFrame,
        Action<string, float, int> setKey,
        Action<Dictionary<string, float>, Dictionary<string, float>, int, int> setKeysForRange,
        ILogger? logger = null)
    {
        _isAvailable = isAvailable;
        _getCurrentFrame = getCurrentFrame;
        _setCurrentFrame = setCurrentFrame;
        _setKey = setKey;
        _setKeysForRange = setKeysForRange;
        _logger = logger ?? new BepInExLogger();
    }

    public bool IsAvailable
    {
        get
        {
            try { return _isAvailable(); }
            catch (Exception ex)
            {
                _logger.Warn($"Timeline availability check failed: {ex.Message}");
                return false;
            }
        }
    }

    public int GetCurrentFrame()
    {
        try { return _getCurrentFrame(); }
        catch (Exception ex)
        {
            _logger.Warn($"Failed to get current frame from timeline: {ex.Message}");
            return 0;
        }
    }

    public void SetCurrentFrame(int frame)
    {
        try { _setCurrentFrame(frame); }
        catch (Exception ex)
        {
            _logger.Warn($"Failed to set timeline frame {frame}: {ex.Message}");
        }
    }

    public void SetKey(string paramKey, float value, int frame)
    {
        try { _setKey(paramKey, value, frame); }
        catch (Exception ex)
        {
            _logger.Warn($"Failed to write key '{paramKey}' at frame {frame}: {ex.Message}");
        }
    }

    public void SetKeysForRange(Dictionary<string, float> fromValues, Dictionary<string, float> toValues, int frameStart, int frameEnd)
    {
        try { _setKeysForRange(fromValues, toValues, frameStart, frameEnd); }
        catch (Exception ex)
        {
            _logger.Warn($"Failed to write key range {frameStart}-{frameEnd}: {ex.Message}");
        }
    }
}
