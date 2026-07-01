# dreieck

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
