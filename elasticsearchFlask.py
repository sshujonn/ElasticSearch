from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch()


@app.route('/', methods=["GET", "POST"])
def search():
    query = request.args.get('query')
    if query is not None:
        search=request.args.get('Search')
        # Fuzzy Search
        if search == 'Fuzzy Search':
            body={
                    "query": {
                        "multi_match" : {
                            "query" : query,
                            "fields": ["name", "address", "url", "feed", "price"],
                            "fuzziness": "AUTO"
                        }
                    }
                }

        # wildcard search
        elif search == 'Wildcard Search':
            body={
                    "query": {
                        "wildcard" : {
                            "name" : query+"*"
                        }
                    }
                }

        # regexp search
        elif search == 'Regexp Search':
            body={
                    "query":{
                        "regexp" : {
                            "name" : query[0]+"[a-z]*"+query[2]
                        }
                    }
                }

        # multi-match search
        else:
            body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["name", "address", "url", "feed"]
                    }
                }
            }

        res = es.search(index='rentalhomes', doc_type='items', body=body)
        return render_template('search.html', response=res['hits']['hits'])
    return render_template('search.html')


@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form['name']
        address = request.form['address']
        price = request.form['price']
        url = request.form['url_link']
        sleeps = request.form['sleeps']
        feed = request.form['feed']
        if name != "" or address != "" or price != "" or url != "" or sleeps != "" or feed != "":
            body = {
                'name': name,
                'address': address,
                'price': price,
                'url': url,
                'sleeps': sleeps,
                'feed': feed
            }
            es.index(index='rentalhomes', doc_type='items', body=body)
    return render_template('add.html')


@app.route('/update', methods=["GET", "POST"])
def update():
    if request.method == "POST":
        id = request.form['id']
        body = {
            "query": {
                "term": {
                    "_id": id
                }
            }
        }
        res = es.search(index='rentalhomes', doc_type='items', body=body)

        return render_template('update.html', item=res['hits']['hits'])
    if request.method == "GET":
        name = request.args.get('name')
        address = request.args.get('address')
        price = request.args.get('price')
        url = request.args.get('url_link')
        sleeps = request.args.get('sleeps')
        feed = request.args.get('feed')
        upId = request.args.get('id')
        if (name != "" or address != "" or price != "" or url != "" or sleeps != "" or feed != ""):
            body = {
                "doc": {
                    'name': name,
                    'address': address,
                    'price': price,
                    'url': url,
                    'sleeps': sleeps,
                    'feed': feed
                }
            }
            es.update(index='rentalhomes', doc_type='items', id=upId, body=body)
    return render_template('search.html')


@app.route('/delete', methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        id = request.form['id']
        es.delete(index="rentalhomes", doc_type="items", id=id)
        return render_template('search.html')
    return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True)
