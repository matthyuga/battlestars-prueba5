using System;
using System.IO;
using Xunit;

namespace ExpressionLayerEditorSkeleton.Tests;

public sealed class JsonFilePresetRepositoryTests : IDisposable
{
    private readonly string _dir = Path.Combine(Path.GetTempPath(), "ele-tests-" + Guid.NewGuid().ToString("N"));

    [Fact]
    public void SaveLoadExistsDelete_Roundtrip_Works()
    {
        var repo = new JsonFilePresetRepository(_dir);
        var preset = new ExpressionPreset { Name = "angry_face" };
        preset.Values["eye_face.f00_def_cl"] = 0.5f;

        repo.Save(preset);

        Assert.True(repo.Exists("angry_face"));

        var loaded = repo.Load("angry_face");
        Assert.Equal("angry_face", loaded.Name);
        Assert.True(loaded.Values.ContainsKey("eye_face.f00_def_cl"));

        repo.Delete("angry_face");
        Assert.False(repo.Exists("angry_face"));
    }

    [Fact]
    public void Rename_ChangesName_AndHonorsOverwrite()
    {
        var repo = new JsonFilePresetRepository(_dir);
        repo.Save(new ExpressionPreset { Name = "base" });
        repo.Save(new ExpressionPreset { Name = "target" });

        Assert.Throws<IOException>(() => repo.Rename("base", "target", overwrite: false));

        repo.Rename("base", "target", overwrite: true);
        Assert.False(repo.Exists("base"));
        Assert.True(repo.Exists("target"));
    }

    public void Dispose()
    {
        if (Directory.Exists(_dir))
            Directory.Delete(_dir, recursive: true);
    }
}
