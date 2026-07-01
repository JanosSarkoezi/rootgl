#include <glad/glad.h>
#include <GLFW/glfw3.h>
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
        fprintf(stderr, "FEHLER: Shader-Kompilierung (%s) fehlgeschlagen: %s\n",
                (type == GL_VERTEX_SHADER) ? "Vertex" : "Fragment", info);
        return 0;
    }
    return shader;
}

static unsigned int create_program(const char* vert_name, const char* frag_name) {
    const char* vsrc = get_shader_source(vert_name);
    const char* fsrc = get_shader_source(frag_name);
    if (!vsrc || !fsrc) {
        fprintf(stderr, "FEHLER: Shader '%s' oder '%s' nicht gefunden.\n", vert_name, frag_name);
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
        fprintf(stderr, "FEHLER: Shader-Linking fehlgeschlagen: %s\n", info);
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
        fprintf(stderr, "FEHLER: GLFW konnte nicht initialisiert werden.\n");
        return -1;
    }

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWwindow* window = glfwCreateWindow(800, 600, "OpenGL mit eingebetteten Shadern", NULL, NULL);
    if (!window) {
        fprintf(stderr, "FEHLER: Fenster konnte nicht erstellt werden.\n");
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);

    // GLAD laden
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        fprintf(stderr, "FEHLER: GLAD konnte nicht geladen werden.\n");
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
