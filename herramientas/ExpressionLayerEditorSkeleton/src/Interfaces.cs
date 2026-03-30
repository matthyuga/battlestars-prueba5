using System.Collections.Generic;

namespace ExpressionLayerEditorSkeleton;

public interface ILogger
{
    void Info(string message);
    void Warn(string message);
    void Error(string message);
}

public interface ICharacterRuntimeAdapter
{
    CharacterContext GetActiveCharacter();
    IReadOnlyCollection<BlendshapeParam> GetBlendshapeRegistry(CharacterContext context);
    ExpressionState ReadCurrentState(CharacterContext context);
    void ApplyState(CharacterContext context, ExpressionState state);
}

public interface IExpressionComposer
{
    ExpressionState Compose(ExpressionState baseState, ExpressionState layerState, float layerIntensity, float globalIntensity);
}

public interface IConstraintEngine
{
    ExpressionState ValidateAndFix(ExpressionState state, IEnumerable<BlendshapeConstraint> constraints);
    IReadOnlyList<string> GetWarnings();
}

public interface IPresetRepository
{
    void Save(ExpressionPreset preset);
    ExpressionPreset Load(string presetName);
    IReadOnlyCollection<string> ListPresetNames();
}

public interface ISnapshotService
{
    void SaveA(ExpressionState state);
    void SaveB(ExpressionState state);
    ExpressionState Interpolate(float t, bool smoothStep = false);
}

public interface ITimelineBridge
{
    bool IsAvailable { get; }
    int GetCurrentFrame();
    void SetKey(string paramKey, float value, int frame);
    void SetKeysForRange(Dictionary<string, float> fromValues, Dictionary<string, float> toValues, int frameStart, int frameEnd);
}
