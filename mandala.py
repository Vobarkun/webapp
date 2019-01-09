import math
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, MultiPoint
from shapely import affinity, wkt, geometry, ops
import random
import copy
import itertools
import sys
import colorsys
import svgwrite
import string

from stuff import printAt, argmin, removeSmallStuff, linspace, shapetopaths

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

def getSkeleton(ntries, distance, bounds, nsym = 1, rng = None):
    if rng is None:
        rng = random.Random()
        
    points = [Point(0.5, 0)] if nsym != 1 else [bounds.centroid]
    skeleton = ops.cascaded_union(points)
    openends = [(x, x) for x in points]

    segments = [LineString([Point(0, 0), Point(1, 0)]),
                LineString([Point(-math.cos(math.pi*x) / math.sqrt(2) + 0.5, math.sin(math.pi*x) / math.sqrt(2) - 0.5) for x in linspace(0.25, 0.75, 20)]),
                LineString([Point(-math.cos(math.pi*x) / math.sqrt(2) + 0.5,-math.sin(math.pi*x) / math.sqrt(2) + 0.5) for x in linspace(0.25, 0.75, 20)])]

    nsucesses = 0
    for i in range(ntries):
        printAt(4, "{}/{}".format(nsucesses, i))
        printAt(12, str(len(points)) + " ")
        rng.shuffle(segments)

        index = rng.randrange(len(points))
        start = points[index]

        fact = 20
        nangles = 10
        angles = [360 / nangles * x + rng.uniform(0, 360 / nangles) for x in range(nangles)]
        rng.shuffle(angles)
        lengths = linspace(distance, distance / fact, 5)
        lengths = [l + rng.uniform(0, (distance - distance / fact) / 5) for l in lengths]
        
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

def generateMandala(nsym, mirror, ntries, distance, ribbon, minsize, colors, rng = None):
    if rng is None:
        rng = random.Random()
    disc = Point(0, 0).buffer(0.95, 100)
    angle = math.pi / nsym
    wedge = Polygon([(0, 0), (2, 0), (2 * math.cos(angle), 2 * math.sin(angle), 0)]).intersection(disc)

    bounds = wedge if mirror else disc
    notnsym = 1 if mirror else nsym

    skeleton, openends = getSkeleton(ntries, distance, bounds, nsym = notnsym, rng = rng)
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
        if not shape.is_empty:
            mshape = shape.mandalify(nsym, mirror = mirror).buffer(0.001, 4).buffer(-0.001, 4).buffer(-0.001, 4).buffer(0.001, 4).simplify(0.0001)
            result.append((mshape, color))
            
            otherColors = copy.copy(colors)
            otherColors.remove(color)
            rng.shuffle(otherColors)
            for i in range(1, 100):
                msbuffer = mshape.buffer(-ribbon * i).simplify(0.0001)
                bigStuff = removeSmallStuff(msbuffer, minsize)
                if bigStuff.is_empty:
                    break
                result.append((bigStuff, otherColors[i % len(otherColors)]))    
    
    return result


def getMandalaSVG(nsym, mirror, seed = None, colorindex = None):
    schemes = [[(105, 210, 231), (167, 219, 216), (224, 228, 204), (243, 134, 48), (250, 105, 0)], [(254, 67, 101), (252, 157, 154), (249, 205, 173), 
        (200, 200, 169), (131, 175, 155)], [(236, 208, 120), (217, 91, 67), (192, 41, 66), (84, 36, 55), (83, 119, 122)], [(85, 98, 112), (78, 205, 196), (199, 244, 100), (255, 107, 107), (196, 77, 88)], [(119, 79, 56), (224, 142, 121), (241, 212, 175), (236, 229, 206), (197, 224, 220)], [(232, 221, 203), (205, 179, 128), (3, 101, 100), (3, 54, 73), (3, 22, 52)], [(73, 10, 61), (189, 21, 80), (233, 127, 2), (248, 202, 0), (138, 155, 15)], [(89, 79, 79), (84, 121, 128), (69, 173, 168), (157, 224, 173), (229, 252, 194)], [(0, 160, 176), (106, 74, 60), (204, 51, 63), (235, 104, 65), (237, 201, 81)], [(233, 78, 119), (214, 129, 137), (198, 164, 154), (198, 229, 217), (244, 234, 213)], [(63, 184, 175), (127, 199, 175), (218, 216, 167), (255, 158, 157), (255, 61, 127)], [(217, 206, 178), (148, 140, 117), (213, 222, 217), (122, 106, 83), (153, 178, 183)], [(255, 255, 255), (203, 232, 107), (242, 233, 225), (28, 20, 13), (203, 232, 107)], [(239, 255, 205), (220, 233, 190), (85, 81, 82), (46, 38, 51), (153, 23, 60)], [(52, 56, 56), (0, 95, 107), (0, 140, 158), (0, 180, 204), (0, 223, 252)], [(65, 62, 74), (115, 98, 110), (179, 129, 132), (240, 180, 158), (247, 228, 190)], [(255, 78, 80), (252, 145, 58), (249, 212, 35), (237, 229, 116), (225, 245, 196)], [(153, 184, 152), (254, 206, 168), (255, 132, 124), (232, 74, 95), (42, 54, 59)], [(101, 86, 67), (128, 188, 163), (246, 247, 189), (230, 172, 39), (191, 77, 40)], [(0, 168, 198), (64, 192, 203), (249, 242, 231), (174, 226, 57), (143, 190, 0)], [(53, 19, 48), (66, 66, 84), (100, 144, 138), (232, 202, 164), (204, 42, 65)], [(85, 66, 54), (247, 120, 37), (211, 206, 61), (241, 239, 165), (96, 185, 154)], [(93, 65, 87), (131, 134, 137), (168, 202, 186), (202, 215, 178), (235, 227, 170)], [(140, 35, 24), (94, 140, 106), (136, 166, 94), (191, 179, 90), (242, 196, 90)], [(250, 208, 137), (255, 156, 91), (245, 99, 74), (237, 48, 60), (59, 129, 131)], [(255, 66, 66), (244, 250, 210), (212, 238, 94), (225, 237, 185), (240, 242, 235)], [(248, 177, 149), (246, 114, 128), (192, 108, 132), (108, 91, 123), (53, 92, 125)], [(209, 231, 81), (255, 255, 255), (0, 0, 0), (77, 188, 233), (38, 173, 228)], [(27, 103, 107), (81, 149, 72), (136, 196, 37), (190, 242, 2), (234, 253, 230)], [(94, 65, 47), (252, 235, 182), (120, 192, 168), (240, 120, 24), (240, 168, 48)], [(188, 189, 172), (207, 190, 39), (242, 116, 53), (240, 36, 117), (59, 45, 56)], [(69, 38, 50), (145, 32, 77), (228, 132, 74), (232, 191, 86), (226, 247, 206)], [(238, 230, 171), (197, 188, 142), (105, 103, 88), (69, 72, 75), (54, 57, 59)], [(240, 216, 168), (61, 28, 0), (134, 184, 177), (242, 214, 148), (250, 42, 0)], [(42, 4, 74), (11, 46, 89), (13, 103, 89), (122, 179, 23), (160, 197, 95)], [(240, 65, 85), (255, 130, 58), (242, 242, 111), (255, 247, 189), (149, 207, 183)], [(185, 215, 217), (102, 130, 132), (42, 40, 41), (73, 55, 54), (123, 59, 59)], [(187, 187, 136), (204, 198, 141), (238, 221, 153), (238, 194, 144), (238, 170, 136)], [(179, 204, 87), (236, 240, 129), (255, 190, 64), (239, 116, 111), (171, 62, 91)], [(163, 169, 72), (237, 185, 46), (248, 89, 49), (206, 24, 54), (0, 153, 137)], [(48, 0, 48), (72, 0, 72), (96, 24, 72), (192, 72, 72), (240, 114, 65)], [(103, 145, 122), (23, 4, 9), (184, 175, 3), (204, 191, 130), (227, 50, 88)], [(170, 179, 171), (196, 203, 183), (235, 239, 201), (238, 224, 183), (232, 202, 175)], [(232, 213, 183), (14, 36, 48), (252, 58, 81), (245, 179, 73), (232, 213, 185)], [(171, 82, 107), (188, 162, 151), (197, 206, 174), (240, 226, 164), (244, 235, 195)], [(96, 120, 72), (120, 144, 72), (192, 216, 96), (240, 240, 216), (96, 72, 72)], [(182, 216, 192), (200, 217, 191), (218, 218, 189), (236, 219, 188), (254, 220, 186)], [(168, 230, 206), (220, 237, 194), (255, 211, 181), (255, 170, 166), (255, 140, 148)], [(62, 65, 71), (255, 254, 223), (223, 186, 105), (90, 46, 46), (42, 44, 49)], [(81, 81, 81), (255, 255, 255), (0, 180, 255), (238, 238, 238)], [(252, 53, 76), (41, 34, 31), (19, 116, 125), (10, 191, 188), (252, 247, 197)], [(204, 12, 57), (230, 120, 30), (200, 207, 2), (248, 252, 193), (22, 147, 167)], [(167, 197, 189), (229, 221, 203), (235, 123, 89), (207, 70, 71), (82, 70, 86)], [(28, 33, 48), (2, 143, 118), (179, 224, 153), (255, 234, 173), (209, 67, 52)], [(218, 214, 202), (27, 176, 206), (79, 134, 153), (106, 94, 114), (86, 52, 68)], [(237, 235, 230), (214, 225, 199), (148, 199, 182), (64, 59, 51), (211, 100, 59)], [(92, 50, 62), (168, 39, 67), (225, 94, 50), (192, 210, 62), (229, 240, 76)], [(253, 241, 204), (198, 214, 184), (152, 127, 105), (227, 173, 64), (252, 208, 54)], [(35, 15, 43), (242, 29, 65), (235, 235, 188), (188, 227, 197), (130, 179, 174)], [(185, 211, 176), (129, 189, 164), (178, 135, 116), (248, 143, 121), (246, 170, 147)], [(58, 17, 28), (87, 73, 81), (131, 152, 142), (188, 222, 165), (230, 249, 188)], [(94, 57, 41), (205, 140, 82), (183, 209, 163), (222, 232, 190), (252, 247, 211)], [(28, 1, 19), (107, 1, 3), (163, 0, 6), (194, 26, 1), (240, 60, 2)], [(0, 0, 0), (159, 17, 27), (177, 22, 35), (41, 44, 55), (204, 204, 204)], [(56, 47, 50), (255, 234, 242), (252, 217, 229), (251, 197, 216), (241, 57, 109)], [(227, 223, 186), (200, 214, 191), (147, 204, 198), (108, 189, 181), (26, 31, 30)], [(246, 246, 246), (232, 232, 232), (51, 51, 51), (153, 1, 0), (185, 5, 4)], [(161, 219, 178), (254, 229, 173), (250, 202, 102), (247, 165, 65), (244, 93, 76)], [(27, 50, 95), (156, 196, 228), (233, 242, 249), (58, 137, 201), (242, 108, 79)], [(94, 159, 163), (220, 209, 180), (250, 184, 127), (248, 126, 123), (176, 85, 116)], [(149, 31, 43), (245, 244, 215), (224, 223, 177), (165, 163, 108), (83, 82, 51)], [(193, 179, 152), (96, 89, 81), (251, 238, 194), (97, 166, 171), (172, 206, 192)], [(141, 204, 173), (152, 136, 100), (254, 166, 162), (249, 214, 172), (255, 233, 175)], [(45, 45, 41), (33, 90, 109), (60, 162, 162), (146, 199, 163), (223, 236, 230)], [(65, 61, 61), (4, 0, 4), (200, 255, 0), (250, 2, 60), (75, 0, 15)], [(239, 243, 205), (178, 213, 186), (97, 173, 160), (36, 143, 141), (96, 80, 99)], [(255, 239, 211), (255, 254, 228), (208, 236, 234), (159, 214, 210), (139, 122, 94)], [(207, 255, 221), (180, 222, 193), (92, 88, 99), (168, 81, 99), (255, 31, 76)], [(157, 201, 172), (255, 254, 199), (245, 98, 24), (255, 157, 46), (145, 145, 103)], [(78, 57, 93), (130, 112, 133), (142, 190, 148), (204, 252, 142), (220, 91, 62)], [(248, 237, 209), (216, 138, 138), (71, 72, 67), (157, 157, 147), (197, 207, 198)], [(168, 167, 167), (204, 82, 122), (232, 23, 93), (71, 71, 71), (54, 54, 54)], [(243, 138, 138), (85, 68, 61), (160, 202, 181), (205, 233, 202), (241, 237, 208)], [(4, 109, 139), (48, 146, 146), (47, 184, 172), (147, 164, 42), (236, 190, 19)], [(255, 0, 60), (255, 138, 0), (250, 190, 40), (136, 193, 0), (0, 193, 118)], [(167, 2, 103), (241, 12, 73), (251, 107, 65), (246, 216, 107), (51, 145, 148)], [(78, 77, 74), (53, 52, 50), (148, 186, 101), (39, 144, 176), (43, 78, 114)], [(12, 165, 176), (78, 63, 48), (254, 254, 235), (248, 244, 228), (165, 179, 170)], [(255, 237, 191), (247, 128, 60), (245, 72, 40), (46, 13, 35), (248, 228, 193)], [(77, 59, 59), (222, 98, 98), (255, 184, 140), (255, 208, 179), (245, 224, 211)], [(255, 251, 183), (166, 246, 175), (102, 182, 171), (91, 124, 141), (79, 41, 88)], [(157, 126, 121), (204, 172, 149), (154, 148, 124), (116, 139, 131), (91, 117, 108)], [(237, 246, 238), (209, 192, 137), (179, 32, 77), (65, 46, 40), (21, 17, 1)], [(252, 254, 245), (233, 255, 225), (205, 207, 183), (214, 230, 195), (250, 251, 227)], [(156, 221, 200), (191, 216, 173), (221, 217, 171), (247, 175, 99), (99, 61, 46)], [(170, 255, 0), (255, 170, 0), (255, 0, 170), (170, 0, 255), (0, 170, 255)], [(48, 38, 28), (64, 56, 49), (54, 84, 79), (31, 95, 97), (11, 129, 133)], [(209, 49, 61), (229, 98, 92), (249, 191, 118), (142, 178, 197), (97, 83, 117)], [(255, 225, 129), (238, 233, 229), (250, 211, 178), (255, 186, 127), (255, 156, 151)], [(115, 200, 169), (222, 225, 182), (225, 184, 102), (189, 85, 50), (55, 59, 68)]]
    if colorindex is None:
        colorindex = random.randrange(len(schemes))
        while colorindex == 74:
            colorindex = random.randrange(len(schemes))
    colors = [(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255) for rgb in schemes[colorindex % len(schemes)]]
    
    if seed is None:
        seed = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    rng = random.Random(seed)
    printAt(16, seed)
    
    dwg = svgwrite.Drawing(title = "Mandala {}/{}/{}".format(nsym, seed, colorindex), width = 700, height = 700, viewBox = ("-1 -1 2 2"), preserveAspectRatio="xMidYMin", debug = False)
    dwg.add(dwg.rect((-1, -1), (2, 2), fill = "white"))
    
    mandala = generateMandala(nsym = nsym, mirror = mirror, ntries = 200, distance = 0.4, minsize = 0.011, ribbon = 0.03, colors = colors, rng = rng)
    for cell, color in mandala:
        for svgpath in shapetopaths(dwg, cell, fill = color):
            dwg.add(svgpath)

    print()
    return dwg.tostring().replace("/><", "/>\n<")
    

if __name__ == '__main__':  
    try:
        width, height = 700, 700
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