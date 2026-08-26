# Kozmetični Katalog

## Namen:

Namen projekta je ustvariti spletno aplikacijo za pregledovanje, iskanje, upravljanje in analiziranje kozmetičnih izdelkov. Aplikacija vsebuje obsežno zbirko izdelkov, pri katerih so shranjeni podatki o imenu izdelka, blagovni znamki, kategoriji, ceni, oceni, številu ocen, sestavinah in drugih lastnostih.

Uporabnik lahko izdelke išče, filtrira in razvršča ter si ogleda njihove podrobnosti. Registrirani uporabniki lahko izdelke dodajo med priljubljene in jih ocenijo s komentarjem. Aplikacija omogoča tudi dodajanje, urejanje in brisanje izdelkov ter statistično analizo celotne zbirke.

## Funkcionalnosti:

* **pregled vseh izdelkov:** uporabniku se prikaže seznam kozmetičnih izdelkov, shranjenih v podatkovni bazi
* **iskanje izdelkov:** izdelke je mogoče iskati po imenu, blagovni znamki ali kategoriji
* **filtriranje izdelkov:** uporabnik lahko izdelke filtrira glede na blagovno znamko, kategorijo, ceno in minimalno oceno
* **razvrščanje izdelkov:** izdelke je mogoče razvrstiti po imenu, ceni, oceni, priljubljenosti ali novosti
* **podroben ogled izdelka:** uporabnik lahko odpre posamezen izdelek in si ogleda njegove podrobnosti, kot so cena, ocena, sestavine in druge lastnosti
* **registracija uporabnika:** uporabnik lahko ustvari svoj račun
* **prijava in odjava:** registrirani uporabniki se lahko prijavijo in odjavijo iz aplikacije
* **priljubljeni izdelki:** uporabnik lahko izdelke doda med priljubljene in si jih pozneje ogleda na posebni strani
* **ocenjevanje izdelkov:** prijavljen uporabnik lahko izdelku dodeli oceno od 1 do 5 in napiše komentar
* **urejanje ocene:** uporabnik lahko svojo obstoječo oceno in komentar za izdelek spremeni
* **dodajanje izdelka:** prijavljen uporabnik lahko v podatkovno bazo doda nov kozmetični izdelek
* **urejanje izdelka:** uporabnik lahko spremeni podatke o obstoječem izdelku
* **brisanje izdelka:** uporabnik lahko izdelek odstrani iz podatkovne baze
* **pregled statistike:** aplikacija prikazuje osnovne statistične podatke o celotni zbirki izdelkov
* **analiza kategorij:** prikazuje število izdelkov v posameznih kategorijah
* **analiza blagovnih znamk:** prikazuje blagovne znamke z največ izdelki
* **analiza ocen:** prikazuje porazdelitev izdelkov glede na njihove ocene
* **analiza cen:** izdelke razvrsti v različne cenovne razrede
* **analiza akcijskih izdelkov:** prikaže število izdelkov na znižanju in povprečni odstotek popusta
* **statistični kazalniki:** aplikacija izračuna mediano cene, standardni odklon cen, mediano ocen in Pearsonov korelacijski koeficient med ceno in oceno
* **grafični prikaz podatkov:** statistični rezultati so prikazani tudi z različnimi grafi, kar omogoča lažje razumevanje podatkov

## Baza:

Baza je sestavljena iz štirih glavnih tabel.

### Tabela uporabnik

Tabela uporabnik vsebuje podatke o registriranih uporabnikih:

* `id` – primarni ključ
* `username` – uporabniško ime
* `password_hash` – varno shranjeno geslo
* `created_at` – datum in čas ustvarjanja računa

### Tabela izdelek

Tabela izdelek je glavna tabela aplikacije in vsebuje podatke o kozmetičnih izdelkih:

* `id` – primarni ključ
* `product_id` – identifikacijska oznaka izdelka
* `product_name` – ime izdelka
* `brand_name` – blagovna znamka
* `loves_count` – število uporabnikov, ki jim je izdelek všeč
* `rating` – povprečna ocena izdelka
* `reviews` – število ocen
* `size` – velikost izdelka
* `ingredients` – sestavine izdelka
* `price_usd` – osnovna cena
* `sale_price_usd` – cena izdelka na akciji
* `limited_edition` – oznaka omejene izdaje
* `new_product` – oznaka novega izdelka
* `online_only` – oznaka izdelka, ki je na voljo samo na spletu
* `out_of_stock` – oznaka, ali je izdelek trenutno razprodan
* `sephora_exclusive` – oznaka ekskluzivnega izdelka
* `primary_category` – glavna kategorija
* `secondary_category` – dodatna kategorija
* `tertiary_category` – podkategorija

### Tabela priljubljeni izdelki

Tabela `favorites` povezuje uporabnike z izdelki, ki so jih dodali med priljubljene:

* `user_id` – tuji ključ na tabelo uporabnikov
* `product_id` – tuji ključ na tabelo izdelkov
* `PRIMARY KEY(user_id, product_id)` – preprečuje, da bi isti uporabnik isti izdelek dodal večkrat

### Tabela ocene

Tabela `reviews` vsebuje ocene in komentarje uporabnikov:

* `id` – primarni ključ
* `user_id` – tuji ključ na tabelo uporabnikov
* `product_id` – tuji ključ na tabelo izdelkov
* `rating` – ocena od 1 do 5
* `comment` – komentar uporabnika
* `created_at` – datum in čas oddaje ocene

Uporabnik lahko za posamezen izdelek odda eno oceno. Če oceno ponovno odda, se obstoječa ocena posodobi.

## Analiza podatkov:

Aplikacija vsebuje posebno analitično stran, kjer so rezultati podatkovne zbirke predstavljeni s statističnimi kazalniki in grafi.

Prikazani so:

* število vseh izdelkov in blagovnih znamk
* povprečna cena izdelkov
* povprečna ocena izdelkov
* skupno število všečkov
* izdelki po kategorijah
* 10 blagovnih znamk z največ izdelki
* porazdelitev ocen
* izdelki po cenovnih razredih
* število izdelkov na akciji
* povprečni odstotek popusta
* mediana cene
* standardni odklon cene
* mediana ocene
* Pearsonova korelacija med ceno in oceno

Pearsonov korelacijski koeficient prikazuje moč linearne povezave med ceno in oceno izdelka. Vrednost koeficienta sama po sebi ne pomeni, da cena povzroča višjo ali nižjo oceno.

## ER diagram:

Uporabnik je v relaciji **1 : N** z ocenami, saj lahko en uporabnik oceni več izdelkov. Izdelek je prav tako v relaciji **1 : N** z ocenami, saj lahko posamezen izdelek prejme ocene več uporabnikov.

Tabela `favorites` predstavlja povezovalno tabelo med uporabniki in izdelki. En uporabnik lahko ima več priljubljenih izdelkov, posamezen izdelek pa je lahko med priljubljenimi pri več uporabnikih.

## Zagon:

1. Odpri mapo projekta `MAKEUP_APP_BAZE`.
2. Preveri, ali je podatkovna baza `sephora.db` pravilno ustvarjena oziroma zaženi skripto za pripravo baze.
3. Zaženi glavno aplikacijo.
4. Odpri aplikacijo v spletnem brskalniku na lokalnem naslovu, ki ga izpiše program.
5. Za uporabo funkcij, kot so priljubljeni izdelki, ocenjevanje ter dodajanje, urejanje in brisanje izdelkov, se mora uporabnik najprej registrirati in prijaviti.
korelacijski koeficient med ceno in oceno
* **grafični prikaz podatkov:** rezultati analize so prikazani tudi z različnimi grafi za lažje razumevanje podatkov

## Avtorja:
Pia Tominec, Ivona Zikova
