using System;
using System.Collections.Generic;
using System.Linq;

namespace ForgottenJobs.ExtensionCore;

public enum AddressKind { RipRelative, ImageRelative }
public sealed record RelocationSite(string Table, long InstructionRva, byte[] Original,
    int DisplacementOffset, int TargetByteOffset, AddressKind Kind, bool BaseOriginVerified);
public sealed record TableAddress(string Name, long OriginalRva, int OriginalLength, long NewAddress, int NewLength);
public sealed record MemoryPatch(long Address, byte[] Original, byte[] Replacement);

public static class RelocationPlanner
{
    // Does not allocate, write memory, change bounds, or approve an engine ID.
    public static MemoryPatch[] Build(long moduleBase, IEnumerable<RelocationSite> sites,
        IEnumerable<TableAddress> addresses)
    {
        var tables = addresses.ToDictionary(t => t.Name, StringComparer.Ordinal);
        var patches = new List<MemoryPatch>();
        foreach (var table in tables.Values)
            if (table.OriginalRva < 0 || table.OriginalLength <= 0 || table.NewLength < table.OriginalLength || table.NewAddress <= 0)
                throw new InvalidOperationException("Invalid source/destination table bounds.");
        foreach (var site in sites)
        {
            if (!tables.TryGetValue(site.Table, out var table)) throw new InvalidOperationException("Unknown table.");
            if (!site.BaseOriginVerified) throw new InvalidOperationException("Address base origin not verified.");
            if (site.InstructionRva < 0 || site.Original.Length < 5 || site.DisplacementOffset < 1 ||
                site.DisplacementOffset + 4 > site.Original.Length || site.TargetByteOffset < 0 || site.TargetByteOffset >= table.OriginalLength)
                throw new InvalidOperationException("Invalid relocation site.");
            long address = checked(moduleBase + site.InstructionRva);
            long oldDisplacement = BitConverter.ToInt32(site.Original, site.DisplacementOffset);
            long origin = site.Kind switch {
                AddressKind.RipRelative => checked(address + site.Original.Length),
                AddressKind.ImageRelative => moduleBase,
                _ => throw new InvalidOperationException("Unsupported address kind.")
            };
            long expected = checked(moduleBase + table.OriginalRva + site.TargetByteOffset);
            if (checked(origin + oldDisplacement) != expected) throw new InvalidOperationException("Decoded target disagrees with table evidence.");
            long newTarget = checked(table.NewAddress + site.TargetByteOffset);
            long displacement = checked(newTarget - origin);
            if (displacement < int.MinValue || displacement > int.MaxValue)
                throw new InvalidOperationException("Destination outside signed disp32 range: near allocation required.");
            byte[] replacement = (byte[])site.Original.Clone();
            BitConverter.GetBytes((int)displacement).CopyTo(replacement, site.DisplacementOffset);
            patches.Add(new(address, (byte[])site.Original.Clone(), replacement));
        }
        var ordered = patches.OrderBy(p => p.Address).ToArray();
        for (int i = 1; i < ordered.Length; i++)
            if (ordered[i].Address < checked(ordered[i - 1].Address + ordered[i - 1].Original.Length))
                throw new InvalidOperationException("Overlapping/duplicate instruction patches.");
        return ordered;
    }

    public static byte[] AppendTable(byte[] original, int entrySize, IReadOnlyList<byte[]> appended)
    {
        if (entrySize <= 0 || original.Length == 0 || original.Length % entrySize != 0)
            throw new InvalidOperationException("Incomplete original table.");
        if (appended.Any(row => row.Length != entrySize)) throw new InvalidOperationException("Invalid appended row size.");
        var result = new byte[checked(original.Length + checked(entrySize * appended.Count))];
        original.CopyTo(result, 0);
        for (int i = 0; i < appended.Count; i++) appended[i].CopyTo(result, original.Length + i * entrySize);
        if (!result.AsSpan(0, original.Length).SequenceEqual(original)) throw new InvalidOperationException("Vanilla prefix changed.");
        return result;
    }
}

public interface IPatchMemory
{
    byte[] Read(long address, int length);
    // Adapter must preserve protection and flush the instruction cache.
    void Write(long address, byte[] bytes);
}

public sealed class PatchTransaction
{
    private readonly IPatchMemory memory;
    private readonly MemoryPatch[] patches;
    private readonly List<MemoryPatch> attempted = new();
    public bool Active { get; private set; }
    public bool Faulted { get; private set; }
    public PatchTransaction(IPatchMemory memory, IEnumerable<MemoryPatch> patches)
    {
        this.memory = memory;
        this.patches = patches.Select(p => new MemoryPatch(p.Address, (byte[])p.Original.Clone(), (byte[])p.Replacement.Clone())).OrderBy(p => p.Address).ToArray();
        foreach (var patch in this.patches)
            if (patch.Address <= 0 || patch.Original.Length == 0 || patch.Original.Length != patch.Replacement.Length)
                throw new InvalidOperationException("Invalid memory patch.");
        for (int i = 1; i < this.patches.Length; i++)
            if (this.patches[i].Address < checked(this.patches[i - 1].Address + this.patches[i - 1].Original.Length))
                throw new InvalidOperationException("Overlapping memory patches.");
    }
    private void Expect(long address, byte[] expected)
    {
        if (!memory.Read(address, expected.Length).SequenceEqual(expected))
            throw new InvalidOperationException($"Memory drift at 0x{address:X}; refusing patch.");
    }
    public void Apply(bool dryRun = false)
    {
        if (Active || Faulted || attempted.Count != 0) throw new InvalidOperationException("Transaction cannot be reused in this state.");
        // Validate every site before the first write.
        foreach (var patch in patches) Expect(patch.Address, patch.Original);
        if (dryRun) return;
        try
        {
            foreach (var patch in patches)
            {
                Expect(patch.Address, patch.Original);
                attempted.Add(patch); // Include a write that fails after partial mutation.
                memory.Write(patch.Address, patch.Replacement);
                Expect(patch.Address, patch.Replacement);
            }
            Active = true;
        }
        catch (Exception applyFailure)
        {
            var failures = RestoreAttempted();
            if (failures.Count != 0) throw new AggregateException("Apply failed and rollback is incomplete: retain all relocated buffers.", new[] { applyFailure }.Concat(failures));
            throw;
        }
    }
    public void Rollback()
    {
        if (Faulted) throw new InvalidOperationException("Incomplete rollback: do not release buffers.");
        // Do not overwrite changes made by another mod after activation.
        foreach (var patch in attempted) Expect(patch.Address, patch.Replacement);
        var failures = RestoreAttempted();
        if (failures.Count != 0) throw new AggregateException("Rollback incomplete: retain all relocated buffers.", failures);
    }
    private List<Exception> RestoreAttempted()
    {
        var failures = new List<Exception>();
        foreach (var patch in attempted.AsEnumerable().Reverse())
            try { memory.Write(patch.Address, patch.Original); Expect(patch.Address, patch.Original); }
            catch (Exception error) { failures.Add(error); }
        Faulted = failures.Count != 0;
        Active = Faulted;
        if (!Faulted) attempted.Clear();
        return failures;
    }
}
