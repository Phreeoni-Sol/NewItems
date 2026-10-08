using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Runtime.InteropServices;
using ForgottenJobs.ExtensionCore;

internal static class Program
{
    private static int passed;
    static void Check(bool value, string name) { if (!value) throw new Exception(name); passed++; Console.WriteLine("PASS " + name); }
    static void Reject(Action action, string name) { try { action(); } catch (InvalidOperationException) { Check(true, name); return; } throw new Exception("Unexpected acceptance: " + name); }
    static byte[] Rip(long site,long target) { var bytes=new byte[]{0x48,0x8d,0x15,0,0,0,0};BitConverter.GetBytes(checked((int)(target-site-7))).CopyTo(bytes,3);return bytes; }
    public static void Main(string[] args)
    {
        const long module=0x140000000, originalRva=0x1000, siteRva=0x100;
        var original = Rip(module+siteRva,module+originalRva+3);
        var site = new RelocationSite("Job",siteRva,original,3,3,AddressKind.RipRelative,true);
        var address=new TableAddress("Job",originalRva,98,module+0x8000,147);
        var plan=RelocationPlanner.Build(module,new[]{site},new[]{address});
        Check(module+siteRva+7+BitConverter.ToInt32(plan[0].Replacement,3)==address.NewAddress+3,"RIP target relocated with field offset preserved");
        Check(original.SequenceEqual(Rip(module+siteRva,module+originalRva+3)),"planner does not mutate input instruction");
        Reject(()=>RelocationPlanner.Build(module,new[]{site with {BaseOriginVerified=false}},new[]{address}),"unknown address origin rejected");
        Reject(()=>RelocationPlanner.Build(module,new[]{site},new[]{address with {NewAddress=module+0x90000000}}),"out-of-range signed disp32 rejected");
        Reject(()=>RelocationPlanner.Build(module,new[]{site with {TargetByteOffset=98}},new[]{address}),"source table overrun rejected");
        Reject(()=>RelocationPlanner.Build(module,new[]{site,site},new[]{address}),"duplicate relocation rejected");
        var image=site with {Kind=AddressKind.ImageRelative,Original=new byte[]{0x8b,0x84,0x8a,3,0x10,0,0}};
        var imagePlan=RelocationPlanner.Build(module,new[]{image},new[]{address});
        Check(BitConverter.ToInt32(imagePlan[0].Replacement,3)==0x8003,"image-relative target relocated separately from RIP math");
        byte[] vanilla={1,2,3,4};var expanded=RelocationPlanner.AppendTable(vanilla,2,new[]{new byte[]{5,6}});
        Check(expanded.SequenceEqual(new byte[]{1,2,3,4,5,6}) && vanilla.SequenceEqual(new byte[]{1,2,3,4}),"append preserves vanilla bytes and source ownership");
        Reject(()=>RelocationPlanner.AppendTable(vanilla,3,Array.Empty<byte[]>()),"incomplete vanilla row rejected");
        Reject(()=>RelocationPlanner.AppendTable(vanilla,2,new[]{new byte[]{7}}),"appended row size rejected");
        var patches=new[]{new MemoryPatch(100,new byte[]{1,2},new byte[]{3,4}),new MemoryPatch(200,new byte[]{5,6},new byte[]{7,8})};
        var memory=new FakeMemory(patches);var transaction=new PatchTransaction(memory,patches);
        transaction.Apply(dryRun:true);Check(memory.Writes==0,"dry-run verifies all sites with zero writes");
        memory.Data[200][0]=99;
        Reject(()=>transaction.Apply(),"foreign-mod byte drift rejected before first write");Check(memory.Writes==0,"preflight failure does not partially patch earlier sites");
        memory=new FakeMemory(patches);transaction=new PatchTransaction(memory,patches);transaction.Apply();
        Check(transaction.Active && memory.Data[100].SequenceEqual(patches[0].Replacement),"transaction commits all patches");
        transaction.Rollback();Check(!transaction.Active && memory.Data[100].SequenceEqual(patches[0].Original) && memory.Data[200].SequenceEqual(patches[1].Original),"rollback restores every instruction");
        memory=new FakeMemory(patches){FailWriteNumber=2};transaction=new PatchTransaction(memory,patches);
        Reject(()=>transaction.Apply(),"partial failing write is rolled back");
        Check(!transaction.Active && !transaction.Faulted && memory.Data[100].SequenceEqual(patches[0].Original) && memory.Data[200].SequenceEqual(patches[1].Original),"rollback includes partially written current site");
        memory=new FakeMemory(patches){FailWriteNumber=2,FailRollback=true};transaction=new PatchTransaction(memory,patches);
        bool aggregate=false;try{transaction.Apply();}catch(AggregateException){aggregate=true;}
        Check(aggregate && transaction.Faulted && transaction.Active,"incomplete rollback marks faulted state and retains ownership requirement");
        Reject(()=>transaction.Apply(),"faulted transaction cannot be reused");
        memory=new FakeMemory(patches);transaction=new PatchTransaction(memory,patches);transaction.Apply();memory.Data[100][0]=9;
        Reject(()=>transaction.Rollback(),"rollback refuses to overwrite a later foreign-mod change");
        Check(transaction.Active,"buffers remain owned when rollback preflight fails");
        CommandFixture();
        MenuFixture();
        ProgressionFixture(args[0]);
        NativeLookupFixture();
        Console.WriteLine($"{passed} checks passed. Native fixture only; game not accessed or patched.");
    }

    private static void CommandFixture()
    {
        var router=new AdditiveCommandRouter(Enumerable.Range(0,227));
        // Internal fixture registration only: no native table or engine ID is allocated.
        router.RegisterVerified(227,new ushort[]{138,511},new ushort[]{447,466,486});
        int delegated=0;ushort Original(int command,int slot){delegated++;return (ushort)((command+slot)%512);}
        bool preserved=true;
        for(int command=0;command<227;command++)for(int slot=0;slot<22;slot++)
            if(router.Read(command,slot,Original)!=(ushort)((command+slot)%512))preserved=false;
        Check(preserved && delegated==227*22,"router delegates all vanilla/monster/WotL command fixtures unchanged");
        Check(router.Read(227,0,Original)==138 && router.Read(227,1,Original)==511 && router.Read(227,16,Original)==447 && router.Read(227,18,Original)==486,"custom command resolves active and RSM slots separately");
        Check(router.Read(227,-1,Original)==0 && router.Read(227,22,Original)==0,"custom command rejects out-of-range slots without vanilla fallback");
        Reject(()=>router.RegisterVerified(7,Array.Empty<ushort>(),Array.Empty<ushort>()),"vanilla command cannot be repurposed");
        Reject(()=>router.RegisterVerified(227,Array.Empty<ushort>(),Array.Empty<ushort>()),"duplicate custom command rejected");
        Reject(()=>router.RegisterVerified(228,new ushort[]{512},Array.Empty<ushort>()),"unsupported local ability ID encoding rejected");
    }

    private static void MenuFixture()
    {
        var vanilla=Enumerable.Range(0,21).Select(i=>new JobMenuEntry("vanilla-fixture-"+i,true)).ToArray();
        var custom=new[]{new JobMenuEntry("blade_breaker",false)};
        var menu=new AdditiveMenuPages(vanilla,custom,19);
        Check(menu.PageCount==2 && menu.Page(0).SequenceEqual(vanilla.Take(19)),"first menu page preserves vanilla job order");
        Check(menu.Page(1).SequenceEqual(vanilla.Skip(19).Concat(custom)),"additional page preserves remaining vanilla jobs before additions");
        Check(menu.Select(1,2).Key=="blade_breaker" && vanilla.Length==21,"menu selection identifies custom entry without changing source list");
        Reject(()=>menu.Select(1,3),"empty menu slot cannot select a job");
        Reject(()=>menu.Page(2),"page beyond menu bounds rejected");
        Reject(()=>new AdditiveMenuPages(vanilla,new[]{new JobMenuEntry(vanilla[0].Key,false)},19),"custom menu identity cannot collide with vanilla");
    }

    private static void ProgressionFixture(string scratch)
    {
        var abilities=new[]{new AbilityDefinition("blade_breaker","fixture-active",200),new AbilityDefinition("blade_breaker","fixture-other",900)};
        var progress=new AdditiveProgression(new[]{"blade_breaker"},abilities);
        var binding=new SaveBinding("fixture-save-lineage",new string('A',64));
        var requirement=new UnlockRequirement("knight",3,400);
        Check(AdditiveProgression.IsUnlocked(requirement,3,400) && !AdditiveProgression.IsUnlocked(requirement,2,400) && !AdditiveProgression.IsUnlocked(requirement,3,399),"Brise-Lame prerequisite checks both Knight level and invested JP");
        Reject(()=>progress.Earn("fixture-unit-a","knight",100),"vanilla job is outside custom progression registry");
        progress.Earn("fixture-unit-a","blade_breaker",800);
        Check(progress.Learn("fixture-unit-a","blade_breaker","fixture-active"),"custom ability learning spends only configured custom JP");
        Check(!progress.Learn("fixture-unit-a","blade_breaker","fixture-active") && progress.Read("fixture-unit-a","blade_breaker").AvailableJp==600,"repeat learning never spends JP twice");
        Reject(()=>progress.Learn("fixture-unit-a","blade_breaker","fixture-other"),"insufficient JP leaves learned abilities unchanged");
        Reject(()=>progress.Learn("fixture-unit-a","blade_breaker","undefined-ability"),"unknown ability/JP cost rejected");
        Check(progress.Read("fixture-unit-a","blade_breaker").TotalJp==800 && progress.Level("fixture-unit-a","blade_breaker",new[]{0,100,200,400,700,1100,1600,2200,3000})==5,"job level uses earned JP independently of remaining balance");
        var copy=progress.Read("fixture-unit-a","blade_breaker");copy.LearnedAbilities[0]="bad";
        Check(progress.Read("fixture-unit-a","blade_breaker").LearnedAbilities[0]=="fixture-active","reading state cannot mutate learned-ability storage");
        progress.Earn("fixture-unit-b","blade_breaker",50);
        Check(progress.Read("fixture-unit-a","blade_breaker").TotalJp==800 && progress.Read("fixture-unit-b","blade_breaker").TotalJp==50,"unit progression remains independent");
        ProgressionSidecar.Write(scratch,progress.Capture(binding));
        var restored=new AdditiveProgression(new[]{"blade_breaker"},abilities);
        restored.Restore(ProgressionSidecar.Read(scratch,binding),binding);
        Check(restored.Read("fixture-unit-a","blade_breaker").AvailableJp==600 && restored.Read("fixture-unit-a","blade_breaker").LearnedAbilities.SequenceEqual(new[]{"fixture-active"}),"custom JP and learned abilities survive sidecar round-trip");
        var snapshot=progress.Capture(binding);
        Reject(()=>restored.Restore(snapshot,binding with {VanillaSaveSHA256=new string('B',64)}),"progression from another vanilla-save fingerprint rejected");
        Reject(()=>restored.Restore(snapshot with {SchemaVersion=2},binding),"unknown progression schema rejected");
        var corrupt=snapshot with {Jobs=snapshot.Jobs.Concat(new[]{snapshot.Jobs[0]}).ToArray()};
        Reject(()=>restored.Restore(corrupt,binding),"duplicate unit/job identity rejected before committing state");
        Check(restored.Read("fixture-unit-a","blade_breaker").AvailableJp==600,"failed restore preserves previously loaded progress");
        Check(!ProgressionSidecar.PathFor(scratch,binding).Contains(binding.LineageKey),"sidecar paths use hashed lineage identity");
    }

    private sealed class FakeMemory : IPatchMemory
    {
        public Dictionary<long,byte[]> Data=new();public int Writes,FailWriteNumber;public bool FailRollback;
        public FakeMemory(IEnumerable<MemoryPatch> patches){foreach(var p in patches)Data.Add(p.Address,(byte[])p.Original.Clone());}
        public byte[] Read(long address,int length)=>(byte[])Data[address].Clone();
        public void Write(long address,byte[] bytes)
        {
            Writes++;
            if(Writes==FailWriteNumber){Data[address][0]=bytes[0];throw new InvalidOperationException("Injected partial write failure.");}
            if(FailRollback && Writes>FailWriteNumber)throw new InvalidOperationException("Injected restoration failure.");
            Data[address]=(byte[])bytes.Clone();
        }
    }
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int Lookup(int index);
    [DllImport("kernel32.dll",SetLastError=true)] private static extern nint VirtualAlloc(nint address,nuint size,uint type,uint protection);
    [DllImport("kernel32.dll",SetLastError=true)] private static extern bool VirtualFree(nint address,nuint size,uint type);
    [DllImport("kernel32.dll",SetLastError=true)] private static extern bool VirtualProtect(nint address,nuint length,uint protection,out uint previous);
    private static void NativeLookupFixture()
    {
        if(!OperatingSystem.IsWindows() || !Environment.Is64BitProcess)throw new InvalidOperationException("Windows x64 fixture required.");
        nint page=VirtualAlloc(0,4096,0x3000,0x04);if(page==0)throw new Exception("Fixture allocation failed");
        NearTableBuffer? buffer=null;PatchTransaction? transaction=null;
        try
        {
            // LEA RDX,[RIP+table]; MOV EAX,[RDX+RCX*4]; RET. Only owned fixture memory.
            long code=(long)page;var instruction=Rip(code,code+256);
            var function=instruction.Concat(new byte[]{0x8b,0x04,0x8a,0xc3}).ToArray();
            Marshal.Copy(function,0,page,function.Length);
            byte[] original=BitConverter.GetBytes(123).Concat(BitConverter.GetBytes(456)).ToArray();
            Marshal.Copy(original,0,page+256,original.Length);
            if(!VirtualProtect(page,4096,0x20,out _))throw new Exception("Fixture protection failed");
            var lookup=Marshal.GetDelegateForFunctionPointer<Lookup>(page);
            Check(lookup(0)==123 && lookup(1)==456,"native lookup baseline reads vanilla fixture entries");
            byte[] expanded=RelocationPlanner.AppendTable(original,4,new[]{BitConverter.GetBytes(789)});
            buffer=NearTableBuffer.Allocate(code,expanded);
            var memory=new WindowsPatchMemory();
            var site=new RelocationSite("Fixture",0,instruction,3,0,AddressKind.RipRelative,true);
            var patches=RelocationPlanner.Build(code,new[]{site},new[]{new TableAddress("Fixture",256,8,buffer.Address,12)});
            transaction=new PatchTransaction(memory,patches);transaction.Apply();
            Check(lookup(0)==123 && lookup(1)==456 && lookup(2)==789,"executed native consumer sees added row while vanilla values stay identical");
            Check(memory.Read(code+256,8).SequenceEqual(original),"original native table is never overwritten");
            Check(memory.ProtectionAt(code)==0x20,"code-page execute/read protection restored after patch");
            transaction.Rollback();
            Check(lookup(0)==123 && lookup(1)==456 && memory.Read(code,7).SequenceEqual(instruction),"native rollback restores original pointer and lookup");
            Check(memory.ProtectionAt(code)==0x20,"code-page protection restored after rollback");
        }
        finally
        {
            if(transaction?.Active==true){buffer?.RetainForProcessLifetime();}
            buffer?.Dispose();
            if(transaction?.Active!=true && !VirtualFree(page,0,0x8000))throw new Exception("Fixture release failed");
        }
    }
}
