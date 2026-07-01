# OpenGL‑Meson‑Bootstrapper

Dieses Skript erstellt ein **sofort lauffähiges Grundgerüst** für ein OpenGL‑Projekt in C mit **Meson** als Build‑System.
Es erzeugt eine vollständige Projektstruktur, inklusive Shader‑Einbettung, Wrap‑Dateien für GLFW und cglm sowie einer Beispiel‑Anwendung.

---

## Voraussetzungen

Stelle sicher, dass folgende Werkzeuge auf deinem System installiert sind:

- **Python 3** (für die Shader‑Einbettung und das Skript selbst)
- **Meson** (Build‑System) – Installation z.B. via `pip install meson` oder Paketmanager
- **Ninja** (Build‑Executor) – `apt install ninja-build` / `brew install ninja` / …
- **Git** (zum Herunterladen von Abhängigkeiten via Wrap‑Dateien)

---

## Verwendung

1. **Lade das Skript herunter** und speichere es als `bootscript.py`.

2. **Führe es aus** und übergib den gewünschten Projektnamen:

   ```bash
   python3 bootscript.py MeinNeuesProjekt
   ```
