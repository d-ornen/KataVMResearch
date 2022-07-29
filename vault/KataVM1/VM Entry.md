#VMEntry
[[VM Dispatcher]]
Trying to learn registers' roles
eax = 0
r12d = 0
lea rsi, [0x00003008] - cxa_finalize + 0x3008
xmm0  = 0
memcpy(stackTop+0x30, rsi, 0x3b1a) // loads bytecode?
rdx = stackTop+0x30
16.07 15:56 - don't see any traces of virtual stack pointer. Perhaps, it is register-based