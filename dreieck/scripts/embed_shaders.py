#!/usr/bin/env python3
import os
import sys

def escape_c_string(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n"\n"')

def main():
    # Meson übergibt die Argumente aus dem 'command'-Array:
    # sys.argv[1] = @OUTPUT0@ (Header-Pfad)
    # sys.argv[2] = @OUTPUT1@ (C-File-Pfad)
    # sys.argv[3:] = @INPUT@ (Liste der Shader-Dateien)
    if len(sys.argv) < 3:
        print("Fehler: Zu wenige Argumente übergeben.", file=sys.stderr)
        sys.exit(1)

    out_h = sys.argv[1]
    out_c = sys.argv[2]
    shader_files = sys.argv[3:] # Alle restlichen Argumente sind Shader-Dateien

    if not shader_files:
        print('Warnung: Keine Shader-Dateien übergeben.', file=sys.stderr)

    # 1. Header-Datei schreiben
    with open(out_h, 'w', encoding='utf-8') as h:
        h.write('#pragma once\n\n')
        h.write('typedef struct { const char* name; const char* source; } ShaderEntry;\n\n')
        h.write('extern const ShaderEntry shader_entries[];\n')
        h.write('extern const unsigned int shader_entries_count;\n')

    # 2. C-Datei schreiben
    with open(out_c, 'w', encoding='utf-8') as c:
        c.write('#include "shaders_embedded.h"\n\n')

        if not shader_files:
            c.write('const ShaderEntry shader_entries[] = {{NULL, NULL}};\n\n')
            c.write('const unsigned int shader_entries_count = 0;\n')
            return

        var_names = []
        for path in shader_files:
            name = os.path.basename(path)
            var = 'shader_src_' + name.replace('.', '_')
            var_names.append((name, var))
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            c.write(f'static const char {var}[] = \n"{escape_c_string(content)}";\n\n')

        c.write('const ShaderEntry shader_entries[] = {\n')
        for name, var in var_names:
            c.write(f'  {{ "{name}", {var} }},\n')
        c.write('};\n\n')
        c.write(f'const unsigned int shader_entries_count = {len(var_names)};\n')

if __name__ == '__main__':
    main()
