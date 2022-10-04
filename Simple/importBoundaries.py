import csv
import numpy as np
import pprint
import math

def rotateNode(angle, node):
    # add check for node and angle

    l = math.sqrt(node[0] ** 2 + node[1] ** 2)
    #if node[1] == 0 and node[0] >= 0:
    #    theta = 0
    #elif node[1] == 0 and node[0] < 0:
    #    theta = math.pi
    #else:
    #if node[1] != 0:
    theta = math.atan2(node[1], node[0])
    #else:
    #    theta = 0
    
    theta = theta + math.radians(-angle)
    
    x = l * math.cos(theta)
    y = l * math.sin(theta)
    
    return (x, y)


def importNodes(fileName, length, resolution):
    pp = pprint.PrettyPrinter(indent=4)

    nodes = []
    angle = 20 #degrees
    rotatedNodes = []

    with open(fileName, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            nodes.append([float(x) * length for x in row])

    for node in nodes:
        rotatedNodes.append(rotateNode(angle, node))

    boundaryNodes = []

    xs, ys = zip(*rotatedNodes)

    for x in range(0, length + 1, resolution):
        yVal = int(round(abs(np.interp(x, xs, ys))))
        boundaryNodes.append([x, yVal, -yVal])

    #pp.pprint(boundaryNodes)

    with open('out.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(boundaryNodes)

    return boundaryNodes
