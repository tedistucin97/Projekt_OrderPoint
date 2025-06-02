from flask import Flask, render_template
from database import init_db
from routes import artikli_blueprint, narudzbe_blueprint
from pony.orm import db_session
from models import Artikl

# Inicijalizacija Flask aplikacije, s definiranjem foldera gdje se nalaze HTML predlošci
app = Flask(__name__, template_folder="templates")

# Inicijalizacija baze podataka (spajanje i generiranje tablica ako ne postoje)
init_db()

# Funkcija koja inicijalno puni bazu s nekoliko artikala ako baza još nema podataka
@db_session
def seed_data():
    if not Artikl.select().exists():
        Artikl(naziv="Kava", cijena=1.5, kategorija="Piće")
        Artikl(naziv="Pivo", cijena=2.0, kategorija="Piće")
        Artikl(naziv="Sok", cijena=2.2, kategorija="Piće")
        Artikl(naziv="Pizza", cijena=6.0, kategorija="Hrana")
        Artikl(naziv="Hamburger", cijena=5.5, kategorija="Hrana")

# Pozivanje funkcije za inicijalno punjenje baze
seed_data()

# Registracija blueprintova za artikle i narudžbe (rute definirane u routes.py)
app.register_blueprint(artikli_blueprint)
app.register_blueprint(narudzbe_blueprint)

# --------------------------------------
# DEFINIRANJE RUTA ZA FRONTEND STRANICE
# --------------------------------------

# Početna stranica – prikaz stola
@app.route("/")
@db_session
def index():
    return render_template("index.html")

# Stranica za izradu narudžbe
@app.route("/narudzba.html")
@db_session
def narudzba():
    return render_template("narudzba.html")

# Stranica za pregled svih narudžbi
@app.route("/narudzbe.html")
def pregled_narudzbi():
    return render_template("narudzbe.html")

# Alias za početnu stranicu
@app.route("/index.html")
@db_session
def index_alias():
    return render_template("index.html")

# Stranica za dodavanje novih artikala
@app.route("/artikli.html")
def artikli():
    return render_template("artikli.html")

# Stranica za pregled i uređivanje artikala
@app.route("/pregled_artikala.html")
def pregled_artikala():
    return render_template("pregled_artikala.html")

# Stranica s grafičkim prikazom zarade
@app.route("/zarada.html")
def zarada():
    return render_template("zarada.html")

# Pokretanje Flask aplikacije – na 0.0.0.0 da je dostupna i van containera (Docker)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
