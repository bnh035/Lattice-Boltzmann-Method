import csv
import numpy as np
import pprint
import math

def rotateNode(angle, node):
    # add check for node and angle

    length = math.sqrt(node[0] ** 2 + node[1] ** 2)
    theta = math.atan2(node[1], node[0])
    
    theta = theta + math.radians(-angle)
    
    x = length * math.cos(theta)
    y = length * math.sin(theta)
    
    return (x, y)


def distance(x1, y1, x2, y2):
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)


def ellipseDistance(x1, y1, x2, y2, a, b):
    return np.sqrt((x1-x2//a)**2 + (y1-y2//b)**2)


def rectangle(objs, My, Mx, xc, yc, xside, yside):
    for y in range(0, My):
        for x in range(0, Mx):
            if(x > xc - 0.5 * xside and x < xc + 0.5 * xside and y > yc - 0.5 * yside and y < yc + 0.5 * yside):
                objs[y][x] = True
    return objs


def ellipse(objs, My, Mx, xc, yc, xaxis, yaxis):
    for y in range(0, My):
        for x in range(0, Mx):
            if(ellipseDistance(xc, yc, x, y, xaxis, yaxis)<1):
                objs[y][x] = True
    return objs


def rightTriangle(objs, My, Mx, xc, yc, xside, yside):
    for y in range(0, My):
        for x in range(0, Mx):
            if(x > 0.25 * Mx and x < 0.25 * Mx + xside and y > 0.5 * My and y < 0.5 * My + yside * (x - 0.25 * Mx) / xside):
                objs[y][x] = True
    return objs


def cylinder(objs, My, Mx, xc, yc, r):
    for y in range(0, My):
        for x in range(0, Mx):
            if(distance(xc, yc, x, y) < r):
                objs[y][x] = True
    return objs


def halfCylinder(objs, My, Mx, xc, yc, r):
    for y in range(0, My):
        for x in range(0, Mx):
            if(distance(xc, yc, x, y) < r and x < xc):
                objs[y][x] = True
    return objs


def hollowHalfCylinder(objs, My, Mx, xc, yc, r1, r2):
    for y in range(0, My):
        for x in range(0, Mx):
            if(distance(xc, yc, x, y) < r1 and distance(xc, yc, x, y) > r2 and x > xc):
                objs[y][x] = True
    return objs


def airFoil(fileName, length, angle, resolution):
    pp = pprint.PrettyPrinter(indent=4)

    nodes = []
    rotatedNodes = []

    with open(fileName, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            nodes.append([float(x) * length for x in row])

    for node in nodes:
        rotatedNodes.append(rotateNode(angle, node))

    boundaryNodes = []

    xs, ys = zip(*rotatedNodes)
    xs1 = xs[:len(xs)//2]
    xs2 = xs[len(xs)//2:]
    ys1 = ys[:len(ys)//2]
    ys2 = ys[len(ys)//2:]

    for x in range(0, length + 1, resolution):
        yVal1 = int(round(abs(np.interp(x, xs1, ys1))))
        yVal2 = int(round(abs(np.interp(x, xs2, ys2))))
        boundaryNodes.append([x, yVal1, yVal2])

    return boundaryNodes
