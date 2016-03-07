#!/usr/bin/env python

"""
This module facilitates creating images for the 3D POV display.

Use it as follows:
- open python shell in the same directory as this file
>>> from mkmodel import *
>>> image = newImage()
- Modify the image using all the provided functions
>>> writeSketch(image, 'sketchName')
- Open the file in ./sketchName/sketchName.ino using the arduino
  IDE and upload it to the display



Coordinate formats: 
polar (angle 0-99, height 0-9, radius 0-15)
cartesian (x, y, z) [mm]

Voxel format: 0b010 (all colors defined below)
	            rgb
"""

from matplotlib import pyplot as plt
from itertools import combinations
from random import randint
import numpy as np
import math
import os

# Settings

# template file, contains the whole program without the preceding
# image definition and #include <SPI.h>
template = 'template.cpp'

# declare colour values
black  = 0b000
blue   = 0b001
green  = 0b010
teal   = 0b011
red    = 0b100
pink   = 0b101
yellow = 0b110
white  = 0b111

def newImage():
	"""
	Return an empty numpy 3-D Array with the dimensions of the image
	"""
	return np.zeros((100, 10, 16), dtype = int)

def randPoint():
	return (randint(0, 99), randint(0, 9), randint(0, 15))

def cartesian(angle, height, radius):
	"""
	Convert polar coordinates to cartesian ones
	Polar: angle [0-99], height [0-9], radius [0-15]
	Cartesian: x [mm], y [mm], z [mm]
	"""

	# 17.4625 is the radius of the innermost LED
	radius_mm = 17.4625 + px_to_mm(radius)
	angle_rad = math.radians(angle * 3.6)

	x_mm = math.cos(angle_rad) * radius_mm
	y_mm = math.sin(angle_rad) * radius_mm

	height_mm = px_to_mm(9 - height)

	return (x_mm, y_mm, height_mm)


def px_to_mm(px):
	"""
	Convert pixels to mm (not perfectly exact since pixels are not evenly spaced)

	Each pixel is assumed to be exactly 125 mil = 3.175 mm
	"""
	return px * 3.175


def point_dst(point_a, point_b):
	"""
	Distance between two points in n-dimensional euclidian space
	point_a, point_b: 3-Tuples with cartesian coordinates, same unit as desired return value
	(Works for any number of dimensions)
	"""
	if (len(point_a) is not len(point_b)):
		raise ValueError("Point A is {}-dimensional but point B is {}-dimensional".format(len(point_a), len(point_b)))
	return math.sqrt(sum([(a - b) ** 2 for a,b in zip(point_a, point_b)]))


def angle_law_of_cosines(a, b, c):
	"""
	Calculate the angle between the sides {b} and {c} in a triangle with
	side lengths {a}, {b} and {c}.
	"""
	# Law of cosines
	cos_of_angle = float(-(a**2) + (b**2) + (c**2)) / float(2*b*c)

	# This is necessary because when b or c are very small, floating 
	# point inaccuracies make |cos_of_angle| > 1 which makes the
	# return value undefined
	if cos_of_angle > 1:
		cos_of_angle = 1
	elif cos_of_angle < -1:
		cos_of_angle = -1

	return math.acos(cos_of_angle)


def point_line_dst(point, line_start, line_end, cylinder=False):
	"""
	Calculates the minimum distance between {point} and the line between 
	{line_start} and {line_end} points. All arguments are cartesian (x,y,z).

	If the closest point is not between {line_start} and {line_end}, the distance 
	between {point} and the closest end point of the line is returned instead.

	If cylinder is set to true, we instead return 2**63 - 1 for points beyond line_start and line_end
	"""
	# These points are of course on the line, but would result in division by 0
	if point == line_start or point == line_end:
		return 0.0

	# If the start and end point are equal (line is undefined), we'll just
	# treat the line as a point.
	if (line_start == line_end):
		return point_dst(line_start, point)

	# Calculate side lengths of triangle start-end-point
	line_len = point_dst(line_start, line_end)
	start_to_point = point_dst(line_start, point)
	end_to_point = point_dst(line_end, point)

	# Calculate angles in that triangle (all in radians)
	angle_start = angle_law_of_cosines(end_to_point, line_len, start_to_point)
	angle_end = angle_law_of_cosines(start_to_point, line_len, end_to_point)
	# 180° - (two angles) = last angle
	angle_point = math.pi - angle_start - angle_end

	if cylinder:
		# If we want to display a cylinder, return a very high value so that no point
		# beyond the two end points is matched
		return 9223372036854775807
	else:
		# In case the nearest point on the line is not between start and end, 
		# we'll instead return the distance to the nearest end point of the line
		# 1.5707963 rad = 90° = π/2
		if angle_point < 1.5707963 - angle_start:
			return point_dst(point, line_end)
		if angle_point < 1.5707963 - angle_end:
			return point_dst(point, line_start)
	
	# Height of the triangle between line_start, line_end and point
	# is equivalent to distance from point to line
	triangle_height = start_to_point * math.sin(angle_start)

	return triangle_height





def drawLine(image, start, end, colour, thickness):
	"""
	or-equals all pixels in {image} that are closer to the line (between {start}
	and {end}) than {thickness} with the {colour} value (int, 0-7).

	All arguments are in cartesian and mm 
	"""
	for (angle, height, radius), value in np.ndenumerate(image):
		cart = cartesian(angle, height, radius)
		if (point_line_dst(cart, start, end) <= thickness):
			image[angle][height][radius] |= colour


def drawLinePolar(image, start, end, colour, thickness):
	"""
	Converts all arguments from polar to cartesian and then calls drawLine
	"""
	start = cartesian(*start)
	end = cartesian(*end)
	thickness = px_to_mm(thickness)
	drawLine(image, start, end, colour, thickness)


def drawSphere(image, position, colour, radius):
	"""
	Draws a line of length 0, resulting in a sphere
	"""
	drawLine(image, position, position, colour, radius)


def drawSpherePolar(image, position, colour, radius):
	"""
	Converts all arguments from polar to cartesian and then calls drawSphere
	"""
	position = cartesian(*position)
	radius = px_to_mm(radius)
	drawLine(image, position, position, colour, radius)

def plotFunction(function, colour):
	"""
	Plot a function (x, y, z) [mm] -> colour [0-7]
	"""
	for (angle, height, radius), value in np.ndenumerate(image):
		image[angle][height][radius] |= function(*cartesian(*(angle, height, radius)))


def fadenbild_bruteforce(image, radius, interval, twist, colour, thickness):
	"""
	Plots a 'fadenbild', where two circles are connected by a number of lines
	(strings) and are twisted with respect to each other
	"""
	for i in range(0, 100, interval):
		drawLinePolar(image, (i, 0, radius), ((i+twist) % 100, 9, radius), colour, thickness)


#               image    Num
def drawSurface(image, surface_params, colour, thickness):
	"""
	Plot a surface on {image} defined by {a}x + {b}y + {c}z = d
	{colour} = color of the surface (0-7)
	{thicknes} = guess what [mm]
	"""

	(a, b, c, d) = surface_params

	limit = 0.5 * thickness

	for (angle, height, radius), value in np.ndenumerate(image):
		(x, y, z) = cartesian(angle, height, radius)
		if (abs((a * x) + (b * y) + (c * z) - d) < limit):
			image[angle][height][radius] |= colour 

def drawSurfacePx(image, surface_params, colour, thickness):
	(a, b, c, d) = surface_params
	drawSurface(image, (a,b,c, px_to_mm(d)), colour, px_to_mm(thickness))

def connectCircle(image, pointList, colour, thickness):
	"""
	Connect each given point to the next one using drawLine, including
	the last one to the first one.
	image: ndarray of 3d image as given by getImage()
	pointList: List of cartesian points :: [(int, int, int)]
	colour/thickness: Same as drawLine
	"""
	for (start, end) in zip(pointList, pointList[1:]):
		drawLine(image, start, end, colour, thickness)
	drawLine(image, pointList[-1], pointList[0], colour, thickness)

def connectCirclePolar(image, pointList, colour, thickness):
	"""
	Same as connectCircle, but with polar coordinates instead of
	cartesian ones
	"""
	for (start, end) in zip(pointList, pointList[1:]):
		drawLinePolar(image, start, end, colour, thickness)
	drawLinePolar(image, pointList[-1], pointList[0], colour, thickness)

def connectAll(image, pointList, colour, thickness):
	"""
	Connect every given point with every other one.
	SNAIL ALARM: O(n^2)
	"""
	for (start, end) in combinations(pointList, 2):
		drawLine(image, start, end, colour, thickness)

def connectAllPolar(image, pointList, colour, thickness):
	for (start, end) in combinations(pointList, 2):
		drawLinePolar(image, start, end, colour, thickness)

def drawCuboid(image, point, oppositePoint, colour, thickness):
	(x0, y0, z0) = point
	(x1, y1, z1) = oppositePoint

	bottom = [(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)]
	top    = [(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)]

	connectCircle(image, bottom, colour, thickness)
	connectCircle(image, top, colour, thickness)

	for (b, t) in zip(bottom, top):
		drawLine(image, b, t, colour, thickness)

def drawCuboidPolar(image, point, oppositePoint, colour, thickness):
	point, oppositePoint = cartesian(*point), cartesian(*oppositePoint)
	thickness = px_to_mm(thickness)
	drawCuboid(image, point, oppositePoint, colour, thickness)


# ---------------------------------------------------------------------- #

"""
The following functions generate and save an Arduino program for the 3D
display with the given image
"""

def getColourString(voxel):
	"""
	Get a fixed-width binary string representation
	"""
	assert (voxel <= 7), 'Only the last 3 bits may be set'
	return '{0:03b}'.format(voxel)


def printImage(image):
	"""
	Print C representation of image
	"""
	print(getImage(image))


def getImage(image):
	"""
	Generate C array literal representing the image
	"""
	startString = 'const byte image[100][10][16] = {\n'
	endString = '\n};\n\n'
	return startString + '\n'.join(sliceForC(sl, i) for i, sl in enumerate(image)) + endString


def getProgram(image):
	"""
	Generates image array literal, appends template file to it, returns that
	"""
	infile = open(template, 'r')
	lines = infile.readlines()
	infile.close()

	preprocessor = '#include <SPI.h>\n\n'
	imageArrayLiteral = getImage(image)
	program = ''.join(lines)

	return preprocessor + imageArrayLiteral + program


def sliceForC(angSlice, index):
	"""
	Get a slice of the image as a C array literal
	"""
	startString = '\t// {0:02}\n\t{{\n'.format(index)
	endString = '\n\t}'
	if index != 99:
		endString += ',\n'
	return startString + ',\n'.join(lineForC(line) for line in angSlice) + endString


def lineForC(line):
	"""
	Get a line of the image as a C array literal
	"""
	# Get a string representation of the binary data for that LED row
	colourString = ''.join([getColourString(voxel) for voxel in line])
	assert len(colourString) == 48, "Length of colourString is {}, should be 48".format(len(colourString))

	# Print them in chunks of 8 so that they're one byte in C
	cByteLiterals = ['0b' + i for i in chunks(colourString, 8)]
	return '\t\t{' + ', '.join(cByteLiterals) + '}'


def chunks(string, chunksize):
	"""
	Splits a string in chunks of given length
	"""
	return [string[i:i+chunksize] for i in range(0, len(string), chunksize)]


def writeSketch(image, name):
	"""
	Uses all of the above methods to get the Teensy program with the given image, 
	and writes that to a ./$name/$name.ino
	"""
	dirname = name.replace('.ino', '')

	try:
		os.mkdir(dirname)
	except OSError:
		print('Directory already exists. Delete it or choose another name.')
		return

	if not name.endswith('.ino'):
		name += '.ino'

	filepath = os.path.join(dirname, name)
	with open(filepath, 'w') as outfile:
		outfile.write(getProgram(image))
		print('Wrote sketch to ./' + filepath)






