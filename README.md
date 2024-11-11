# WS_Uebung_A1
Non Customizeable Single Producer - Multi Consumer

# WebSocket Server und Client (C++ und Python)

Dieses Projekt besteht aus einem WebSocket-Server, der in C++ mit der **Crow**-Bibliothek geschrieben wurde, und einem WebSocket-Client, der in Python mit **tkinter**, **websocket-client** und **matplotlib** entwickelt wurde. Der Client zeigt Echtzeit-Daten an, die vom Server gesendet werden.

## Projektstruktur

- `client.py`: Python WebSocket-Client, der Daten vom Server empfängt und visualisiert.
- `server.cpp`: C++ WebSocket-Server, der simulierte Daten an alle verbundenen Clients sendet.
- `Crow`: Eine C++ WebSocket-Bibliothek, die im Serverprojekt verwendet wird.
- `CMakeLists.txt`: Build-Datei für das C++-Projekt.
- `README.md`: Diese Datei, die Informationen zum Setup und der Nutzung des Projekts enthält.

## Voraussetzungen

### Für den C++ WebSocket-Server:

1. **Crow**-Bibliothek:
   - Du musst die Crow-Bibliothek installieren, um den Server zu bauen.
   - Weitere Informationen findest du hier: [Crow GitHub Repository](https://github.com/CrowCpp/Crow)

2. **CMake**:
   - Zum Erstellen des C++-Projekts benötigst du CMake. Installiere es mit:

     sudo apt install cmake

### Für den Python WebSocket-Client:

1. **Python 3**:
   - Stelle sicher, dass Python 3 auf deinem System installiert ist.

2. **Python Abhängigkeiten**:
   - Du solltest eine virtuelle Python-Umgebung (venv) erstellen, um die Abhängigkeiten zu installieren:

     python3 -m venv ~/venv
     source ~/venv/bin/activate  # Aktiviert die virtuelle Umgebung
     pip install websocket-client matplotlib

## Kompilieren und Ausführen

### C++ WebSocket-Server (server.cpp)

1. **CMake-Build-Prozess**:

   - Erstelle ein Verzeichnis `build` im Projektordner:

     mkdir build
     cd build

   - Generiere die Makefiles und baue das Projekt:

     cmake ..
     make

   - Der Server wird jetzt erstellt und kann mit folgendem Befehl gestartet werden:

     ./server
    

2. Der C++-Server wird auf Port 8765 laufen und Nachrichten an verbundene Clients senden.

### Python WebSocket-Client (client.py)

1. **Starten des Python-Clients**:

   - Stelle sicher, dass der C++-Server läuft.
   - Aktiviere die Python-virtuelle Umgebung:

     source ~/venv/bin/activate

   - Führe das Python-Skript aus, um den Client zu starten:

     python client.py

   - Du kannst die WebSocket-URI in der `client.py`-Datei anpassen, falls der Server auf einem anderen Host läuft.

### Funktionen des Clients:

- **Start/Stop**: Startet oder stoppt die Verbindung zum Server.
- **Letzte 100 Daten anzeigen**: Zeigt die letzten 100 empfangenen Datenpunkte in einem separaten Fenster an.
- **Letzter Datenpunkt**: Zeigt den letzten empfangenen Datenpunkt auf dem Hauptbildschirm an.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

