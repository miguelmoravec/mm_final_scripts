#!/usr/bin/env python

#Written by Miguel M. Moravec thanks to the teachings of Garrett Wright. For questions please email miguel.moravec@vanderbilt.edu
#This script automatically generates global plots of air temperature RMSE for the current and last calendar year
#This script relies on a standard naming convention of daily air temp NetCDF files in this observations directory: /archive/nmme/NMME/INPUTS/ncep2_am2/
#This script also relies on monthly mean air temp NetCDFs from this model directory: /archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/

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
   		print "ERROR Invalid Syntax. See 'tair.py -h'"
		sys.exit(2)

	for opt, arg in opts:
 		if opt == '-h': #help option
        		print '\nThis script automatically generates global plots of air temperature RMSE for the current and last calendar year \n'
			print 'Options are as follows:'
			print "'-h' launches this help text"
			print "'-t' generates today's most recent plots"
			print "'-d mmyyy' generates 2yr plots up to a specified date i.e. '-d 072016' \n"
			print 'This script relies on a standard naming convention of daily SST NetCDF files in this directory observations:'
			print '/archive/nmme/NMME/INPUTS/ncep2_am2/ \n'
			print 'This script also relies on monthly mean air temp NetCDFs from this model directory: '
			print '/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/ \n'
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

	atmos_outfile = "taircm21_ncepmonthly_" + year + ".nc"
	atmos_outfile_prev = "taircm21_ncepmonthly_" + year_prev + ".nc"
	atmos_outfile_combo = "taircm21_ncepmonthly_" + year_prev_abrev + year_abrev + ".nc"

	print 'Generating plots with available data from ', year_prev, '/', year, '...'

	#checks to see if necessary nc files are available

	if not os.path.isfile('/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/' + year + month + '01.atmos_month.ensm.nc'):
		print 'ERROR: NetCDF data not available yet for ' + month + '/' + year + '. Exiting . . . '
		exit(1)

	#sets parameters for loop function

	d ="." #the local directory

	filename = str('/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/' + year + month + '01.atmos_month.ensm.nc' )

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

		filename = str('/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/' + yearl + monthl + '01.atmos_month.ensm.nc' ) 	

		if os.path.isfile(filename):
			dlist.append(filename) #adds filename for particular date to list

		else:
			print 'ERROR. No data for ' + monthl + '/' + yearl + '!'
			if yearl == year_prev:
				timeline = str(int(month) - 1)
				check = 1 #reports that no data available for prev year, affecting calculations later

	#the following makes a des file using XLY's make_des program and dmget

	finput = "/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/*.atmos_month.ensm.nc"
	child = p.Popen(["dmget", finput],cwd=d)
	myout, myerr = child.communicate()

	cmd = ["/home/atw/util/make_des"]
	outputfile='ecda_v31_atmos_auto.des'
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

	#next ~70 lines replace Xiaosong's csh script and make one NetCDF file in the local dir with two calendar years worth of daily SST data averaged monthly

	if ( not pyferret.start(quiet=True, journal=False, unmapped=True) ):
		print "ERROR. Pyferret start failed. Exiting . . ."
		exit(1)

	if os.path.isfile("tmp1.nc"):
		os.remove("tmp1.nc")

	if os.path.isfile(atmos_outfile_combo):
		os.remove(atmos_outfile_combo)

	#Looks for files in Seth's directory, /net2/sdu/..., to avoid dmgetting the NMME archive of model data if possible

        file_loc = '/archive/nmme/NMME/INPUTS/ncep2_am2/NCEP2_AM2.' + year + '.nc'
	file_loc_alt = '/net2/sdu/NMME/NCEP2_AM2/NetCDF/NCEP2_AM2.' + year + '.nc'

	if os.path.isfile(file_loc_alt):
		cmd1 = 'use ' + file_loc_alt
	else:	
		print 'dmgetting archived data files (this may take a while)'
		child = p.Popen(["dmget", file_loc],cwd=d)
        	child.communicate()
		cmd1 = 'use ' + file_loc


	#The following sets the necessary parameters in pyferret	

	cmd2 = 'set memory/size=600'
	cmd3 = 'DEFINE AXIS/CALENDAR=JULIAN/T=15-jan-' + year + ':15-' + month_abrev_low + '-' + year + ':1/npoint=' + month + '/UNIT=month tmonth'
	cmd4 = 'let temp_month = temp[gt=tmonth@AVE]'
	cmd5 = 'save/clobber/file=tmp1.nc temp_month'

	(errval, errmsg) = pyferret.run(cmd1)
	(errval, errmsg) = pyferret.run(cmd2)
	(errval, errmsg) = pyferret.run(cmd3)
	(errval, errmsg) = pyferret.run(cmd4)
	(errval, errmsg) = pyferret.run(cmd5)

	#Using the command shell, data files are concatenated in the local directory. The new NetCDF file containing averaged SST data from both calendar years will be here

	child = p.Popen(["ncrename","-v", "TEMP_MONTH,temp", "tmp1.nc"],cwd=d)
	child.communicate()
	child = p.Popen(["ncrename","-v", "TMONTH,t", "tmp1.nc"],cwd=d)
	child.communicate() 
	child = p.Popen(["ncrename","-d", "TMONTH,t", "tmp1.nc"],cwd=d)
	child.communicate() 
	child = p.Popen(["ncrcat","-O","-v","temp", "tmp1.nc", atmos_outfile],cwd=d)
	child.communicate()

	if check == 0:

		if not os.path.isfile("/home/x1y/gfdl/ecda_operational/sst/" + atmos_outfile_prev): 
			#if last year's daily SST data not averaged monthly, runs this script for last year creating needed file, then deletes the irrelevant image generated 
			child = p.Popen(["python","SSTrmse.py", "-d", '12' + year_prev ],cwd=d)
			child.communicate()
			print '***DISREGARD PRECEDING ERRORS***'
			child = p.Popen(["ncrcat", atmos_outfile_prev, atmos_outfile, atmos_outfile_combo],cwd=d)
			child.communicate()
			os.remove('tair_amo_' + year_prev + '_12.png')
			
		else:		
   			child = p.Popen(["ncrcat", "/home/x1y/gfdl/ecda_operational/sst/" + atmos_outfile_prev, atmos_outfile, atmos_outfile_combo],cwd=d)
			child.communicate()		


		cmd7 = "use " + atmos_outfile_combo

	else:
		print "WARNING: Only considering one year's worth of data..."
		cmd7 = "use " + atmos_outfile 

	returnCode = child.returncode

	#the following automates the pyferret plot generation and saves a png image file of the plot in the local dir

	filename = 'tair_amo_' + year + '_' + month + '.png'

	header()
	
	cmd8 = "let temp2 = temp[d=2,gxy=temp[d=1],gt=temp[d=1]@asn]"
	cmd9 = "let err1 = temp[d=1,k=24] - temp2[k=24]"
	cmd11 = 'sha/lev=(0.,5.0,0.5)(inf) var1[l=1:' + timeline + '@ave]^0.5'
	cmd12 = 'go land'
	cmd125 = str('ANNOTATE/NOUSER/XPOS=2/YPOS=6.25 "Air Temp RMSE ' + year_prev + '-' + year + '"')
	cmd13 = 'FRAME/FILE=' + filename  #saves png

	(errval, errmsg) = pyferret.run(cmd7)
	(errval, errmsg) = pyferret.run(cmd8)
	(errval, errmsg) = pyferret.run(cmd9)

	body()

	(errval, errmsg) = pyferret.run(cmd11)
	(errval, errmsg) = pyferret.run(cmd12)
	(errval, errmsg) = pyferret.run(cmd125)
	(errval, errmsg) = pyferret.run(cmd13)

	#file clean up
	if os.path.exists("tmp1.nc"):
		os.remove("tmp1.nc")

	#image file/script check
	if os.path.exists(str(filename)):
		if check == 0:
			print 'SUCCESS. Plot image file for Global Air Temp SST RMSE ' + year_prev + '/' + year + ' since ' + month_abrev + ' is located in the local directory and is named: ' + filename

		if check == 1:
			print 'ERROR. PARTIAL SUCCESS. Plot image file for Global Air Temp RMSE (' + year + ' ONLY!!!) is located in the local directory and is named: ' + filename
	else:
		print "ERROR. No plots generated. Please ensure data files are located in their proper directories. See '-h'"
		exit(1)


def header():
	
	#the following clears data from previously running pyferrets, establishes base parameters, and loads ensemble data

	com1 = 'cancel data/all'
	com2 = 'def sym print_opt $1"0"'
	com3 = 'set mem/size=400'
	com4 = 'use ecda_v31_atmos_auto.des'

	(errval, errmsg) = pyferret.run(com1)
	(errval, errmsg) = pyferret.run(com2)
	(errval, errmsg) = pyferret.run(com3)
	(errval, errmsg) = pyferret.run(com4)

def body():
	
	#the following calculates, lists, and plots RMSE. This method depends on functions computed in the main method

	com5 = 'let var1 = err1^2; let rms10 = var1[x=@ave,y=60s:60n@ave]^0.5' 
	com6 = 'set win 1'
	com7 = 'set viewport upper' 
	com8 = 'plot/vl=0.0:1.5:0.1/line=1 rms10' 
	com9 = 'let var1 = err1^2;'
	com10 = 'let rms1 = var1[k=24,x=@ave,y=60s:60n@ave]^0.5'
	com11 = 'list rms10' 
	com12 = 'plot/ov/line=1/DASH rms1'
	com13 = 'set viewport lower'
	com14 = 'let var1 = err1^2; let rms1 = var1[x=@ave,y=60s:60n@ave]^0.5'
	com15 = 'list rms1'
	com16 = 'set win 2'
	com17 = 'cancel mode nodata_lab'
	com18 = 'set viewport upper'
	com19 = 'cancel mode nodata_lab'
	com20 = 'plot/vl=0:2.0:0.1/line=1/DASH rms1'
	com21 = 'set viewport lower'
	com22 = 'set region/y=80s:80n'

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
	(errval, errmsg) = pyferret.run(com17)
	(errval, errmsg) = pyferret.run(com18)
	(errval, errmsg) = pyferret.run(com19)
	(errval, errmsg) = pyferret.run(com20)
	(errval, errmsg) = pyferret.run(com21)
	(errval, errmsg) = pyferret.run(com22)

if __name__=="__main__":
    mymain(sys.argv[1:])



