### crypto
0x1b40 - prologue handler to read from stdin
0x1c60 - where I modified instruction size
0x1b6d - read from stdin

1. ...
2. ...
3. [8-b] xor [c-f]
4. a lot of xoring, adding and subtracting operations, no chance getting through this just by following execution steps

### symbolic execution
I stuided symbolic execution engines and decided to choose angr, cause it provides extensive functionality easy installation and good documentation

### fuzzing
since angr failed to find any interesting traces in 6 hours session and ate all my swap space (58 GB) (no fun in consuming so much resources)
I have to find another way of analyzing this vm.

#### fuzzing options
i was reading all day about different fuzzing techniques, but they are quite hard to get into. For now i decided to stick to afl++ fuzzer with dumb mode. The backup option is hooking to vm with frida and doing dirty stuff using this tool.

fuzzers that take snapshots are cool, but they require intel_pt technology in processor. It doesn't fit me because my processor is gen 3 and this thing is present on gen 5+ processors, so i will use more traditional fuzzers

afl++ searches for crashes in software which doesn't fit my current goal. I need to rewrite binary - on VM EXIT we pick r12d value. If it is 0 (right answer) i crash the app, if it is not 0 i close it normally.

#### rewriting binary
It is not so easy to rewrite binary annd not break something. I added crash in 'success' branch. What I haven't done is not changed read() instruction and therefore, my fuzzer doesn't work. I need to change bytecode to read 8 bytes at once, not 4+4 with 2 read() calls, but there is a problem - it requires modification of obfuscated bytecode, so I will be doing this for now.

#### bytecode format
rdx = 0x7ffe6d2f9f27
bytecode start = 0x7ffe6d2f9870
instruction offset (first read) = 0x6b7
bytecode size = 0x3b1a
bytecode position in static = 0x3008
instruction position in static = rsp+0x30+0x6b7
![[Pasted image 20220720132727.png]] located instruction in static code

![[Pasted image 20220720132800.png]] located instruction in live version
|0|1|2|3|4|5|6|7|8|9|a|b|c|d|e|f|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|rdx -> 5d|8c|rax -> 8c|5d|94|a9|f6|60|60|93|44|f6|bc|d3|bc|fb|
```nasm
lea rax, [rdx + 2]
mov qword [rsp + 0x20], rax; load address
```

|0|1|2|3|4|5|6|7|8|9|a|b|c|d|e|f|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|rdx -> 5d|eax -> 8c|8c|5d|94|a9|f6|60|60|93|44|f6|bc|d3|bc|fb|
```nasm
movzx eax, byte [rdx + 1]
mov ecx, eax ; ecx = 8c 
and ecx, 3 ;ecx = 0, so jump to 0x1c60
```

|0|1|2|3|4|5|6|7|8|9|a|b|c|d|e|f|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|5d|eax -> 8c|8c|rdx -> 5d|94|a9|f6|60|60|93|44|f6|bc|d3|bc|fb|
```nasm
mov ecx, eax ; ecx = 8c
add rdx, 3 ; shift to the next instruction (at offset 3)
shr cl, 6 ; 8c >> 6 = bin(0x8c) = '0b10001100', bin(0x8c >> 6 (or 4 + 2)) = '0b10'

```
instructin format (with arguments) 
|8b|4b|4b|8b|
|-|-|-|-|
|instruction|argument|branch switcher|unkown purporse|
* instruction - self-explanatory
* argument is 4 bytes value  that defines offset at which we fetch amount of characters to pick from read(). It is multiplied by 4.
* branch switcher needed for prologue handler

I patched instructions at these offsets:
0x00001c62 - add rdx, 6 ; rdx here points to instrucion in bytecode
0x00001b72 - mov rdx, 8 ; rdx here is 3rd argument to read()
### trampoline or stack modification
Note: `mov rdx, 8` modifies next instruction so code breaks. I need to write a trampoline or modificate value that is written on stack (write 8 instead of 4). I will try second method first, because it is easier than looking for unused place and writing trampoline.
I found where the 04 walue is written to stack. R2 and rizin failed to set watchpoints so i had to find this place for myself. With the help of this macro `(a; dcu 0x560d7833a351; dr rdx; dr rax; px 16 @ rsp`
i was able to repeatedly execute vm instructions. 0x560d7833a351 is last instruction of dispatcher.
What i found:
i suspect that f6aa04 is instruction i am looking for. Next two are 5d8c8c and 5d94a9 which are read() calls. The offset of f6aa04 is **0x6b1**. Let's patch binary
![[Pasted image 20220720213840.png]]

![[Pasted image 20220720215257.png]]
patching data in imhex
![[Pasted image 20220720215851.png]]patched binary (note add rdx, 6 on the left and 08 value in stack on the right)
looks like it is working (previous attempts have shown 0xfff... in eax which means error)
![[Pasted image 20220720220235.png]]
frida: not tested yet

### tracing virtual machine execution steps
using frida I am able to trace vm instructions. There is a problem to pass stdin. I don't know why, but entering data from frida shell breaks crackme. Another way of passing data is via linux pipe. I don't know how to do this with long launch string i got:
`frida --no-pause  -l ~/git/frida-agent-example/agent/index.ts ./patched_KataVM_L1`, so I nopped read() function:
![[Pasted image 20220722003040.png]] 
In frida I am intercepting 0x1b6d and writing byte array at rsi location, after that jumping to `0x1af8`
frida keep failing at random  steps with `process terminated`. I have no idea why. Looks like i need to choose another tool. Gonna give miasm second chance. Miasm failed. Fuck miasm, all my homies write custom disassembler.

![[Pasted image 20220722041823.png]] analysis of graph 

Reversing these instructions where main crypto algo is being used
![[Pasted image 20220724173520.png]]
![[Pasted image 20220724173344.png]]
this is stack state after first enter 0x00001600 - it is first crypto loop encountered during bytecode execution
![[Pasted image 20220724174249.png]]
 this is stack state after first enter 0x1600, but with another data. As we can see, the user input affects value in r2:r3, so we have to understand how it works.
changing last byte always affects a,b and e,f.

![[Pasted image 20220724175510.png]]in first function this loop:
1) swapped these values (result on screenshot)
![[Pasted image 20220724175741.png]]
2) swapped values![[Pasted image 20220724180000.png]]
3) swapped values![[Pasted image 20220724180139.png]]
4) did nothing to first dword.

after that jumped to:
0x17e7 where
1) loaded xmmword [rsp] ito xmm0
and made
2) ![[Pasted image 20220724181610.png]]
after that xmm1 became `xmm1 = 0x00000000a429e30ea002327f38373635`
3) stored xmm0 into rsp+0x10:
![[Pasted image 20220724181858.png]]
Note: first check:
```
0x2103: (0xc3); VCMP r2, 337698fb r12d = 1 if not equal
0x210a: (0xc3); VCMP r3, 880450a2 r12d = 1 if not equal
0x2111: (0xf6); VPUSHDWORD r2, 04000000
0x2117: (0x5d); VREADnsrc: 0, dst:r0, size:r2
```
second check:
```
0x3b0a: (0xc3); VCMP r2, 2d08e76c r12d = 1 if not equal
0x3b11: (0xc3); VCMP r3, 2f493ac0 r12d = 1 if not equal
```

Fuzzer found 500+ hangs. These where correct inputs for the first stage. Now i need at least one of these inputs, but afl++ doesn't save non unique hangings, so i have either to recompile afl with custom rules (save non-unique hangins) or patch machine code of the crackme, like from previous stage.
I have chosen to patch binary because it is simple and  I already know it's structure.
After several days of trying to rewrite code in c I guessed to google some eye-catching parts of algorithm like shl 4 and shr 5 and found out that this is some kind of TEA algorithm - something among xxtea, xtea, tea - There are known attacks on tea algorithm - 
https://github.com/vincebel7/attack-on-tea
https://en.wikipedia.org/wiki/Tiny_Encryption_Algorithm#Reference_code

preparing for bruteforce attack:
info:
entry data - two dwords or qword which is 8 bytes
end state - depends on entry state and i know ethalon value for both stages
v0 = 
v1 = 

k0 =  0x80b86e21
k1 =  0xa268295d
k2 =  0xf171f22d
k3 =  0x28a13c94
delta =  0xe09ffbb1
sum = 0x1c13ff7620
//results
r0 = 61564e78
r1 = 304e5f32
r2 = 33745f37
r3 = 676c4161

![[Pasted image 20220726014930.png]]
virtual assembly code and encryption algorithm for  comparison
```c
#include <stdint.h>

void encrypt (uint32_t v[2], const uint32_t k[4]) {
    uint32_t v0=v[0], v1=v[1], sum=0, i;           /* set up */
    uint32_t delta=0x9E3779B9;                     /* a key schedule constant */
    uint32_t k0=k[0], k1=k[1], k2=k[2], k3=k[3];   /* cache key */
    for (i=0; i<32; i++) {                         /* basic cycle start */
        sum += delta;
        v0 += ((v1<<4) + k0) ^ (v1 + sum) ^ ((v1>>5) + k1);
        v1 += ((v0<<4) + k2) ^ (v0 + sum) ^ ((v0>>5) + k3);
    }                                              /* end cycle */
    v[0]=v0; v[1]=v1;
}

void decrypt (uint32_t v[2], const uint32_t k[4]) {
    uint32_t v0=v[0], v1=v[1], sum=0xC6EF3720, i;  /* set up; sum is (delta << 5) & 0xFFFFFFFF */
    uint32_t delta=0x9E3779B9;                     /* a key schedule constant */
    uint32_t k0=k[0], k1=k[1], k2=k[2], k3=k[3];   /* cache key */
    for (i=0; i<32; i++) {                         /* basic cycle start */
        v1 -= ((v0<<4) + k2) ^ (v0 + sum) ^ ((v0>>5) + k3);
        v0 -= ((v1<<4) + k0) ^ (v1 + sum) ^ ((v1>>5) + k1);
        sum -= delta;
    }                                              /* end cycle */
    v[0]=v0; v[1]=cv1;
}
```

```c
#include <stdint.h>
#include <stdio.h>

void decrypt(uint32_t v[2], const uint32_t k[4]) {
    uint32_t v0=v[0], v1=v[1],  i;  /* set up; sum is (delta << 5) & 0xFFFFFFFF */
    uint32_t sum=0x1c13ff7620;
    uint32_t delta=0xe09ffbb1;                     /* a key schedule constant */
    uint32_t k0=k[0], k1=k[1], k2=k[2], k3=k[3];   /* cache key */
    for (i=0; i<32; i++) {                         /* basic cycle start */
        if ( i == 9){
            v1 -= ((v0<<2) + k2) ^ (v0 + sum) ^ ((v0>>3) + k3);
        }
        else{
            v1 -= ((v0<<4) + k2) ^ (v0 + sum) ^ ((v0>>5) + k3);
        }
            v0 -= ((v1<<4) + k0) ^ (v1 + sum) ^ ((v1>>5) + k1);
        sum -= delta;
    }                                              /* end cycle */
    v[0]=v0; v[1]=v1;
    printf("%x, %x\n", v[0], v[1]);

}


int main(int argc, char *argv[])
{
    uint32_t v[2] = {0x6ce7082d, 0xc03a492f};
    uint32_t k[4] = {0x80b86e21, 0xa268295d, 0xf171f22d, 0x28a13c94};
    decrypt(v, k);
    return 0;
}
```