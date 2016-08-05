#!/usr/bin/env python

#Written by Miguel M. Moravec. For questions please email miguel.moravec@vanderbilt.edu
#This script automatically generates 6 forecast plots of Global SST anomalies by averaging model predictions every 3 months for 11 months succeeding a specified date and then comparing the averages to historical climatologies.
#This script relies on the standard naming convention of historical SST NetCDF files in this archived directory: '/archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_01' + month (mm) + '/maproom/'
#This script also relies on the contemporary data located in this archived directory: '/archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_01' + date_abrev_opp (mmYYYY) + '/pp_ensemble/ocean_month/ts/monthly/1yr/ OR just '/archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_01' + date_abrev_opp (mmYYYY) + '/'

import subprocess as p
import datetime
import os
import os.path
import sys, getopt

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
   		print "ERROR Invalid Syntax. See 'SSTglob3mm.py -h'"
		sys.exit(2)

	for opt, arg in opts:
 		if opt == '-h': #help option
        		print '\nThis script automatically generates 6 forecast plots of Global SST anomalies by averaging model predictions every 3 months for 11 months succeeding a specified date and then comparing the averages to historical climatologies. \n'
			print 'Options are as follows:'
			print "'-h' launches this help text"
			print "'-t' generates forecast plots using today's most recent data"
			print "'-d mmyyy' generates forecast plots for the 11 months succeeding a particular date i.e. '-d 072016' \n"
			print 'This script relies on the standard naming convention of SST NetCDF files in this directory:'
			print '"/archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_01" + month (mm) + "/maproom/" \n'
			print 'This script also relies on the historical data located in this archived file:'
			print "'/archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_01' + date_abrev_opp (mmYYYY) + '/pp_ensemble/ocean_month/ts/monthly/1yr/ \n\nAlternatively located here: \n'/archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_01' + date_abrev_opp (mmYYYY) + '/' \n"
			print 'Written by Miguel M. Moravec. For questions please email miguel.moravec@vanderbilt.edu \n'
        		sys.exit()

		elif opt == '-t':
			#option automatically generates most recent plots
			today = now.strftime('%m%Y')

		elif opt in ('-d', '--input'):
         		#option generates plots for specific date mmyyyy
			today = arg			
	
	#reminds user to select an option

	if today == '':
		print 'ERROR must select an option'
		print "'-t' generates plots for 11 months succeeding today's date"
		print "'-d mmyyy' generates plots for 11 months succeeding a particular date i.e. '-d 072016'"
		exit(1)

	try:
		date = datetime.datetime.strptime('25' + today, '%d%m%Y')

	except ValueError:
		print "ERROR Invalid Syntax. Arguments following '-d' should be formatted: mmyyyy"
		exit(1)

	#sets time variables, used in generation of NetCDFs, plots, and file names	

	date = datetime.datetime.strptime('25' + today, '%d%m%Y')	
	date_abrev = date.strftime('%Y%m')
	date_abrev_opp = date.strftime('%m%Y')
	month = date.strftime('%m')
	month_abrev = date.strftime('%b')
	month_abrev_low = month_abrev.lower()
	year = date.strftime('%Y')
	year_abrev = date.strftime('%y')

	date_fut = date + datetime.timedelta(days=(335))    #advances date 11 months
	date_fut_abrev = date_fut.strftime('%Y%m')
	month_fut = date_fut.strftime('%m')
	month_abrev_fut = date_fut.strftime('%b')
	month_abrev_fut_lower = month_abrev_fut.lower()
	year_fut = date_fut.strftime('%Y')

	print 'Generating plots with available data for ', month, '/', year, '-', month_fut, '/', year_fut, '...'

	#histotical climatology data location     	
	file_clm = str('/archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_01' + month + '/maproom/ocean_month_ens_01-12.1982' + month + '-2012' + month_fut + '.temp.climo.nc')
	file_clm_alt = str('/archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_01' + month + '/maproom/ocean_month_ens01-12.1982' + month + '-2012' + month_fut + '.temp.climo.nc')
	file_clm_alt2 = str('/archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_01' + month + '/maproom/ocean_month_ens_01.1982' + month + '-201112.temp.nc')
	
	#contemporary data location			###NOTE: Exception for input date 032016, currently able to locate nc data
	file_rt = str('/archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_01' + date_abrev_opp + '/pp_ensemble/ocean_month/ts/monthly/1yr/ocean_month.' + date_abrev + '-' + date_fut_abrev + '.temp.nc')
	file_rt_alt = str('/archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_01' + date_abrev_opp + '/pp_ensemble/ocean_month/ts/monthly/1yr/ocean_month.' + year + '02-' + date_fut_abrev + '.temp.nc')	
	#the alternate file naming convention for variable 'file_rt_alt' is exclusively for getting data for 032016

	d = '.'	

	if os.path.isfile(file_clm):
		
		print 'dmgetting archived data files (1/2). Please wait, this may take a while . . .'
		child = p.Popen(["dmget", file_clm],cwd=d)
      		child.communicate()
		cmd = 'use ' + file_clm

	elif os.path.isfile(file_clm_alt):
		
		print 'dmgetting archived data files (1/2). Please wait, this may take a while . . .'
		child = p.Popen(["dmget", file_clm_alt],cwd=d)
      		child.communicate()
		cmd = 'use ' + file_clm_alt

	elif os.path.isfile(file_clm_alt2): #file:///archive/rgg/CM2.5/CM2.5_FLOR_B01_p1_ECDA_2.1Rv3.1_0101/maproom/ocean_month_ens_01.198201-201112.temp.nc
		
		print 'dmgetting archived data files (1/2). Please wait, this may take a while . . .'
		child = p.Popen(["dmget", file_clm_alt2],cwd=d)
      		child.communicate()
		cmd = 'use ' + file_clm_alt2

	else:
		print 'dmgetting archived data files (1/2). Please wait, this may take a while . . .'
		print "ERROR. Unable to locate historical data. Please ensure data files are located in their proper directories. See '-h'"
		exit(1)

	if os.path.isfile(file_rt):

		print 'dmgetting archived data files (2/2). Please wait, this may take a while . . .'
		child = p.Popen(["dmget", file_rt],cwd=d)
	      	child.communicate()
		cmd0 = 'use ' + file_rt

	elif os.path.isfile(file_rt_alt) and month == '03':
		
		print 'dmgetting archived data files (2/2). Please wait, this may take a while . . .'
		child = p.Popen(["dmget", file_rt_alt],cwd=d)
      		child.communicate()
		cmd0 = 'use ' + file_rt_alt

	else:
		print 'dmgetting archived data files (2/2). Please wait, this may take a while . . .'
		print "ERROR. Unable to locate contemporary data. Please ensure data files are located in their proper directories. See '-h'"
		exit(1)

	#does pyferret things

	if ( not pyferret.start(quiet=True, journal=False, unmapped=True) ):
		print "ERROR. Pyferret start failed. Exiting . . ."
		exit(1)

	header ()

	(errval, errmsg) = pyferret.run(cmd)
	(errval, errmsg) = pyferret.run(cmd0)

	#the following variables are set to allow the plot generation loop to run without modifying the date variables
	count = 0
	month_b = int(month)
	month_c = 1

	filename = 'SST_glob_anom_3mm_'+ str(date_abrev) + '.png'

	while (count < 6): 

		month_string = 'JFMAMJJASONDJFMAMJJASOND'
		month_combo = month_string[month_b-1]+month_string[month_b]+month_string[month_b+1]		

		count = count + 1
		
		print 'Generating forecast plot ' + str(count)
		
		cmd1 = 'set viewport V' + str(count)
		cmd2 = 'SHADE/SET_UP/lev=(-inf)(-3,-1,1)(-1,-0.5)(-0.5,0.5,0.25)(0.5,1,0.5)(1,3,1)(inf)/PALETTE=blue_darkred (temp[d=2,L=' + str(month_c) + ':' + str(month_c+1) + '@AVE,K=1]-temp[d=1,L=' + str(month_c) + ':' + str(month_c+1) + '@AVE,K=1])'			#equation essentially subtracts contemporary temp 3month avg from historical temp 3month avg at depth 5m (k=1)
		cmd3 = 'PPL LABSET 0.15, 0.15, 0'
		cmd3alt = 'PPL LABSET 0.15, 0.15, 0.15'
		cmd4 = 'GO unlabel 5'
		cmd4alt = 'GO unlabel 1'
		cmd4alt1 = 'GO unlabel 2'
		cmd4alt2 = 'GO unlabel 3'
		cmd5 = 'PPL TITLE Sea Surface Temp Anomalies (Deg C)'
		cmd6 = 'PPL SHADE'
		cmd7 = 'go fland'
		cmd9 = 'ANNOTATE/NOUSER/XPOS=-0.1/YPOS=4.35 "' + month_combo + '"'
		cmd10 = 'FRAME/FILE=' + filename

		(errval, errmsg) = pyferret.run(cmd1)
		(errval, errmsg) = pyferret.run(cmd2)

		if count > 2:		#this if statement prevents the y axis label 'latitude' from overlapping on other plots after the first two are generated

			(errval, errmsg) = pyferret.run(cmd3)

		else:

			(errval, errmsg) = pyferret.run(cmd3alt)	

		(errval, errmsg) = pyferret.run(cmd4)

		if count == 2 or count == 4 or count == 6: 		#clears pyferret default labels to make room for title

			(errval, errmsg) = pyferret.run(cmd4alt)
			(errval, errmsg) = pyferret.run(cmd4alt1)
			(errval, errmsg) = pyferret.run(cmd4alt2)

		(errval, errmsg) = pyferret.run(cmd5)
		(errval, errmsg) = pyferret.run(cmd6)
		(errval, errmsg) = pyferret.run(cmd7)
		(errval, errmsg) = pyferret.run(cmd9)

		if count == 6:						#title

			cmd11 = str('ANNOTATE/NOUSER/XPOS=-7.9/YPOS=5.25 "SST Global Anomalies ' + month + '/' + year + '-' + month_fut + '/' + year_fut + ' (3-Month Averages)"')
			(errval, errmsg) = pyferret.run(cmd11)

		(errval, errmsg) = pyferret.run(cmd10)

		month_c = month_c + 2
		month_b = month_b + 2

	
	#allows file to save before checking if file exists	
	from time import sleep
	sleep(2)

	if os.path.exists(filename):
		print 'SUCCESS. Plot image file for tri-monthly global SST anom for ', month, '/', year, '-', month_fut, '/', year_fut, ' is located in the local directory and is named: ', filename
	else:
		print "ERROR. No plots generated. Please ensure data files are located in their proper directories. See '-h'"
		exit(1)


def header():
	#the following clears data from previously running pyferrets and establishes base parameters

	com1 = 'cancel data/all'
	com3 = 'set mem/size=240'
	com4 = 'set WINDOW/SIZE=5'
	com5 = 'define VIEWPORT/xlim=0.,0.36/ylim=0.5,1.0 V1'
	com6 = 'define VIEWPORT/xlim=0.,0.36/ylim=0.,0.5 V2'
	com7 = 'define VIEWPORT/xlim=0.315,0.675/ylim=0.5,1.0 V3'
	com8 = 'define VIEWPORT/xlim=0.315,0.675/ylim=0.,0.5 V4'
	com9 = 'define VIEWPORT/xlim=0.63,1/ylim=0.5,1.0 V5'
	com10 = 'define VIEWPORT/xlim=0.63,1/ylim=0.,0.5 V6'


	(errval, errmsg) = pyferret.run(com1)
	(errval, errmsg) = pyferret.run(com3)
	(errval, errmsg) = pyferret.run(com4)
	(errval, errmsg) = pyferret.run(com5)
	(errval, errmsg) = pyferret.run(com6)
	(errval, errmsg) = pyferret.run(com7)
	(errval, errmsg) = pyferret.run(com8)
	(errval, errmsg) = pyferret.run(com9)
	(errval, errmsg) = pyferret.run(com10)


if __name__=="__main__":
    mymain(sys.argv[1:])
