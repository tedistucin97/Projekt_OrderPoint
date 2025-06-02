from pony.orm import Database, Required, Set
from datetime import datetime

db = Database()

class Artikl(db.Entity):
    naziv = Required(str)
    cijena = Required(float)
    kategorija = Required(str)

class Narudzba(db.Entity):
    redni_broj = Required(int, unique=True)
    broj_stola = Required(str)
    vrijeme_narudzbe = Required(datetime, default=datetime.now)
    naplacena = Required(bool, default=False)
    stornirana = Required(bool, default=False)
    stavke = Set("Stavka")

class Stavka(db.Entity):
    narudzba = Required(Narudzba)
    kolicina = Required(int)
    naziv_artikla = Required(str)
    cijena_artikla = Required(float)

class Stol(db.Entity):
    broj = Required(str, unique=True)
