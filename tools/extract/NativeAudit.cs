using System;
using System.Collections.Generic;
using Iced.Intel;

public static class ForgottenNativeAudit {
    public static int[] Matches(byte[] data, string signature) {
        if(data==null || string.IsNullOrWhiteSpace(signature)) throw new ArgumentException("Empty data/signature.");
        string[] tokens=signature.Split(new[]{' '},StringSplitOptions.RemoveEmptyEntries);
        var values=new int[tokens.Length];
        for(int i=0;i<values.Length;i++) {
            if(tokens[i]!="??" && (tokens[i].Length!=2 || !byte.TryParse(tokens[i],System.Globalization.NumberStyles.HexNumber,System.Globalization.CultureInfo.InvariantCulture,out _)))
                throw new ArgumentException("Invalid byte token.");
            values[i]=tokens[i]=="??" ? -1 : Convert.ToInt32(tokens[i],16);
        }
        var result=new List<int>();
        for(int i=0;i<=data.Length-values.Length;i++) {
            if(values[0]>=0 && data[i]!=values[0]) continue;
            bool match=true;
            for(int j=1;j<values.Length;j++) if(values[j]>=0 && data[i+j]!=values[j]) {match=false;break;}
            if(match) result.Add(i);
        }
        return result.ToArray();
    }
    public static string[] References(byte[] code, ulong address, ulong target, ulong length) {
        if(length==0 || target>ulong.MaxValue-length || address>ulong.MaxValue-(ulong)code.Length) throw new ArgumentException("Invalid address range.");
        var reader=new ByteArrayCodeReader(code);
        var decoder=Decoder.Create(64,reader);
        decoder.IP=address;
        var lines=new List<string>();
        while(decoder.IP<address+(ulong)code.Length) {
            var instruction=decoder.Decode();
            if(!instruction.IsIPRelativeMemoryOperand) continue;
            ulong reference=instruction.IPRelativeMemoryAddress;
            if(reference<target || reference>=target+length) continue;
            lines.Add($"{instruction.IP:X16}|{reference:X16}|{instruction.Mnemonic}|op0={instruction.Op0Kind}:{instruction.Op0Register}|op1={instruction.Op1Kind}:{instruction.Op1Register}");
        }
        return lines.ToArray();
    }
}
