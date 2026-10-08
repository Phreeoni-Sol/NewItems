using System;
using System.Collections.Generic;
using System.Linq;

namespace ForgottenJobs.ExtensionCore;

// The local native accessor has 16 active + 6 RSM slots and ninth-bit ability IDs.
// Only the adapter may supply an ID after all native/NXD/mod collisions have been checked.
public sealed class AdditiveCommandRouter
{
    private readonly HashSet<int> reserved;
    private readonly Dictionary<int,ushort[]> commands = new();
    public AdditiveCommandRouter(IEnumerable<int> reservedNativeAndNxdIds) => reserved = new(reservedNativeAndNxdIds);
    public void RegisterVerified(int commandId,IReadOnlyList<ushort> active,IReadOnlyList<ushort> rsm)
    {
        if(commandId<0 || commandId>byte.MaxValue)throw new InvalidOperationException("Command reference does not fit the verified JOB_DATA byte field.");
        if(reserved.Contains(commandId) || commands.ContainsKey(commandId))throw new InvalidOperationException("Native/NXD/custom command collision.");
        if(active.Count>16 || rsm.Count>6 || active.Concat(rsm).Any(id=>id>511))throw new InvalidOperationException("Command entry exceeds the verified local slot/ID encoding.");
        var slots=new ushort[22];for(int i=0;i<active.Count;i++)slots[i]=active[i];for(int i=0;i<rsm.Count;i++)slots[16+i]=rsm[i];
        commands.Add(commandId,slots);
    }
    public ushort Read(int commandId,int slot,Func<int,int,ushort> originalAccessor)
    {
        if(!commands.TryGetValue(commandId,out var slots))return originalAccessor(commandId,slot);
        return slot>=0 && slot<slots.Length ? slots[slot] : (ushort)0;
    }
}
