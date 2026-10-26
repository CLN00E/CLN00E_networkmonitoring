SZKRIPT NYELVEK – PYTHON
PROJEKTFELADAT

Hallgató: Honfi Levente - CLN00E
Projekt neve: Network & Service Monitor
Fejlesztőkörnyezet: PyCharm
Programozási nyelv: Python 3

1. A FELADAT LEÍRÁSA

A Network & Service Monitor egy Python nyelven készített, grafikus felülettel rendelkező hálózat- és szolgáltatásfigyelő alkalmazás. A program nyilvánosan elérhető weboldalak, illetve hálózati címek elérhetőségét ellenőrzi, és megjeleníti a mérési eredményeket.

Az alapértelmezett ellenőrzési célpontok:
- Google (HTTPS)
- Gmail (HTTPS)
- Cloudflare DNS – 1.1.1.1 (PING)
- Wikipédia (HTTPS)

A felhasználó további szolgáltatásokat is felvehet név, cím és ellenőrzési módszer megadásával.

2. A PROGRAM FUNKCIÓI

- Kézi elérhetőség-ellenőrzés gombnyomással.
- Automatikus ellenőrzés 10 másodpercenként, ki- és bekapcsolható módon.
- HTTPS- és PING-alapú ellenőrzés.
- ONLINE/OFFLINE állapot, válaszidő és utolsó mérési időpont megjelenítése.
- Új weboldal vagy hálózati cím hozzáadása a futó programhoz.
- A mérési eredmények mentése CSV-fájlba.
- A mentett válaszidők grafikus megjelenítése.
- A hálózati ellenőrzések külön szálon történő futtatása, hogy a grafikus felület használható maradjon.

A webes ellenőrzés a HTTP(S)-végpont elérhetőségét vizsgálja; önmagában nem igazolja egy teljes online szolgáltatás, például a Gmail levélküldésének hibátlan működését. A PING-ellenőrzés a célpont ICMP-válaszát vizsgálja.

3. A PROGRAM FELÉPÍTÉSE

main.py         – a grafikus felület és az eseménykezelés; a program belépési pontja.
h1_monitor.py   – a hálózati ellenőrzések és az eredményképzés saját modulja.
h1_logger.py    – a mérési eredmények CSV-fájlba mentésének saját modulja.
data/measurements.csv – a program által létrehozott mérési napló.

A grafikus program főablaka: root
A grafikus program fő kerete: app

4. FELHASZNÁLT MODULOK ÉS FÜGGVÉNYEK

4.1. A Python szabványos könyvtárának moduljai

- tkinter, tkinter.ttk: grafikus ablak, táblázat, gombok, jelölőnégyzet és adatbeviteli ablak; például Tk(), Toplevel(), Treeview(), Button(), Checkbutton().
- datetime: az ellenőrzések időbélyegének előállítása; datetime.now(), strftime().
- csv: CSV-napló írása és olvasása; csv.writer(), csv.DictReader().
- pathlib: fájlok és mappák elérési útjainak kezelése; Path(), mkdir(), exists().
- threading: hálózati mérések végrehajtása külön szálon; Thread(), start().
- queue: az ellenőrzések eredményének átadása a grafikus felületnek; Queue(), put(), get_nowait().
- subprocess: a rendszer ping parancsának futtatása; run().
- time: a válaszidő mérése; perf_counter().
- os: operációs rendszer felismerése a ping paraméterezéséhez; os.name.
- dataclasses: az osztály adatmezőinek definiálása; dataclass.

4.2. Külső, telepítendő modulok

- requests: webes HTTPS-ellenőrzések; requests.head(), requests.get(), requests.utils.requote_uri().
- matplotlib.pyplot: a válaszidőgrafikon készítése. A bemutatandó modul három kiemelt függvénye:
  1. plot() – válaszidőmérések vonaldiagramjának kirajzolása.
  2. grid() – a diagram rácsvonalainak bekapcsolása.
  3. legend() – a szolgáltatások jelmagyarázatának megjelenítése.
  További használt függvények: figure(), title(), xlabel(), ylabel(), tight_layout(), show().

4.3. Saját modulok

- h1_monitor.py: az egyes szolgáltatások ellenőrzése és az egységes mérési eredmény létrehozása.
- h1_logger.py: az eredmények CSV-naplóba írása.

5. SAJÁT OSZTÁLY ÉS FÜGGVÉNYEK

Saját osztály:
- HLServiceMonitor: egy szolgáltatás nevét, címét és ellenőrzési módját tárolja; a check(), check_https() és check_ping() metódusokkal végzi az ellenőrzést.

Saját függvények:
- hl_create_result(): egységes szerkezetű eredményt készít az ellenőrzés állapotából, válaszidejéből és időpontjából.
- hl_save_measurement(): az eredményt CSV-fájlba menti.

A saját modulok, osztály és függvények nevében a HL monogram szerepel.

A main.py további függvényei:
- update_table(): frissíti a táblázatot a kapott eredménnyel.
- run_checks(): végigellenőrzi a szolgáltatásokat.
- start_check(): külön szálon elindítja az ellenőrzést.
- automatic_check(): időzítve új ellenőrzést kezdeményez.
- process_results(): átveszi és megjeleníti az eredményeket, valamint elindítja a naplózást.
- show_chart(): a CSV-ben tárolt válaszidőkből grafikont készít.
- add_service(): adatbeviteli ablakot nyit új szolgáltatás hozzáadásához.

6. ESEMÉNYKEZELÉS

Az „Ellenőrzés indítása” gomb elindítja a mérést. Az automatikus ellenőrzés jelölőnégyzetével a rendszeres mérés bekapcsolható vagy kikapcsolható. A grafikon gomb megjeleníti az elmentett adatokat, az új szolgáltatás hozzáadására szolgáló gomb pedig adatbeviteli ablakot nyit. Az időzítéshez a Tkinter after() metódusát használja a program.

7. TELEPÍTÉS ÉS FUTTATÁS

1. Nyissa meg a projektet PyCharmban, és állítson be egy Python 3 virtuális környezetet.
2. Telepítse a szükséges külső csomagokat:

   python -m pip install requests matplotlib

3. Futtassa a main.py fájlt.
4. Az alkalmazásban az „Ellenőrzés indítása” gombbal mérhet, vagy bekapcsolhatja az automatikus ellenőrzést.
5. A mentett mérések a data/measurements.csv állományba kerülnek; a grafikon gombbal jeleníthetők meg.

A működéshez internetkapcsolat szükséges. A PING teszt eredményét a hálózat vagy a tűzfal ICMP-szűrése is befolyásolhatja.

8. MEGJEGYZÉSEK

- Az alkalmazás az elérhetőség ellenőrzésére készült, nem egy teljes körű szolgáltatásállapot- vagy hibadiagnosztikai rendszer.
- Az újonnan hozzáadott szolgáltatások a jelenlegi változatban csak a program futása alatt maradnak a listában.
- A grafikon a naplózott válaszidőket mutatja; a sikertelen, válaszidő nélküli méréseket nem rajzolja fel.
- A GitHub-repozitórium hivatkozását a beadási felületen kell megadni vagy csatolni az oktató előírása szerint.
