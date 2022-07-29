* parse [rdx + 1] and give control to 3 handlers based on results
* taks 1st byte as argument and stores in cl:
* ecx = b[rdx+1] & 3

goto [[(0xef) handler 0x00001f00 VWRITEYYY]] if cl == 2  else
goto [[(0xef) handler 0x00001ca0 VWRITEXXX]] if cl == 3  else 
goto [[(0xef) handler 0x00002180 VWRITE1CHR]] if cl ==  1 else
goto [[(0xef) handler 0x00001abd VWRITEZZZ]]

