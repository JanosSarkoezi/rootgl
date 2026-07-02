#version 330 core
layout (location = 0) in vec3 aPos;   // Position kommt bei Location 0 rein
layout (location = 1) in vec3 aColor; // Farbe kommt bei Location 1 rein (NEU)

out vec3 ourColor; // Ausgangsvariable, die an den Fragment-Shader geschickt wird (NEU)

void main() {
    gl_Position = vec4(aPos, 1.0); // Nutzt die kompakte Schreibweise, die wir besprochen haben!
    ourColor = aColor;             // Reicht die Eckpunkt-Farbe einfach weiter
}
