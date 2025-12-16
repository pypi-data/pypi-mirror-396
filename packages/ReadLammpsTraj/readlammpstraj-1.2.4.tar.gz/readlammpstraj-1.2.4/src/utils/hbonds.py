# calculate h-bonds
from water import Water
from tqdm import tqdm
from itertools import combinations
import numpy as np
import json

def boundary(dVect, lx, ly, lz):
	boundaries = np.array([lx, ly, lz]) * 0.5
	dVect = np.where(dVect >= boundaries, dVect - boundaries * 2, np.where(dVect <= -boundaries, dVect + boundaries * 2, dVect))
	return dVect

def calc_distance(dVect):
	d = np.linalg.norm(dVect)
	return d

def calc_angle(v1, v2):
	# Calculate angle between two vectors in degrees
	cosine_value = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
	cosine_value = np.clip(cosine_value, -1.0, 1.0)
	radian = np.arccos(cosine_value)
	degree = np.degrees(radian)
	return degree

def read_water(traj,typeOfO=1):
	waters  = {}
	for index, row in traj[traj["type"] == str(typeOfO)].iterrows():
		O   = np.array([row["x"],row["y"],row["z"]]).astype(float)
		H1  = traj.loc[index+1,["x","y","z"]].values.astype(float)
		H2  = traj.loc[index+2,["x","y","z"]].values.astype(float)
		waters[row["id"]] = Water(O, H1, H2)
	# print(">>> Read water molecules successfully !")
	return waters

def calc_hbonds(nframe,traj,typeOfO, lx, ly, lz, dist=3.5, angle=45):
	dist_max = np.array([lx,ly,lz])*0.5
	dist_min = -dist_max

	waters = read_water(traj,typeOfO)
	# print(waters)
	hbonds = {}
	total_nhbonds = 0
	# print(f">>> Total number of waters: {len(waters)}")
	for key1, value1 in waters.items():
		hbond = []
		for key2, value2 in waters.items():
			if key1 != key2:
				vector_o2o1 = value1.o-value2.o
				if np.any(vector_o2o1 >= dist_max) or np.any(vector_o2o1 <= dist_min):
					vector_o2o1 = boundary(vector_o2o1, lx, ly, lz)
				dOO = calc_distance(vector_o2o1)
				if dOO <= dist:
					vector_o2h21 = value2.h1-value2.o
					vector_o2h22 = value2.h2-value2.o

					if np.any(vector_o2h21 >= dist_max) or np.any(vector_o2h21 <= dist_min):
						vector_o2h21 = boundary(vector_o2h21,lx, ly, lz)
					if np.any(vector_o2h22 >= dist_max) or np.any(vector_o2h22 <= dist_min):
						vector_o2h22 = boundary(vector_o2h22,lx, ly, lz)

					angle1 = calc_angle(vector_o2o1, vector_o2h21)
					angle2 = calc_angle(vector_o2o1, vector_o2h22)

					if angle1 <= angle:
						total_nhbonds += 1
						hbond.append(int(key2))
					elif angle2 <= angle:
						total_nhbonds += 1
						hbond.append(int(key2))
		if hbond:
			hbonds.update({int(key1):hbond})

	return (hbonds, total_nhbonds)

