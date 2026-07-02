// Sagt der Grafikkarte, dass wir GLSL Version 3.30 im "Core"-Profil nutzen
#version 330 core

// Definiert eine Ausgabe-Variable (ein 4D-Vektor für Rot, Grün, Blau, Alpha)
// OpenGL erwartet von einem Fragment-Shader, dass er hierüber die Pixelfarbe ausgibt
out vec4 FragColor;

// Die Hauptfunktion, die für jeden einzelnen Pixel des Dreiecks aufgerufen wird
void main() {
    // Setzt die Pixelfarbe (Rot = 80%, Grün = 20%, Blau = 60%, Alpha/Deckkraft = 100%)
    // Das ergibt einen schicken Magenta-/Pinkton.
    FragColor = vec4(0.8, 0.2, 0.6, 1.0);
}
