project('dreieck', 'c',
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

executable('dreieck',
  sources,
  [shaders_gen],
  link_with : glad_lib,
  dependencies : [glfw_dep, cglm_dep, gl_dep, dl_dep, m_dep],
  include_directories : inc,
  install : false,
  link_args : ['-static-libgcc']
)
