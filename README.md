# Beauté – Kozmeticni Katalog

## Opis projekta

Beauté je spletna aplikacija za pregledovanje in analizo podatkovne zbirke kozmetičnih izdelkov Sephora.

Aplikacija vsebuje spletni vmesnik in tekstovni vmesnik (CLI). Uporabniki lahko iščejo in filtrirajo izdelke, si ogledajo podrobnosti izdelkov, shranjujejo priljubljene izdelke, dodajajo ocene in komentarje ter uporabljajo osnovne analize podatkov.

Aplikacija uporablja podatkovno bazo SQLite za shranjevanje podatkov o izdelkih in uporabnikih.

---

## Funkcionalnosti

### Spletni vmesnik

Spletna aplikacija omogoča:

- pregled kozmetičnih izdelkov;
- iskanje izdelkov;
- filtriranje izdelkov;
- razvrščanje izdelkov;
- pregled podrobnosti posameznega izdelka;
- registracijo uporabnikov;
- prijavo in odjavo;
- dodajanje izdelkov med priljubljene;
- odstranjevanje izdelkov iz priljubljenih;
- pregled priljubljenih izdelkov;
- dodajanje ocen in komentarjev;
- urejanje lastnih ocen in komentarjev;
- pregled analiz podatkov;
- dodajanje novih izdelkov;
- urejanje izdelkov;
- brisanje izdelkov.

Dodajanje, urejanje in brisanje izdelkov je omogočeno samo uporabnikom z administratorskimi pravicami.

### Tekstovni vmesnik

Projekt vsebuje tudi tekstovni vmesnik, implementiran v datoteki `cli.py`.

Glavni meni vsebuje:

```text
=== BEAUTÉ TEXT INTERFACE ===
1. Search/list products
2. Product details
3. Analytics
4. Login
5. Show favorites
6. Add/remove favorite
0. Exit
```

Tekstovni vmesnik omogoča osnovno pregledovanje izdelkov, pregled podrobnosti izdelkov, prijavo, delo s priljubljenimi izdelki in osnovno analitiko.

Analitika v tekstovnem vmesniku vključuje:

- število izdelkov;
- število blagovnih znamk;
- povprečno ceno izdelkov;
- povprečno oceno izdelkov.

Registracija uporabnika v tekstovnem vmesniku ni implementirana.

---

## Analiza podatkov

Spletna aplikacija vsebuje stran za analizo podatkov o izdelkih.

Analize vključujejo:

- porazdelitev izdelkov po kategorijah;
- porazdelitev izdelkov po blagovnih znamkah;
- analizo ocen izdelkov;
- analizo cen izdelkov;
- primerjavo rednih in znižanih cen;
- osnovne statistične kazalnike.

---

## Podatkovna baza

Projekt uporablja podatkovno bazo SQLite:

```text
sephora.db
```

Podatkovna baza vsebuje naslednje glavne tabele:

### Users

Tabela vsebuje podatke o registriranih uporabnikih.

Glavna polja so:

- `id`
- `username`
- `password`
- `role`

Uporabniški vlogi sta:

- `user`
- `admin`

### Products

Tabela vsebuje podatke o kozmetičnih izdelkih iz izvorne zbirke Sephora.

Med pomembnejšimi polji so:

- `id`
- `brand_name`
- `product_name`
- `category`
- `price_usd`
- `sale_price_usd`
- `value_price_usd`
- `rating`
- `reviews`
- `loves_count`
- `ingredients`
- `highlights`

ter drugi podatki iz izvorne podatkovne zbirke.

### Favorites

Tabela `favorites` povezuje uporabnike z izdelki, ki so jih uporabniki dodali med priljubljene.

### Reviews

Tabela `reviews` vsebuje ocene in komentarje uporabnikov.

Vsaka ocena je povezana z:

- uporabnikom;
- izdelkom;
- oceno;
- komentarjem;
- datumom ustvarjanja.

---

### Cene

Podatkovna zbirka vsebuje več polj, povezanih s cenami:

- `price_usd` – redna oziroma osnovna cena;
- `value_price_usd` – referenčna oziroma vrednostna cena, kadar je podana v izvorni zbirki;
- `sale_price_usd` – znižana cena, kadar je podana v izvorni zbirki.

Če je znižana cena na voljo, jo aplikacija uporabi za prikaz znižane cene; sicer uporabi redno ceno.

### Blagovne znamke in kategorije

Imena blagovnih znamk in kategorij so shranjena neposredno v tabeli `products`.

Uporabljajo se pri iskanju, filtriranju, združevanju in analizi podatkov.

---

## Uporabniške vloge

Aplikacija uporablja dve uporabniški vlogi.

### User

Navaden uporabnik lahko:

- pregleduje izdelke;
- išče in filtrira izdelke;
- pregleduje podrobnosti izdelkov;
- dodaja in odstranjuje priljubljene izdelke;
- pregleduje svoje priljubljene izdelke;
- dodaja in ureja svoje ocene in komentarje.

### Administrator

Administrator ima vse možnosti navadnega uporabnika in lahko dodatno:

- dodaja izdelke;
- ureja izdelke;
- briše izdelke.

Na ta način navadni registrirani uporabniki ne morejo spreminjati podatkov o izdelkih.

---

## Namestitev

Potrebni zunanji paket namestimo z ukazom:

```bash
python -m pip install -r requirements.txt
```
Projekt uporablja paket Flask.
---

## Zagon projekta od začetka

Osnovni vrstni red ukazov za namestitev in zagon projekta je:

```bash
python -m pip install -r requirements.txt
python seed_database.py
python create_admin.py
python app_1.py
```

Tekstovni vmesnik lahko zaženemo ločeno z:

```bash
python cli.py
```
---

## Avtorja

**Pia Tominec**

**Ivona Zikova**
