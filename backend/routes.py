from flask import Blueprint, request, jsonify, Response
from pony.orm import db_session, select, flush, desc
from models import Narudzba, Stavka, Artikl
from datetime import datetime
import json

# Definiramo dva Blueprinta za odvajanje ruta
artikli_blueprint = Blueprint("artikli", __name__)
narudzbe_blueprint = Blueprint("narudzbe", __name__)

# -------------------------
# GET /artikli – vraća sve artikle
# -------------------------
@artikli_blueprint.route("/artikli", methods=["GET"])
@db_session
def get_artikli():
    artikli = select(a for a in Artikl)[:]
    return jsonify([{
        "id": a.id,
        "naziv": a.naziv,
        "cijena": a.cijena,
        "kategorija": a.kategorija
    } for a in artikli])

# -------------------------
# POST /artikli – dodaje novi artikl
# -------------------------
@artikli_blueprint.route("/artikli", methods=["POST"])
@db_session
def add_artikl():
    data = request.get_json()
    a = Artikl(
        naziv=data["naziv"],
        cijena=data["cijena"],
        kategorija=data["kategorija"]
    )
    flush()  # kako bi odmah dobili ID artikla
    return jsonify({"message": "Artikl dodan", "id": a.id}), 201

# -------------------------
# DELETE /artikli/<id> – briše artikl
# -------------------------
@artikli_blueprint.route("/artikli/<int:artikl_id>", methods=["DELETE"])
@db_session
def delete_artikl(artikl_id):
    artikl = Artikl.get(id=artikl_id)
    if artikl:
        artikl.delete()
        return jsonify({"message": "Artikl obrisan"})
    return jsonify({"error": "Artikl ne postoji"}), 404

# -------------------------
# GET /narudzbe – vraća sve narudžbe (s detaljima)
# -------------------------
@artikli_blueprint.route("/narudzbe", methods=["GET"])
@db_session
def get_sve_narudzbe():
    narudzbe = select(n for n in Narudzba).order_by(desc(Narudzba.vrijeme_narudzbe))[:]
    podaci = []
    for n in narudzbe:
        podaci.append({
            "id": n.id,
            "redni_broj": n.redni_broj,
            "broj_stola": n.broj_stola,
            "vrijeme_narudzbe": n.vrijeme_narudzbe.strftime("%Y-%m-%d %H:%M:%S"),
            "naplacena": n.naplacena,
            "stornirana": n.stornirana,
            "stavke": [
                {
                    "naziv": s.naziv_artikla,
                    "kolicina": s.kolicina,
                    "cijena": s.cijena_artikla
                } for s in n.stavke
            ]
        })
    return Response(
        json.dumps(podaci, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )

# -------------------------
# POST /narudzbe – kreira novu narudžbu
# -------------------------
@narudzbe_blueprint.route("/narudzbe", methods=["POST"])
@db_session
def kreiraj_narudzbu():
    data = request.get_json()
    broj_stola = data.get("broj_stola")
    stavke = data.get("stavke")

    if not broj_stola or not stavke:
        return jsonify({"error": "Nedostaju podaci"}), 400

    # Generiramo novi redni broj
    zadnja_narudzba = select(n for n in Narudzba if n.redni_broj is not None).order_by(desc(Narudzba.redni_broj)).first()
    sljedeci_redni = zadnja_narudzba.redni_broj + 1 if zadnja_narudzba else 1

    # Kreiramo narudžbu
    narudzba = Narudzba(
        redni_broj=sljedeci_redni,
        broj_stola=broj_stola,
        vrijeme_narudzbe=datetime.now(),
        naplacena=False,
        stornirana=False
    )

    # Dodajemo stavke narudžbi
    for stavka in stavke:
        artikl_id = stavka.get("artikl_id")
        kolicina = stavka.get("kolicina")
        artikl = Artikl.get(id=artikl_id)
        if not artikl:
            return jsonify({"error": f"Artikl s ID {artikl_id} ne postoji"}), 404
        Stavka(
            narudzba=narudzba,
            kolicina=kolicina,
            naziv_artikla=artikl.naziv,
            cijena_artikla=artikl.cijena
        )

    return jsonify({
        "message": "Narudžba spremljena",
        "narudzba_id": narudzba.id,
        "redni_broj": narudzba.redni_broj
    }), 201

# -------------------------
# GET /narudzbe/<id> – dohvaća pojedinu narudžbu
# -------------------------
@narudzbe_blueprint.route("/narudzbe/<int:id>", methods=["GET"])
@db_session
def get_narudzba(id):
    narudzba = Narudzba.get(id=id)
    if narudzba:
        return jsonify({
            "id": narudzba.id,
            "redni_broj": narudzba.redni_broj,
            "broj_stola": narudzba.broj_stola,
            "vrijeme_narudzbe": narudzba.vrijeme_narudzbe.strftime("%Y-%m-%d %H:%M:%S"),
            "naplacena": narudzba.naplacena,
            "stornirana": narudzba.stornirana,
            "stavke": [{
                "naziv": stavka.naziv_artikla,
                "kolicina": stavka.kolicina,
                "cijena": stavka.cijena_artikla
            } for stavka in narudzba.stavke]
        })
    return jsonify({"error": "Narudžba nije pronađena"}), 404

# -------------------------
# PUT /artikli/<id> – ažuriranje artikla
# -------------------------
@artikli_blueprint.route("/artikli/<int:artikl_id>", methods=["PUT"])
@db_session
def update_artikl(artikl_id):
    artikl = Artikl.get(id=artikl_id)
    if not artikl:
        return jsonify({"error": "Artikl ne postoji"}), 404

    data = request.get_json()
    artikl.naziv = data.get("naziv", artikl.naziv)
    artikl.cijena = data.get("cijena", artikl.cijena)
    artikl.kategorija = data.get("kategorija", artikl.kategorija)

    return jsonify({"message": "Artikl ažuriran"})

# -------------------------
# PUT /narudzbe/<id>/naplati – označava narudžbu kao naplaćenu
# -------------------------
@narudzbe_blueprint.route("/narudzbe/<int:id>/naplati", methods=["PUT"])
@db_session
def naplati_narudzbu(id):
    narudzba = Narudzba.get(id=id)
    if not narudzba:
        return jsonify({"error": "Narudžba nije pronađena"}), 404
    narudzba.naplacena = True
    return jsonify({"message": "Narudžba naplaćena"})

# -------------------------
# GET /zarada – vraća podatke o ukupnoj dnevnoj zaradi
# -------------------------
@narudzbe_blueprint.route("/zarada", methods=["GET"])
@db_session
def get_zarada():
    from collections import defaultdict
    data = defaultdict(float)
    narudzbe = select(n for n in Narudzba if n.naplacena)[:]
    for n in narudzbe:
        datum = n.vrijeme_narudzbe.date().isoformat()
        for s in n.stavke:
            data[datum] += s.kolicina * s.cijena_artikla
    return jsonify(dict(data))

# -------------------------
# PUT /narudzbe/<id>/izmijeni_datum – mijenja datum narudžbe
# -------------------------
@narudzbe_blueprint.route("/narudzbe/<int:id>/izmijeni_datum", methods=["PUT"])
@db_session
def izmijeni_datum(id):
    data = request.get_json()
    narudzba = Narudzba.get(id=id)
    if not narudzba:
        return jsonify({"error": "Nepostojeća narudžba"}), 404
    narudzba.vrijeme_narudzbe = datetime.fromisoformat(data["vrijeme"])
    return jsonify({"message": "Vrijeme ažurirano"})
