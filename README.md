fritzbox-smarthome
==================

Python-Bibliothek um FRITZ!Box SmartHome-Geräte (DECT 200, PowerLine 546E, ...) zu steuern und die Energiewerte auszulesen.

Getestet mit:

* FRITZ!Box 7390 (Firmware 06.03)
* FRITZ!DECT 200
* FRITZ!Powerline 546E

Installation
------------

```
virtualenv ~/fritzenv
source ~/fritzenv/bin/activate
pip install fritzhome
```

SmartHome-Benutzer
------------------

Aus Sicherheisgründen ist es empfehlenswert, einen eigenen Benutzer zum SmartHome-Zugriff zu verwenden. Dazu in der FRITZ!Box:

1. Die Benutzer-basierte Anmeldung aktivieren (unter "System" -> "FRITZ!Box Benutzer")
2. Und einen neuen Benutzer Benutzer "smarthome" erstellen. Dieser braucht nur Rechte auf den Bereich "Smart Home".


Verwendung
----------

Beispiele zur Verwendung der API befindet sich in der Datei __main__.py.

Nach der Installation steht das fritzhome Tool zur Verfügung, mit dem die Energiedaten auf der CLI angezeigt und nach Graphite exportiert werden können.

Befehle:

```
$ fritzhome [--server fritz.box] energy

PowerEingang (087600000000): 35.76 Watt current, 91.500 wH total
SmartHome Wohnzimmer (24:65:11:00:00:00): 56.21 Watt current, 1122.840 wH total
```

```
$ fritzhome [--server fritz.box] [switch-on|switch-off] 24:65:11:00:00:00
Switching SmartHome Wohnzimmer on
```

```
$ fritzhome [--server ip] graphite localhost [--port 2003] [--interval 10] [--prefix smarthome]
```
