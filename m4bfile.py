#!/usr/bin/env python3

from struct import pack, unpack
from shutil import copyfileobj
import os, os.path

# This module defines reading and writing m4b files.

# reads a length-prefixed null-terminated string
def m4b_ReadString(f):
	slen = unpack("<I", f.read(4))[0]
	val = str(f.read(slen - 1), encoding="ascii")
	dummy = f.read(1)
	return val
	
# writes a length-prefixed null-terminated string
def m4b_WriteString(f, s):
	slen = len(s) + 1
	f.write(pack("<I", slen))
	f.write(s.encode("ascii"))
	f.write(pack("b", 0))
	
# helper class for pretty tree printing
class TreeNode:
	def __init__(self, value=None, children=None):
		if children is None:
			children = []
		self.value, self.children = value, children


# The FILE class - contains info on a file in the m4b archive
class m4b_filerecord:
	def __init__(self, filename = None, length = 0, offset = 0, realfile = None):
		self.filename = filename
		self.offset = offset
		self.length = length
		self.realfile = realfile
		
	def Read(self, f):
		self.filename = m4b_ReadString(f)
		(self.length, self.offset) = unpack("<II", f.read(8))
		
	def Write(self, f, offset, filestowrite, parentpath):
		m4b_WriteString(f, self.filename)
		if len(filestowrite) > 0:
			self.offset = filestowrite[-1][1]
		else:
			self.offset = offset
		filestowrite.append( (self.realfile, self.offset + self.length) )
		f.write(pack("<II", self.length, self.offset))
		
	def RecordLen(self):
		return 4 + len(self.filename) + 1 + 8
		
	def Extract(self, destination, pak):
		pak.seek(self.offset)
		
		with open(os.path.normpath(os.path.join(destination, self.filename)), "wb") as df:
			remain = self.length
			while remain > 0:
				chunksize = min(4096, remain)
				chunk = pak.read(chunksize)
				df.write(chunk)
				remain -= len(chunk)
			
		
# the DIRECTORY class - contains information about a directory, including subdirectories and files
class m4b_directoryrecord:
	def __init__(self, f = None, subdir = True):
		self.name = None
		self.subdirs = []
		self.files = []
		
		if f is None:
			return
		
		if subdir:
			self.name = m4b_ReadString(f)
		
		subdircount = unpack("B", f.read(1))[0]
		for x in range(subdircount):
			self.subdirs.append(m4b_directoryrecord(f))
		
		filecount = unpack("<I", f.read(4))[0]
		for x in range(filecount):
			fr = m4b_filerecord()
			fr.Read(f)
			self.files.append(fr)
	
	def Write(self, f, startoffs, filestowrite, parentpath = "/"):
		if self.name is not None:
			m4b_WriteString(f, self.name)
			parentpath = parentpath + self.name + "/"
		
		f.write(pack("B", len(self.subdirs)))
		for d in self.subdirs:
			d.Write(f, startoffs, filestowrite, parentpath)
		
		f.write(pack("<I", len(self.files)))
		for fil in self.files:
			fil.Write(f, startoffs, filestowrite, parentpath)
			
	def RecordLen(self):
		val = 0
		
		if self.name is not None:
			val = val + 4 + len(self.name) + 1
			
		val = val + 1
		for d in self.subdirs:
			val = val + d.RecordLen()
			
		val = val + 4
		for fil in self.files:
			val = val + fil.RecordLen()
			
		return val
		
	def Build(self, root):
		with os.scandir(root) as scan:
			for dirent in scan:
				if dirent.is_dir():
					nd = m4b_directoryrecord()
					nd.name = dirent.name
					nd.Build(dirent.path)
					self.subdirs.append(nd)
				elif dirent.is_file():
					self.files.append(m4b_filerecord(dirent.name, dirent.stat().st_size, realfile=dirent.path))
				
	def ListContents(self, mynode):
		if self.name is None:
			mynode.value = "/"
		else:
			mynode.value = self.name + "/"
			
		for d in self.subdirs:
			n = TreeNode()
			d.ListContents(n)
			mynode.children.append(n)
		
		for f in self.files:
			mynode.children.append(TreeNode('{:<60s} {:15,d} {:15,d}'.format(f.filename, f.length, f.offset)))
			
	def Extract(self, destination, pak):
		if self.name is not None:
			destination = os.path.normpath(os.path.join(destination, self.name))
		
		os.makedirs(destination, exist_ok=True)
		
		for d in self.subdirs:
			d.Extract(destination, pak)
			
		for f in self.files:
			f.Extract(destination, pak)
				
		
# the m4b file itself
class m4b_file:
	def __init__(self, fname = None):
		self.rootdir = m4b_directoryrecord()
		self.realroot = None
		self.pakname = fname
		
		if self.pakname is None:
			return
			
		with open(self.pakname, "rb") as f:
			
			siglen = unpack("<I", f.read(4))[0]
			if siglen != 11:
				raise ValueError
			
			sigstring = f.read(siglen)
			if sigstring != b'UBI_BF_SIG\0':
				raise ValueError
			
			dummy = unpack("<II", f.read(8))
			
			self.rootdir = m4b_directoryrecord(f, False)
		
	def Write(self, f):
		m4b_WriteString(f, "UBI_BF_SIG")
		f.write(pack("<II", 1, 0))
		startoffs = 23 + self.rootdir.RecordLen()
		filestowrite = []
		self.rootdir.Write(f, startoffs, filestowrite)
		for fil in filestowrite:
			with open(fil[0], "rb") as sf:
				copyfileobj(sf, f)
	
	
	def Build(self, rootpath):
		self.rootdir = m4b_directoryrecord()
		self.realroot = rootpath
		
		self.rootdir.Build(rootpath)
		
	def ListContents(self, file=None):
		rootnode = TreeNode()
		self.rootdir.ListContents(rootnode)
		
		def pprint_tree(node, file=None, _prefix="", _last=True):
			print(_prefix, "`- " if _last else "|- ", node.value, sep="", file=file)
			_prefix += "   " if _last else "|  "
			child_count = len(node.children)
			for i, child, in enumerate(node.children):
				_last = i == (child_count - 1)
				pprint_tree(child, file, _prefix, _last)
				
		pprint_tree(rootnode, file)
		
	def Extract(self, destination, one_file = None):
		if self.pakname is None:
			raise ValueError
			
		if one_file is not None:
			raise NotImplementedError
			
		with open(self.pakname, "rb") as pak:
			# need to loop through everything in the pak and extract it to disk files
			self.rootdir.Extract(destination, pak)
			
