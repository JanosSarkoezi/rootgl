#version 330 core
out vec4 FragColor;

in vec3 ourColor; // Eingangsvariable, die vom Vertex-Shader gefüttert wird (NEU)

void main() {
    // Nutzt die übergebene (und von der Hardware automatisch interpolierte) Farbe.
    // Wir hängen hinten eine 1.0 für die volle Deckkraft (Alpha) an.
    FragColor = vec4(ourColor, 1.0);
}
