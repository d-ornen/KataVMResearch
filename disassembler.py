import struct
from termcolor import colored
vip = 0
bytecode = bytearray.fromhex(open('bytecode', 'r').readline())

def get_register_byte(vip):
    return (bytecode[vip+1] >> 4)&3

def get_register(offset):
    return f'r{offset}'

while True:
    instruction  = bytecode[vip]
    print(f'{hex(vip)}: ', end='')

    if instruction == 0xf6:
        branch = bytecode[vip+1] & 3
        if branch == 2:
            arg = bytecode[vip+2:vip+6]
            registerd = get_register_byte(vip)
            print(f'''(0xf6); {colored("VMOVDWORD", "green")} {get_register(registerd)}, {arg.hex()}''')
            vip += 6
            continue
        elif branch == 0:
            registerd = (bytecode[vip+1] >> 4) & 3 #rax
            register2 = (bytecode[vip+1] >> 6) & 3 #rcx
            print(f'''(0xf6); {colored('VMOVDWORD', "green")} {get_register(registerd)}, {get_register(register2)}''')
            vip += 5
            continue
        else:
            print('''0xf6 second branch not implemented''')

    elif instruction == 0xaa:
        branch = bytecode[vip+1] & 3
        if branch == 2:
            registerd = get_register_byte(vip)
            sub_value = bytecode[vip+2:vip+6]
            print(f'''(0xaa); {colored('VSUBDWORD', 'green')} {get_register(registerd)}, {sub_value.hex()}''')
            vip += 8
            continue
        elif branch == 0:
            register2 = (bytecode[vip +1] >> 6) & 3
            register1 = (bytecode[vip +1] >> 4) & 3
            print(f'''(0xaa); {colored('VSUBDWORD', 'green')} {get_register(register2)}, {get_register(register1)}''')
            vip += 3
            continue

        else:
            print('''0xaa second branch not implemented''')

    elif instruction == 0xef:
        branch = bytecode[vip+1] & 3
        if branch == 1:
            registerd = bytecode[vip + 1] >> 6
            print(f'''(0xef); {colored('VWRITE', 'yellow')} dst:{bytecode[vip+2]}, src:{get_register(registerd)}, size:{1}''')
            vip += 4
            continue
        else:
            print('''0xef second, third branch not implemented''')

    elif instruction == 0x4a:
        branch = bytecode[vip+1] & 3
        if branch == 2:
            registerd = (bytecode[vip + 1] >> 4)&3
            add_value = bytecode[vip+2:vip+6]
            print(f'''(0x4a); {colored('VADD', 'green')} {get_register(registerd)}, {add_value.hex()}''')
            vip += 7
            continue
        elif branch == 0:
            register1 = (bytecode[vip + 1] >> 6)&3 #eax
            register2 = (bytecode[vip + 1] >> 4)&3 #edx
            print(f'''(0x4a); {colored('VADD', 'green')} {get_register(register2)}, {get_register(register1)}''')
            vip += 2
            continue
        else:
            print('''0x4a second, third branch not implemented''')

    if instruction == 0x8b:
        branch = bytecode[vip+1] & 3
        if branch == 2:
            registerd = (bytecode[vip + 1] >> 4)&3
            register2 = bytecode[vip+2:vip+6]
            print(f'''(0x8b); {colored('VXOR', 'red')} {get_register(registerd)}, {register2.hex()}''')
            vip += 6
            continue
        if branch == 0:
            register2 = (bytecode[vip+1] >> 6)&3 #rax
            registerd = (bytecode[vip+1] >> 4)&3 #rcx
            print(f'''(0x8b); {colored('VXOR', 'red')} {get_register(registerd)}, {get_register(register2)}''')
            vip += 3
            continue
        else:
            print('''0x8b second, third branch not implemented''')
            break

    elif instruction == 0x5d:
        branch = bytecode[vip+1] & 3
        if branch == 0:
            registerd = (bytecode[vip + 1] >> 4)&3
            register2 = bytecode[vip+2:vip+6]
            print(f'''(0x5d); {colored('VREAD', 'yellow')} src: 0, dst:{get_register(registerd)}, size:{get_register(2)}''')
            vip += 3
            continue
        else:
            print('''0x5d second, third branch not implemented''')
            break

    elif instruction == 0x7c:
        branch = bytecode[vip+1] & 3
        if branch == 2:
            registerd = (bytecode[vip + 1] >> 4)&3
            shl_value = bytecode[vip+2]
            print(f'''(0x7c); {colored('VSHL', 'cyan')} {get_register(registerd)}, {shl_value}''')
            vip += 7
            continue
        else:
            print('''0x7c second, branch not implemented''')
            break

    elif instruction == 0xb1:
        branch = bytecode[vip+1] & 3
        if branch == 2:
            registerd = (bytecode[vip + 1] >> 4)&3
            shr_value = bytecode[vip+2]
            print(f'''(0xb1); {colored('VSHR', 'blue')} {get_register(registerd)}, {shr_value}''')
            vip += 6
            continue
        else:
            print('''0xb1 second, branch not implemented''')
            break

    elif instruction == 0xd5:
        branch = bytecode[vip+1] & 3
        if branch == 3:
            r8d = struct.unpack('''<i''', bytecode[vip + 2: vip+6])[0]
            rax = r8d
            rax = ~rax
            rax &= 7 # b111
            rax <<= 2
            print(f'''(0xd5); {colored('SHUFFLE3', 'magenta')} // shuffle stack dqwords and swap them (3rd branch)''')
            vip += 9
            continue
        elif branch == 2:
            r8d = struct.unpack("<i" , (bytecode[vip +2: vip+6]))[0]
            r8d = ~r8d
            r8d &= 7
            r8d <<= 2
            print(f'''(0xd5); {colored('SHUFFLE2', 'magenta')}''')
            vip += 5
            continue
        elif branch == 1:
            r8d = struct.unpack("<i" , (bytecode[vip +2: vip+6]))[0]
            r8d = ~r8d
            r8d &= 7
            r8d <<= 2
            print(f'''(0xd5); {colored('SHUFFLE1', 'magenta')} ''')
            vip += 3
            continue
        elif branch == 0:
            r8d = struct.unpack("<i" , (bytecode[vip +2: vip+6]))[0]
            r8d = ~r8d
            r8d &= 7
            r8d <<= 2
            print(f'''(0xd5); {colored('SHUFFLE0', 'magenta')} ''')
            vip += 3
            continue
        else:
            print('''0xd5 second, third branch not implemented''')

    elif instruction == 0x1e:
        branch = bytecode[vip+1] & 3
        #print(f'''(0x1e); VGWORDSWAP''')
        if branch == 1:
            print(f''' {colored('VSWAP1', 'green')} ''')
            registerd = (bytecode[vip + 1] >> 4)&3
            shl_value = bytecode[vip+2]
            vip += 8
            continue
        elif branch == 2:
            print(f'''(0x1e); {colored('VSWAP2', 'green')} r1:r4, r5:r8''')
            vip += 9
            continue
        elif branch ==3:
            print(f'''(0x1e); {colored('VSWAP3', 'green')} r1:r4, r5:r8''')
            vip += 10
            continue
        elif branch == 0 or branch == 1:

            vip = vip + 3 if branch == 0 else vip + 8
            if bytecode[vip+1] == 0xaa:
                subbranch = bytecode[vip+1]&3
                if subbranch == 0:
                    r1 = (bytecode[vip+1] >> 6) & 3
                    r2 = (bytecode[vip+1] >> 4) & 3
                    print(f'''(0x1e); VSWAP_SUB {get_register(r2)}, {get_register(r1)}''')
                    vip += 3
                    continue
                elif subbranch == 2:
                    r1 = (bytecode[vip+1] >> 6) & 3
                    data = bytecode[vip+2:vip+6]
                    print(f'''(0x1e); VSWAP_SUB {get_register(r1)}, {data.hex()}''')
                    vip += 8
                    continue
            else:
                print('''(0x1e); VSWAP_NOP r1:r4, r5:r8''')
                continue
            print('''(0x1e); ''')
            continue
        else:
            print('''0x1e not implemented''')
            break

    elif instruction == 0xc3:
        branch = bytecode[vip+1] & 3
        if branch == 3:
            register1 = (bytecode[vip + 1] >> 6)&3
            register2 = (bytecode[vip + 1] >> 4)&3
            print(f'''(0xc3); VCMP {get_register(register2)}, {get_register(register1)} r12d = 1 if not equal''')
            vip += 4
            continue
        elif branch == 2:
            register1 = (bytecode[vip + 1] >> 4)&3
            cmp_value = bytecode[vip+2:vip+6]
            print(f'''(0xc3); VCMP {get_register(register1)}, {cmp_value.hex()} r12d = 1 if not equal''')
            vip += 7
            continue
        else:
            print('''0xc3 second, branch not implemented''')
            break

    else:
        print(hex(bytecode[vip]), "VM EXIT")
        break


