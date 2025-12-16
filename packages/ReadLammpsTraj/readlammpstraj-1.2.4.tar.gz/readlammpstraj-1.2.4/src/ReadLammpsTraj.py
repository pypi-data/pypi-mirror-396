# calculating the density,msd and rdf from lammps traj
# id mol type mass x y z vx vy vz fx fy fz q
import numpy as np 
import pandas as pd
from scipy.integrate import simpson, trapezoid
from tqdm import tqdm
import datetime
from itertools import islice
import periodictable as pt
import time
import functools
import readlammpsdata as rld

def __version__():
	with open('./__init__.py', 'r', encoding='utf-8') as f:
		data = json.load(f)
	version = data["version"]
	return version

def print_line(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		print(21*"-"," Program Start ",21*"-")
		start_time = time.time()
		results = func(*args, **kwargs)
		end_time = time.time()
		elapsed_time = end_time - start_time
		print(20*"-","Run time:",round(elapsed_time,2),"s ",20*"-")
		return results
	return wrapper

def __print_version__():
	cloud = [
			"______                   _    _       _____                 _ ",
			"| ___ \                 | |  | |     |_   _|               (_)",
			"| |_/ /  ___   __ _   __| |  | |       | |   _ __   __ _    _ ",
			"|    /  / _ \ / _` | / _` |  | |       | |  | '__| / _` |  | |",
			"| |\ \ |  __/| (_| || (_| |  | |____   | |  | |   | (_| |  | |",
			"\_| \_| \___| \__,_| \__,_|  \_____/   \_/  |_|    \__,_|  | |",
			"                                                          _/ |",
			"                                                         |__/ ",
	]
	n = 32
	print(n*"- ")
	print(n*". ")
	for line in cloud:
		print(line)
	version = __version__()
	print('@ReadLammpsTraj-'+version,", Good Luck!")
	print(n*". ")
	print(n*"- ")
	current_datetime = datetime.datetime.now()
	return print("Time:",current_datetime)


def element2mass(elements,modify=False):
	"""
	elements to masses
	Parameters:
	elements: a list of elements
	modify: need to modify mass, default False, modify={"C": 16.043}
	"""
	allelements = pt.elements
	# print(elements)
	masses = []
	for elementi in elements:
		for elementj in allelements:
			if modify == False:
				if elementi == elementj.symbol:
					masses.append(elementj.mass)
			else:
				if elementi == elementj.symbol:
					for key, value in modify.items():
						if elementi == key:
							masses.append(value)
						else:
							masses.append(elementj.mass)
	return masses



def array2str(array):
	"""
	convert a array to string format for writing directly. 
	array: a array
	"""

	array = array.astype(str)

	string = ""

	for row in array:
		string += "  ".join(row)+"\n"
	string = "\n"+string+"\n"
	
	return string

def unwrap_coordinates(xyzs, lxs, lys, lzs):
	# Unwrap xyzs based on box vectors
	nf, m, n = xyzs.shape
	# for i in tqdm(range(1, nf),desc="Unwrap coordinates"):
	for i in range(1, nf):
		displacement = xyzs[i] - xyzs[i-1]
		dVect = boundary(displacement,lxs[i],lys[i],lzs[i])
		for j in range(n):
			xyzs[i] = xyzs[i-1] + dVect
	return xyzs

def boundary(dVect, lx, ly, lz):
	boundaries = np.array([lx, ly, lz]) * 0.5
	dVect = np.where(dVect >= boundaries, dVect - boundaries * 2, np.where(dVect <= -boundaries, dVect + boundaries * 2, dVect))
	# m, n = dVect.shape
	# lx2 = lx/2
	# ly2 = ly/2
	# lz2 = lz/2
	# for i in range(1,m):
	# 	if dVect[i][0] > lx2:
	# 		while dVect[i][0] > lx2:
	# 			dVect[i][0] -= lx
	# 	elif dVect[i][0] < -lx2:
	# 		while dVect[i][0] < -lx2:
	# 			dVect[i][0] += lx
	
	# 	if dVect[i][1] > lx2:
	# 		while dVect[i][1] > ly2:
	# 			dVect[i][1] -= ly
	# 	elif dVect[i][1] < -ly2:
	# 		while dVect[i][1] < -ly2:
	# 			dVect[i][1] += ly
	
	# 	if dVect[i][2] > lz2:
	# 		while dVect[i][2] > lz2:
	# 			dVect[i][2] -= lz
	# 	elif dVect[i][2] < -lz2:
	# 		while dVect[i][2] < -lz2:
	# 			dVect[i][2] += lz
	
	return dVect

def select_atoms(iframe,atomtype):
	condition = (iframe['type'].astype(int).isin(atomtype))
	df_select = iframe[condition]
	xyz = df_select[["x","y","z"]].values.astype(float)
	return xyz

# def select_atoms_return_idxyz(iframe,atomtype):
# 	condition = (iframe['type'].astype(int).isin(atomtype))
# 	df_select = iframe[condition]
# 	idxyz = df_select[["id","x","y","z"]].values
# 	return idxyz

def select_atoms_return_idxyz(iframe,atomtype):
	"""
	- iframe, a dataframe
	- atomtype, a dict
	"""
	key = list(atomtype.keys())[0]
	if key == "atom_id":
		condition = (iframe['id'].astype(int).isin(atomtype[key]))
		df_select = iframe[condition]

	elif key == "atom_type":
		condition = (iframe['type'].astype(int).isin(atomtype[key]))
		df_select = iframe[condition]
	else:
		pass
		print(">>> Warning: your key is error!!!")
	idxyz = df_select[["id","x","y","z"]].values
	return idxyz


def read_nframe(f):
	"""
	read the nframe info
	Parameters:
	- f: ave/chunk dump file
	"""
	with open(f,"r") as fo:
		for i in range(4):
			line = fo.readline()
		temp = line.strip().split()
		nbin = int(temp[1]) # Number-of-chunks
		lines = fo.readlines()
	nframe = int((len(lines)+1)/(nbin+1)) # dump number of frame
	return nbin, nframe

def average_avechunk(f,nframe=None,fr=None):
	"""
	average the data of every nframes
	Parameters:
	- f: ave/chunk dump file
	- nframe: number of frame
	- fr: frame range [start,stop] or [start,stop,interval]
	"""
	nbin, nf = read_nframe(f) # read the number of chunks and number of frames
	if nframe:
		n0 = 0
		nf = nframe
		inter = 1
	elif fr:
		n0 = fr[0]
		nf = fr[1]
		try:
			inter = fr[2]
		except:
			inter = 1
	else:
		n0 = 0
		inter = 1
	data0 = np.loadtxt(f,skiprows=4,max_rows=nbin) # read first frame
	sum_data = np.zeros_like(data0)
	for i in tqdm(range(n0,nf,inter)):
		skip = 3 + (i + 1) + nbin * i
		data = np.loadtxt(f,skiprows=skip,max_rows=nbin).astype(float)
		sum_data += data
	average_data = sum_data/np.ceil((nf-n0)/inter)
	return average_data



class ReadLammpsTraj(object):
	"""Read lammps trajectory file"""
	def __init__(self,f):
		super(ReadLammpsTraj, self).__init__()
		self.f = f
		self.amu2g = 6.02214076208112e23
		self.A2CM = 1e-8 
		self.read_info()

	def read_info(self,):
		header = []
		with open(self.f,'r') as f:
			for line in islice(f, 0, 9):
				header.append(line)
		self.natoms = int(header[3])
		try:
			header0 = self.read_header(0)
			header1 = self.read_header(1)
			self.step_inter = int(header1[1])-int(header0[1])
		except:
			self.step_inter = 1
			print(">>> Warning: No extra frames for 'step_inter'...")
		self.col = header0[8].strip().split()[2:]

		box = self.read_box(0)
		self.xlo,self.xhi = box["xhi"], box["xlo"]
		self.ylo,self.yhi = box["yhi"], box["ylo"]
		self.zlo,self.zhi = box["zhi"], box["zlo"]
		self.Lx = abs(self.xhi-self.xlo)
		self.Ly = abs(self.yhi-self.ylo)
		self.Lz = abs(self.zhi-self.zlo)
		return self.step_inter, self.natoms, self.Lx, self.Ly, self.Lz

	def read_header(self,nframe):
		"""
		read header of nth-frame
		Parameters:
		- nframe: number of frame
		Return a list
		"""
		# try:
		skip = int(9*(nframe)+self.natoms*(nframe))
		# except:
		# 	skip = 0
		header = []
		with open(self.f,'r') as f:
			for line in islice(f,skip,skip+9):
				header.append(line)
		return header

	def read_traj(self,nframe):
		"""
		read data of nth frame from traj...
		nframe: number of frame 
		"""
		skip = 9*(nframe+1)+self.natoms*(nframe)
		# traj = np.loadtxt(self.f,skiprows=skip,max_rows=self.natoms,dtype="str")
		traj = np.genfromtxt(self.f,skip_header=skip,max_rows=self.natoms,dtype="str")
		traj = pd.DataFrame(traj,columns=self.col)
		traj["id"] = pd.to_numeric(traj["id"],errors='coerce').astype("Int64")
		traj = traj.sort_values(by="id")
		traj.set_index('id', inplace=True, drop=False)
		traj.rename_axis('', inplace=True)
		traj.index = traj.index - 1
		return traj

	def read_num_of_frames(self):
		natoms = self.natoms
		inputfile = self.f
		with open(inputfile,"r") as f:
			lines = f.readlines()
		total_nframe = int(len(lines)/(natoms+9))

		return total_nframe


	def read_steps(self):
		total_nframe = self.read_num_of_frames()
		natoms = self.natoms
		inputfile = self.f
		steps = []
		with open(inputfile,"r") as f:
			for index, line in enumerate(f):
				for j in range(total_nframe):
					if index == (natoms+9)*j+1:
						steps.append(int(line.strip()))
		return steps

	def read_item(self,item):
		traj = self.read_traj(0)
		if item in ["id","mol","type"]:
			traj[item] = pd.to_numeric(traj[item],errors='coerce').astype("Int64")
			item_data = traj[item].values.tolist()
		elif item in ["mass","x","y","z","xs","ys","zs","xu","yu","zu","xsu","ysu","zsu",
					  "ix","iy","iz","vx","vy","vz","fx","fy","fz","q","mux","muy","muz",
					  "mu","radius","diameter","omegax","omegay","omegaz","angmomx","angmomy","angmomz",
					  "tqx","tqy","tqz","heatflow","temperature"]:
			traj[item] = pd.to_numeric(traj[item],errors='coerce').astype("Float64")
			item_data = traj[item].values.tolist()
		elif item in ["element"]:
			item_data = traj[item].values.tolist()
			# item_data = " ".join(item_data)
		else:
			item_data = traj[item].values.tolist()

		return item_data

	def read_types(self):
		types  = self.read_item("type")
		types, index = np.unique(np.array(types),return_index=True)
		types = types[np.argsort(index)].tolist()
		return types

	def read_elements(self):
		elements  = self.read_item("element")
		elements, index = np.unique(np.array(elements),return_index=True)
		elements = elements[np.argsort(index)].tolist()
		return elements

	def read_box(self,nframe):
		"""
		read box from header
		Parameters:
		nframe: number of frame
		Return a dict
		"""
		header = self.read_header(nframe)
		xlo = float(header[5].split()[0])
		xhi = float(header[5].split()[1])
		ylo = float(header[6].split()[0])
		yhi = float(header[6].split()[1])
		zlo = float(header[7].split()[0])
		zhi = float(header[7].split()[1])
		box = {
				"xlo": xlo,
				"xhi": xhi,
				"ylo": ylo,
				"yhi": yhi,
				"zlo": zlo,
				"zhi": zhi
		}
		return box

	def read_lengths(self,nframe):
		box = self.read_box(nframe)
		lx = abs(box["xhi"]-box["xlo"])
		ly = abs(box["yhi"]-box["ylo"])
		lz = abs(box["zhi"]-box["zlo"])
		return lx, ly, lz

	def read_vol(self,nframe):
		"""
		read and calculate vol from header
		Parameters:
		nframe: number of frame
		Return a vol value unit/A^3
		"""
		lx, ly, lz = self.read_lengths(nframe)
		vol = lx*ly*lz
		return  vol

	def read_xyz(self,nframe):
		"""
		read x, y, z coordinates of nth frame from traj...
		nframe: number of frame 
		"""
		traj = self.read_traj(nframe)
		xyz = traj.loc[:,"x":"z"].values.astype(np.float64) # x y z
		return xyz


	def read_mxyz(self,nframe,modify=False):
		"""
		read mass, and x, y, z coordinates of nth frame from traj...
		nframe: number of frame 
		modify: need to modify mass, default False, modify={"C": 16.043}
		"""
		traj = self.read_traj(nframe)

		try:
			self.atom = traj.loc[:,"type"].values.astype(np.int64)#id atom type
		except:
			print(">>> No atom types in traj...")

		xyz = traj.loc[:,"x":"z"].values.astype(np.float64) # x y z

		try:
			mass = traj.loc[:,"mass"].values.astype(np.float64)#mass
		except:
			print(">>> No mass out in traj...")
			try:
				self.element = traj.loc[:,"element"].values
				mass = element2mass(self.element,modify=modify)
				mass = np.array(mass)
				print(">>> Read mass from elements successfully !")
			except:
				print(">>> No element types in traj...")
				mass = np.zeros(len(xyz))

		mxyz = np.hstack((mass.reshape(-1,1),xyz))

		position = mxyz

		return position

	def read_mxyz_add_mass(self,nframe,atomtype_list,mass_list):
		# 不区分分子类型，计算所有的密度所需
		traj = self.read_traj(nframe)
		# print(traj)
		self.mol = traj.loc[:,"mol"].values.astype(np.int64)#id mol type
		self.atom = traj.loc[:,"type"].values.astype(np.int64)#id atom type
		xyz = traj.loc[:,"x":"z"].values.astype(np.float64) # x y z
		mass_array = np.zeros(len(xyz)).reshape(-1,1)
		for i in range(len(xyz)):
			for j in range(len(mass_list)):
				if self.atom[i] == atomtype_list[j]:
					mass_array[i] = mass_list[j]
		mxyz = np.hstack((mass_array,xyz))
		return mxyz

	@print_line
	def dump(self,nframe,dumpfile=False):
		header = self.read_header(nframe)
		traj = self.read_traj(nframe).values
		header = "".join(header).strip()
		traj = array2str(traj)
		if dumpfile:
			dumpfile = dumpfile
		else:
			dumpfile = f"{nframe}.lammpstrj"
		with open(dumpfile,"w") as f:
			f.write(header)
			f.write(traj)
		
		return

	@print_line
	def dump_xyz(self,nframe,element=True,del_atoms=False,dumpfile=False):
		"""
		dump xyz from lammpstrj file
		Parameters:
		- nframe: number of frame
		- element: True or False element, default: True
		- del_atoms: A list of atoms contains the ones you want to remove
		- dumpfile: xyz file name
		"""
		traj = self.read_traj(nframe)
		if del_atoms:
			traj = traj[~traj["type"].isin(del_atoms)]
		
		if element:
			xyz = traj[["element","x","y","z"]]
		else:
			xyz = traj[["type","x","y","z"]]
		Natom = len(xyz)
		if dumpfile:
			dumpfile = dumpfile
		else:
			dumpfile = f"{nframe}.xyz"
		current_time = datetime.datetime.now()
		formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
		with open(dumpfile,"w") as f:
			f.write(str(Natom))
			f.write(f"\n{formatted_time}: Generated by dump_xyz in 'ReadLammpsTraj' package!")
			xyz = array2str(xyz.values).strip()

			f.write("\n")
			f.write(xyz)
		
		return


	@print_line
	def dump_minish(self,mframe,nframe,interval=1,dumpfile=False):
		"""
		dump minish lammpstrj file
		Parameters:
		- mframe: start number of frame
		- nframe: end number of frame
		- interval: interval of frame
		- dumpfile: lammpstrj file name
		"""
		if dumpfile:
			dumpfile = dumpfile
		else:
			dumpfile = f"traj_{mframe}_{nframe}.lammpstrj"
		f = open(dumpfile,"w")
		for i in tqdm(range(mframe,nframe+interval,interval)):
			traj = self.read_traj(i).values
			header = self.read_header(i)
			header = "".join(header).strip()
			trajstr = array2str(traj).strip()
			f.write(header)
			f.write("\n")
			f.write(trajstr)
			f.write("\n")
		f.close()
		return

	@print_line
	def dump_unwrap(self,mframe,nframe,interval=1,dumpfile=False):
		"""
		dump unwrap lammpstrj
		Parameters:
		- mframe: start number of frame
		- nframe: end number of frame
		- interval: interval of frame
		- dumpfile: lammpstrj file name
		"""
		if dumpfile:
			dumpfile = dumpfile
		else:
			dumpfile = f"unwrap_{mframe}_{nframe}.lammpstrj"
		f = open(dumpfile,"w")
		trajs = []
		lxs,lys,lzs = [],[],[]
		for i in tqdm(range(mframe,nframe+interval,interval),desc="Reading positions"):
			traj = self.read_traj(i).values.tolist()
			box = self.read_box(i)
			lx = box["xhi"]-box["xlo"]
			ly = box["yhi"]-box["ylo"]
			lz = box["zhi"]-box["zlo"]
			trajs.append(traj)
			lxs.append(lx)
			lys.append(ly)
			lzs.append(lz)
		trajs = np.array(trajs)
		# print(trajs.shape)
		trajs[:,:,-3:] = unwrap_coordinates(trajs[:,:,-3:].astype(float), lxs, lys, lzs)
		for i in tqdm(range(len(trajs)),desc="Unwrap positions"):
			header = self.read_header(i)
			header = "".join(header).strip()
			traj = array2str(trajs[i]).strip()
			f.write(header)
			f.write("\n")
			f.write(traj)
			f.write("\n")
		f.close()
		return
	@print_line
	def oneframe_alldensity(self,nframe,mxyz,Nbin,mass_dict=False,density_type="mass",direction="z"):
		"""
		calculating density of all atoms......
		mxyz: array of mass, x, y, and z;
		Nbin: number of bins in x/y/z-axis
		mass_dict: masses of atoms ,default=False
		density_type: calculated type of density 
		"""

		unitconvert = self.amu2g*(self.A2CM)**3
		box = self.read_box(nframe)
		Lx,Ly,Lz = self.read_lengths(nframe)
		xlo, xhi = box["xlo"], box["xhi"]
		ylo, yhi = box["ylo"], box["yhi"]
		zlo, zhi = box["zlo"], box["zhi"]
		direction = direction.lower()
		if direction=="z":
			dr = Lz/Nbin #z方向bin
			L = mxyz[:,3]
			lo = zlo
			vlo = (Lx*Ly*dr)*unitconvert
		elif direction=="y":
			dr = Ly/Nbin
			L = mxyz[:,2]
			lo = ylo
			vlo = (Lx*Lz*dr)*unitconvert
		elif direction=="x":
			dr = Lx/Nbin
			L = mxyz[:,1]
			lo = xlo
			vlo = (Ly*Lz*dr)*unitconvert
		if mass_dict:
			mass_key=list(mass_dict.keys())
			for i in range(len(self.atom)):
				for j in range(len(mass_key)):
					if self.atom[i] == mass_key[j]:
						mxyz[i,0] = mass_dict[mass_key[j]]
		MW = mxyz[:,0] #相对分子质量

		if np.all(MW==0):
			density_type = "number"
			print("\nNo provided mass, will calculate number density!\n")
		else:
			density_type = "mass"

		rho_n = [] #average density list in every bins
		lc_n  = []
		for n in range(Nbin):
			mass_n=0 #tot mass in bin
			l0 = lo+dr*n #down coord of bin
			l1 = lo+dr*(n+1)#up coord of bin
			lc = (l0+l1)*0.5
			for i in range(self.natoms):
				if L[i]>=l0 and L[i]<=l1:
					if density_type == "mass":
						mass_n = MW[i]+mass_n
					else:
						mass_n = mass_n+1
			rho = mass_n/vlo
			# print(rho)
			rho_n.append(rho)
			lc_n.append(lc)
		lc_n = np.array(lc_n).reshape(-1,1)
		rho_n = np.array(rho_n).reshape(-1,1)

		return lc_n,rho_n
	@print_line
	def oneframe_moldensity(self,nframe,mxyz,Nbin,id_range,mass_dict=False,id_type="mol",density_type="mass",direction="z"):
		"""
		calculating density of some molecules......
		mxyz: array of mass, x, y, and z;
		Nbin: number of bins in x/y/z-axis
		id_range: range of molecule/atom id;
		mass_dict: masses of atoms ,default=False
		id_type: according to the molecule/atom id, to recognize atoms, args: mol, atom
		density_type: calculated type of density 
		"""
		
		unitconvert = self.amu2g*(self.A2CM)**3
		
		box = self.read_box(nframe)
		
		Lx,Ly,Lz = self.read_lengths(nframe)
		xlo, xhi = box["xlo"], box["xhi"]
		ylo, yhi = box["ylo"], box["yhi"]
		zlo, zhi = box["zlo"], box["zhi"]
		direction = direction.lower()
		if direction=="z":
			dr = Lz/Nbin #z方向bin
			L = mxyz[:,3]
			lo = zlo
			vlo = (Lx*Ly*dr)*unitconvert
		elif direction=="y":
			dr = Ly/Nbin
			L = mxyz[:,2]
			lo = ylo
			vlo = (Lx*Lz*dr)*unitconvert
		elif direction=="x":
			dr = Lx/Nbin
			L = mxyz[:,1]
			lo = xlo
			vlo = (Ly*Lz*dr)*unitconvert
		if mass_dict:
			mass_key=list(mass_dict.keys())
			for i in range(len(self.atom)):
				for j in range(len(mass_key)):
					if self.atom[i] == mass_key[j]:
						mxyz[i,0] = mass_dict[mass_key[j]]
		MW = mxyz[:,0] # 相对分子质量
		if np.all(MW==0):
			density_type = "number"
			print("\nNo provided mass, will calculate number density!\n")
		else:
			density_type = "mass"

		rho_n = [] #average density list in every bins
		lc_n  = []
		# print(MW.shape,Z.shape)
		if id_type == "mol":
			id_know = self.mol
		elif id_type == "atom":
			id_know = self.atom
		for n in range(Nbin):
			mass_n=0 #tot mass in bin
			l0 = lo+dr*n #down coord of bin
			l1 = lo+dr*(n+1)#up coord of bin
			lc = (l0+l1)*0.5
			# print(z0,z1,zc)
			for i in range(self.natoms):
				if id_know[i]>=id_range[0] and id_know[i]<=id_range[1]:
					# if i atom in [z0:z1]
					if L[i]>=l0 and L[i]<=l1:
						if density_type == "mass":
							mass_n = MW[i]+mass_n
						else:
							mass_n = mass_n+1
			rho = mass_n/vlo
			# print(rho)
			rho_n.append(rho)
			lc_n.append(lc)
		lc_n = np.array(lc_n).reshape(-1,1)
		rho_n = np.array(rho_n).reshape(-1,1)	
		return lc_n,rho_n
	@print_line
	def TwoD_Density(self,nframe,mxyz,atomtype_n,Nx=1,Ny=1,Nz=1,mass_or_number="mass",id_type="mol"):
		'''
		nframe: n-th frame
		mxyz: mass x y z
		natoms: tot number of atoms
		atomtype_n: type of molecules,list,natoms=[1,36], the 1 is the first atom type and 36 is the last one atom type
		Nx,Ny,Nz: layer number of x , y, z for calculating density, which is relate to the precision of density,
		and default is 1, that is, the total density.
		mass_or_number: "mass: mass density; number: number density"
		id_type:"mol" or "atom" for atomtype_n
		'''
		unitconvert = self.amu2g*(self.A2CM)**3
		box = self.read_box(nframe)
		Lx,Ly,Lz = self.read_lengths(nframe)
		xlo, xhi = box["xlo"], box["xhi"]
		ylo, yhi = box["ylo"], box["yhi"]
		zlo, zhi = box["zlo"], box["zhi"]

		dX = Lx/Nx #x方向bin
		dY = Ly/Ny #y方向bin
		dZ = Lz/Nz #z方向bin

		MW = mxyz[:,0] #相对分子质量
		X = mxyz[:,1] #x
		Y = mxyz[:,2] #y
		Z = mxyz[:,3] #z
		if id_type == "mol":
			id_know = self.mol
		elif id_type == "atom":
			id_know = self.atom
		xc_n,yc_n,zc_n = [],[],[]
		rho_n = [] #average density list in every bins
		for xi in range(Nx):
			x0 = xlo+dX*xi #down coord of bin
			x1 = xlo+dX*(xi+1) #down coord of bin
			xc = (x0+x1)*0.5
			xc_n.append(xc)
			# print(xi,'---Nx:---',Nx)
			for yi in tqdm(range(Ny)):
				# print(yi,'---Ny:---',Ny)
				y0 = ylo+dY*yi #down coord of bin
				y1 = ylo+dY*(yi+1) #down coord of bin
				yc = (y0+y1)*0.5
				# print(yc)
				yc_n.append(yc)
				for zi in range(Nz):
					# print(zi,'---Nz:---',Nz)
					z0 = zlo+dZ*zi #down coord of bin
					z1 = zlo+dZ*(zi+1) #down coord of bin
					zc = (z0+z1)*0.5
					zc_n.append(zc)
		
					n=0 #tot mass or number in bin

					for i in range(self.natoms):
						
						if id_know[i]>=atomtype_n[0] and id_know[i]<=atomtype_n[1]:
							if X[i]>=x0 and X[i]<=x1 and Y[i]>=y0 and Y[i]<=y1 and Z[i]>=z0 and Z[i]<=z1:
								if mass_or_number == "mass":
									n = MW[i]+n
								elif mass_or_number == "number":
									n = n+1
									# print(i,'---',self.natoms,MW[i])
					vlo = (dX*dY*dZ)*unitconvert
					rho = n/vlo
					# print(rho)
					rho_n.append(rho)

		xc_n = np.array(xc_n)
		xc_n = np.unique(xc_n).reshape((Nx,1))

		yc_n = np.array(yc_n)
		yc_n = np.unique(yc_n).reshape((Ny,1))

		zc_n = np.array(zc_n)
		zc_n = np.unique(zc_n).reshape((Nz,1))
		rho_nxyz = np.array(rho_n).reshape((Nx,Ny,Nz))
		# print(rho_nxyz)
		minx = min(xc_n)
		miny = min(yc_n)
		minz = min(zc_n)
		xc_n = xc_n-minx
		yc_n = yc_n-miny
		zc_n = zc_n-minz
		
		# print(xc_n,yc_n,zc_n,rho_nxyz)

		return xc_n,yc_n,zc_n,rho_nxyz


	def zoning(self,sorted_traj,axis_range,direc="y"):
		"""
		Divide a coordinate interval along a direction, such as, x or y or z
		sorted_traj: sorted lammps traj, pandas dataframe format, it includes at least 'id mol type x y z'
		axis_range: Divide interval, a list, such as, axis_range = [0,3.5], unit/Angstrom
		direc: The direction to be divided, default direc="y"
		"""
		# whether in the interval
		direc = direc.lower()
		condition1 = (sorted_traj[direc].between(axis_range[0],axis_range[1]))
		sorted_zoning_traj = sorted_traj[condition1]

		return sorted_zoning_traj


	def zoning_molecule(self,sorted_traj,axis_range,direc="y"):
		"""
		Divide a coordinate interval along a direction, such as, x or y or z
		sorted_traj: sorted lammps traj, pandas dataframe format, it includes at least 'id mol type x y z'
		axis_range: Divide interval, a list, such as, axis_range = [0,3.5], unit/Angstrom
		direc: The direction to be divided, default direc="y"
		"""
		# whether in the interval
		direc = direc.lower()
		condition1 = (sorted_traj[direc].between(axis_range[0],axis_range[1]))
		sorted_zoning_traj = sorted_traj[condition1]
		# Whether it's the same molecule
		mols = sorted_zoning_traj["mol"]
		condition2 = (sorted_traj["mol"].isin(mols))
		sorted_zoning_traj = sorted_traj[condition2]
		return sorted_zoning_traj


	def zoning_water_in_hydrate(self,sorted_traj,axis_range,direc="y"):
		"""
		Divide a coordinate interval along a direction, such as, x or y or z for hydrate/water big molecules
		sorted_traj: sorted lammps traj, pandas dataframe format, it includes at least 'id mol type x y z'
		axis_range: Divide interval, a list, such as, axis_range = [0,3.5], unit/Angstrom
		direc: The direction to be divided, default direc="y"
		"""
		# whether in the interval
		direc = direc.lower()
		condition1 = (sorted_traj[direc].between(axis_range[0],axis_range[1]))
		sorted_zoning_traj = sorted_traj[condition1] # select H2O between axis_range0 and axis_range1, but there are some abnormal water
		condition2 = (sorted_zoning_traj["type"] == 1) # select O atoms in axis_range
		selected_O = sorted_zoning_traj[condition2]
		ids = selected_O["id"]
		def expand_element(element):
			return [element, element + 1, element + 2]
		expanded_data = ids.map(expand_element)
		ids = pd.Series([item for sublist in expanded_data for item in sublist])
		# print(ids)
		condition3 = (sorted_traj["id"].isin(ids)) 
		water_inaxis_range = sorted_traj[condition3]
		return water_inaxis_range


	def dividing(self,L0,L1,lbin):
		nLs = np.arange(L0, L1, lbin)
		matrix = np.array([[nLs[i], nLs[i + 1]] for i in range(len(nLs) - 1)])
		return matrix

	@print_line
	def calc_bulk_density(self, nframe, modify=False):
		"""
		calculate bulk mass density from lammpstrj
		Parameters:
		- nframe: number of frame
		- modify: need to modify mass, default False, modify={"C": 16.043}
		Return a density value
		"""
		unitconvert = self.amu2g*(self.A2CM)**3 # g/mL
		mxyz = self.read_mxyz(nframe,modify=modify)
		vol = self.read_vol(nframe)*unitconvert
		total_mass = np.sum(mxyz[:,0])
		rho = total_mass/vol
		return rho


	@print_line
	def msd(self,atomtype,mframe,nframe,interval,outputfile=False):
		"""
		calculating msd
		Parameters:
		- atomtype: atomtype, list, example: [1,2]
		- mframe: start number of frame
		- nframe: end number of frame
		- interval: interval number of frame
		- outputfile: msd file
		"""
		# trj = rlt.ReadLammpsTraj(trjfile)
		# 1. load select atom position
		xyzs = []
		lxs,lys,lzs = [],[],[]
		for i in tqdm(range(mframe,nframe+interval,interval),desc="Reading positions"):
			iframe = self.read_traj(i)
			xyz_i = select_atoms(iframe,atomtype).tolist()
			xyzs.append(xyz_i)
			box = self.read_box(i)
			lx = box["xhi"]-box["xlo"]
			ly = box["yhi"]-box["ylo"]
			lz = box["zhi"]-box["zlo"]
			lxs.append(lx)
			lys.append(ly)
			lzs.append(lz)
		xyzs = np.array(xyzs)
		# print(xyzs.shape)
		xyzs = unwrap_coordinates(xyzs, lxs, lys, lzs)

		nf, m, n=xyzs.shape
		# 2. calculating msd
		t = []
		msd_x, msd_y, msd_z, msd = [], [], [], []
		lagtimes = np.arange(1, nf)
		for i in tqdm(lagtimes,desc="Calculating MSD"):
			dists = 0
			disp = xyzs[:-i,:,:] - xyzs[i:,:,:]
			# disp = boundary(disp,lx,ly,lz)
			sqdist = np.square(disp)
			dist = np.mean(sqdist,axis=0) # 平均lagtimes
			dist = np.mean(dist,axis=0) # 平均原子
			t.append(i*interval)
			msd_x.append(dist[0])
			msd_y.append(dist[1])
			msd_z.append(dist[2])
			msd.append(np.sum(dist))
		tmsd = np.array([t,msd_x,msd_y,msd_z,msd]).T

		if outputfile == False:
			outputfile = "msd.dat"
		np.savetxt(outputfile,tmsd,fmt="%f")
		return tmsd
	@print_line
	def rdf(self,mframe,nframe,interval,atomtype1,atomtype2,cutoff=12,Nb=120,rdffile=False):
		"""
		calculate rdf from lammpstrj
		Parameters:
		- mframe: start number of frame
		- nframe: end number of frame
		- interval: interval of frame
		- atomtype1: selected atom type1, a list, example, [1,2]
		- atomtype2: selected atom type2, a list, example, [1,2]
		- cutoff: cutoff, default 12 Angstrom
		- Nb: number of bins
		- rdffile: lammpstrj file name
		"""
		if rdffile==False:
			rdffile = "rdf.dat"
		rgrs = []
		for nf in range(mframe,nframe+1,interval):
			traj = self.read_traj(nf)
			box = self.read_box(nf)
			lx = box["xhi"]-box["xlo"]
			ly = box["yhi"]-box["ylo"]
			lz = box["zhi"]-box["zlo"]
			xyz_1 = select_atoms(traj,atomtype1)
			xyz_2 = select_atoms(traj,atomtype2)
			m, _ = xyz_1.shape
			n, _ = xyz_2.shape
			bs = cutoff/Nb
			gr = np.zeros((Nb+1))
			for i in tqdm(range(m),desc=f"Frame-{nf}"):
				for j in range(n):
					if i!=j:
						dr = xyz_2[j]-xyz_1[i]
						dr = boundary(dr, lx, ly, lz)
						dist = np.linalg.norm(dr)
						if dist <= cutoff+bs:
							index_bin = int(np.ceil(dist/bs))-1
							gr[index_bin] = gr[index_bin]+1

			rho_all = n/(lx*ly*lz)

			r = np.zeros((Nb+1))
			for i in range(Nb+1):
				dV = np.pi*(np.power(bs*(i+1),3)-np.power(bs*i,3))*4.0/3.0
				gr[i] = gr[i]/m/dV
				gr[i] = gr[i]/rho_all
				r[i] = bs*(2*i+1)/2.0
			rgr = np.vstack((r,gr)).T
			rgrs.append(rgr.tolist())
		rgrs = np.array(rgrs)
		rgr_ave = np.mean(rgrs,axis=0)
		np.savetxt(rdffile,rgr_ave,fmt="%f %e",header=str(rho_all), comments='# ')
		print(">>> RDF calculation successfully !")
		return rho_all, rgr_ave
	@print_line
	def calc_coordination_number(self,rho,r,gr):
		"""
		Applied the trapezoidal rule to integrate 
		the RDF cumulatively and stores the CN function
		Parameters:
		- rho: number density
		- r: radial distance
		- gr: radial distribution functions (RDF)
		return coordination number (cn)
		"""
		dr = r[1] - r[0]
		cn = 4*np.pi*rho*np.cumsum(gr*r*r)*dr
		return cn
	@print_line
	def calc_PMF(self,r,gr,T):
		"""
		Calculating the potential of mean force (PMF) by ln RDF
		Parameters:
		- r: radial distance
		- gr: radial distribution functions (RDF)
		- T: Temerature
		return PMF
		"""
		# PMF = np.zeros((len(r)))
		k = 1.380649e-23 # J/K
		J2kcal = 2.390057361377e-4 # 1J/K = 2.390057361377e-4 kcal/K
		PMF = -k*J2kcal*T*np.log(gr)

		rPMF = np.vstack((r,PMF)).T
		return rPMF

	# def structureFactor(self,lammpstrj,frames,atomtype1,atomtype2,cutoff=12,Nb=120,kmin=False,kmax=5,nk=500,rdffile=False,skfile=False):
	# 	"""
	# 	calculating the structure factor from RDF
	# 	Parameters:
	# 	- lammpstrj: lammpstraj file
	# 	- frames: range of frame, [start,stop,interval]
	# 	- atomtype1: selected atom type1, a list, example, [1,2]
	# 	- atomtype2: selected atom type2, a list, example, [1,2]
	# 	- cutoff: cutoff, default 12 Angstrom
	# 	- Nb: number of bins
	# 	- kmin: minimum value of vector k
	# 	- kmin: maximum value of vector k
	# 	- nk: number of vector k
	# 	- rdffile: saved rdf file
	# 	- skfile:  saved sk file
	# 	"""
	# 	mframe,nframe,interval = frames[0],frames[1],frames[2]
	# 	# rlt = ReadLammpsTraj(lammpstrj)
	# 	rho, rgr_ave = self.rdf(mframe,nframe,interval,atomtype1,atomtype2,cutoff=cutoff,Nb=Nb,rdffile=rdffile)
	# 	r, gr = rgr_ave[:,0], rgr_ave[:,1]

	# 	if kmin:
	# 		pass
	# 	else:
	# 		lx,ly,lz = self.read_lengths(mframe)
	# 		# ll = (lx + ly +lz)/3.0
	# 		ll = lx 
	# 		kmin = 2*np.pi/ll

	# 	k_vals = np.linspace(kmin,kmax,nk)
	# 	dr = r[1]-r[0]
	# 	Sk = []
	# 	for k in k_vals:
	# 		integrand = (gr - 1) * (np.sin(k * r) / (k * r)) * 4 * np.pi * r**2
	# 		Sk_val = 1 + rho * simpson(integrand, dx=dr)
	# 		Sk.append(Sk_val)
	# 	Sk = np.array(Sk)
	# 	kSk = np.vstack((k_vals,Sk)).T
	# 	np.savetxt(skfile,kSk,"%f")
	# 	return kSk


	def structureFactor(self,rho,rgr,frames,kmin=False,kmax=5,nk=500,skfile=False):
		"""
		calculating the structure factor from RDF
		Parameters:
		- rho: number density
		- rgr: rdf
		- frames: range of frame, [start,stop,interval]
		- kmin: minimum value of vector k
		- kmin: maximum value of vector k
		- nk: number of vector k
		- skfile:  saved sk file
		"""
		mframe,nframe,interval = frames[0],frames[1],frames[2]
		r, gr = rgr[:,0], rgr[:,1]

		if kmin:
			pass
		else:
			lx,ly,lz = self.read_lengths(mframe)
			# ll = (lx + ly +lz)/3.0
			ll = min([lx,ly,lz])
			kmin = 2*np.pi/ll

		k_vals = np.linspace(kmin,kmax,nk)
		dr = r[1]-r[0]
		Sk = []
		for k in k_vals:
			integrand = (gr - 1) * (np.sin(k * r) / (k * r)) * 4 * np.pi * r**2
			Sk_val = 1 + rho * simpson(integrand, dx=dr)
			Sk.append(Sk_val)
		Sk = np.array(Sk)
		kSk = np.vstack((k_vals,Sk)).T
		np.savetxt(skfile,kSk,"%f")
		return kSk

	@print_line
	def density(self,nframe,id_range,mass_dict,Nz=100,id_type="atom",density_type="mass",direction="z"):
		"""
		Calculating the density
		Parameters:
		- nframe: number of frame
		- id_range: calculated id range of atoms [1,2]
		- mass_dict: masses dict
		- Nz: number of bins
		- id_type: "atoms" or "mol"
		- density_type: "mass" or "number"
		- direction: x, or y, or z
		return coord, rho
		"""
		position = self.read_mxyz(nframe)
		coord, rho = self.oneframe_moldensity(nframe,position,Nz,id_range,mass_dict,id_type=id_type,density_type=density_type,direction=direction)
		
		return coord, rho

	@print_line
	def trj2lmp(self,nframe,lmp,relmp):
		"""
		write lammps data from lammpstrj and original lmp
		Parameters:
		- nframe: number of frame
		- lmp: original lammps data
		- relmp: final writed lammps data
		"""
		traj = self.read_traj(nframe)
		box = self.read_box(nframe)
		Atoms_init = rld.read_data(lmp,"Atoms")
		Atoms_init = rld.str2array(Atoms_init)
		Atoms_init = Atoms_init[Atoms_init[:,0].astype(int).argsort()]
		Atoms_init[:,4] = traj["x"].values
		Atoms_init[:,5] = traj["y"].values
		Atoms_init[:,6] = traj["z"].values
		Atoms_final = rld.array2str(Atoms_init)
		terms = rld.read_terms(lmp)
		f = open(relmp,"w")
		header = rld.read_data(lmp,"Header")
		header = rld.modify_header(header,hterm="xlo xhi",value=[box["xlo"],box["xhi"]])
		header = rld.modify_header(header,hterm="ylo yhi",value=[box["ylo"],box["yhi"]])
		header = rld.modify_header(header,hterm="zlo zhi",value=[box["zlo"],box["zhi"]])
		f.write(header)
		for term in terms:
			if "Atoms" in term:
				terminfo = Atoms_final
			else:
				terminfo = rld.read_data(lmp,term)
			f.write(term)
			f.write(terminfo)
		print(">>> Write lmp from lammpstrj successfully!")
		return
	
	@print_line
	def count_hbonds(self,lammpstrj,frames,typeOfO=1,dist=3.5,angle=30):
		"""
		count hbonds of water molecules, O H H
		Parameters:
		- lammpstrj: lammpstrj file
		- frames: range of frame, [start,end,interval]
		- typeOfO: type id of O atom, default 1
		- dist: distance  for hbonds, default 3.5 A
		- angle: angle for hbonds, default 30 degree
		"""
		import utils.hbonds as hb
		ts = []
		nhbonds = []
		mframe,nframe,interval = frames[0],frames[1],frames[2]
		for i in tqdm(range(mframe,nframe,interval)):
			traj = self.read_traj(nframe=i)
			box = self.read_box(nframe=i)
			hbonds = hb.calc_hbonds(i,traj,typeOfO,
								lx=box["xhi"]-box["xlo"], 
								ly=box["yhi"]-box["ylo"], 
								lz=box["zhi"]-box["zlo"],
								dist=dist, angle=angle)
			ts.append(i)
			nhbonds.append(hbonds[1])
		tnhbonds = [ts,nhbonds]
		tnhbonds = np.array([tnhbonds]).reshape(2,-1).T
		return tnhbonds


	def adsorbedNum(self,mframe,nframe,interval=1,atomtype1=False,atomtype2=False,cutoff=6,savefile=False):
		"""
		count number of adsorbed molecules
		Parameters:
		- mframe: start
		- nframe: stop
		- interval: interval
		- atomtype1: adsorber atom type/id, a dict, atomtype1={"atom_id":[7]} 
		- atomtype2: adsorbent atom type/id, a dict, atomtype2={"atom_type": [3]}
		- cutoff: cutoff
		- savefile: save file
		"""
		ts, nums = [], []
		for nf in tqdm(range(mframe,nframe,interval)):
			traj = self.read_traj(nf)
			idxyz1 = select_atoms_return_idxyz(traj,atomtype1)
			idxyz2 = select_atoms_return_idxyz(traj,atomtype2)
			a1 = idxyz1[:,1:].astype(float)
			a2 = idxyz2[:,1:].astype(float)
			id2 = idxyz2[:,0].astype(int)
			m,_ = a1.shape
			n,_ = a2.shape
			box = self.read_box(nf)
			lx = box["xhi"]-box["xlo"]
			ly = box["yhi"]-box["ylo"]
			lz = box["zhi"]-box["zlo"]
			adsorbs = []
			for i in range(m):
				for j in range(n):
					dr = a2[j]-a1[i]
					dr = boundary(dr,lx,ly,lz)
					dist = np.linalg.norm(dr)
					if dist <= cutoff:
						adsorbs.append(id2[j])
			adsorbs = np.unique(np.array(adsorbs))
			num = len(adsorbs)

			ts.append(nf)
			nums.append(num)
		tsnums = np.array([ts,nums])
		tsnums = np.vstack((tsnums)).T
		np.savetxt(savefile,tsnums,fmt="%d")

		return

	def center_of_mass(self,atomtype,mframe,nframe,interval=1,outputfile=False):
		t, comxs,comys,comzs,coms = [], [], [], [], []
		for i in tqdm(range(mframe,nframe+1)):
			trj = self.read_traj(i)
			mask = (trj['type'].astype(int) >= atomtype[0]) & (trj['type'].astype(int) <= atomtype[1])
			new_df = trj[mask].copy()
			elements = new_df["element"].values
			masses = np.array(element2mass(elements))
			total_mass = np.sum(masses)
			
			x = new_df["x"].values.astype(float)
			comx_sum = np.sum(masses * x)
			comx = comx_sum / total_mass
			
			y = new_df["y"].values.astype(float)
			comy_sum = np.sum(masses * y)
			comy = comy_sum / total_mass
			
			z = new_df["z"].values.astype(float)
			comz_sum = np.sum(masses * z)
			comz = comz_sum / total_mass
			t.append(i)
			comxs.append(comx)
			comys.append(comy)
			comzs.append(comz)
			com = np.linalg.norm([comx,comy,comz])
			coms.append(com)
		t = np.array(t)
		comxs = np.array(comxs)
		comys = np.array(comys)
		comzs = np.array(comzs)
		coms = np.array(coms)
		tcoms = np.column_stack((t, comxs, comys, comzs, coms))
		np.savetxt(outputfile,tcoms,"%f",header='Time (frame) com_x com_y com_z com_ave', comments='# ')
		return










import fastdataing as fd
import matplotlib.pyplot as plt

if __name__ == "__main__":
	__print_version__()
	lammpstrj = "traj_npt_relax_260_1.lammpstrj"
	frames = [0,3,1]
	rlt = ReadLammpsTraj(lammpstrj)

	rho_all, rgr = rlt.rdf(mframe=0,nframe=1,interval=1,
							atomtype1=[3],atomtype2=[3],
							cutoff=12,Nb=100,
							rdffile="rdf.dat")
	rlt.structureFactor(rho_all,rgr,frames=frames,
		kmin=False,kmax=10,nk=500,skfile="sk.dat")
	ksk = np.loadtxt("sk.dat")
	r, gr = rgr[:,0]*0.1,rgr[:,1]
	k, sk = ksk[:,0]*0.1,ksk[:,1]
	fig=fd.add_fig()
	ax = fd.add_ax(fig,subplot=(2,1,1))
	ay = fd.add_ax(fig,subplot=(2,1,2))
	ax.plot(r,gr,lw = 2)
	ay.plot(k,sk,lw = 2)

	ax.set_xlabel(r"$\regular \it r$ (Å)",fontsize=22)
	ax.set_ylabel(r"$\regular \it g(r)$",fontsize=22)
	ay.set_xlabel(r"$\regular \it k$  ($Å^{-1}$)",fontsize=22)
	ay.set_ylabel(r"$\regular \it S(k)$",fontsize=22)
	fd.set_fig(ax)
	fd.set_fig(ay)
	plt.show()
