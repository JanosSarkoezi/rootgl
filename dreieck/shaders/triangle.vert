// Sagt der Grafikkarte, dass wir GLSL Version 3.30 im "Core"-Profil nutzen
#version 330 core

// Ein-/Ausgänge des Shaders:
// 'layout (location = 0)' verknüpft diese Variable direkt mit der ID 0 aus unserem
// C-Programm (wo wir 'glVertexAttribPointer(0, ...)' aufgerufen haben).
// 'in vec3 aPos' bedeutet: Hier fliegt pro Vertex ein 3D-Vektor (X, Y, Z) rein.
layout (location = 0) in vec3 aPos;

void main() {
    // 'gl_Position' ist eine vordefinierte, eingebaute OpenGL-Variable.
    // Der Vertex-Shader MUSS dieser Variable die finale Position im 4D-Raum (Clip Space) zuweisen.
    // Da unsere Daten als 'vec3' (3 Werte) vorliegen, erweitern wir sie mit 'vec4(..., 1.0)' um die
    // sogenannte homogene Koordinate (W = 1.0), die für die Matrix-Mathematik in OpenGL wichtig ist.
    gl_Position = vec4(aPos, 1.0);
}
