import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rcParams
from importBoundaries import airFoil
import math
import time
import datetime
import os

currentPath = os.path.dirname(__file__)

rcParams['animation.convert_path'] = r'/usr/bin/convert'

def importFoil(objs, fileName, Mx, P, wingLength, latticResolution, angle):
	nodes = airFoil(fileName, wingLength, angle, latticResolution)

	for point in nodes:
		for y in range(point[1] + P[1], point[2] + P[1]):
			objs[y][point[0]+P[1]] = True

	return objs


def setupObjects(My, Mx, foilPath, angle):
	objects = np.full((My, Mx), False)

	objects = importFoil(objects, foilPath, Mx, [40, 100], 100, 1, angle)
	return objects


def main():
	start = time.time()

	Nx = 800 # Number of nodes in the x direction
	Ny = 200 # Number of nodes in the y direction
	tau = 0.53 # Time constant for collision equation
	Nt = 100 # Number of time steps
	Nl = 9 # Number of nodes around a lattice node
	angle = 5

	foilNumber = 'naca0012'
	foilPath = os.path.join(currentPath, r'../../Foils/' + foilNumber + '.csv')

	cxs = np.array([0,0,1,1,1,0,-1,-1,-1])
	cys = np.array([0,1,1,0,-1,-1,-1,0,1])
	wts = np.array([4/9, 1/9, 1/36, 1/9, 1/36, 1/9, 1/36, 1/9, 1/36])

	F = np.ones((Ny, Nx, Nl)) + 0.01 * np.random.randn(Ny, Nx, Nl)

	F[:, :, 3] = 2 # velocity in terms of relative speed of sound

	# setup object in lattice
	obj = setupObjects(Ny, Nx, foilPath, angle)

	# Setup of plotting objects
	f, [ax1, ax2] = plt.subplots(2,1)
	ims = []

	for it in range(Nt):
		# Print status
		progString = math.floor((it+1) * 10/ Nt) * "=" + (10 - math.floor((it+1) * 10/ Nt)) * " "
		timeInt = round(time.time() - start)
		percInt = math.floor(100*it/Nt) + 1
		print(f"\r{it}/{Nt}" + "[" + progString + "]" + f"({percInt}%, {timeInt} sec)", end="")

		# set window boundary conditions
		F[:, -1, [6, 7, 8]] = F[:, -2, [6, 7, 8]]
		F[:, 0, [2, 3, 4]] = F[:, 1, [2, 3, 4]]

		for i, cx, cy in zip(range(Nl), cxs, cys):
			F[:, :, i] = np.roll(F[:, :, i], cx, axis=1)
			F[:, :, i] = np.roll(F[:, :, i], cy, axis=0)

		# Set object condition to oppposite
		boundaryF = F[obj,:]
		boundaryF = boundaryF[:, [0, 5, 6, 7, 8, 1, 2, 3, 4]]

		# Calc density, ux, and uy
		rho = np.sum(F, 2)
		ux = np.sum(F*cxs, 2)/rho
		uy = np.sum(F*cys, 2)/rho

		# Import boundary from initial setup
		F[obj, :] = boundaryF

		# Set boundary velocities to 0
		ux[obj] = 0
		uy[obj] = 0

		# Set equilibrium function shape of 0
		Feq = np.zeros(F.shape)

		# Calculate the equilibrium function
		for i, cx, cy, w in zip(range(Nl), cxs, cys, wts):
			Feq[:, :, i] = w * rho*(1 + 3 * (cx*ux + cy*uy) + 9 * (cx*ux + cy*uy)**2 / 2 - 3 * (ux**2 + uy**2)/2)

		# Update flow profile
		F = F - (1/tau)*(F-Feq)

		# Calculate curl
		dfxdy = ux[2:, 1:-1] - ux[0:-2, 1:-1]
		dfydx = uy[1:-1, 2:] - uy[1:-1, 0:-2]
		curl = dfxdy - dfydx

		# Calculate velocity
		velo = np.sqrt(ux**2 + uy**2)

		# Set first axis to curl, second to velocity, and append to ims
		im1 = ax1.imshow(curl, cmap='bwr', animated=True)
		im2 = ax2.imshow(velo, animated=True)
		ims.append([im1, im2])

	# Print final stats
	progString = math.floor((it+1) * 10/ Nt) * "=" + (10 - math.floor((it+1) * 10/ Nt)) * " "
	timeInt = round(time.time() - start)
	percInt = math.floor(100*it/Nt) + 1
	print(f"\r{it+1}/{Nt}" + "[" + progString + "]" + f"({percInt}%, {timeInt} sec)", end="")	
	
	# Begin saving
	print("\nSaving results...")
	ani = animation.ArtistAnimation(f, ims, interval=50, blit=True, repeat_delay=1000)

	saveName = "Results/" + foilNumber + "_" + str(angle) + "_" + str(Nx) + "x" + str(Ny) + "_" + str(Nt) + "s" + ".mp4"

	writer = animation.FFMpegWriter(
		fps=15, metadata=dict(artist='Me'), bitrate=1800)
	ani.save(saveName, writer=writer)

	# Notify on completed save
	print("Finished.")


if __name__ == "__main__":
	main()
