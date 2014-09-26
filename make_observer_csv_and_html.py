import sqlite3
import datetime
import numpy as np
import csv
import argparse
import sys
import subprocess

# argument parser
parser = argparse.ArgumentParser(description='Generate a csv to show observer usage by day.')
parser.add_argument('observer', nargs=1, type=str, help='observer name')
args = parser.parse_args()
observer = args.observer[0]

print '------------------------------'
print 'observer ' + '[' + observer + ']'
print '------------------------------'
# database connection
print 'connecting to database...'
conn = sqlite3.connect("gbtarchive.db")
# c = conn.execute('select * from Scans')
# fields = list(map(lambda x: x[0], c.description))
c = conn.cursor()

# run db query
sqlstring = 'select date(filedate) as day,sum(scanlen) from Scans where observer = "{a}" group by day order by day'.format(a=observer)
print 'running query...'
c.execute(sqlstring)

time_by_day = c.fetchall()
if len(time_by_day) == 0:
    print 'No hours for observer', observer
    sys.exit()

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
outfilename = '{be}.csv'.format(be=observer.replace(',','').replace(' ',''))
outfile = open(outfilename, 'w')
writer = csv.writer(outfile)
writer.writerow(['Date','Time'])

hrs_by_day = np.array((dates,times)).T
for row in hrs_by_day:
    writer.writerow(row)
outfile.close()

print 'creating html file...'
inp = 'Observer.html_template'
outp = observer.replace(',','').replace(' ','') + '.html'
out_file = open(outp, 'w')

sed_replace = 's/{{searchterm}}/'+ observer.replace(',','').replace(' ','') +'/g; s/{{startyear}}/'+ str(startyear) +'/g; s/{{endyear}}/'+ str(endyear) +'/g;'
sub = subprocess.call(['sed', sed_replace, inp], stdout=out_file)

out_file.close()

print 'done.'

