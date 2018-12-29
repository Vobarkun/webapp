import cairo
from shapely.geometry import Polygon
from shapely import ops
from operator import itemgetter

def printAt(x, string):
    if type(string) is not str:
        string = str(string)
    print("\r\033[" + str(x) + "C" + string + "\r", flush = True, end = "")

def argmin(l):
    return min(enumerate(l), key=itemgetter(1))[0] 

def linspace(start, stop, num):
    return [start + i * (stop - start) / (num - 1) for i in range(num)]

class PContext(cairo.Context):
    def drawPolygon(self, polygons, color = None):
        if polygons.is_empty:
            return
        randomColor = color == "random"
        if randomColor:
            color = (random.random(), random.random(), random.random())
        if color is None:
            color = (0, 0, 0)
        
        self.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        self.set_source_rgb(*color)
        
        if type(polygons) is Polygon:
            self.move_to(*polygons.exterior.coords[-1])
            for x, y in polygons.exterior.coords:
                self.line_to(x, y)
            for hole in polygons.interiors:
                self.move_to(*hole.coords[-1])
                for x, y in hole.coords:
                    self.line_to(x, y)
            self.set_source_rgb(*color)
            self.fill()

        else:
            for polygon in polygons:
                if randomColor:
                    color = (random.random(), random.random(), random.random())
                    self.set_source_rgb(*color)
                self.move_to(*polygon.exterior.coords[-1])
                for x, y in polygon.exterior.coords:
                    self.line_to(x, y)
                for hole in polygon.interiors:
                    self.move_to(*hole.coords[-1])
                    for x, y in hole.coords:
                        self.line_to(x, y)
                self.set_source_rgb(*color)
                self.fill()

    def drawTransformed(self, polygons, color = None, outline = True, fill = True):
        polygons = polygons.scale(xfact = 0.5, yfact = 0.5, origin = (0, 0)).translate(xoff = 0.5, yoff = 0.5)
        if fill:
            self.drawPolygon(polygons, color)
        if outline:
            self.drawPolygon(polygons.boundary.buffer(0.001, 4), color = (0, 0, 0))

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