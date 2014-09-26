import numpy as np
import collections
import csv

c.execute('select min(date(filedate)) as day from Scans group by observer having day like "20%" order by day')
newbies = c.fetchall()


na = np.array(newbies)
newbies = map(str,na[:,0])

newbiecount = collections.Counter(newbies)

outfile = open('newusers.csv','w')
writer = csv.writer(outfile)
writer.writerow(['Date','Time'])
for x in newbiecount.items():
    writer.writerow(x)
outfile.close()


