```nasm
shr al, 4
mov ecx, dword[rdx + 2]
add rdx, 7
and eax, 3
add dword [rsp + rax * 4], ecx ; likely rax * 4 = 0
```
* size 7
* adds to some value on stack another from argument