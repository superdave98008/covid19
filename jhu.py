#!/usr/bin/python

import csv, string, itertools, subprocess, shlex, os, time
from math import log10
from datetime import datetime

# Data source is Novel Coronavirus (COVID-19) Cases,
# Center For Systems Science and Engineering at Johns Hopkins University
DATA_FILENAME='time_series_covid19_confirmed_global.csv'
DATA_URL='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
# Re-fetch the file if it is this age or older
REFRESH_INTERVAL_SECONDS=3600
#COUNTRY='Korea, South'
COUNTRY='US'

# Yields tuples of (date, cumulative number of cases for the USA)
def group_by_date(iterable, country):
  columns=map(lambda d: datetime.strptime(d,'%m/%d/%y'),iterable.next()[4:])
  def gen(row):
    for cell in map(string.atoi,row[4:]):
      yield cell
  for row in itertools.izip(*map(gen, itertools.ifilter(lambda row: row[1]==country, iterable))):
     yield (columns.pop(0), reduce(lambda x,y: x+y, row))

# Calculate log10(current day) - log10(previous day)
def exponents(iterable):
  def gen(previous):
    for (day,current) in iterable:
      yield (day, current, log10(current)-log10(previous))
      previous=current
  return gen(iterable.next()[1])

# Indicate the value of current compared to previous
def trend(iterable): 
  def gen(previous): 
    for (day,current) in iterable: 
      yield (datetime.strftime(day,'%Y-%m-%d'), current, '>=' if current>=previous else '<')
      previous=current
  return gen(iterable.next()[1])


if __name__=="__main__":
  if not os.path.isfile(DATA_FILENAME) or time.time()-os.stat(DATA_FILENAME).st_mtime>REFRESH_INTERVAL_SECONDS:
    subprocess.check_call(shlex.split('curl -o %s %s' % (DATA_FILENAME, DATA_URL)))
  csvfile=open(DATA_FILENAME)
  reader=csv.reader(csvfile)

  by_date=group_by_date(reader,COUNTRY)

  print '\nCOVID 19 Cases for %s' % COUNTRY
  print 'source: %s' % DATA_URL
  print 'exponent is log10(current/previous)'
  print 'date\t\tcases\texponent'
  print '-'*32
  for (day, current, exponent) in exponents(by_date):
    if day.month<3:
      continue
    print '%s\t%d\t%.3f' % (datetime.strftime(day,'%Y-%m-%d'), current, exponent)

