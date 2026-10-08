using System;
using System.Collections.Generic;
using Iced.Intel;

public sealed class DecodedConsumerInstruction {
    public ulong Address {get;set;}
    public int Length {get;set;}
    public string Mnemonic {get;set;}
    public string Operands {get;set;}
    public string Hex {get;set;}
    public ulong RipTarget {get;set;}
    public int DisplacementOffset {get;set;}
    public int DisplacementSize {get;set;}
    public string FlowControl {get;set;}
    public ulong BranchTarget {get;set;}
    public ulong MemoryDisplacement {get;set;}
    public string MemoryBase {get;set;}
    public string MemoryIndex {get;set;}
}
public static class ConsumerDecoder {
    public static DecodedConsumerInstruction[] DecodeReachable(byte[] bytes,ulong address) {
        var pending=new Queue<int>();pending.Enqueue(0);
        var visited=new Dictionary<ulong,DecodedConsumerInstruction>();
        while(pending.Count!=0) {
            int start=pending.Dequeue();
            var block=new byte[bytes.Length-start];Array.Copy(bytes,start,block,0,block.Length);
            var decoder=Decoder.Create(64,new ByteArrayCodeReader(block));decoder.IP=address+(ulong)start;
            while(decoder.IP<address+(ulong)bytes.Length) {
                if(visited.ContainsKey(decoder.IP)) break;
                var i=decoder.Decode();
                if(i.Code==Code.INVALID || i.Length==0)throw new ArgumentException("Invalid reachable instruction.");
                var raw=new byte[i.Length];Array.Copy(bytes,checked((int)(i.IP-address)),raw,0,raw.Length);
                visited.Add(i.IP,Decode(raw,i.IP)[0]);
                if(i.Mnemonic==Mnemonic.Ret)break;
                var kind=i.Op0Kind;
                if((kind==OpKind.NearBranch16 || kind==OpKind.NearBranch32 || kind==OpKind.NearBranch64) && i.Mnemonic!=Mnemonic.Call) {
                    ulong target=i.NearBranchTarget;
                    if(target<address || target>=address+(ulong)bytes.Length)throw new ArgumentException("Branch exits the preview window: function coverage unknown.");
                    pending.Enqueue(checked((int)(target-address)));
                    if(i.Mnemonic==Mnemonic.Jmp)break;
                }
            }
        }
        var result=new List<DecodedConsumerInstruction>(visited.Values);result.Sort((a,b)=>a.Address.CompareTo(b.Address));
        return result.ToArray();
    }
    public static ulong[] ImageRelativeSites(byte[] code,ulong address,ulong rva,ulong length) {
        var decoder=Decoder.Create(64,new ByteArrayCodeReader(code));decoder.IP=address;
        var sites=new List<ulong>();
        while(decoder.IP<address+(ulong)code.Length) {
            var i=decoder.Decode();
            if(i.Code==Code.INVALID || i.IsIPRelativeMemoryOperand) continue;
            bool memory=false;for(int op=0;op<i.OpCount;op++) if(i.GetOpKind(op)==OpKind.Memory) memory=true;
            if(memory && i.MemoryDisplacement64>=rva && i.MemoryDisplacement64<rva+length) sites.Add(i.IP);
        }
        return sites.ToArray();
    }
    public static DecodedConsumerInstruction[] Decode(byte[] bytes,ulong address,bool stopAtFirstReturn=false) {
        var decoder=Decoder.Create(64,new ByteArrayCodeReader(bytes));
        decoder.IP=address;
        var result=new List<DecodedConsumerInstruction>();
        while(decoder.IP<address+(ulong)bytes.Length) {
            var i=decoder.Decode();
            int offset=checked((int)(i.IP-address));
            if(i.Code==Code.INVALID || i.Length==0 || offset+i.Length>bytes.Length) throw new ArgumentException("Invalid/truncated instruction in function.");
            int displacementOffset=0;
            if(i.IsIPRelativeMemoryOperand) {
                int found=0;
                for(int candidate=1;candidate+4<=i.Length;candidate++) {
                    long displacement=BitConverter.ToInt32(bytes,offset+candidate);
                    if(unchecked((ulong)((long)i.NextIP+displacement))==i.IPRelativeMemoryAddress){displacementOffset=candidate;found++;}
                }
                if(found!=1) throw new ArgumentException("RIP displacement could not be uniquely recovered.");
            }
            var operands=new List<string>();
            for(int operand=0;operand<i.OpCount;operand++) {
                var kind=i.GetOpKind(operand);
                if(kind==OpKind.Register) operands.Add(i.GetOpRegister(operand).ToString());
                else if(kind==OpKind.Memory) operands.Add(i.IsIPRelativeMemoryOperand ? "[RIP=>0x"+i.IPRelativeMemoryAddress.ToString("X")+"]" : "["+i.MemoryBase+"+"+i.MemoryIndex+"*"+i.MemoryIndexScale+"+0x"+i.MemoryDisplacement64.ToString("X")+"]");
                else if(kind==OpKind.NearBranch16 || kind==OpKind.NearBranch32 || kind==OpKind.NearBranch64) operands.Add("0x"+i.NearBranchTarget.ToString("X"));
                else if(kind.ToString().StartsWith("Immediate")) {
                    ulong immediate;
                    switch(kind) {
                        case OpKind.Immediate8: immediate=i.Immediate8;break;
                        case OpKind.Immediate8_2nd: immediate=i.Immediate8_2nd;break;
                        case OpKind.Immediate16: immediate=i.Immediate16;break;
                        case OpKind.Immediate32: immediate=i.Immediate32;break;
                        case OpKind.Immediate64: immediate=i.Immediate64;break;
                        case OpKind.Immediate8to16: immediate=unchecked((ulong)i.Immediate8to16);break;
                        case OpKind.Immediate8to32: immediate=unchecked((ulong)i.Immediate8to32);break;
                        case OpKind.Immediate8to64: immediate=unchecked((ulong)i.Immediate8to64);break;
                        case OpKind.Immediate32to64: immediate=unchecked((ulong)i.Immediate32to64);break;
                        default: throw new ArgumentException("Unsupported immediate operand.");
                    }
                    operands.Add("0x"+immediate.ToString("X"));
                }
                else operands.Add(kind.ToString());
            }
            var raw=new byte[i.Length];Array.Copy(bytes,offset,raw,0,raw.Length);
            result.Add(new DecodedConsumerInstruction{Address=i.IP,Length=i.Length,Mnemonic=i.Mnemonic.ToString(),Operands=string.Join(", ",operands),Hex=BitConverter.ToString(raw),RipTarget=i.IsIPRelativeMemoryOperand?i.IPRelativeMemoryAddress:0,DisplacementOffset=displacementOffset,DisplacementSize=i.IsIPRelativeMemoryOperand?4:0,MemoryDisplacement=i.MemoryDisplacement64,MemoryBase=i.MemoryBase.ToString(),MemoryIndex=i.MemoryIndex.ToString()});
            if(stopAtFirstReturn && i.Mnemonic==Mnemonic.Ret) break;
        }
        return result.ToArray();
    }
}
