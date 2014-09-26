import sqlite3
import datetime
import numpy as np

conn = sqlite3.connect("gbtArchivePickles/gbtarchive.db")
c = conn.execute('select * from Scans')
fields = list(map(lambda x: x[0], c.description))

c = conn.cursor()

c.execute('select date(filedate) as day,sum(scanlen) from Scans group by day order by day')

time_by_day = c.fetchall()

na = np.array(time_by_day)
mask = na[:,1]/3600.0 > 0
nam = na[mask]

mask = nam[:,1]/3600.0 < 24
na_masked = nam[mask]

print 'minimum', na_masked[:,1].min()
print 'maximum', na_masked[:,1].max()


outfile = open('timeonsky.csv','w')
writer = csv.writer(outfile)
writer.writerow(['Date','Time'])
hrs_by_day = np.array((na_masked[:,0],na_masked[:,1]/3600.)).T
for row in hrs_by_day:
    writer.writerow(row)
outfile.close()
