#!/usr/bin/env python

#Written by Miguel M. Moravec thanks to the teachings of Garrett Wright. For questions please email miguel.moravec@vanderbilt.edu
#This script automatically generates plots of tropical SST RMSE for the current and last calendar year
#This script relies on a standard naming convention of daily SST NetCDF files in this observations directory: /archive/nmme/NMME/INPUTS/oisst/
#This script also relies on monthly mean ocean SST NetCDFs from this model directory: /archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/

import subprocess as p
import datetime
import os
import os.path
import glob
import sys, getopt
from dateutil import relativedelta

try:
	import pyferret
except ImportError:
	print "You must module load pyferret"
	exit(1)   

def mymain(argv):

	now = datetime.datetime.now()
	today = ''
	
	#the following establishes the three options for the script

	try:
		opts, args = getopt.getopt(argv,"thd:",["input="])

	except getopt.GetoptError:
   		print "ERROR Invalid Syntax. See 'SSTrmse.py -h'"
		sys.exit(2)

	for opt, arg in opts:
 		if opt == '-h': #help option
        		print '\nThis script automatically generates plots of tropical SST RMSE for the current and last calendar year \n'
			print 'Options are as follows:'
			print "'-h' launches this help text"
			print "'-t' generates today's most recent plots"
			print "'-d mmyyy' generates 2yr plots up to a specified date i.e. '-d 072016' \n"
			print 'This script relies on a standard naming convention of daily SST NetCDF files in this observations directory:'
			print '/archive/nmme/NMME/INPUTS/oisst/ \n'
			print 'This script also relies on monthly mean ocean SST NetCDFs from this model directory:'
			print '/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/ \n'
			print 'For best results, this script should be run from "/home/x1y/gfdl/ecda_operational/sst/" !!!! \n'
			print 'Written by Miguel M. Moravec. For questions please email miguel.moravec@vanderbilt.edu \n'
        		sys.exit()

		elif opt == '-t':
			#option automatically generates most recent plots
			today = now.strftime('%m%Y')

		elif opt in ('-d', '--input'):
         		#option generates plots up to specific date mmyyyy
			today = arg			
	
	#reminds user to select an option
	if today == '':
		print 'ERROR must select an option'
		print "'-t' generates plots for 2 calendar years preceding today's date"
		print "'-d mmyyy' generates plots for 2 calendar years preceding a particular date i.e. '-d 072016'"
		exit(1)

	try:
		date = datetime.datetime.strptime('25' + today, '%d%m%Y')

	except ValueError:
		print "ERROR Invalid Syntax. Arguments following '-d' should be formatted: mmyyyy"
		exit(1)

	#sets time variables, used in generation of NetCDFs, plots, and file names	

	date = datetime.datetime.strptime('25' + today, '%d%m%Y')
	month = date.strftime('%m')
	month_abrev = date.strftime('%b')
	month_abrev_low = month_abrev.lower()
	year = date.strftime('%Y')
	year_abrev = date.strftime('%y')
	year_prev = str(int(year)-1)
	year_prev_abrev = year_prev[-2:]
	timeline = str(int(month)+11)

	sst_outfile = "sstcm21_oimonthly_" + year + ".nc"
	sst_outfile_prev = "sstcm21_oimonthly_" + year_prev + ".nc"
	sst_outfile_combo = "sstcm21_oimonthly_" + year_prev_abrev + year_abrev + ".nc"

	print 'Generating plots with available data from ', year_prev, '/', year, '...'

	#checks to see if necessary nc files are available

	if not os.path.isfile('/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/' + year + month + '01.ocean_month.ensm.nc'):
		print 'ERROR: NetCDF data not available yet for ' + month + '/' + year + '. Exiting . . . '
		exit(1)

	#sets parameters for loop function
	
	d ="." #the local directory

	filename = str('/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/' + year + month + '01.ocean_month.ensm.nc' )

	count = 11 + int(month)

	dlist = [filename] #will be list of netCDF files after loop is finished

	datel = date #date for the loop

	check = 0 #error return

	while count > 0:

		#generates list of relevant netCDF files one month at a time to be made into a DES file 

		count = count - 1

		datel = datel + relativedelta.relativedelta(months=-1)
		monthl = datel.strftime('%m')
		yearl = datel.strftime('%Y')

		filename = str('/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/' + yearl + monthl + '01.ocean_month.ensm.nc' ) 	

		if os.path.isfile(filename):
			dlist.append(filename) #adds filename for particular date to list

		else:
			print 'ERROR. No data for ' + monthl + '/' + yearl + '!'
			if yearl == year_prev:
				timeline = str(int(month) - 1)
				check = 1 #reports that no data available for prev year, affecting calculations later

	#the following makes a des file using XLY's make_des program and dmget

	finput = "/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/*.ocean_month.ensm.nc"
	child = p.Popen(["dmget", finput],cwd=d)
	myout, myerr = child.communicate()

	cmd = ["/home/atw/util/make_des"]
	outputfile='ecda_v31_ocean_auto.des'
	[cmd.append(item) for item in dlist]

	chd = p.Popen(cmd, stdout=p.PIPE, stderr=p.PIPE)
	myout, myerr = chd.communicate()
	print myerr

	with open(outputfile,'w') as F:
	    F.write(myout)

	#checks make_des

	if os.path.isfile(str(outputfile))==False:
		print "ERROR. Make_des process fail. Please ensure data files are located in their proper directories. See '-h'. \nExiting . . ."
		exit(1)
	if not '&FORMAT_RECORD' in open(outputfile).read():
    		print "ERROR. Make_des process fail. Please ensure data files are located in their proper directories. See '-h'. \nExiting . . ."
		exit(1)

	#next ~70 lines replace Xiaosong's csh script and makeS one NetCDF file in the local dir with two calendar years worth of daily SST data averaged monthly	

	if ( not pyferret.start(quiet=True, journal=False, unmapped=True) ):
		print "ERROR. Pyferret start failed. Exiting . . ."
		exit(1)

	if os.path.isfile("tmp1.nc"):
		os.remove("tmp1.nc")

	if os.path.isfile(sst_outfile_combo):
		os.remove(sst_outfile_combo)

	if month == "01":

		#Janurary is a special case that can only consider sst data from the previous year, and so the file naming convention for the desired data file is unique
		#Looks for files in Seth's directory, /net2/sdu/..., to avoid dmgetting the archive if possible

        	file_loc = '/archive/nmme/NMME/INPUTS/oisst/sstcm2_daily_' + year_prev_abrev + '0101_' + year_abrev + month + '01.nc'
		file_loc_alt = '/net2/sdu/NMME/oisst/NetCDF/sstcm2_daily_' + year_prev_abrev + '0101_' + year_abrev + month + '01.nc'	

		if os.path.isfile(file_loc_alt):
			cmd1 = 'use ' + file_loc_alt
		else:	
			print 'dmgetting archived data files (this may take a while)'
			child = p.Popen(["dmget", file_loc],cwd=d)
        		child.communicate()
			cmd1 = 'use ' + file_loc
			
	else:

		#All other months obey this file naming convention for their data files
		#Looks for files in Seth's directory, /net2/sdu/..., to avoid dmgetting the archive if possible

		file_loc = '/archive/nmme/NMME/INPUTS/oisst/sstcm2_daily_' + year_abrev + '0101_' + year_abrev + month + '01.nc'
		file_loc_alt = '/net2/sdu/NMME/oisst/NetCDF/sstcm2_daily_' + year_abrev + '0101_' + year_abrev + month + '01.nc'

		if os.path.isfile(file_loc_alt):
			cmd1 = 'use ' + file_loc_alt
		else:
			print 'dmgetting archived data files (this may take a while)'	        	
			child = p.Popen(["dmget", file_loc],cwd=d)
	        	child.communicate()
			cmd1 = 'use ' + file_loc

	#The following sets the necessary parameters in pyferret	

	cmd2 = 'set memory/size=400'
	cmd3 = 'DEFINE AXIS/T=15-jan-' + year + ':15-' + month_abrev_low + '-' + year + ':1/npoint=' + month + '/UNIT=month tmonth'
	cmd4 = 'let sst_month = temp[gt=tmonth@AVE]'
	cmd5 = 'save/clobber/file=tmp1.nc sst_month'

	(errval, errmsg) = pyferret.run(cmd1)
	(errval, errmsg) = pyferret.run(cmd2)
	(errval, errmsg) = pyferret.run(cmd3)
	(errval, errmsg) = pyferret.run(cmd4)
	(errval, errmsg) = pyferret.run(cmd5)

	#Using the command shell, data files are concatenated in the local directory. The new NetCDF file containing averaged SST data from both calendar years will be here

	child = p.Popen(["ncrename","-v", "SST_MONTH,temp", "tmp1.nc"],cwd=d)
	child.communicate()
	child = p.Popen(["ncrename","-v", "TMONTH,t", "tmp1.nc"],cwd=d)
	child.communicate() 
	child = p.Popen(["ncrename","-d", "TMONTH,t", "tmp1.nc"],cwd=d)
	child.communicate() 
	child = p.Popen(["ncrcat","-O","-v","temp", "tmp1.nc", sst_outfile],cwd=d)
	child.communicate()

	if check == 0:

		if not os.path.isfile("/home/x1y/gfdl/ecda_operational/sst/" + sst_outfile_prev): 
			#if last year's daily SST data not averaged monthly, runs this script for last year creating needed file, then deletes the irrelevant generated image
			child = p.Popen(["python","SSTrmse.py", "-d", '12' + year_prev ],cwd=d)
			child.communicate()
			print '***DISREGARD PRECEDING ERRORS***'
			child = p.Popen(["ncrcat", sst_outfile_prev, sst_outfile, sst_outfile_combo],cwd=d)
			child.communicate()
			os.remove('sst_amo_' + year_prev + '_12.png')
			
		else:		
			child = p.Popen(["ncrcat", "/home/x1y/gfdl/ecda_operational/sst/" + sst_outfile_prev, sst_outfile, sst_outfile_combo],cwd=d)
			child.communicate()

		cmd7 = "use " + sst_outfile_combo

	else:
		print "WARNING: Only considering one year's worth of data..."
		cmd7 = "use " + sst_outfile 
		

	returnCode = child.returncode

	#the following automates the pyferret plot generation and saves a png image file in the local dir

	filename = 'sst_amo_' + year + '_' + month + '.png'

	header()
	
	cmd8 = "let temp2 = temp[d=2, gxy=sst[d=1],gt=sst[d=1]@asn]"
	cmd9 = "let err1 = sst[d=1,z=0,l=1:" + timeline + "] - temp2[d=2,l=1:" + timeline+ "]"

	cmd10 = 'sha/lev=(0.,2.0,0.25)(2.0,3.0,0.5) var1[y=30s:30n,l=1:' + timeline + '@ave]^0.5'
	cmd11 = str('ANNOTATE/NOUSER/XPOS=2/YPOS=6.25 "SST RMSE ' + year_prev + '-' + year + '"')
	cmd12 = 'set mode/last verify'
	cmd13 = 'FRAME/FILE=' + filename #saves png

	(errval, errmsg) = pyferret.run(cmd7)
	(errval, errmsg) = pyferret.run(cmd8)
	(errval, errmsg) = pyferret.run(cmd9)

	body() #####runs before cmd10-13

	(errval, errmsg) = pyferret.run(cmd10)
	(errval, errmsg) = pyferret.run(cmd11)
	(errval, errmsg) = pyferret.run(cmd12)
	(errval, errmsg) = pyferret.run(cmd13)

	#file clean up
	if os.path.exists("tmp1.nc"):
		os.remove("tmp1.nc")

	#image file/script check
	if os.path.exists(str(filename)):
		if check == 0:
			print 'SUCCESS. Plot image file for tropical SST RMSE ' + year_prev + '/' + year + ' since ' + month_abrev + ' is located in the local directory and is named: ' + filename

		if check == 1:
			print 'ERROR. PARTIAL SUCCESS. Plot image file for tropical SST RMSE (' + year + ' ONLY!!!) is located in the local directory and is named: ' + filename
	else:
		print "ERROR. No plots generated. Please ensure data files are located in their proper directories. See '-h'"
		exit(1)

def header():
	
	#the following clears data from previously running pyferrets, establishes base parameters, and loads ensemble data

	com1 = 'cancel data/all'
	com2 = 'def sym print_opt $1"0"'
	com3 = 'set mem/size=240'
	com4 = 'use ecda_v31_ocean_auto.des'

	(errval, errmsg) = pyferret.run(com1)
	(errval, errmsg) = pyferret.run(com2)
	(errval, errmsg) = pyferret.run(com3)
	(errval, errmsg) = pyferret.run(com4)

def body():
	
	#the following calculates, lists, and plots RMSE. This method depends on functions computed in the main method

	com5 = 'let var1 = err1^2; let rms10 = var1[x=@ave,y=40n:90n@ave]^0.5'
	com6 = 'let rms11 = var1[x=@ave,y=40s:90s@ave]^0.5'
	com7 = 'list rms10+rms11'
	com8 = 'let var1 = err1^2; let rms1 = var1[x=@ave,y=30s:30n@ave]^0.5'
	com9 = 'list rms1'
	com10 = 'set win 1'
	com11 = 'cancel mode nodata_lab'
	com12 = 'set viewport upper'
	com13 = 'cancel mode nodata_lab'
	com14 = 'plot/vl=0.0:1.5:0.1/line=1/DASH rms1'
	com15 = 'set viewport lower'
	com16 = 'set region/y=30s:30n'

	(errval, errmsg) = pyferret.run(com5)
	(errval, errmsg) = pyferret.run(com6)
	(errval, errmsg) = pyferret.run(com7)
	(errval, errmsg) = pyferret.run(com8)
	(errval, errmsg) = pyferret.run(com9)
	(errval, errmsg) = pyferret.run(com10)
	(errval, errmsg) = pyferret.run(com11)
	(errval, errmsg) = pyferret.run(com12)
	(errval, errmsg) = pyferret.run(com13)
	(errval, errmsg) = pyferret.run(com14)
	(errval, errmsg) = pyferret.run(com15)
	(errval, errmsg) = pyferret.run(com16)


if __name__=="__main__":
    mymain(sys.argv[1:])
