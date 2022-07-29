* size 6
```nasm
shr al, 4
add rdx, 6
and eax, 3
mov ecx, dword [rsp + rax*4]
xor ecx, dword [rdx - 4]
mov dword [rsp + rax*4], ecx
```
* moves dword from stack, xors it and pushes result back
* * value = 0x8b
* rax = 1st byte of instruction
* size = 6
* offset from TOS is rax & 3 (i guess 3 determines boundary of shift like from 0 to 3)
* ![[Pasted image 20220716221502.png]]
* [rdx - 4] ^ cb92 bc2f == 20 == ' '
