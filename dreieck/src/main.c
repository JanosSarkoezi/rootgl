#include <glad/glad.h>   // Lädt die OpenGL-Funktionszeiger (muss VOR GLFW stehen)
#include <GLFW/glfw3.h>  // Erstellt das Fenster und verwaltet Eingaben
#include <cglm/cglm.h>   // Mathematik-Bibliothek für Vektoren und Matrizen (in OpenGL üblich)
#include <stdio.h>       // Für Standard-Ein-/Ausgabe wie z.B. Fehlermeldungen (fprintf)
#include <string.h>      // Für String-Vergleiche (strcmp)
#include "shaders_embedded.h" // Eigene Header-Datei, die Shader-Code als Strings enthält

// -------------------------------------------------------------
// Hilfsfunktionen für Shader
// -------------------------------------------------------------

// Sucht in einem Array aus eingebetteten Shadern nach dem passenden Namen
static const char* get_shader_source(const char* name) {
    // Schleife läuft durch alle registrierten Shader-Einträge
    for (unsigned int i = 0; i < shader_entries_count; i++) {
        // Wenn der gesuchte Name mit dem Eintrag übereinstimmt...
        if (strcmp(shader_entries[i].name, name) == 0)
            return shader_entries[i].source; // ...gib den Quellcode-String zurück
    }
    return NULL; // Nichts gefunden
}

// Kompiliert den Shader-Quellcode auf der Grafikkarte
static unsigned int compile_shader(GLenum type, const char* src) {
    // Erstellt ein leeres Shader-Objekt für den jeweiligen Typ (Vertex oder Fragment)
    unsigned int shader = glCreateShader(type);

    // Verknüpft den Quellcode-String mit dem Shader-Objekt
    glShaderSource(shader, 1, &src, NULL);

    // Befiehlt der Grafikkarte, den Shader-Code in Maschinensprache zu übersetzen
    glCompileShader(shader);

    // Prüfen, ob die Kompilierung erfolgreich war
    int success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success); // Status abfragen
    if (!success) {
        char info[512]; // Puffer für die Fehlermeldung
        glGetShaderInfoLog(shader, sizeof(info), NULL, info); // Fehlermeldung auslesen
        fprintf(stderr, "FEHLER: Shader-Kompilierung (%s) fehlgeschlagen: %s\n",
                (type == GL_VERTEX_SHADER) ? "Vertex" : "Fragment", info);
        return 0;
    }
    return shader; // Gibt die ID des einsatzbereiten Shaders zurück
}

// Erstellt das finale Shader-Programm (verknüpft Vertex- und Fragment-Shader)
static unsigned int create_program(const char* vert_name, const char* frag_name) {
    // Holt den Quellcode für beide Shader aus dem Speicher
    const char* vsrc = get_shader_source(vert_name);
    const char* fsrc = get_shader_source(frag_name);

    // Sicherheitscheck: Wurde der Code überhaupt gefunden?
    if (!vsrc || !fsrc) {
        fprintf(stderr, "FEHLER: Shader '%s' oder '%s' nicht gefunden.\n", vert_name, frag_name);
        return 0;
    }

    // Kompiliert beide Shader einzeln
    unsigned int v = compile_shader(GL_VERTEX_SHADER, vsrc);
    unsigned int f = compile_shader(GL_FRAGMENT_SHADER, fsrc);

    // Erstellt ein leeres Programm-Objekt auf der Grafikkarte
    unsigned int prog = glCreateProgram();

    // Heftet die beiden kompilierten Shader an das Programm an
    glAttachShader(prog, v);
    glAttachShader(prog, f);

    // Linkt das Programm (verbindet die Ein- und Ausgänge der Shader miteinander)
    glLinkProgram(prog);

    // Prüfen, ob das Linking erfolgreich war
    int success;
    glGetProgramiv(prog, GL_LINK_STATUS, &success);
    if (!success) {
        char info[512];
        glGetProgramInfoLog(prog, sizeof(info), NULL, info);
        fprintf(stderr, "FEHLER: Shader-Linking fehlgeschlagen: %s\n", info);
        return 0;
    }

    // Nach dem Linken können die einzelnen Shader-Objekte gelöscht werden,
    // da sie nun fest im fertigen 'prog' verankert sind.
    glDeleteShader(v);
    glDeleteShader(f);

    return prog; // Gibt die ID des einsatzbereiten Shader-Programms zurück
}

// -------------------------------------------------------------
// main
// -------------------------------------------------------------
int main(void) {
    // Initialisiert die GLFW-Bibliothek
    if (!glfwInit()) {
        fprintf(stderr, "FEHLER: GLFW konnte nicht initialisiert werden.\n");
        return -1;
    }

    // Konfiguriert GLFW: Wir wollen OpenGL Version 3.3 nutzen
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    // Wir nutzen das Core-Profil (ohne veraltete, abwärtskompatible Funktionen)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    // Erstellt ein Fenster (800x600 Pixel) mit einem Titel
    GLFWwindow* window = glfwCreateWindow(800, 600, "OpenGL mit eingebetteten Shadern", NULL, NULL);
    if (!window) {
        fprintf(stderr, "FEHLER: Fenster konnte nicht erstellt werden.\n");
        glfwTerminate(); // Räumt GLFW auf, falls es schiefgeht
        return -1;
    }
    // Sagt OpenGL, dass alle folgenden Befehle in dieses Fenster zeichnen sollen
    glfwMakeContextCurrent(window);

    // GLAD initialisieren: Sucht die systemspezifischen Adressen der OpenGL-Befehle
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        fprintf(stderr, "FEHLER: GLAD konnte nicht geladen werden.\n");
        glfwTerminate();
        return -1;
    }

    // Ruft unsere Hilfsfunktion auf, um das Shader-Programm zu erstellen
    unsigned int shader_program = create_program("triangle.vert", "triangle.frag");
    if (!shader_program) {
        glfwTerminate();
        return -1;
    }

    // Die Eckpunkte (X, Y, Z Koordinaten) für ein einfaches 2D-Dreieck
    float vertices[] = {
        -0.5f, -0.5f, 0.0f,  // Unten links
         0.5f, -0.5f, 0.0f,  // Unten rechts
         0.0f,  0.5f, 0.0f   // Oben Mitte
    };

    unsigned int VAO, VBO;

    // Generiert ein Vertex Array Object (VAO). Es speichert, WIE die Daten interpretiert werden.
    glGenVertexArrays(1, &VAO);

    // Generiert ein Vertex Buffer Object (VBO). Das ist der eigentliche Speicher auf der GPU.
    glGenBuffers(1, &VBO);

    // Aktiviert (bindet) das VAO, damit alle folgenden Einstellungen hier drin gespeichert werden
    glBindVertexArray(VAO);

    // Aktiviert das VBO als aktuellen Puffer für Vertex-Daten
    glBindBuffer(GL_ARRAY_BUFFER, VBO);

    // Kopiert die CPU-Daten (das vertices-Array) in den GPU-Speicher (das VBO)
    // GL_STATIC_DRAW bedeutet: Die Daten ändern sich so gut wie nie.
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

    // Sagt OpenGL, wie die Rohdaten im VBO zu lesen sind:
    // Position 0, 3 Werte (X,Y,Z), vom Typ Float, nicht normalisiert,
    // Schrittweite im Array sind 3 * Float-Größe, Start-Offset ist 0.
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void*)0);

    // Aktiviert den Vertex-Attribut-Eintrag mit der ID 0 (die wir gerade definiert haben)
    glEnableVertexAttribArray(0);

    // Der Render-Loop (Hauptschleife): Läuft so lange, bis das Fenster geschlossen wird
    while (!glfwWindowShouldClose(window)) {
        // Setzt die Hintergrundfarbe (ein dunkles Blau-Grau)
        glClearColor(0.1f, 0.1f, 0.15f, 1.0f);

        // Löscht den Bildschirm und füllt ihn mit der oben definierten Hintergrundfarbe
        glClear(GL_COLOR_BUFFER_BIT);

        // Aktiviert das vorhin kompilierte Shader-Programm für die kommenden Zeichenbefehle
        glUseProgram(shader_program);

        // Bindet das VAO, welches der GPU sagt, wo die Dreiecksdaten liegen
        glBindVertexArray(VAO);

        // Zeichnet das Dreieck: Modus ist TRIANGLES, startet bei Vertex 0, zeichnet 3 Vertices
        glDrawArrays(GL_TRIANGLES, 0, 3);

        // Tauscht den unsichtbaren Hintergrundpuffer (auf dem gezeichnet wurde) mit dem sichtbaren Vordergrundpuffer
        glfwSwapBuffers(window);

        // Prüft, ob Events vorliegen (z.B. Tastaturdrücke, Fenster bewegen, Schließen-Kreuz geklickt)
        glfwPollEvents();
    }

    // Wenn die Schleife endet, wird aufgeräumt: Fenster zerstören...
    glfwDestroyWindow(window);

    // ...und GLFW komplett beenden und Ressourcen freigeben
    glfwTerminate();
    return 0; // Programm erfolgreich beendet
}
