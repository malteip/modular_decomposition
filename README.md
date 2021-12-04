# **MODULARE ZERLEGUNG**

##### Python3-Programm zur Bachelorarbeit *Die Berechnung der modularen Zerlegung eines ungerichteten Graphen in linearer Zeit entsprechend dem Algorithmus von Tedder et al.* von Malte Quiter.

## Verzeichnisübersicht
| Datei                 | Funktion                                                          |
|-----------------------|-------------------------------------------------------------------|
| `md.py`               | Implementiert den Algorithmus sowie die nötigen Datenstrukturen.  |
| `tui.py`              | Implementiert eine textbasierte Benutzeroberfläche.               |
| `dot.py`              | Implementiert I/O-Funktionen für die Nutzung von DOT-Dateien.     |
| `graph_generators.py` | Implementiert Funktionen zum Erzeugen von Graphen.                |
| `test.py`             | Implementiert Funktionen zum Testen der Laufzeit.                 |
| `plot.py`             | Implementiert Funktionen zur Darstellung der Testergebnisse.      |
| `small_graphs_dot`    | Dieses Verzeichnis enthält DOT-Dateien zu einigen Graphen.        |
| `graphs`, `md_trees`  | Verzeichnisse für erzeugte Graphen und Zerlegungsbäume (DOT/PDF). |
| `test_data`           | Dieses Verzeichnis enthält die Testdaten zu den Experimenten.     |

## Installation
Um das Programm über die Benutzeroberfläche nutzen zu können, werden die Python Module `graphviz` [https://graphviz.readthedocs.io/] und `npyscreen` [https://npyscreen.readthedocs.io/] benötigt.

Auf einem Mac kann `graphviz` über Homebrew [https://brew.sh/] installiert werden:
```sh
brew install graphviz
```
Auf einem Linux Computer mit Ubuntu kann `graphviz` über apt-get installiert werden:
```sh
sudo apt-get install graphviz
```
Das Modul `npyscreen` lässt in beiden Fällen über pip3 installieren:
```sh
pip3 install npyscreen
```

## DOT (.dot)
Für die Darstellung von Graphen/Zerlegungsbäumen, d.h. für die Ein-/Ausgabe, wird die Beschreibungssprache DOT mit der Dateiendung `.dot` verwendet. Hierbei werden nur essentielle Funktionen durch das Programm unterstützt. Die Verwendung von Semikolons ist verpflichtend. Beispiel:
```
graph {
    a--b;
    b--c--d--b;
    d--e;
}
```

## Verwendung
Das Programm lässt sich aus dem Verzeichnis über den folgenden Befehl starten:
```sh
python3 tui.py
```
**Weitere Hinweise:**
- Zur Navigation werden die Pfeiltasten, die Tab-Taste und die Enter-Taste verwendet.
- Im Fall großer Graphen ist es empfehlenswert die Option `No rendering` unter dem Menüpunkt `Settings` auszuwählen, da das Generieren großer PDF-Dateien sehr lange dauert.
- Unter dem Menüpunkt `Editor` können Graphen ohne das Konstrukt `graph{...} ` eingegeben werden.
