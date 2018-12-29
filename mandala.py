import math
import cairo
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, MultiPoint
from shapely import affinity, wkt, geometry, ops
import random
import copy
import itertools
import sys

from stuff import printAt, argmin, PContext, removeSmallStuff, linspace

def rotate(shape, angle, origin = (0, 0)):
    return affinity.rotate(shape, angle, origin = origin)
def scale(shape, xfact, yfact, origin = (0, 0)):
    return affinity.scale(shape, xfact = xfact, yfact = yfact, origin = origin)
geometry.base.BaseGeometry.translate = affinity.translate
geometry.base.BaseGeometry.scale = scale
geometry.base.BaseGeometry.rotate = rotate

def mandalify(shape, nsym, mirror = False, keepOriginal = True):
    if shape.is_empty:
        return shape
    original = shape
    if mirror:
        shape = shape.union(shape.scale(1, -1)).buffer(0.001, 1).buffer(-0.001, 1)
    if keepOriginal:
        return ops.cascaded_union([shape.rotate(i * 360 / nsym) for i in range(nsym)])
    return ops.cascaded_union([shape.rotate(i * 360 / nsym) for i in range(1, nsym)]).union(original.scale(1, -1))
geometry.base.BaseGeometry.mandalify = mandalify

def getSkeleton(ntries, distance, bounds, nsym = 1):
    points = [Point(0.5, 0)] if nsym != 0 else [bounds.centroid]
    skeleton = ops.cascaded_union(points)
    openends = [(x, x) for x in points]

    segments = [LineString([Point(0, 0), Point(1, 0)]),
                LineString([Point(-math.cos(math.pi*x) / math.sqrt(2) + 0.5, math.sin(math.pi*x) / math.sqrt(2) - 0.5) for x in linspace(0.25, 0.75, 20)]),
                LineString([Point(-math.cos(math.pi*x) / math.sqrt(2) + 0.5,-math.sin(math.pi*x) / math.sqrt(2) + 0.5) for x in linspace(0.25, 0.75, 20)])]

    nsucesses = 0
    for i in range(ntries):
        printAt(0, "{}/{}".format(nsucesses, i))
        rng.shuffle(segments)

        index = rng.randrange(len(points))
        start = points[index]

        fact = 20
        nangles = 10
        angles = [360 / nangles * x + rng.uniform(0, 360 / nangles) for x in range(nangles)]
        rng.shuffle(angles)
        lengths = linspace(distance, distance / fact, 5)
        lengths = [l + rng.uniform(0, distance / fact / 2) for l in lengths]
        
        for angle, segment, length in itertools.product(angles, segments, lengths):
            end = Point(length, 0).rotate(angle).translate(start.x, start.y)
            newLine = segment.scale(length, length).rotate(angle).translate(start.x, start.y)


            tail = newLine.difference(start.buffer(length / 3))
            if (nsym != 1 and (not newLine.crosses(newLine.mandalify(nsym, keepOriginal = False)) and newLine.within(bounds) 
                               and not newLine.mandalify(nsym).crosses(skeleton) and tail.mandalify(nsym).distance(skeleton) > distance / fact) or 
                nsym == 1 and (newLine.within(bounds) and not newLine.crosses(skeleton) and tail.distance(skeleton) > distance / fact 
                               and tail.distance(bounds.boundary) > distance / fact / 2)):
                skeleton = skeleton.union(newLine)
                points.append(end)
                openends = [o for o in openends if o[0] != start]
                openends.append((end, newLine))
                nsucesses += 1
                break
        else:
            del points[index]
        if len(points) == 0:
            break

    return skeleton, openends


def extendOpenEnds(skeleton, openends, bounds, nsym = 1):
    outline = skeleton.mandalify(nsym)
    for end, endLine in openends:
        line = LineString([end, end.buffer(0.0002).boundary.intersection(endLine).representative_point()])
        ray = line.rotate(180, origin = end).scale(100000, 100000, origin = end)
        rayIntersection = ray.intersection(outline.union(bounds.boundary).union(ray.mandalify(nsym, keepOriginal = False)).difference(end))
        if rayIntersection.is_empty:
            continue
        p = ops.nearest_points(end, rayIntersection)[1]
        newLine = LineString([end, p])
        outline = outline.union(newLine.mandalify(nsym))
    return outline

def getCells(outline, bounds, nsym = 1):
    complement = bounds.difference(outline.buffer(0.0001, 4))
    if nsym == 1:
        return [cell for cell in complement if type(cell) is Polygon]
    
    cells = []
    for count in itertools.count():
        if complement.is_empty:
            break
        if type(complement) is Polygon:
            cells.append(complement)
            break

        p = list(complement)[0]
        if type(p) is Polygon:
            mp = p.mandalify(nsym)    
            complement = complement.difference(mp.buffer(0.0001, 4))
            if type(mp) is not Polygon:
                cells.append(p)
            else:
                cells.append(mp)
        else: 
            print(type(p))
            break
    return cells

def generateMandala(nsym, mirror, ntries, distance, ribbon, minsize, colors): 
    disc = Point(0, 0).buffer(0.95, 100)
    angle = math.pi / nsym
    wedge = Polygon([(0, 0), (2, 0), (2 * math.cos(angle), 2 * math.sin(angle), 0)]).intersection(disc)

    bounds = wedge if mirror else disc
    notnsym = 1 if mirror else nsym

    skeleton, openends = getSkeleton(ntries, distance, bounds, notnsym)
    outline = extendOpenEnds(skeleton, openends, bounds, notnsym)
    cells = getCells(outline, bounds, notnsym)    
    cells = [cell for cell in cells if cell.distance(disc.boundary) > 0.0002 or cell.intersects(Point(0, 0).buffer(0.3))]
    
    byColor = [Point(0, 0).difference(Point(0, 0)) for color in colors]
    for cell in cells:
        index = rng.randrange(len(colors))
        byColor[index] = byColor[index].union(cell)
    byColor = [shape.buffer(0.001, 4).buffer(-0.001, 4).simplify(0.0001) for shape in byColor]
    
    result = []
    for count, (shape, color) in enumerate(zip(byColor, colors)):
        printAt(12, count)
        if not shape.is_empty:
            mshape = shape.mandalify(nsym, mirror = mirror).buffer(0.001, 4).buffer(-0.001, 4).buffer(-0.001, 4).buffer(0.001, 4).simplify(0.0001)
            result.append((mshape, color))
            
            otherColors = copy.copy(colors)
            otherColors.remove(color)
            rng.shuffle(otherColors)
            for i in range(1, 100):
                printAt(18, i)
                msbuffer = mshape.buffer(-ribbon * i).simplify(0.0001)
                bigStuff = removeSmallStuff(msbuffer, minsize)
                if bigStuff.is_empty:
                    break
                result.append((bigStuff, otherColors[i % len(otherColors)]))    
    
    return result


def saveMandala(path, nsym, mirror, seed = None, colorindex = None):
    if seed is None:
        seed = random.randrange(sys.maxsize)
    global rng
    rng = random.Random(seed)
    if colorindex is None:
        colorindex = random.randrange(30)

    width, height = 700, 700
    surface = cairo.SVGSurface(path, width, height)
    cr = PContext(surface)
    cr.scale(width, height)
    cr.drawPolygon(geometry.box(0, 0, 1, 1), color = (1, 1, 1))

    schemes = [[[124, 157, 104], [157, 149, 101], [192, 178, 116], [164, 170, 139], [222, 75, 77]], [[202, 161, 72], [199, 205, 135], [165, 203, 189], 
        [57, 66, 68], [41, 39, 47]], [[22, 47, 71], [29, 165, 199], [253, 251, 243], [240, 119, 121], [178, 53, 29]], [[71, 88, 108], [92, 158, 176], [222, 193, 193], [209, 137, 104], [198, 71, 63]], [[231, 114, 50], [223, 171, 84], [128, 96, 72], [79, 106, 78], [32, 54, 53]], [[195, 69, 12], [232, 128, 31], [231, 218, 142], [160, 224, 168], [86, 145, 133]], [[101, 104, 79], [148, 138, 150], [216, 150, 159], [220, 93, 96], [210, 44, 86]], [[241, 85, 75], [158, 172, 33], [162, 222, 203], [52, 172, 217], [101, 131, 82]], [[72, 88, 99], [149, 175, 142], [245, 213, 147], [238, 154, 79], [237, 78, 41]], [[49, 56, 59], [85, 119, 102], [151, 180, 160], [248, 244, 225], [203, 85, 79]], [[156, 128, 152], [157, 204, 207], [164, 216, 218], [245, 193, 183], [210, 109, 130]], [[55, 56, 66], [78, 81, 83], [155, 71, 47], [176, 57, 45], [238, 223, 199]], [[165, 27, 46], [205, 97, 53], [209, 173, 92], [183, 229, 60], [125, 196, 163]], [[87, 44, 38], [112, 95, 59], [175, 173, 69], [227, 186, 38], [250, 146, 34]], [[66, 61, 51], [149, 171, 166], [239, 246, 241], [139, 172, 176], [81, 91, 113]], [[203, 225, 181], [83, 114, 129], [68, 86, 99], [228, 107, 66], [92, 99, 105]], [[171, 94, 27], [163, 141, 72], [210, 197, 130], [27, 42, 80], [7, 34, 148]], [[254, 73, 7], [253, 155, 78], [149, 207, 157], [27, 169, 171], [10, 75, 81]], [[56, 56, 66], [123, 160, 157], [195, 160, 141], [186, 141, 125], [204, 102, 52]], [[89, 75, 65], [86, 157, 154], [150, 213, 212], [196, 208, 187], [202, 111, 58]], [[37, 105, 101], [146, 208, 174], [172, 233, 124], [242, 217, 89], [177, 61, 56]], [[72, 90, 84], [141, 122, 58], [241, 164, 82], [250, 166, 76], [81, 144, 131]], [[252, 133, 82], [204, 116, 108], [165, 99, 110], [111, 79, 101], [41, 47, 83]], [[250, 251, 229], [201, 208, 159], [163, 134, 117], [107, 99, 112], [172, 200, 226]], [[50, 124, 77], [122, 203, 143], [232, 229, 100], [222, 86, 64], [130, 10, 51]], [[247, 83, 76], [240, 217, 139], [89, 202, 99], [49, 142, 127], [19, 63, 83]], [[71, 40, 44], [140, 134, 105], [203, 199, 153], [200, 198, 148], [146, 145, 92]], [[6, 57, 75], [21, 148, 163], [219, 216, 174], [237, 138, 76], [213, 72, 56]], [[55, 53, 44], [94, 146, 125], [209, 200, 141], [241, 207, 164], [185, 96, 63]], [[39, 37, 39], [49, 85, 99], [154, 191, 203], [129, 163, 190], [134, 200, 218]]]
    colors = [(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255) for rgb in schemes[colorindex]]

    mandala = generateMandala(nsym = nsym, mirror = mirror, ntries = 1000, distance = 0.4, minsize = 0.011, ribbon = 0.03, colors = colors)
    for cell, color in mandala:
        cr.drawTransformed(cell, color = color, outline = True, fill = True)

    print()
    surface.finish()
        
    

if __name__ == '__main__':  
    try:
        saveMandala(nsym = 5, mirror = False)
        # width, height = 700, 700
        # surface = cairo.SVGSurface("mandala.svg", width, height)
        # cr = PContext(surface)
        # cr.scale(height, height)
        # cr.drawPolygon(geometry.box(0, 0, 1, 1), color = (1, 1, 1))

        # skeleton, openends = getSkeleton(m = 100, distance = 0.4, bounds = Point(0, 0).buffer(0.95, 100))
        # cr.drawTransformed(skeleton.buffer(0.002))

        # print()
        # surface.write_to_png("mandala.png")
        # surface.finish()

    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)