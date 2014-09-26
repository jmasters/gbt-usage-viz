import sqlite3
import datetime
import numpy as np
import csv
import argparse
import sys
import subprocess

# argument parser
parser = argparse.ArgumentParser(description='Generate a csv to show reciever usage by day.')
parser.add_argument('receiver', nargs='?', 
                    choices=['Holography','Rcvr12_18', 'Rcvr18_26', 'Rcvr1_2',
                             'Rcvr26_40', 'Rcvr2_3', 'Rcvr40_52', 'Rcvr4_6', 
                             'Rcvr68_92', 'Rcvr8_10', 'RcvrArray18_26', 
                             'RcvrPF_1', 'RcvrPF_2', 'Rcvr_PAR', 'all'],
                    default='all', help='receiver name')
args = parser.parse_args()
receiver = args.receiver

print '------------------------------'
print 'receiver ' + '[' + receiver + ']'
print '------------------------------'
# database connection
print 'connecting to database...'
conn = sqlite3.connect("test.db")
# c = conn.execute('select * from Scans')
# fields = list(map(lambda x: x[0], c.description))
c = conn.cursor()

# run db query
if receiver.lower() == 'all':
    sqlstring = 'select date(filedate) as day,sum(scanlen) from Scans group by day order by day'
else:
    sqlstring = 'select date(filedate) as day,sum(scanlen) from Scans where receiver = "{rx}" group by day order by day'.format(rx=receiver)
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
outfilename = '{rx}.csv'.format(rx=receiver)
outfile = open(outfilename, 'w')
writer = csv.writer(outfile)
writer.writerow(['Date','Time'])

hrs_by_day = np.array((dates,times)).T
for row in hrs_by_day:
    writer.writerow(row)
outfile.close()

print 'creating html file...'
inp = 'Rcvr.html_template'
outp = receiver + '.html'
out_file = open(outp, 'w')

sed_replace = 's/{{receiver}}/'+ receiver +'/g; s/{{startyear}}/'+ str(startyear) +'/g; s/{{endyear}}/'+ str(endyear) +'/g;'
sub = subprocess.call(['sed', sed_replace, inp], stdout=out_file)

out_file.close()

print 'done.'

