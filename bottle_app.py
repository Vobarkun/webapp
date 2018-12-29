from bottle import route, static_file, run, Bottle
import sentence
import mandala

app = Bottle()

@app.route('/')
def top():
    satz = sentence.sentence()
    return "<h1>" + satz + "<h1>"

@app.route('/mandala')
@app.route('/mandala/<nsym:int>')
@app.route('/mandala/<nsym:int>/<seed:int>')
@app.route('/mandala/<nsym:int>/<seed:int>/<colorindex:int>')
@app.route('/mandala/<nsym:int>/<seed:int>/<colorindex:int>/<outline:int>')
def bla(nsym = None, seed = None, colorindex = None, outline = 0):
    if nsym is None:
        nsym = 5
    nsym = min(max(nsym, 2), 16)
    if colorindex is not None:
        colorindex = min(max(colorindex, 0), 29)
    outline = False if outline != 1 else True
    return mandala.getMandalaSVG(nsym, True, seed, colorindex)

        
@app.route('/mandala2')
@app.route('/mandala2/<nsym:int>')
@app.route('/mandala2/<nsym:int>/<seed:int>')
@app.route('/mandala2/<nsym:int>/<seed:int>/<colorindex:int>')
@app.route('/mandala2/<nsym:int>/<seed:int>/<colorindex:int>/<outline:int>')
def bla(nsym = None, seed = None, colorindex = None, outline = 0):
    if nsym is None:
        nsym = 5
    nsym = min(max(nsym, 2), 16)
    if colorindex is not None:
        colorindex = min(max(colorindex, 0), 29)
    outline = False if outline != 1 else True
    return mandala.getMandalaSVG(nsym, False, seed, colorindex)


run(app, host="0.0.0.0", port = 10001, debug = True)
