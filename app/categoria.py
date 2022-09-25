from flask import Flask, jsonify, request, abort
from flask_caching import Cache
import requests
import json

config = {
    "DEBUG": True,         
    "CACHE_TYPE": "SimpleCache",  
    "CACHE_DEFAULT_TIMEOUT": 120
}

app = Flask(__name__)

app.config.from_mapping(config)
cache = Cache(app)

@app.route('/alive')
def alive():
    return jsonify({"mensaje": "Alive"})

@app.route('/artist', methods=['GET'])
@cache.cached()
def artist_info():
    artist_name = request.args.get('name')
    
    data = requests.get(f"https://www.theaudiodb.com/api/v1/json/2/search.php?s={artist_name}")
    
    if data.status_code != 200:
        return abort(data.status_code)
    else:
        data = data.json()

    respuesta = {
        "Response": {
            "artist": data["artists"][0].get("strArtist"),
            "style": data["artists"][0].get("strStyle"),
            "mood": data["artists"][0].get("strMood"),
            "country": data["artists"][0].get("strCountry"),
        }
    }
    

    data_discos = requests.get(f"https://theaudiodb.com/api/v1/json/2/discography.php?s={artist_name}")

    if data_discos.status_code != 200:
        return abort(data_discos.status_code)
    else:
        data_discos = data_discos.json()
    discos = [{"album":album.get("strAlbum"), "year":album.get("intYearReleased")} for album in data_discos.get("album")]

    respuesta["Response"]["discography"] = discos

    return jsonify(respuesta)

if __name__ == "__main__":
    app.run(debug=True)