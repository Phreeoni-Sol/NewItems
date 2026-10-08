using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using Reloaded.Mod.Interfaces;
using Reloaded.Mod.Interfaces.Internal;

namespace ForgottenJobs.ReadOnlyProbe;

public sealed record TableEvidence(string Name, int Rva, int EntrySize, string[] OriginalRowHashes);
public sealed record ProbeManifest(string ExecutableSHA256, TableEvidence[] Tables);
public sealed record TableObservation(string Name, int ObservedRows, int[] DifferentRows);

public static class ProbeChecks
{
    public static void ValidateManifest(ProbeManifest manifest, string hash, int moduleSize)
    {
        if (!string.Equals(hash, manifest.ExecutableSHA256, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("Unrecognized executable: no memory read attempted.");
        if (manifest.Tables.Length == 0) throw new InvalidOperationException("Empty table manifest.");
        var names = new HashSet<string>(StringComparer.Ordinal);
        foreach (var table in manifest.Tables)
        {
            long end = (long)table.Rva + (long)table.EntrySize * table.OriginalRowHashes.Length;
            if (!names.Add(table.Name) || table.Rva < 0 || table.EntrySize <= 0 ||
                table.OriginalRowHashes.Length == 0 || end > moduleSize ||
                table.OriginalRowHashes.Any(h => h.Length != 64 || !h.All(Uri.IsHexDigit)))
                throw new InvalidOperationException("Invalid table bounds or row hashes.");
        }
        foreach (var a in manifest.Tables)
        foreach (var b in manifest.Tables)
            if (!ReferenceEquals(a, b) && a.Rva < b.Rva + (long)b.EntrySize * b.OriginalRowHashes.Length &&
                b.Rva < a.Rva + (long)a.EntrySize * a.OriginalRowHashes.Length)
                throw new InvalidOperationException("Overlapping observed table ranges.");
    }

    public static TableObservation Compare(TableEvidence table, byte[] memory)
    {
        if (memory.Length != checked(table.EntrySize * table.OriginalRowHashes.Length))
            throw new InvalidOperationException("Incomplete memory snapshot.");
        var differences = new List<int>();
        for (int row = 0; row < table.OriginalRowHashes.Length; row++)
        {
            var actual = Convert.ToHexString(SHA256.HashData(memory.AsSpan(row * table.EntrySize, table.EntrySize)));
            if (!actual.Equals(table.OriginalRowHashes[row], StringComparison.OrdinalIgnoreCase)) differences.Add(row);
        }
        return new(table.Name, table.OriginalRowHashes.Length, differences.ToArray());
    }
}

public sealed class Startup : IMod
{
    // Observation only: no hooks, allocations, pointer writes or save access.
    public void StartEx(IModLoaderV1 api, IModConfigV1 configuration)
    {
        var loader = (IModLoader)api;
        var logger = (ILogger)loader.GetLogger();
        try
        {
            using var source = typeof(Startup).Assembly.GetManifestResourceStream("probe-manifest.json")
                ?? throw new InvalidOperationException("Missing manifest.");
            var manifest = JsonSerializer.Deserialize<ProbeManifest>(source)
                ?? throw new InvalidOperationException("Unreadable manifest.");
            using var process = Process.GetCurrentProcess();
            var module = process.MainModule ?? throw new InvalidOperationException("Missing main module.");
            using var executable = File.OpenRead(module.FileName);
            string hash = Convert.ToHexString(SHA256.HashData(executable));
            ProbeChecks.ValidateManifest(manifest, hash, module.ModuleMemorySize);
            var observations = new List<TableObservation>();
            foreach (var table in manifest.Tables)
            {
                nint address = module.BaseAddress + table.Rva;
                var snapshot = new byte[checked(table.EntrySize * table.OriginalRowHashes.Length)];
                EnsureReadable(address, snapshot.Length);
                Marshal.Copy(address, snapshot, 0, snapshot.Length);
                observations.Add(ProbeChecks.Compare(table, snapshot));
            }
            // Launcher-managed configuration directory, never a game/save path.
            string directory = loader.GetModConfigDirectory(configuration.ModId);
            Directory.CreateDirectory(directory);
            string report = Path.Combine(directory, "read-only-probe.json");
            File.WriteAllText(report, JsonSerializer.Serialize(new {
                ExecutableSHA256 = hash, Mode = "Read-only startup snapshot",
                Tables = observations, AllocationApproved = false,
                Note = "Differences may be from other mods. Matching rows do not validate extension/menu/save behavior."
            }, new JsonSerializerOptions { WriteIndented = true }));
            logger.WriteLine($"[Forgotten Jobs diagnostic] {report}; no job added, no table modified.");
        }
        catch (Exception error)
        {
            logger.WriteLine($"[Forgotten Jobs diagnostic] stopped: {error.Message}; no patch applied.");
        }
    }

    private static void EnsureReadable(nint start, int length)
    {
        nuint cursor = (nuint)start;
        nuint end = checked(cursor + (nuint)length);
        while (cursor < end)
        {
            if (VirtualQuery((nint)cursor, out var region, (nuint)Marshal.SizeOf<MemoryBasicInformation>()) == 0)
                throw new InvalidOperationException("Memory range unavailable.");
            uint access = region.Protect & 0xff;
            if (region.State != 0x1000 || (region.Protect & 0x100) != 0 ||
                access is not (0x02 or 0x04 or 0x08 or 0x20 or 0x40 or 0x80))
                throw new InvalidOperationException("Memory range is not readable.");
            nuint next = checked((nuint)region.BaseAddress + region.RegionSize);
            if (next <= cursor) throw new InvalidOperationException("Invalid memory region.");
            cursor = next;
        }
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct MemoryBasicInformation
    {
        public nint BaseAddress, AllocationBase;
        public uint AllocationProtect;
        public ushort PartitionId;
        public nuint RegionSize;
        public uint State, Protect, Type;
    }
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern nuint VirtualQuery(nint address, out MemoryBasicInformation information, nuint length);
    public void Suspend() { }
    public void Resume() { }
    public void Unload() { }
    public bool CanUnload() => true;
    public bool CanSuspend() => false;
    public Action Disposing => () => { };
}
