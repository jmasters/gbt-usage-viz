import sqlite3
import datetime
import numpy as np
import csv
import argparse
import sys
import subprocess

# argument parser
parser = argparse.ArgumentParser(description='Generate a csv to show backend usage by day.')
parser.add_argument('backend', nargs='?', 
                    choices=['CCB26_40', 'DCR', 'DCR, CCB26_40', 'DCR, SpectralProcessor', 'DCR, Spectrometer', 'GUPPI', 'MUSTANG', 'Rcvr_PAR', 'SPIGOT', 'SpectralProcessor', 'SpectralProcessor, DCR', 'Spectrometer', 'Spectrometer, DCR', 'Spectrometer, SpectralProcessor', 'VEGAS', 'VLBA_DAR', 'Zpectrometer'],
                    default='all', help='backend name')
args = parser.parse_args()
backend = args.backend

print '------------------------------'
print 'backend ' + '[' + backend + ']'
print '------------------------------'
# database connection
print 'connecting to database...'
conn = sqlite3.connect("test.db")
# c = conn.execute('select * from Scans')
# fields = list(map(lambda x: x[0], c.description))
c = conn.cursor()

# run db query
if backend.lower() == 'all':
    sqlstring = 'select date(filedate) as day,sum(scanlen) from Scans group by day order by day'
else:
    sqlstring = 'select date(filedate) as day,sum(scanlen) from Scans where backend = "{be}" group by day order by day'.format(be=backend)
print 'running query...'
c.execute(sqlstring)

time_by_day = c.fetchall()

na = np.array(time_by_day)
times = np.array(map(int,na[:,1]))/3600.
dates = na[:,0]

# create a mask to filter times <= 0
mask = times > 0

times = times[mask]
dates = dates[mask]

# create a mask to filter times > 24 hrs
mask = times < 24

times = times[mask]
dates = dates[mask]

startyear = int(dates[0].split('-')[0])
endyear = int(dates[-1].split('-')[0])+1

#print 'minimum', times.min()
#print 'maximum', times.max()

print 'creating csv file...'
outfilename = '{be}.csv'.format(be=backend.replace(',','').replace(' ',''))
outfile = open(outfilename, 'w')
writer = csv.writer(outfile)
writer.writerow(['Date','Time'])

hrs_by_day = np.array((dates,times)).T
for row in hrs_by_day:
    writer.writerow(row)
outfile.close()

print 'creating html file...'
inp = 'Backend.html_template'
outp = backend.replace(',','').replace(' ','') + '.html'
out_file = open(outp, 'w')

sed_replace = 's/{{backend}}/'+ backend.replace(',','').replace(' ','') +'/g; s/{{startyear}}/'+ str(startyear) +'/g; s/{{endyear}}/'+ str(endyear) +'/g;'
sub = subprocess.call(['sed', sed_replace, inp], stdout=out_file)

out_file.close()

print 'done.'

