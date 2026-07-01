#!/usr/bin/env python3
"""
OpenGL + Meson + C Projekt-Bootstrapper (ohne automatischen GLAD-Download).
Verwendung: python3 create_opengl_project.py <PROJEKTNAME>
"""

import os
import sys
import shutil
from pathlib import Path

# ------------------------------------------------------------
# 1. HILFSFUNKTIONEN
# ------------------------------------------------------------
def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ Erstellt: {path}")

# ------------------------------------------------------------
# 2. HAUPTPROGRAMM
# ------------------------------------------------------------
def main():
    if len(sys.argv) != 2:
        print("Verwendung: python3 create_opengl_project.py <PROJEKTNAME>")
        sys.exit(1)

    project_name = sys.argv[1]
    base_path = Path.cwd() / project_name

    if base_path.exists():
        print(f"❌ Ordner '{base_path}' existiert bereits. Bitte anderen Namen wählen.")
        sys.exit(1)

    print(f"🚀 Erstelle OpenGL-Meson-Projekt: {project_name}")
    print(f"📁 Ziel: {base_path}")

    # --------------------------------------------------------
    # 2a. Ordnerstruktur anlegen
    # --------------------------------------------------------
    dirs = [
        base_path / "src",
        base_path / "include",
        base_path / "shaders",
        base_path / "scripts",
        base_path / "subprojects",
        base_path / "fonts",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print("  ✅ Ordnerstruktur erstellt.")

    # --------------------------------------------------------
    # 2b. meson.build
    # --------------------------------------------------------
    meson_build = f'''project('{project_name}', 'c',
  version : '0.1.0',
  default_options : ['warning_level=3', 'c_std=c11', 'default_library=static'])

cc = meson.get_compiler('c')
python = import('python').find_installation('python3')

# Shader einbetten (alle Dateien in shaders/)
shaders_gen = custom_target('shader_embedding',
  output : ['shaders_embedded.h', 'shaders_embedded.c'],
  command : [python, files('scripts/embed_shaders.py')],
  build_by_default : true
)

# (Optional) Font-Einbettung – hier auskommentiert
# font_gen = custom_target('font_embedding',
#   input : 'fonts/DeineSchrift.ttf',
#   output : ['font_embedded.h', 'font_embedded.c'],
#   command : [python, files('scripts/embed_binary.py'), '@INPUT@', 'font_data', '@OUTPUT0@', '@OUTPUT1@'],
#   build_by_default : true
# )

# Abhängigkeiten (GLFW über WrapDB, cglm per Git-Wrap)
glfw_dep = dependency('glfw3', static : true, fallback : ['glfw', 'glfw_dep'])
cglm_dep = dependency('cglm', static : true, fallback : ['cglm', 'cglm_dep'],
                      default_options : ['install=false'])
gl_dep = dependency('gl')
dl_dep = cc.find_library('dl', required : false)
m_dep  = cc.find_library('m', required : false)

inc = include_directories('include', 'src')

# GLAD als separate statische Bibliothek
glad_lib = static_library('glad', 'src/glad.c',
  include_directories : include_directories('include'),
  c_args : ['-w']
)

sources = [
  'src/main.c',
  # weitere eigene .c-Dateien hier
]

executable('{project_name}',
  sources,
  [shaders_gen],
  link_with : glad_lib,
  dependencies : [glfw_dep, cglm_dep, gl_dep, dl_dep, m_dep],
  include_directories : inc,
  install : false,
  link_args : ['-static-libgcc']
)
'''
    write_file(base_path / "meson.build", meson_build)

    # --------------------------------------------------------
    # 2c. Wrap-Dateien (GLFW via WrapDB, cglm per Git)
    # --------------------------------------------------------
    glfw_wrap = '''[wrap-file]
directory = glfw-3.4
source_url = https://github.com/glfw/glfw/archive/refs/tags/3.4.tar.gz
source_filename = glfw-3.4.tar.gz
source_hash = c038d34200234d071fae9345bc455e4a8f2f544ab60150765d7704e08f3dac01
patch_filename = glfw_3.4-1_patch.zip
patch_url = https://wrapdb.mesonbuild.com/v2/glfw_3.4-1/get_patch
patch_hash = 58a6a6cdb28195d7f7e6f5de85dff7044d378e49b46bf1d4a9b04c97ed93e6b0
source_fallback_url = https://github.com/mesonbuild/wrapdb/releases/download/glfw_3.4-1/glfw-3.4.tar.gz
wrapdb_version = 3.4-1

[provide]
glfw3 = glfw_dep
'''
    write_file(base_path / "subprojects" / "glfw.wrap", glfw_wrap)

    cglm_wrap = '''[wrap-git]
url = https://github.com/recp/cglm.git
revision = v0.9.1

[provide]
cglm = cglm_dep
'''
    write_file(base_path / "subprojects" / "cglm.wrap", cglm_wrap)

    # --------------------------------------------------------
    # 2d. Python-Embedding-Skripte (KORRIGIERT)
    # --------------------------------------------------------
    embed_shaders = '''#!/usr/bin/env python3
import os
import glob
import sys

# Pfad zum Shader-Verzeichnis relativ zu diesem Skript
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SHADER_DIR = os.path.join(SCRIPT_DIR, '..', 'shaders')
OUT_H = 'shaders_embedded.h'
OUT_C = 'shaders_embedded.c'

def escape_c_string(s):
    return s.replace('\\\\', '\\\\\\\\').replace('"', '\\\\"').replace('\\n', '\\\\n"\\n"')

def main():
    shader_files = glob.glob(os.path.join(SHADER_DIR, '*'))
    # Sicherstellen, dass nur Dateien (keine Ordner) genommen werden
    shader_files = [f for f in shader_files if os.path.isfile(f)]

    if not shader_files:
        print(f'Warnung: Keine Shader-Dateien in {SHADER_DIR}/ gefunden.', file=sys.stderr)

    with open(OUT_H, 'w') as h:
        h.write('#pragma once\\n\\n')
        h.write('typedef struct { const char* name; const char* source; } ShaderEntry;\\n\\n')
        h.write('extern const ShaderEntry shader_entries[];\\n')
        h.write('extern const unsigned int shader_entries_count;\\n')

    with open(OUT_C, 'w') as c:
        c.write('#include "shaders_embedded.h"\\n\\n')

        if not shader_files:
            # Leere Liste – trotzdem gültigen C‑Code erzeugen
            c.write('const ShaderEntry shader_entries[] = {{NULL, NULL}};\\n\\n')
            c.write('const unsigned int shader_entries_count = 0;\\n')
            return

        var_names = []
        for path in shader_files:
            name = os.path.basename(path)
            var = 'shader_src_' + name.replace('.', '_')
            var_names.append((name, var))
            with open(path, 'r') as f:
                content = f.read()
            c.write(f'static const char {var}[] = \\n"{escape_c_string(content)}";\\n\\n')

        c.write('const ShaderEntry shader_entries[] = {\\n')
        for name, var in var_names:
            c.write(f'  {{ "{name}", {var} }},\\n')
        c.write('};\\n\\n')
        c.write(f'const unsigned int shader_entries_count = {len(var_names)};\\n')

if __name__ == '__main__':
    main()
'''
    write_file(base_path / "scripts" / "embed_shaders.py", embed_shaders)
    os.chmod(base_path / "scripts" / "embed_shaders.py", 0o755)

    embed_binary = '''#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) != 6:
        print(f'Aufruf: {{sys.argv[0]}} <input_file> <array_name> <out_header> <out_source>')
        sys.exit(1)
    infile, array_name, out_h, out_c = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    with open(infile, 'rb') as f:
        data = f.read()
    with open(out_h, 'w') as h:
        h.write('#pragma once\\n\\n')
        h.write(f'extern const unsigned char {array_name}[];\\n')
        h.write(f'extern const unsigned int {array_name}_size;\\n')
    with open(out_c, 'w') as c:
        c.write(f'#include "{out_h}"\\n\\n')
        c.write(f'const unsigned char {array_name}[] = {{\\n')
        for i, b in enumerate(data):
            if i % 16 == 0: c.write('  ')
            c.write(f'0x{b:02x}}, ')
            if i % 16 == 15: c.write('\\n')
        if len(data) % 16 != 0: c.write('\\n')
        c.write('}};\\n\\n')
        c.write(f'const unsigned int {array_name}_size = {len(data)};\\n')

if __name__ == '__main__':
    main()
'''
    write_file(base_path / "scripts" / "embed_binary.py", embed_binary)
    os.chmod(base_path / "scripts" / "embed_binary.py", 0o755)

    # --------------------------------------------------------
    # 2e. Beispiel-Shader
    # --------------------------------------------------------
    vert = '''#version 330 core
layout (location = 0) in vec3 aPos;
void main() {
    gl_Position = vec4(aPos, 1.0);
}
'''
    frag = '''#version 330 core
out vec4 FragColor;
void main() {
    FragColor = vec4(0.8, 0.2, 0.6, 1.0);
}
'''
    write_file(base_path / "shaders" / "triangle.vert", vert)
    write_file(base_path / "shaders" / "triangle.frag", frag)

    # --------------------------------------------------------
    # 2f. main.c (KORRIGIERT – GLFW_INCLUDE_NONE)
    # --------------------------------------------------------
    main_c = '''#define GLFW_INCLUDE_NONE   // GLFW lädt keine OpenGL-Header – das übernimmt GLAD
#include <GLFW/glfw3.h>
#include <glad/glad.h>        // GLAD muss nach GLFW kommen
#include <cglm/cglm.h>
#include <stdio.h>
#include <string.h>
#include "shaders_embedded.h"

// -------------------------------------------------------------
// Hilfsfunktionen für Shader
// -------------------------------------------------------------
static const char* get_shader_source(const char* name) {
    for (unsigned int i = 0; i < shader_entries_count; i++) {
        if (strcmp(shader_entries[i].name, name) == 0)
            return shader_entries[i].source;
    }
    return NULL;
}

static unsigned int compile_shader(GLenum type, const char* src) {
    unsigned int shader = glCreateShader(type);
    glShaderSource(shader, 1, &src, NULL);
    glCompileShader(shader);
    int success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char info[512];
        glGetShaderInfoLog(shader, sizeof(info), NULL, info);
        fprintf(stderr, "FEHLER: Shader-Kompilierung (%s) fehlgeschlagen: %s\\n",
                (type == GL_VERTEX_SHADER) ? "Vertex" : "Fragment", info);
        return 0;
    }
    return shader;
}

static unsigned int create_program(const char* vert_name, const char* frag_name) {
    const char* vsrc = get_shader_source(vert_name);
    const char* fsrc = get_shader_source(frag_name);
    if (!vsrc || !fsrc) {
        fprintf(stderr, "FEHLER: Shader '%s' oder '%s' nicht gefunden.\\n", vert_name, frag_name);
        return 0;
    }
    unsigned int v = compile_shader(GL_VERTEX_SHADER, vsrc);
    unsigned int f = compile_shader(GL_FRAGMENT_SHADER, fsrc);
    unsigned int prog = glCreateProgram();
    glAttachShader(prog, v);
    glAttachShader(prog, f);
    glLinkProgram(prog);
    int success;
    glGetProgramiv(prog, GL_LINK_STATUS, &success);
    if (!success) {
        char info[512];
        glGetProgramInfoLog(prog, sizeof(info), NULL, info);
        fprintf(stderr, "FEHLER: Shader-Linking fehlgeschlagen: %s\\n", info);
        return 0;
    }
    glDeleteShader(v);
    glDeleteShader(f);
    return prog;
}

// -------------------------------------------------------------
// main
// -------------------------------------------------------------
int main(void) {
    if (!glfwInit()) {
        fprintf(stderr, "FEHLER: GLFW konnte nicht initialisiert werden.\\n");
        return -1;
    }

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWwindow* window = glfwCreateWindow(800, 600, "OpenGL mit eingebetteten Shadern", NULL, NULL);
    if (!window) {
        fprintf(stderr, "FEHLER: Fenster konnte nicht erstellt werden.\\n");
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);

    // GLAD laden
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        fprintf(stderr, "FEHLER: GLAD konnte nicht geladen werden.\\n");
        glfwTerminate();
        return -1;
    }

    // Shader aus den eingebetteten Daten laden
    unsigned int shader_program = create_program("triangle.vert", "triangle.frag");
    if (!shader_program) {
        glfwTerminate();
        return -1;
    }

    // Dreieck-Vertex-Daten
    float vertices[] = {
        -0.5f, -0.5f, 0.0f,
         0.5f, -0.5f, 0.0f,
         0.0f,  0.5f, 0.0f
    };
    unsigned int VAO, VBO;
    glGenVertexArrays(1, &VAO);
    glGenBuffers(1, &VBO);
    glBindVertexArray(VAO);
    glBindBuffer(GL_ARRAY_BUFFER, VBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);

    // Hauptschleife
    while (!glfwWindowShouldClose(window)) {
        glClearColor(0.1f, 0.1f, 0.15f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        glUseProgram(shader_program);
        glBindVertexArray(VAO);
        glDrawArrays(GL_TRIANGLES, 0, 3);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
'''
    write_file(base_path / "src" / "main.c", main_c)

    # --------------------------------------------------------
    # 2g. README.md
    # --------------------------------------------------------
    readme = f'''# {project_name}

Ein minimales OpenGL‑Projekt in C, das mit **Meson** gebaut wird und alle Shader **eingebettet** in die ausführbare Datei enthält.

---

## Voraussetzungen

- **Python 3** (für die Shader‑Einbettung)
- **Meson** (`pip install meson` oder über den Paketmanager)
- **Ninja** (`apt install ninja-build` / `brew install ninja` / …)
- **Git** (zum Herunterladen der Abhängigkeiten via Wrap)

---

## Erste Schritte (nach dem Bootstrappen)

Dieses Projekt wurde mit dem **Bootstrapper‑Skript** erstellt. Die Grundstruktur liegt bereits vor, aber **GLAD** fehlt noch – das musst du manuell einfügen.

### 1. GLAD herunterladen und einbinden

Öffne diesen Link in deinem Browser (die Einstellungen sind bereits vorkonfiguriert):

[https://glad.dav1d.de/#profile=core&language=c&specification=gl&loader=on&api=gl%3D3.3](https://glad.dav1d.de/#profile=core&language=c&specification=gl&loader=on&api=gl%3D3.3)

- Klicke auf **„Generate“** und lade das ZIP‑Archiv herunter.
- Entpacke das ZIP und kopiere die folgenden Dateien/Ordner in dein Projekt:

| Aus dem ZIP | Ziel im Projekt |
|-------------|-----------------|
| `glad.c`    | `src/glad.c`    |
| Ordner `glad/` | `include/glad/` |
| Ordner `KHR/`  | `include/KHR/`  |

Danach ist dein Projekt vollständig.

### 2. Meson‑Build initialisieren

Wechsle in das Projektverzeichnis und führe aus:

```bash
meson setup build
```
'''
    write_file(base_path / "README.md", readme)

    # --------------------------------------------------------
    # 2h. .gitignore
    # --------------------------------------------------------
    gitignore_content = '''# -------------------------------
# Build- & Ausgabe-Verzeichnisse
# -------------------------------
build/
build-*/
builddir/
*.exe
*.out
*.app

# -------------------------------
# Von Meson generierte Dateien
# -------------------------------
compile_commands.json
meson-logs/
meson-private/
.cache/
.dirstamp

# -------------------------------
# Temporäre Dateien (Editoren, Compiler)
# -------------------------------
*.swp
*.swo
*~
*.tmp
*.bak
*.log
*.o
*.obj
*.a
*.so
*.dylib
*.dll
*.pdb
*.ilk
*.exp

# -------------------------------
# Von den Embedding-Skripten generierte Dateien
# (werden zwar im Build-Ordner erzeugt, aber zur Sicherheit)
# -------------------------------
shaders_embedded.h
shaders_embedded.c
font_embedded.h
font_embedded.c

# -------------------------------
# IDE-spezifisch (VS Code, CLion, …)
# -------------------------------
.vscode/
.idea/
*.iml
.vs/
*.user
*.suo

# -------------------------------
# Abhängigkeiten, die von Wrap heruntergeladen werden
# (nur die .wrap-Dateien sollen versioniert werden)
# -------------------------------
subprojects/*/
!subprojects/*.wrap
'''
    write_file(base_path / ".gitignore", gitignore_content)

if __name__ == "__main__":
    main()
