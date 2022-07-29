* calls write syscall
* suppose it prints one character (cmp eax, 1) at the end of handler
* size 2
* writes 1 byte to file descriptor (2nd byte) as src buffer takes 1st byte >> 6 (usually it is 0) + TOS
* next instruction addr = stored_addr + 2
