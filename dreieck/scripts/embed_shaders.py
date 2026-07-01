#!/usr/bin/env python3
import os
import glob
import sys

# Pfad zum Shader-Verzeichnis relativ zu diesem Skript
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SHADER_DIR = os.path.join(SCRIPT_DIR, '..', 'shaders')
OUT_H = 'shaders_embedded.h'
OUT_C = 'shaders_embedded.c'

def escape_c_string(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n"\n"')

def main():
    shader_files = glob.glob(os.path.join(SHADER_DIR, '*'))
    # Sicherstellen, dass nur Dateien (keine Ordner) genommen werden
    shader_files = [f for f in shader_files if os.path.isfile(f)]

    if not shader_files:
        print(f'Warnung: Keine Shader-Dateien in {SHADER_DIR}/ gefunden.', file=sys.stderr)

    with open(OUT_H, 'w') as h:
        h.write('#pragma once\n\n')
        h.write('typedef struct { const char* name; const char* source; } ShaderEntry;\n\n')
        h.write('extern const ShaderEntry shader_entries[];\n')
        h.write('extern const unsigned int shader_entries_count;\n')

    with open(OUT_C, 'w') as c:
        c.write('#include "shaders_embedded.h"\n\n')

        if not shader_files:
            # Leere Liste – trotzdem gültigen C‑Code erzeugen
            c.write('const ShaderEntry shader_entries[] = {{NULL, NULL}};\n\n')
            c.write('const unsigned int shader_entries_count = 0;\n')
            return

        var_names = []
        for path in shader_files:
            name = os.path.basename(path)
            var = 'shader_src_' + name.replace('.', '_')
            var_names.append((name, var))
            with open(path, 'r') as f:
                content = f.read()
            c.write(f'static const char {var}[] = \n"{escape_c_string(content)}";\n\n')

        c.write('const ShaderEntry shader_entries[] = {\n')
        for name, var in var_names:
            c.write(f'  {{ "{name}", {var} }},\n')
        c.write('};\n\n')
        c.write(f'const unsigned int shader_entries_count = {len(var_names)};\n')

if __name__ == '__main__':
    main()
