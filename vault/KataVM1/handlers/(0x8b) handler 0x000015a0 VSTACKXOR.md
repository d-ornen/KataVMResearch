```nasm
shr al, 6
add rdx, 3
shr cl, 4
and eax, 3
and ecx, 3
mov eax, dword [rsp + rax*4] ; get 1st xor
xor dword [rsp + rcx*4], eax ; xor with second
```

* size 3
* xores two values from stack
* xores [8-B] and [c-f] :
* ![[Pasted image 20220718190746.png]]before
* ![[Pasted image 20220718191420.png]] after

