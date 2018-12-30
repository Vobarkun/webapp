import cairo
from shapely.geometry import Polygon, Point
from shapely import ops, affinity
from operator import itemgetter
import svgwrite
import re

def printAt(x, string):
    if type(string) is not str:
        string = str(string)
    print("\r\033[" + str(x) + "C" + string + "\r", flush = True, end = "")

def argmin(l):
    return min(enumerate(l), key=itemgetter(1))[0] 

def linspace(start, stop, num):
    return [start + i * (stop - start) / (num - 1) for i in range(num)]

def removeSmallStuff(shape, minsize):
    if type(shape) is Polygon:
        if not shape.buffer(-minsize, 4).is_empty:
            return shape
        return shape.difference(shape)
    keep = []
    for component in shape:
        if not component.buffer(-minsize, 4).is_empty:
            keep.append(component)
    return ops.cascaded_union(keep)

def roundAllNumbersinString(string, precision):
    dec = re.compile(r"\d*\.\d+")
    return re.sub(dec, lambda match: str(round(float(match.group()), precision)), svg)

def shapetopaths(dwg, shape, fill = "green"):
    if type(fill) is tuple:
        fill = "rgb({}, {}, {})".format(int(fill[0] * 256), int(fill[1] * 256), int(fill[2] * 256))
    if type(shape) is Polygon:
        svg = roundAllNumbersinString(shape.svg(), 3)
        commands = svg[svg.find("d=") + 3:-4].split(" ")
        return [dwg.path(commands, stroke_width = 0.004, stroke = "black", fill = fill)]
    paths = []
    for polygon in shape:
        svg = polygon.svg()
        commands = svg[svg.find("d=") + 3:-4].split(" ")
        paths.append(dwg.path(commands, stroke_width = 0.004, stroke = "black", fill = fill))
    return paths

if __name__ == '__main__':  
    try:
        rectangle = Polygon([[1, -1], [1, 1], [-1, 1], [-1, -1]])
        p = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        p = p.difference(affinity.scale(p, 0.5, 0.5)).union(Point(-0.5, -0.5).buffer(0.5, 1))
        
        dwg = svgwrite.Drawing(viewBox = ("-400 -400 800 800"))
        for path in shapetopaths(dwg, rectangle, fill = "white"):
            dwg.add(path)
        for path in shapetopaths(dwg, p, fill = (1, 0, 1)):
            dwg.add(path)
        
        dwg.saveas("test.svg")
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)


