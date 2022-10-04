import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rcParams
from importBoundary import importNodes
import math
import time
import datetime

plot_every = 50
rcParams['animation.convert_path'] = r'/usr/bin/convert'

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

def importObjects(objs, fileName, Mx, P, wingLength, latticResolution):
	nodes = importNodes(fileName, wingLength, latticResolution)
	for point in nodes:
		for y in range(point[2] + P[1], point[1] + P[1]):
			objs[y][point[0]+P[1]] = True
	return objs

def setupObjects(My, Mx):
	objects = np.full((My, Mx), False)

	#objects = cylinder(objects, My, Mx, 0.25 * Mx, 0.5 * My, 13)
	#objects = rectangle(objects, My, Mx, 0.25 * Mx, 0.5 * My, 26, 26)
	#objects = rectangle(objects, My, Mx, 0.25 * Mx, 0.5 * My, 10, 60)
	#objects = hollowHalfCylinder(objects, My, Mx, 0.25 * Mx, 0.5 * My, 13, 10)
	#objects = rightTriangle(objects, My, Mx, 0.25 * My, 0.75 * Mx, 40, 40)

	objects = importObjects(objects, "naca0012.csv", Mx, [40, 100], 100, 1)
	return objects

def main():
	start = time.time()

	Nx = 800 # Number of nodes in the x direction
	Ny = 200 # Number of nodes in the y direction
	tau = 0.53 # Time constant for collision equation
	Nt = 10 # Number of time steps

	Nl = 9 # 
	cxs = np.array([0,0,1,1,1,0,-1,-1,-1])
	cys = np.array([0,1,1,0,-1,-1,-1,0,1])
	wts = np.array([4/9, 1/9, 1/36, 1/9, 1/36, 1/9, 1/36, 1/9, 1/36])

	F = np.ones((Ny, Nx, Nl)) + 0.01 * np.random.randn(Ny, Nx, Nl)

	F[:, :, 3] = 2 # velocity in terms of relative speed of sound

	# setup object in lattice
	obj = setupObjects(Ny, Nx)

	# Setup of plotting objects
	f, [ax1, ax2] = plt.subplots(2,1)
	ims = []

	for it in range(Nt):
		progString = math.floor((it+1) * 10/ Nt) * "=" + (10 - math.floor((it+1) * 10/ Nt)) * " "
		timeInt = round(time.time() - start)
		percInt = math.floor(100*it/Nt) + 1
		print(f"\r{it}/{Nt}" + "[" + progString + "]" + f"({percInt}%, {timeInt} sec)", end="")

		F[:, -1, [6, 7, 8]] = F[:, -2, [6, 7, 8]]
		F[:, 0, [2, 3, 4]] = F[:, 1, [2, 3, 4]]

		for i, cx, cy in zip(range(Nl), cxs, cys):
			F[:, :, i] = np.roll(F[:, :, i], cx, axis=1)
			F[:, :, i] = np.roll(F[:, :, i], cy, axis=0)

		boundaryF = F[obj,:]
		boundaryF = boundaryF[:, [0, 5, 6, 7, 8, 1, 2, 3, 4]]

		rho = np.sum(F, 2)

		ux = np.sum(F*cxs, 2)/rho
		uy = np.sum(F*cys, 2)/rho

		F[obj, :] = boundaryF

		ux[obj] = 0
		uy[obj] = 0

		Feq = np.zeros(F.shape)

		for i, cx, cy, w in zip(range(Nl), cxs, cys, wts):
			Feq[:, :, i] = w * rho*(1 + 3 * (cx*ux + cy*uy) + 9 * (cx*ux + cy*uy)**2 / 2 - 3 * (ux**2 + uy**2)/2)

		F = F - (1/tau)*(F-Feq)

		if(it%plot_every == 0):
			dfxdy = ux[2:, 1:-1] - ux[0:-2, 1:-1]
			dfydx = uy[1:-1, 2:] - uy[1:-1, 0:-2]
			curl = dfxdy - dfydx
			velo = np.sqrt(ux**2 + uy**2)

			im1 = ax1.imshow(curl, cmap='bwr', animated=True)

			im2 = ax2.imshow(velo, animated=True)
			ims.append([im1, im2])
	progString = math.floor((it+1) * 10/ Nt) * "=" + (10 - math.floor((it+1) * 10/ Nt)) * " "
	timeString = str(round(time.time() - start))
	print(f"\r{(it+1)}/{Nt}" + "[" + progString + "]" + f"({math.floor(100*(it+1)/Nt)}%)" + " " + timeString, end="")		
	
	print("\nSaving results...")
	ani = animation.ArtistAnimation(f, ims, interval=50, blit=True, repeat_delay=1000)

	writer = animation.FFMpegWriter(
		fps=15, metadata=dict(artist='Me'), bitrate=1800)
	ani.save("movie.mp4", writer=writer)
	print("Finished.")


if __name__ == "__main__":
	main()
