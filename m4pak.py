#!/usr/bin/env python3

import argparse
import m4bfile

parser = argparse.ArgumentParser(description="create/extract/list Myst4 m4b archive files")
parser.add_argument('--open', dest='inputpak', help="Open an existing archive file")
parser.add_argument('--build', dest='srcdir', help="build an archive from a directory tree")
parser.add_argument('--list', dest='list', action='store_true', help='output a listing of the contents of an archive file')
parser.add_argument('--extract', dest='extract_dest',  help='extract the contents of an archive file')
parser.add_argument('--write-m4b', dest='writeto', help='write a built archive to a file (without this, you can build to list)')

args = parser.parse_args()

pak = None
if args.inputpak is not None:
	pak = m4bfile.m4b_file(args.inputpak)
	
if args.srcdir is not None:
	pak = m4bfile.m4b_file()
	pak.Build(args.srcdir)

if args.list:
	if pak:
		pak.ListContents()
		
if args.extract_dest is not None:
	pak.Extract(args.extract_dest)

if args.writeto is not None:
	with open(args.writeto, "wb") as dest:
		pak.Write(dest)
		