# OpenGL Interpolated Triangle

Ein minimalistisches OpenGL 3.3 (Core Profile) C-Programm, das ein Dreieck mit sanften RGB-Farbverläufen auf den Bildschirm zeichnet. Dieses Projekt demonstriert den Einsatz von eingebetteten Shadern, VBOs, VAOs und erklärt die Magie der Hardware-Rasterisierung.

---

## Features & Architektur

* **Modern OpenGL (3.3 Core):** Keine veralteten Funktionen, sauberer Einsatz von modernen Pipeline-Strukturen.
* **Eingebettete Shader:** Vertex- und Fragment-Shader werden direkt aus dem Speicher geladen, statt externe Dateien einzulesen.
* **RGB-Interpolation:** Übergabe von Positions- und Farbdaten in einem einzigen Vertex-Buffer (Interleaved Data).

---

## 🛠️ Der Daten-Layout (C-Code)

Im C-Programm sind die Positionen ($X, Y, Z$) und die Farben ($R, G, B$) kompakt in einem einzigen Array hinterlegt. Ein sogenannter **Stride** (Schrittweite) von `6 * sizeof(float)` sagt OpenGL, wo die Daten des nächsten Eckpunkts beginnen.

```c
// Layout im Speicher: [X, Y, Z,  R, G, B]
float vertices[] = {
    -0.5f, -0.5f, 0.0f,    1.0f, 0.0f, 0.0f,  // Unten links (ROT)
     0.5f, -0.5f, 0.0f,    0.0f, 1.0f, 0.0f,  // Unten rechts (GRÜN)
     0.0f,  0.5f, 0.0f,    0.0f, 0.0f, 1.0f   // Oben Mitte (BLAU)
};

```

---

## Was passiert jetzt im Hintergrund?

Wenn die Grafikkarte das Dreieck zeichnet, laufen im Hintergrund hochoptimierte mathematische Prozesse ab:

### 1. Der Einschlusstest (Edge Functions)

Die Grafikkarte spannt Linien zwischen den drei vom Vertex-Shader berechneten Ecken auf. Für jedes Pixel auf dem Bildschirm wird ein mathematischer Test (meistens über das 2D-Kreuzprodukt) durchgeführt:

$$f(P) = \Delta x \cdot p_y - \Delta y \cdot p_x$$

* **$f(P) > 0$:** Der Pixel-Mittelpunkt liegt innerhalb der Kante.
* **$f(P) < 0$:** Der Pixel liegt außerhalb.

Nur wenn ein Pixel den Test für **alle drei Kanten** besteht, wird für ihn der Fragment-Shader gestartet.

### 2. Die automatische Interpolation

Das Geniale ist: Die Grafikkarte nutzt die Ergebnisse dieser Kantenfunktionen gleichzeitig, um die sogenannten **baryzentrischen Koordinaten** (die relative Gewichtung zu den drei Ecken) für jeden Pixel zu ermitteln.

> Ein Pixel, das genau in der Mitte zwischen der roten und der blauen Ecke liegt, erhält mathematisch exakt 50 % Rot und 50 % Blau. Das Ergebnis im Fragment-Shader ist an dieser Stelle automatisch ein perfektes Violett!

---

## Shader-Implementierung

### Vertex-Shader (`triangle.vert`)

Der Vertex-Shader nimmt Position und Farbe entgegen, transformiert die Position und reicht die Farbe an die Rasterisierungsstufe weiter.

```glsl
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

out vec3 ourColor;

void main() {
    gl_Position = vec4(aPos, 1.0);
    ourColor = aColor; // Wird für die Pixel-Ebene interpoliert!
}

```

### Fragment-Shader (`triangle.frag`)

Der Fragment-Shader empfängt die bereits perfekt interpolierte Farbe für den spezifischen Pixel und gibt sie aus.

```glsl
#version 330 core
out vec4 FragColor;
in vec3 ourColor; // Automatisch gemischter RGB-Wert

void main() {
    FragColor = vec4(ourColor, 1.0);
}

```

---

## Voraussetzungen & Kompilierung

Zum Bauen des Projekts werden folgende Bibliotheken benötigt:

* [GLFW3](https://www.glfw.org/) (Fenster- & Event-Management)
* [GLAD](https://glad.dav1d.de/) (OpenGL Multi-Language GL/GLES/WGL/GLX Puffer-Loader)
* [cglm](https://github.com/recp/cglm) (Optimierte 3D-Mathematik für C)

Kompiliert werden kann das Projekt mit jedem gängigen C-Compiler (z. B. GCC, Clang oder MSVC), sofern die Header und Bibliotheken im Suchpfad liegen.
