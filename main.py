from bs4 import BeautifulSoup
from urllib.request import urlopen
from flask import Flask, jsonify, request, render_template
import json, time

dct = {
    "178": ["397", "303", "398", "301", "399", "480"],
    "177": ["385", "293", "386", "297", "387", "478"],
    "176": ["405", "321", "404", "323", "403", "482"],
    "174": ["391", "313", "392", "311", "393", "476"],
    "274": ["379", "281", "381", "283", "383", "279"]
}
names = {
    "178": "bca",
    "177": "bba",
    "176": "bsc",
    "174": "bcom",
    "274": "ba"
}

app = Flask(__name__)
extime = 3.5 * 24 * 60 *60

url = "http://136.233.78.185:8080/saclib/handle/123456789/"
def sdata(course_code):
    data = {}
    for code in dct[course_code]:
        text = urlopen(url + code).read()
        soup = BeautifulSoup(text, "html.parser")
        artifacts = soup.findAll('div', attrs={'class': 'artifact-title'})
        for artifact in artifacts:
            links = artifact.findAll('a')
            for link in links:
                file_url = "http://136.233.78.185:8080" + link['href']
                text = urlopen(file_url).read()
                soup = BeautifulSoup(text, 'html.parser')
                title = soup.title.string
                file_links = soup.findAll('div', attrs={'class': 'file-link'})
                for file_link in file_links:
                    file_a_tags = file_link.findAll('a')
                    for file_a_tag in file_a_tags:
                        data[title] = "http://136.233.78.185:8080" + file_a_tag['href']
        
    return data

def txtres():
    t1 = "Helo, this is *ALOPAPERS-API*, "
    t2 = "built for NoteVault. "
    t3 = "https://collegerepo.vercel.app/ "
    t4 = " This API returns previous year question papers and other stuff, "
    t5 = "add a /exampapers to check it out, "
    t6 = "add a /scrapedata to refresh scraped data."
    txt = t1+t2+t3+t4+t5+t6
    return txt

class jsn:
    def crjson():
        cdata={}
        for n in dct:
            cdata[n]=sdata(n)
        ndata = {names[k]:v for k,v in cdata.items()}

        with open("test.json", "w") as outfile: 
            json.dump(ndata, outfile,indent=4)

    def rdjson(code):
        with open("test.json") as json_file:
            rdata = json.load(json_file)
        if code is not None:
            return rdata[code]
        else:
            return rdata

class cch:
    @staticmethod
    def load():
        try:
            with open("cache.json","r") as json_fil:
                cac = json.load(json_fil)
        except (FileNotFoundError, json.JSONDecodeError):
            cac={}
        return cac
    
    @staticmethod
    def save(cache):
        with open("cache.json","w") as infil:
            json.dump(cache,infil,indent=4)
cache = cch.load()

@app.route("/")
def home():
    return txtres()

@app.route("/scrapedata", methods=["GET"])
def scraper():
    jsn.crjson()
    scp = jsn.rdjson(None)
    tm = time.time()
    cache["time"] = tm
    cch.save(cache)
    return scp

@app.route("/exampapers", methods=["GET"])
def get_cours():
    if time.time() - cache.get("time",0) < extime:
        print("cache exists")
        mdata = jsn.rdjson(None)
        ccode = request.args.get("code")
        if ccode is not None and ccode in mdata:
            return jsonify({ccode:mdata[ccode]})
        else:
            return jsonify(mdata)
    else:
        print("creating cache")
        jsn.crjson()
        mdata = jsn.rdjson(None)
        tm = time.time()
        cache["time"] = tm
        cch.save(cache)
        ccode = request.args.get("code")
        if ccode is not None and ccode in mdata:
            return jsonify({ccode:mdata[ccode]})
        else:
            return jsonify(mdata)

@app.route("/bca-data",methods=["GET"])
def bcadata():
    with open("BCA.txt") as json_file:
        bdata = json.load(json_file)
    return jsonify(bdata)

if __name__ == '__main__':
    app.run(debug=True)