#!/usr/bin/env python

#Written by Miguel M. Moravec. For questions please email miguel.moravec@vanderbilt.edu
#This script automatically generates plots of Pacific SST anomalies for the 4 months preceding a specified date
#This script relies on the standard naming convention of SST NetCDF files in this model directory: /archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/
#This script also relies on the historical data located in this archived climatology file: /archive/x1y/yxue/realtime/temp.clim.1981_2010.nc

import subprocess
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
   		print "ERROR Invalid Syntax. See 'SSTanom.py -h'"
		sys.exit(2)

	for opt, arg in opts:
 		if opt == '-h': #help option
        		print '\nThis script automatically generates plots of Pacific SST anomalies for the 4 months preceding a specified date \n'
			print 'Options are as follows:'
			print "'-h' launches this help text"
			print "'-t' generates today's most recent plots"
			print "'-d mmyyy' generates plots for months preceding a particular date i.e. '-d 072016' \n"
			print 'This script relies on the standard naming convention of SST NetCDF files in this model directory:'
			print '/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/ \n'
			print 'This script also relies on the historical data located in this archived climatology file:'
			print '/archive/x1y/yxue/realtime/temp.clim.1981_2010.nc \n'
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
		print "'-t' generates plots for months preceding today's date"
		print "'-d mmyyy' generates plots for months preceding a particular date i.e. '-d 072016'"
		exit(1)

	try:
		date = datetime.datetime.strptime('25' + today, '%d%m%Y')
	except ValueError:
		print "ERROR Invalid Syntax. Arguments following '-d' should be formatted: mmyyyy"
		exit(1)
    
	#the following sets file naming convention and time variables, used in generation of NetCDFs, plots, and file names

	basedir = '/archive/x1y/FMS/c3/CM2.1_ECDA/CM2.1R_ECDA_v3.1_1960_pfl_auto/gfdl.ncrc3-intel-prod-openmp/history/tmp/'
	filetail = "01.ocean_month.ensm.nc"
    
	month = date.strftime('%m')
	year = date.strftime('%Y')

	#the following automates the pyferret plot generation and saves a png image file in the local directory	

	print 'Generating plots for Pacific SST anomalies for months preceeding', month,'/', year, '...'

	filename = 'tempa_latest4mon_' + year + '_' + month + '.png'

	if ( not pyferret.start(quiet=True, journal=False, unmapped=True) ):
		print "ERROR. Pyferret start failed. Exiting . . ."
		exit(1)

	header()

	count = 0

	while (count < 4): 

		#this loop selects the appropriate dataset and generates a plot for each month comparing that month's data to the historical average. 
		#The increasing 'count' variable is used both to subtract a month from the date and to ensure each plot is generated in a unique corner of the image.
		#The historical data was already loaded into pyferret using the header() method, and then each monthly data set is loaded into the loop in reverse chronological order
	
		count = count + 1

    		math = date + datetime.timedelta(days=(-30*count))
    		prev_date =  str(math.strftime('%Y%m'))
        	prev_month =  str(math.strftime('%m'))
		prev_year =  str(math.strftime('%Y'))

		d="." #uses local directory
        	child = subprocess.Popen(["dmget", basedir + prev_date + filetail, "/archive/x1y/yxue/realtime/temp.clim.1981_2010.nc"],cwd=d)
        	child.communicate()

        	cmd1 ="Use " + basedir + prev_date + filetail
        	cmd2 = 'Let diff1 = temp[d=' + str(count+1) + ',l=1] - temp[d=1,l=' + prev_month + ']'
       	 	cmd3 = 'set viewport V' + str(count)

        	(errval, errmsg) = pyferret.run(cmd1)
        	(errval, errmsg) = pyferret.run(cmd2)
        	(errval, errmsg) = pyferret.run(cmd3)

		body()

	cmd8 = str('ANNOTATE/NOUSER/XPOS=-2.5/YPOS=5 "Pacific SST Anomalies"')
	cmd9 = 'set mode/last verify'
	cmd10 = 'FRAME/FILE=' + filename

	(errval, errmsg) = pyferret.run(cmd8)
	(errval, errmsg) = pyferret.run(cmd9)
	(errval, errmsg) = pyferret.run(cmd10)

	if os.path.exists(str(filename)):
		print 'SUCCESS. The image file containing the SST anomaly plots for the 4 months preceeding ', month,'/', year, ' is located in the local directory and is named:', filename
	else:
		print "ERROR. No plots generated. Please ensure data files are located in their proper directories. See '-h'"
		exit(1)
def header():

	#the following clears data from previously running pyferrets, establishes base parameters, and loads historical data

	com2 = 'cancel data/all'
	com3 = 'def sym print_opt $1"0"'
	com4 = 'define VIEWPORT/xlim=0.,0.5/ylim=0.5,1.0 V1'
	com5 = 'define VIEWPORT/xlim=0.,0.5/ylim=0.,0.5 V2'
	com6 = 'define VIEWPORT/xlim=0.5,1.0/ylim=0.5,1.0 V3'
	com7 = 'define VIEWPORT/xlim=0.5,1.0/ylim=0.,0.5 V4'
	com8 = 'set mem/size=240'
	com9 = 'use "/archive/x1y/yxue/realtime/temp.clim.1981_2010.nc"'

	(errval, errmsg) = pyferret.run(com2)
	(errval, errmsg) = pyferret.run(com3)
	(errval, errmsg) = pyferret.run(com4)
	(errval, errmsg) = pyferret.run(com5)
	(errval, errmsg) = pyferret.run(com6)
	(errval, errmsg) = pyferret.run(com7)
	(errval, errmsg) = pyferret.run(com8)
	(errval, errmsg) = pyferret.run(com9)

def body():

	#the following plots SST anomalies for each month. This method depends on functions computed in the loop in the main method and will be run 4 times

	com10 = 'cancel mode nodata_lab'
	com11 = 'fill/lev=(-inf)(-7,-3,1)(-3,3,0.5)(3,7,1)(inf)/PALETTE=blue_darkred diff1[z=0:300,y=2s:2n@ave,x=120e:78w]'

	(errval, errmsg) = pyferret.run(com10)
	(errval, errmsg) = pyferret.run(com11)

if __name__=="__main__":
    mymain(sys.argv[1:])
