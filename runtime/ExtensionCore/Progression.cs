using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;

namespace ForgottenJobs.ExtensionCore;

public sealed record CustomJobState(string UnitKey, string JobKey, int TotalJp, int AvailableJp, string[] LearnedAbilities);
public sealed record SaveBinding(string LineageKey, string VanillaSaveSHA256);
public sealed record ProgressionSnapshot(int SchemaVersion, SaveBinding Binding, CustomJobState[] Jobs);
public sealed record UnlockRequirement(string PrerequisiteJob, int MinimumLevel, int MinimumJpSpent);
public sealed record AbilityDefinition(string JobKey,string AbilityKey,int JpCost);

// Own symbolic IDs and progression only. Native unit identity and save hooks are not inferred.
public sealed class AdditiveProgression
{
    private readonly HashSet<string> jobs;
    private readonly Dictionary<(string Job,string Ability),int> costs = new();
    private readonly Dictionary<(string Unit,string Job),CustomJobState> states = new();
    private readonly object sync = new();
    public AdditiveProgression(IEnumerable<string> customJobKeys,IEnumerable<AbilityDefinition>? abilityDefinitions=null)
    {
        jobs = new(StringComparer.Ordinal);
        foreach (var key in customJobKeys)
        {
            ValidateKey(key);
            if (!jobs.Add(key)) throw new InvalidOperationException("Duplicate custom job key.");
        }
        if (jobs.Count == 0) throw new InvalidOperationException("Empty custom job registry.");
        foreach(var ability in abilityDefinitions ?? Array.Empty<AbilityDefinition>())
        {
            ValidateKey(ability.AbilityKey);
            if(!jobs.Contains(ability.JobKey) || ability.JpCost<0 || !costs.TryAdd((ability.JobKey,ability.AbilityKey),ability.JpCost))
                throw new InvalidOperationException("Unknown job, invalid JP cost or duplicate ability definition.");
        }
    }
    private static void ValidateKey(string key)
    {
        if (string.IsNullOrWhiteSpace(key) || key.Length > 128 || key.Any(char.IsControl))
            throw new InvalidOperationException("Invalid stable identity key.");
    }
    private CustomJobState Get(string unit, string job)
    {
        ValidateKey(unit);
        if (!jobs.Contains(job)) throw new InvalidOperationException("Job is outside the custom registry: delegate vanilla to the game.");
        return states.TryGetValue((unit,job),out var value) ? value : new(unit,job,0,0,Array.Empty<string>());
    }
    public CustomJobState Read(string unit, string job)
    {
        lock(sync) { var state=Get(unit,job);return state with {LearnedAbilities=(string[])state.LearnedAbilities.Clone()}; }
    }
    public void Earn(string unit,string job,int amount)
    {
        if(amount<0) throw new InvalidOperationException("Negative JP grant.");
        lock(sync)
        {
            var state=Get(unit,job);
            states[(unit,job)]=state with {TotalJp=checked(state.TotalJp+amount),AvailableJp=checked(state.AvailableJp+amount)};
        }
    }
    public bool Learn(string unit,string job,string ability)
    {
        ValidateKey(ability);
        if(!costs.TryGetValue((job,ability),out int cost))throw new InvalidOperationException("Unknown custom ability or undefined JP cost.");
        lock(sync)
        {
            var state=Get(unit,job);
            if(state.LearnedAbilities.Contains(ability,StringComparer.Ordinal))return false;
            if(state.AvailableJp<cost)throw new InvalidOperationException("Insufficient custom-job JP.");
            states[(unit,job)]=state with {AvailableJp=state.AvailableJp-cost,LearnedAbilities=state.LearnedAbilities.Append(ability).OrderBy(k=>k,StringComparer.Ordinal).ToArray()};
            return true;
        }
    }
    public int Level(string unit,string job,int[] cumulativeThresholds)
    {
        if(cumulativeThresholds.Length==0 || cumulativeThresholds[0]!=0)throw new InvalidOperationException("Level thresholds must start at zero.");
        for(int i=1;i<cumulativeThresholds.Length;i++)if(cumulativeThresholds[i]<=cumulativeThresholds[i-1])throw new InvalidOperationException("Level thresholds must increase.");
        int total=Read(unit,job).TotalJp,level=1;
        for(int i=1;i<cumulativeThresholds.Length;i++)if(total>=cumulativeThresholds[i])level=i+1;else break;
        return level;
    }
    // Inputs must come from verified vanilla accessors. Does not inspect or modify a vanilla record.
    public static bool IsUnlocked(UnlockRequirement requirement,int verifiedLevel,int verifiedJpSpent)
    {
        ValidateKey(requirement.PrerequisiteJob);
        if(verifiedLevel<0 || verifiedJpSpent<0 || requirement.MinimumLevel<0 || requirement.MinimumJpSpent<0)throw new InvalidOperationException("Invalid prerequisite evidence.");
        return verifiedLevel>=requirement.MinimumLevel && verifiedJpSpent>=requirement.MinimumJpSpent;
    }
    public ProgressionSnapshot Capture(SaveBinding binding)
    {
        ValidateBinding(binding);
        lock(sync) {return new(1,binding,states.Values.OrderBy(v=>v.UnitKey,StringComparer.Ordinal).ThenBy(v=>v.JobKey,StringComparer.Ordinal).Select(v=>v with {LearnedAbilities=(string[])v.LearnedAbilities.Clone()}).ToArray());}
    }
    public void Restore(ProgressionSnapshot snapshot,SaveBinding expected)
    {
        ValidateBinding(expected);
        if(snapshot.SchemaVersion!=1 || snapshot.Binding!=expected || snapshot.Jobs==null)throw new InvalidOperationException("Progression schema/save binding mismatch.");
        var restored=new Dictionary<(string Unit,string Job),CustomJobState>();
        foreach(var state in snapshot.Jobs)
        {
            ValidateKey(state.UnitKey);
            if(!jobs.Contains(state.JobKey) || state.TotalJp<0 || state.AvailableJp<0 || state.AvailableJp>state.TotalJp || state.LearnedAbilities==null)
                throw new InvalidOperationException("Invalid custom progression record.");
            foreach(var ability in state.LearnedAbilities) {
                ValidateKey(ability);
                if(!costs.ContainsKey((state.JobKey,ability)))throw new InvalidOperationException("Unknown learned ability: explicit migration required.");
            }
            if(state.LearnedAbilities.Distinct(StringComparer.Ordinal).Count()!=state.LearnedAbilities.Length || !restored.TryAdd((state.UnitKey,state.JobKey),state with {LearnedAbilities=(string[])state.LearnedAbilities.Clone()}))
                throw new InvalidOperationException("Duplicate unit/job or learned ability.");
        }
        lock(sync) {states.Clear();foreach(var pair in restored)states.Add(pair.Key,pair.Value);}
    }
    public static void ValidateBinding(SaveBinding binding)
    {
        ValidateKey(binding.LineageKey);
        if(binding.VanillaSaveSHA256.Length!=64 || !binding.VanillaSaveSHA256.All(Uri.IsHexDigit))
            throw new InvalidOperationException("Verified vanilla-save SHA-256 required.");
    }
}

public static class ProgressionSidecar
{
    // The caller passes a separate mod-data root and binding from a completed save event.
    // No save path is accepted, and no game file is opened by this component.
    public static string PathFor(string root,SaveBinding binding)
    {
        AdditiveProgression.ValidateBinding(binding);
        string lineage=Convert.ToHexString(SHA256.HashData(System.Text.Encoding.UTF8.GetBytes(binding.LineageKey)));
        return Path.Combine(Path.GetFullPath(root),lineage,binding.VanillaSaveSHA256.ToUpperInvariant()+".forgotten-jobs.json");
    }
    public static void Write(string root,ProgressionSnapshot snapshot)
    {
        string path=PathFor(root,snapshot.Binding);
        string parent=Path.GetDirectoryName(path)!;
        Directory.CreateDirectory(parent);
        string temp=Path.Combine(parent,Guid.NewGuid().ToString("N")+".tmp");
        try
        {
            byte[] bytes=JsonSerializer.SerializeToUtf8Bytes(snapshot);
            using(var file=new FileStream(temp,FileMode.CreateNew,FileAccess.Write,FileShare.None)) {file.Write(bytes);file.Flush(flushToDisk:true);}
            File.Move(temp,path,overwrite:true); // Same-volume atomic publication; bind to the exact vanilla save.
        }
        finally {if(File.Exists(temp))File.Delete(temp);}
    }
    public static ProgressionSnapshot Read(string root,SaveBinding expected)
    {
        string path=PathFor(root,expected);
        var snapshot=JsonSerializer.Deserialize<ProgressionSnapshot>(File.ReadAllBytes(path)) ?? throw new InvalidOperationException("Missing progression snapshot.");
        if(snapshot.SchemaVersion!=1 || snapshot.Binding!=expected)throw new InvalidOperationException("Sidecar schema/save binding mismatch.");
        return snapshot;
    }
}
