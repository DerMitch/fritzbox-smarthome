fritzbox-smarthome
==================

**(DE) Bitte beachten**: Diese Bibliothek wird nicht aktiv vom Autor weiterentwickelt, Pull Requests werden jedoch geprüft und eingepflegt.

**(EN) Please note:** This library is not in active development by the author, yet pull requests are reviewed and merged.

Python-Bibliothek um FRITZ!Box SmartHome-Geräte (DECT 200, PowerLine 546E, ...) zu steuern und die Energiewerte auszulesen.

Getestet mit:

* FRITZ!Box 7390 (Firmware 06.23, 06.50+)
* FRITZ!DECT 200
* FRITZ!Powerline 546E

Installation
------------

Es ist empfehlenswert, ein eigenes virtualenv zur Verwendung anzulegen. Unter macOS kann dieses Tool vorher mit `brew install virtualenv` installiert werden, unter Linux-Systemen hängt dies von der Distribution ab. Windows wird nicht offiziell unterstützt.

```
virtualenv ~/fritzenv
. ~/fritzenv/bin/activate
git clone https://github.com/DerMitch/fritzbox-smarthome.git
cd fritzbox-smarthome
pip install .
```

**Hinweis:** Das PyPi-Paket `fritzhome` wird nur selten aktualisiert, daher ist die Verwendung des git-Masters zu bevorzugen.

SmartHome-Benutzer
------------------

Aus Sicherheisgründen ist es empfehlenswert, einen eigenen Benutzer zum SmartHome-Zugriff zu verwenden. Dazu in der FRITZ!Box:

1. Die Benutzer-basierte Anmeldung aktivieren (unter "System" -> "FRITZ!Box Benutzer")
2. Und einen neuen Benutzer Benutzer "smarthome" erstellen. Dieser braucht nur Rechte auf den Bereich "Smart Home".


Verwendung
----------

Beispiele zur Verwendung der API befindet sich in der Datei `__main__.py`.

Nach der Installation steht das `fritzhome` Tool zur Verfügung, mit dem die Energiedaten auf der CLI angezeigt und nach Graphite exportiert werden können.

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

Aufruf außerhalb des virtualenv
-------------------------------

Das `fritzhome` kann mit Hilfe seines absoluten Pfades innerhalb des virtualenv ausgeführt werden:

```
~/fritzenv/bin/fritzhome --help
```

Referenzen
----------

* [AHA-HTTP-Interface](https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/AHA-HTTP-Interface.pdf)
* [PHP AHA Reader](http://www.tdressler.net/ipsymcon/download/fritz_aha_reader2.phps)
