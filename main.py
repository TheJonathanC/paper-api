from bs4 import BeautifulSoup
from urllib.request import urlopen
from flask import Flask, jsonify, request, render_template
import json

dct = {
    "178": ["397", "303", "398", "301", "399", "480"],
    "177": ["385", "293", "386", "297", "387", "478"],
    "176": ["405", "321", "404", "323", "403", "482"],
    "174": ["391", "313", "392", "311", "393", "476"],
    "274": ["379", "281", "381", "283", "383", "279"]
}
names = {
    "178": "BCA",
    "177": "BBA",
    "176": "BSC",
    "174": "BCOM",
    "274": "BA"
}

app = Flask(__name__)

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

@app.route("/")
def home():
    return render_template("body.html")

@app.route("/scrapedata", methods=["GET"])
def scraper():
    crjson()
    return rdjson(None)

@app.route("/exampapers", methods=["GET"])
def get_cours():
    mdata = rdjson(None)
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