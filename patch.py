#!/usr/bin/env python3

import base64
import bz2
import m4bfile
import os.path
import os

# Bink file with a single 8x8 frame of black
black8by8 = bz2.decompress(base64.b64decode(b'QlpoOTFBWSZTWUsjWKwAACV/TGzYWABAAAIAUCgAQAQgBAQCAEAAIABURAANAyZBJKPUDRoPKMkPw15+zNKYK2PjukcsHSZAQMi8TMLJTqN76AIrgl8XckU4UJBLI1is'))


filestoblank = [
	"video_2/shared/video/w5_z01_n010_p_yee2_s02b_p01.bik",
	"video_3/w1/z07/n030/video/w1_z07_n030_p_bibli1_descent_f.bik",
	"video_3/w1/z07/n030/video/w1_z07_n030_p_bibli1_descent2_f.bik",
	"video_6/w4/z03/n010/video/w4_z03_n010_p_m01_s12_p01.bik",
	"video_6/w4/z05/n050/video/w4_z05_n050_p_ach_s17_p01.bik",
	"video_6/w4/z05/n050/video/w4_z05_n050_p_ach02_s17_p02.bik",
	"video_6/w4/z06/n200/video/w4_z06_n200_p_yee_s25_p01.bik",
	"video_6/w4/z06/n210/video/w4_z06_n210_p_ach_s27_p01.bik",
	"video_6/w4/z06/n200/video/w4_z06_n210_p_ach_s27_p07.bik",
	"video_6/w4/z06/n200/video/w4_z06_n210_p_ach_s35_p01.bik",
	"video_6/w4/z06/n200/video/w4_z06_n210_p_cin2_s36_p01.bik",
	"video_7/w5/z04/n050/video/w5_z04_n050_p_yee_s05_p01.bik",
	"video_7/w5/z04/n090/video/w5_z04_n090_p_yee_s06_p02.bik",
	"video_7/w5/z04/n090/video/w5_z04_n090_p_yee_s06_p03.bik",
	"video_7/w5/z04/n090/video/w5_z04_n090_p_yee2_s06_p01.bik",
	"video_7/w5/z01/n010/video/w5_z01_n010_p_yee_s02_p05.bik",
	"video_7/w5/z01/n010/video/w5_z01_n010_p_yee_s02b_p02.bik",
	"video_7/w5/z01/n010/video/w5_z01_n010_p_yee_s02b_p03.bik",
	"video_7/w5/z02/n030/video/w5_z02_n030_p_atr_s03_p02.bik",
	"video_7/w5/z02/n030/video/w5_z02_n030_p_atr2_s03_p04.bik",
	"video_7/w5/z02/n030/video/w5_z02_n030_p_atr3_s03_p06.bik",
	"video_7/w5/z02/n030/video/w5_z02_n030_p_atr4_s03_p04a.bik",
	]


# directory with source m4b files
sourcedir = "orig"

# directory to write modified m4b files
destdir = "mod"

# m4b files to modify. this is also the first path element above
pakfiles = ["video_2", "video_3", "video_6", "video_7"]

# extract the pak files we need to change
for k in pakfiles:
	print("Extracting " + k)
	pak = m4bfile.m4b_file(os.path.join(sourcedir, k + ".m4b"))
	pak.Extract(k)
	
# overwrite the files we need to change
for fn in filestoblank:
	print("Replacing " + fn)
	with open(fn, "wb") as f:
		f.write(black8by8)
		

os.makedirs(destdir, exist_ok=True)

# now pack them all back up
for k in pakfiles:
	pak = m4bfile.m4b_file()
	print("Building new " + k)
	pak.Build(k)
	print("Writing new " + k)
	with open(os.path.join(destdir, k + ".m4b"), "wb") as f:
		pak.Write(f)
	
