from bottle import route, run, Bottle, response
import sentence
import mandala

app = Bottle()

@app.route('/')
def top():
    satz = sentence.sentence()
    return "<h1>" + satz + "<h1>"

@app.route('/mandala')
@app.route('/mandala/<nsym:int>')
@app.route('/mandala/<nsym:int>/<seed>')
@app.route('/mandala/<nsym:int>/<seed>/<colorindex:int>')
def bla(nsym = None, seed = None, colorindex = None, outline = 0):
    if nsym is None:
        nsym = 5
    nsym = min(max(nsym, 1), 16)
    if colorindex is not None:
        colorindex = min(max(colorindex, 0), 99)
    if seed == "r":
        seed = None
    response.set_header('Content-Type', 'image/svg+xml')
    return '<?xml version="1.0" encoding="utf-8" ?>\n' + mandala.getMandalaSVG(nsym, True, seed, colorindex)

        
@app.route('/mandalar')
@app.route('/mandalar/<nsym:int>')
@app.route('/mandalar/<nsym:int>/<seed:int>')
@app.route('/mandalar/<nsym:int>/<seed:int>/<colorindex:int>')
def bla(nsym = None, seed = None, colorindex = None, outline = 0):
    if nsym is None:
        nsym = 5
    nsym = min(max(nsym, 1), 16)
    if colorindex is not None:
        colorindex = min(max(colorindex, 0), 99)
    response.set_header('Content-Type', 'image/svg+xml')
    return '<?xml version="1.0" encoding="utf-8" ?>\n' +  mandala.getMandalaSVG(nsym, False, seed, colorindex)


run(app, host="0.0.0.0", port = 10001, debug = True)
