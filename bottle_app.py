from bottle import route, run, Bottle, response
import sentence
import mandala
import queue
import threading
import time
from stuff import printAt

app = Bottle()

queueM = queue.Queue(20)
queueR = queue.Queue(10)

def fillQueue():
    while True:
        time.sleep(1)
        for _ in range(2):
            if not queueM.full():
                printAt(0, "M" + str(queueM.qsize() + 1))
                queueM.put(mandala.getMandalaSVG(5, True))
        if not queueR.full():
            printAt(0, "R" + str(queueR.qsize() + 1))
            queueR.put(mandala.getMandalaSVG(5, False))

queueFiller = threading.Thread(name = "Queue Filler", target = fillQueue)
queueFiller.setDaemon(True)
queueFiller.start()

lastM = ""
@app.route('/mandala')
def mandalafromQueueM():
    response.set_header('Content-Type', 'image/svg+xml')
    global lastM
    try:
        svg = queueM.get(block = False)
        lastM = svg
    except queue.Empty:
        svg = lastM
    return svg
    
lastR = ""
@app.route('/mandalar')
def mandalafromQueueR():
    response.set_header('Content-Type', 'image/svg+xml')
    global lastR
    try:
        svg = queueR.get(block = False)
        lastR = svg
    except queue.Empty:
        svg = lastR
    return svg

@app.route('/mandala/<nsym:int>')
@app.route('/mandala/<nsym:int>/<seed>')
@app.route('/mandala/<nsym:int>/<seed>/<colorindex:int>')
def bla(nsym = None, seed = None, colorindex = None, outline = 0):
    if nsym is None:
        nsym = 5
    nsym = min(max(nsym, 1), 16)
    if seed == "r":
        seed = None
    response.set_header('Content-Type', 'image/svg+xml')
    return '<?xml version="1.0" encoding="utf-8" ?>\n' + mandala.getMandalaSVG(nsym, True, seed, colorindex)


@app.route('/mandalar/<nsym:int>')
@app.route('/mandalar/<nsym:int>/<seed>')
@app.route('/mandalar/<nsym:int>/<seed>/<colorindex:int>')
def blaR(nsym = None, seed = None, colorindex = None, outline = 0):
    if nsym is None:
        nsym = 5
    nsym = min(max(nsym, 1), 16)
    if seed == "r":
        seed = None
    response.set_header('Content-Type', 'image/svg+xml')
    return '<?xml version="1.0" encoding="utf-8" ?>\n' +  mandala.getMandalaSVG(nsym, False, seed, colorindex)

@app.route('/')
def top():
    satz = sentence.sentence()
    return "<h1>" + satz + "<h1>"

run(app, host="0.0.0.0", port = 10001, debug = True)
