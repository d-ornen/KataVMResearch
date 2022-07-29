

* al = b[rdx + 1] & 3
goto [[(0xf6) handler 0x000015e0 VCPYDWORD]] if al & 3  else
goto [[(0xf6) handler 0x000013ef VPUSHBDWORD]] if al & 3 == 2 else
