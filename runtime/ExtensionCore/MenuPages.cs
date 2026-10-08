using System;
using System.Collections.Generic;
using System.Linq;

namespace ForgottenJobs.ExtensionCore;

public sealed record JobMenuEntry(string Key, bool Vanilla);

// Pure projection; native list pointers, input hooks, display names and entry IDs are separate adapters.
public sealed class AdditiveMenuPages
{
    private readonly JobMenuEntry[] entries;
    public int Capacity { get; }
    public int PageCount => Math.Max(1,(entries.Length+Capacity-1)/Capacity);
    public AdditiveMenuPages(IEnumerable<JobMenuEntry> vanilla,IEnumerable<JobMenuEntry> additional,int capacity)
    {
        if(capacity<=0)throw new InvalidOperationException("Page capacity must come from a verified UI adapter.");
        var original=vanilla.ToArray();var extra=additional.ToArray();
        if(original.Any(e=>!e.Vanilla) || extra.Any(e=>e.Vanilla))throw new InvalidOperationException("Vanilla/custom menu ownership mismatch.");
        entries=original.Concat(extra).ToArray();Capacity=capacity;
        if(entries.Any(e=>string.IsNullOrWhiteSpace(e.Key)) || entries.Select(e=>e.Key).Distinct(StringComparer.Ordinal).Count()!=entries.Length)
            throw new InvalidOperationException("Empty or duplicate menu identity.");
    }
    public JobMenuEntry[] Page(int page)
    {
        if(page<0 || page>=PageCount)throw new InvalidOperationException("Page out of bounds.");
        return entries.Skip(checked(page*Capacity)).Take(Capacity).ToArray();
    }
    public JobMenuEntry Select(int page,int visibleIndex)
    {
        var visible=Page(page);
        if(visibleIndex<0 || visibleIndex>=visible.Length)throw new InvalidOperationException("Selection targets no job.");
        return visible[visibleIndex];
    }
}
