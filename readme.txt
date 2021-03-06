GFDL NMME Automation Scripts
Written by Miguel Moravec

The Scripts

Global forecasts:
Generates 6 plots which compare forecasted data with historical climatology data and plot anomalies on a map of the Earth. The data is either averaged monthly or tri-monthly for each variable. The variables are precipitation, Sea Surface Temperature, and Reference Temperature respectively.

precip_glob1mm.py
precip_glob3mm.py
SST_glob1mm.py
SST_glob3mm.py
T_ref_glob1mm.py
T_ref_glob3mm.py

RMSE:
Generates two plots: The first plots changes in overall RMSE per month (averaged from daily data), the second graphs RMSE averaged for the whole data set over the geographical location its occurring.

Tair.py
SSTrmse.py

Pacific Anomalies:
Plots 4 graphs of Pacific subsurface sea temperature anomalies (averaged latitudinally) at certain longitudes vs depth for first the present and then the preceding three months.

SSTanom.py

Location:
home/mmm/FINAL_SCRIPTS

System Requirements:
Red Hat Enterprise Linux 6
Python v2.7.3
Pyferret (Module) v6.97

Required Python Packages:
subprocess
datetime
os
os.path
sys, getopt

User Documentation:
These scripts automatically generate a number of plots of for NetCDF data anomalies for specific climate variables. When running the program, the user is presented with three options, which are listed as follows:
-h launches this help text
-t generates plots using today's most recent data
-d takes the argument mmyyy and generates plots for a particular date i.e. '-d 072016'

These scripts generally rely on archived files being located in specific directories with particular naming conventions. The commented script can easily be read/modified to locate/change the directories and naming conventions.

For questions please email Miguel Moravec at miguel.moravec@vanderbilt.edu
