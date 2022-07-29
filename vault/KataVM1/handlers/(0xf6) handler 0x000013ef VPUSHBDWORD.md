* value = 0xf6
* size 6
* modifies stack
* takes argument from [rdx+2]
* argument either 3 or 2
* i guess it pushes dword base in stack, next [[(0xf6) handler 0x000015e0 VCPYDWORD]] will [[(0x8b) handler 0x000014dd VSTACKXOR]] it with [rdx-4] value and then print it with [[(0xef) handler 0x00002180 VWRITE1CHR]]
* base dword for xoring
* ![[Pasted image 20220718180246.png]] duplicated 3-7 bytes to 4-8 after second read() call
* ![[Pasted image 20220718180433.png]]after that duplicated  