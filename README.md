# Kozmetični Katalog

Spletna in tekstovna aplikacija za pregledovanje, iskanje, filtriranje in analiziranje kozmetičnih izdelkov.

## Namen

Namen projekta je ustvariti spletno aplikacijo za delo s podatki o kozmetičnih izdelkih. Aplikacija uporablja podatkovno bazo SQLite, v kateri so shranjeni podatki o izdelkih, uporabnikih, priljubljenih izdelkih in uporabniških ocenah.

Uporabnik lahko izdelke išče, filtrira in razvršča ter si ogleda njihove podrobnosti. Registrirani uporabniki lahko izdelke dodajo med priljubljene in oddajo oceno s komentarjem. Administratorji lahko poleg tega dodajajo, urejajo in brišejo izdelke.

Aplikacija vsebuje tudi analitično stran, kjer so podatki o izdelkih predstavljeni s statističnimi kazalniki in grafi.

Poleg spletnega vmesnika aplikacija vsebuje tudi tekstovni vmesnik, ki omogoča uporabo izbranih funkcionalnosti aplikacije brez spletnega brskalnika.

## Funkcionalnosti

### Spletni vmesnik

- **pregled izdelkov:** uporabniku se prikaže seznam kozmetičnih izdelkov, shranjenih v podatkovni bazi
- **iskanje izdelkov:** izdelke je mogoče iskati po imenu, blagovni znamki ali kategoriji
- **filtriranje izdelkov:** uporabnik lahko izdelke filtrira glede na blagovno znamko, kategorijo, ceno in minimalno oceno
- **razvrščanje izdelkov:** izdelke je mogoče razvrstiti po imenu, ceni, oceni, priljubljenosti ali novosti
- **podroben ogled izdelka:** uporabnik lahko odpre posamezen izdelek in si ogleda njegove podrobnosti
- **registracija uporabnika:** uporabnik lahko ustvari svoj račun
- **prijava in odjava:** registrirani uporabniki se lahko prijavijo in odjavijo iz aplikacije
- **priljubljeni izdelki:** prijavljen uporabnik lahko izdelke doda med priljubljene in jih pozneje pregleda na posebni strani
- **ocenjevanje izdelkov:** prijavljen uporabnik lahko izdelku dodeli oceno od 1 do 5 in napiše komentar
- **urejanje ocene:** uporabnik lahko svojo obstoječo oceno in komentar spremeni
- **upravljanje izdelkov:** administrator lahko doda, uredi ali izbriše izdelek
- **analitika:** aplikacija prikazuje osnovne statistične podatke in grafe o zbirki izdelkov

### Tekstovni vmesnik

Tekstovni vmesnik je implementiran v datoteki `cli.py`.

Omogoča naslednje funkcionalnosti:

- pregled izdelkov,
- iskanje izdelkov,
- pregled podrobnosti izdelka,
- prikaz osnovnih statističnih podatkov,
- prijavo uporabnika,
- pregled priljubljenih izdelkov,
- dodajanje in odstranjevanje izdelkov med priljubljenimi.

Registracija v tekstovnem vmesniku ni implementirana.

## Baza

Podatkovna baza je implementirana v SQLite in vsebuje štiri glavne tabele:

- `users`
- `products`
- `favorites`
- `reviews`

### Tabela `users`

Tabela `users` vsebuje podatke o registriranih uporabnikih:

- `id` – primarni ključ
- `username` – uporabniško ime
- `password_hash` – varno shranjeno geslo
- `role` – uporabniška vloga (`user` ali `admin`)
- `created_at` – datum in čas ustvarjanja računa

Ob registraciji se uporabniku samodejno dodeli vloga `user`.

Administrator ima dodatne pravice za upravljanje izdelkov.

### Tabela `products`

Tabela `products` je glavna tabela aplikacije in vsebuje podatke o kozmetičnih izdelkih:

- `id` – primarni ključ
- `product_id` – identifikacijska oznaka izdelka iz izvornega nabora podatkov
- `product_name` – ime izdelka
- `brand_name` – blagovna znamka
- `loves_count` – število všečkov iz izvornega nabora podatkov
- `rating` – povprečna ocena izdelka iz izvornega nabora podatkov
- `reviews` – število ocen iz izvornega nabora podatkov
- `size` – velikost izdelka
- `ingredients` – sestavine izdelka
- `price_usd` – osnovna cena
- `value_price_usd` – referenčna oziroma vrednostna cena, če je podana v izvornem naboru
- `sale_price_usd` – akcijska cena, če je podana
- `limited_edition` – oznaka omejene izdaje
- `new_product` – oznaka novega izdelka
- `online_only` – oznaka izdelka, ki je na voljo samo na spletu
- `out_of_stock` – oznaka, ali je izdelek trenutno razprodan
- `sephora_exclusive` – oznaka ekskluzivnega izdelka
- `primary_category` – glavna kategorija
- `secondary_category` – dodatna kategorija
- `tertiary_category` – podkategorija

### Tabela `favorites`

Tabela `favorites` predstavlja povezovalno tabelo med uporabniki in izdelki, ki so jih uporabniki dodali med priljubljene.

Vsebuje:

- `user_id` – tuji ključ na tabelo `users`
- `product_id` – tuji ključ na tabelo `products`

Primarni ključ je sestavljen iz para:

`PRIMARY KEY(user_id, product_id)`

S tem preprečimo, da bi isti uporabnik isti izdelek dodal med priljubljene večkrat.

Relacije so:

`users 1 : N favorites`

`products 1 : N favorites`

En uporabnik ima lahko več priljubljenih izdelkov, posamezen izdelek pa je lahko med priljubljenimi pri več uporabnikih.

### Tabela `reviews`

Tabela `reviews` vsebuje ocene in komentarje uporabnikov:

- `id` – primarni ključ
- `user_id` – tuji ključ na tabelo `users`
- `product_id` – tuji ključ na tabelo `products`
- `rating` – ocena od 1 do 5
- `comment` – komentar uporabnika
- `created_at` – datum in čas oddaje ocene

Relacije so:

`users 1 : N reviews`

`products 1 : N reviews`

En uporabnik lahko odda več ocen za različne izdelke, posamezen izdelek pa lahko prejme ocene več uporabnikov.

Vsak uporabnik lahko za posamezen izdelek odda eno oceno. Če uporabnik oceno ponovno odda, se obstoječa ocena posodobi.


## Uporabniške vloge

Aplikacija ima dve uporabniški vlogi.

### Navaden uporabnik

Navaden uporabnik lahko:

- pregleduje izdelke,
- išče in filtrira izdelke,
- dodaja izdelke med priljubljene,
- pregleduje svoje priljubljene izdelke,
- oddaja ocene in komentarje,
- ureja svoje ocene.

### Administrator

Administrator ima vse pravice navadnega uporabnika in lahko dodatno:

- dodaja izdelke,
- ureja izdelke,
- briše izdelke.

## Analiza podatkov

Aplikacija vsebuje posebno analitično stran, kjer so rezultati podatkovne zbirke predstavljeni s statističnimi kazalniki in grafi.

Prikazani so:

- število vseh izdelkov,
- število blagovnih znamk,
- povprečna cena izdelkov,
- povprečna ocena izdelkov,
- skupno število všečkov,
- izdelki po kategorijah,
- blagovne znamke z največ izdelki,
- porazdelitev izdelkov glede na ocene,
- izdelki po cenovnih razredih,
- število izdelkov na akciji,
- povprečni odstotek popusta,
- mediana cene,
- standardni odklon cene,
- mediana ocene,
- Pearsonov korelacijski koeficient med ceno in oceno.

Pearsonov korelacijski koeficient prikazuje moč linearne povezave med ceno in oceno. Vrednost koeficienta sama po sebi ne pomeni, da cena povzroča višjo ali nižjo oceno.

## Zagon

### 1. Namestitev potrebnih paketov

V mapi projekta zaženemo:

```bash
python -m pip install -r requirements.txt
