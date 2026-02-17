SELECT i.ID,
       i.Naziv,
       i.Cena,
       i.Valuta,
       b.Naziv AS Znamka,
       k.Naziv AS Kategorija,
       t.Naziv AS Tip
FROM Izdelki i
JOIN Blagovne_Znamke b ON i.Znamka_ID = b.ID
JOIN Kategorije k ON i.Kategorija_ID = k.ID
JOIN Tipi_Izdelkov t ON i.TipIzdelka_ID = t.ID;
