using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace ForgottenJobs.ExtensionCore;

// Current-process adapter. Caller must establish a safe execution point before patching code.
// No thread suspension or game hook is implied by this API.
public sealed class WindowsPatchMemory : IPatchMemory
{
    public byte[] Read(long address, int length)
    {
        if (address <= 0 || length <= 0) throw new ArgumentOutOfRangeException();
        ValidateReadable(address, length);
        byte[] bytes = new byte[length];
        Marshal.Copy((nint)address, bytes, 0, length);
        return bytes;
    }
    public void Write(long address, byte[] bytes)
    {
        if (bytes.Length == 0) throw new ArgumentException("Empty write.");
        ValidateReadable(address, bytes.Length);
        var protections = new List<(long Address, nuint Length, uint Original)>();
        Exception? failure = null;
        try
        {
            long cursor = address, end = checked(address + bytes.Length);
            while (cursor < end)
            {
                var region = Query(cursor);
                long next = Math.Min(end, checked((long)region.BaseAddress + (long)region.RegionSize));
                // Changes occur at page granularity; query each page to preserve heterogeneous permissions.
                long pageEnd = checked((cursor / Environment.SystemPageSize + 1) * Environment.SystemPageSize);
                next = Math.Min(next, pageEnd);
                nuint length = (nuint)(next - cursor);
                if (!VirtualProtect((nint)cursor, length, 0x40, out uint original))
                    throw new InvalidOperationException("Unable to temporarily change code-page protection.");
                protections.Add((cursor, length, original));
                cursor = next;
            }
            Marshal.Copy(bytes, 0, (nint)address, bytes.Length);
            if (!FlushInstructionCache(GetCurrentProcess(), (nint)address, (nuint)bytes.Length))
                throw new InvalidOperationException("Instruction cache flush failed.");
        }
        catch (Exception error) { failure = error; }
        finally
        {
            for (int i = protections.Count - 1; i >= 0; i--)
            {
                var p = protections[i];
                if (!VirtualProtect((nint)p.Address, p.Length, p.Original, out _))
                {
                    var restore = new InvalidOperationException("Code-page protection restoration failed.");
                    failure = failure == null ? restore : new AggregateException(failure, restore);
                }
            }
        }
        if (failure != null) throw failure;
    }
    public uint ProtectionAt(long address) => Query(address).Protect;
    private static void ValidateReadable(long start, int length)
    {
        long end = checked(start + length), cursor = start;
        while (cursor < end)
        {
            var region = Query(cursor);
            uint access = region.Protect & 0xff;
            if (region.State != 0x1000 || (region.Protect & 0x100) != 0 ||
                access is not (0x02 or 0x04 or 0x08 or 0x20 or 0x40 or 0x80))
                throw new InvalidOperationException("Unreadable memory range.");
            long next = checked((long)region.BaseAddress + (long)region.RegionSize);
            if (next <= cursor) throw new InvalidOperationException("Invalid virtual memory region.");
            cursor = next;
        }
    }
    private static MemoryBasicInformation Query(long address)
    {
        if (VirtualQuery((nint)address, out var info, (nuint)Marshal.SizeOf<MemoryBasicInformation>()) == 0)
            throw new InvalidOperationException("VirtualQuery failed.");
        return info;
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
    [DllImport("kernel32.dll",SetLastError=true)] private static extern nuint VirtualQuery(nint address,out MemoryBasicInformation information,nuint length);
    [DllImport("kernel32.dll",SetLastError=true)] private static extern bool VirtualProtect(nint address,nuint length,uint protection,out uint previous);
    [DllImport("kernel32.dll",SetLastError=true)] private static extern bool FlushInstructionCache(nint process,nint address,nuint length);
    [DllImport("kernel32.dll")] private static extern nint GetCurrentProcess();
}

public sealed class NearTableBuffer : IDisposable
{
    public long Address { get; private set; }
    public int Length { get; }
    private bool retained;
    private NearTableBuffer(long address, int length) { Address = address; Length = length; }
    public static NearTableBuffer Allocate(long anchor, byte[] bytes)
    {
        if (anchor <= 0 || bytes.Length == 0) throw new ArgumentException("Invalid near allocation request.");
        const long granularity = 0x10000; // Windows allocation-granularity value checked below.
        GetSystemInfo(out var information);
        if (information.AllocationGranularity != granularity)
            throw new InvalidOperationException("Unexpected Windows allocation granularity.");
        long aligned = anchor / granularity * granularity;
        for (long distance = granularity; distance < 0x7fff0000; distance += granularity)
        {
            foreach (long sign in new long[] { 1, -1 })
            {
                long candidate = checked(aligned + sign * distance);
                if (candidate < granularity || candidate > long.MaxValue - bytes.Length) continue;
                nint allocated = VirtualAlloc((nint)candidate, (nuint)bytes.Length, 0x3000, 0x04);
                if (allocated == 0) continue;
                try
                {
                    Marshal.Copy(bytes, 0, allocated, bytes.Length);
                    return new NearTableBuffer((long)allocated, bytes.Length);
                }
                catch { VirtualFree(allocated, 0, 0x8000); throw; }
            }
        }
        throw new InvalidOperationException("No suitable near table allocation; no patch applied.");
    }
    // Keep storage alive if any consumer still points at it, including incomplete rollback.
    public void RetainForProcessLifetime() => retained = true;
    public void Dispose()
    {
        if (Address == 0 || retained) return;
        if (!VirtualFree((nint)Address, 0, 0x8000)) throw new InvalidOperationException("Table release failed.");
        Address = 0;
    }
    [StructLayout(LayoutKind.Sequential)]
    private struct SystemInfo
    {
        public uint ArchitectureAndReserved, PageSize;
        public nint MinimumAddress, MaximumAddress;
        public nuint ActiveProcessorMask;
        public uint NumberOfProcessors, ProcessorType, AllocationGranularity;
        public ushort ProcessorLevel, ProcessorRevision;
    }
    [DllImport("kernel32.dll")] private static extern void GetSystemInfo(out SystemInfo info);
    [DllImport("kernel32.dll",SetLastError=true)] private static extern nint VirtualAlloc(nint address,nuint size,uint allocationType,uint protection);
    [DllImport("kernel32.dll",SetLastError=true)] private static extern bool VirtualFree(nint address,nuint size,uint freeType);
}
