using System;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Reflection.PortableExecutable;
using System.Security.Cryptography;
using ForgottenJobs.ExtensionCore;

internal static class Program
{
    const string Expected="937233F7FE76182A665C487C8802F5CEC6662DDD09967E87CD09FB146FC6B5D5";
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate ushort ReadCommand(int command,int slot);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] delegate int JobSlot(ushort job);
    [DllImport("kernel32.dll",SetLastError=true)] static extern nint VirtualAlloc(nint address,nuint size,uint type,uint protection);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool VirtualFree(nint address,nuint size,uint type);
    [DllImport("kernel32.dll",SetLastError=true)] static extern bool VirtualProtect(nint address,nuint length,uint protection,out uint previous);
    static void Assert(bool value,string text){if(!value)throw new Exception(text);Console.WriteLine("PASS "+text);}
    static int FileOffset(PEHeaders headers,int rva)
    {
        var sections=headers.SectionHeaders.Where(s=>rva>=s.VirtualAddress && rva<s.VirtualAddress+s.SizeOfRawData).ToArray();
        if(sections.Length!=1)throw new Exception("RVA not file-backed");
        return rva-sections[0].VirtualAddress+sections[0].PointerToRawData;
    }
    public static void Main(string[] args)
    {
        byte[] exe=File.ReadAllBytes(args[0]);Assert(Convert.ToHexString(SHA256.HashData(exe))==Expected,"exact audited executable hash checked before copying leaf accessors");
        using var reader=new PEReader(new MemoryStream(exe));var headers=reader.PEHeaders;
        // These exact ranges were traversed in consumer-map.json, including every direct branch.
        byte[] commandCode=exe.AsSpan(FileOffset(headers,0x275860),0x11e).ToArray();
        byte[] slotCode=exe.AsSpan(FileOffset(headers,0x2b8f18),0x33).ToArray();
        const int firstTable=0x67e210,lastByte=0x67f5b0;
        byte[] tables=exe.AsSpan(FileOffset(headers,firstTable),lastByte-firstTable).ToArray();
        nint code=VirtualAlloc(0,4096,0x3000,0x04);if(code==0)throw new Exception("Fixture code allocation failed");
        NearTableBuffer? data=null;
        try
        {
            data=NearTableBuffer.Allocate((long)code,tables);
            long syntheticImageBase=data.Address-firstTable;
            foreach(int local in new[]{0x1b,0x7d,0xd3})
            {
                // Original LEA R10,[RIP=>image base]; no other RIP targets in this leaf getter.
                if(commandCode[local]!=0x4c || commandCode[local+1]!=0x8d || commandCode[local+2]!=0x15)
                    throw new Exception("Native getter LEA shape changed");
                long originalTarget=(long)headers.PEHeader!.ImageBase+0x275860+local+7+BitConverter.ToInt32(commandCode,local+3);
                if(originalTarget!=(long)headers.PEHeader.ImageBase)throw new Exception("Native getter base target changed");
                BitConverter.GetBytes(checked((int)(syntheticImageBase-((long)code+local+7)))).CopyTo(commandCode,local+3);
            }
            Marshal.Copy(commandCode,0,code,commandCode.Length);
            Marshal.Copy(slotCode,0,code+512,slotCode.Length);
            var original=Marshal.GetDelegateForFunctionPointer<ReadCommand>(code);
            var router=new AdditiveCommandRouter(Enumerable.Range(0,227));
            router.RegisterVerified(227,new ushort[]{138,139},new ushort[]{447,466,486});
            ReadCommand callback=(command,slot)=>router.Read(command,slot,(id,index)=>original(id,index));
            nint callbackPointer=Marshal.GetFunctionPointerForDelegate(callback);
            // Native tail-jump ensures an actual ABI crossing into the managed router.
            byte[] bridge=new byte[]{0x48,0xb8}.Concat(BitConverter.GetBytes((long)callbackPointer)).Concat(new byte[]{0xff,0xe0}).ToArray();
            Marshal.Copy(bridge,0,code+768,bridge.Length);
            if(!VirtualProtect(code,4096,0x20,out _))throw new Exception("Fixture RX protection failed");
            var throughRouter=Marshal.GetDelegateForFunctionPointer<ReadCommand>(code+768);
            int compared=0;
            for(int command=0;command<256;command++)for(int slot=0;slot<22;slot++)
            {
                ushort expected=DecodeExpected(tables,command,slot);
                if(original(command,slot)!=expected)throw new Exception($"Native command decoding mismatch: {command}/{slot}");
                if(command!=227 && throughRouter(command,slot)!=expected)throw new Exception($"Vanilla forwarding mismatch: {command}/{slot}");
                compared++;
            }
            Assert(compared==5632,"copied native command getter matches independent decoder on 5632 command/slot pairs");
            Assert(throughRouter(227,0)==138 && throughRouter(227,1)==139 && throughRouter(227,16)==447 && throughRouter(227,18)==486,"native caller reaches custom command through managed router while vanilla routes remain intact");
            var slotMapper=Marshal.GetDelegateForFunctionPointer<JobSlot>(code+512);
            for(ushort job=0;job<256;job++)
            {
                int expected=job>=0x4a && job<=0x5d ? job-0x4a : job==0xa0 ? 20 : job==0xa1 ? 21 : 0;
                if(slotMapper(job)!=expected)throw new Exception("Job-slot mapper mismatch");
            }
            Assert(slotMapper(174)==0,"copied native slot mapper aliases candidate 174 to slot zero; vanilla slot reuse is forbidden");
            Assert(new WindowsPatchMemory().Read(data.Address,tables.Length).SequenceEqual(tables),"all copied native command/monster/WotL table bytes preserved");
            GC.KeepAlive(callback);
            Console.WriteLine("Native leaf routines executed only in owned fixture memory. No game process, file patch, engine ID or user save modified.");
        }
        finally {data?.Dispose();if(!VirtualFree(code,0,0x8000))throw new Exception("Fixture release failed");}
    }
    static ushort DecodeExpected(byte[] tables,int command,int slot)
    {
        int offset;
        if(command<176)offset=command*25;
        else if(command<224){if(slot>3)return 0;offset=0x67f4c0-0x67e210+(command-176)*5;return (ushort)(tables[offset+1+slot]+(((tables[offset]<<(slot+1))&256)!=0 ? 256 : 0));}
        else if(command<227)offset=0x67f340-0x67e210+(command-224)*25;
        else return 0;
        return (ushort)(tables[offset+3+slot]+(((tables[offset+slot/8]<<((slot%8)+1))&256)!=0 ? 256 : 0));
    }
}
