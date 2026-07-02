#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) != 6:
        print(f'Aufruf: {{sys.argv[0]}} <input_file> <array_name> <out_header> <out_source>')
        sys.exit(1)
    infile, array_name, out_h, out_c = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    with open(infile, 'rb') as f:
        data = f.read()
    with open(out_h, 'w') as h:
        h.write('#pragma once\n\n')
        h.write(f'extern const unsigned char {array_name}[];\n')
        h.write(f'extern const unsigned int {array_name}_size;\n')
    with open(out_c, 'w') as c:
        c.write(f'#include "{out_h}"\n\n')
        c.write(f'const unsigned char {array_name}[] = {{\n')
        for i, b in enumerate(data):
            if i % 16 == 0: c.write('  ')
            c.write(f'0x{b:02x}}, ')
            if i % 16 == 15: c.write('\n')
        if len(data) % 16 != 0: c.write('\n')
        c.write('}};\n\n')
        c.write(f'const unsigned int {array_name}_size = {len(data)};\n')

if __name__ == '__main__':
    main()
