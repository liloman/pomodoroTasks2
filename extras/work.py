#!/usr/bin/env python
################################################################################
##
## Copyright 2016, liloman
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included
## in all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
## OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
## THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
## SOFTWARE.
##
## http:##www.opensource.org/licenses/mit-license.php
##
################################################################################

import json
import sys
# import datetime and timedelta
from datetime import datetime, timedelta

def formatSeconds(seconds):
  sec = timedelta(seconds=int(seconds))
  d = datetime(1,1,1) + sec
  if d.day == 1: 
    return "{}, {}".format("0 days",sec)
  else:
    return sec

DATEFORMAT = '%Y%m%dT%H%M%SZ'

# Extract the configuration settings.
header = 1
configuration = dict()
body = ''
for line in sys.stdin:
  if header:
    if line == '\n':
      header = 0
    else:
      fields = line.strip().split(': ', 2)
      if len(fields) == 2:
        configuration[fields[0]] = fields[1]
      else:
        configuration[fields[0]] = ''
  else:
    body += line


#print body

# Sum time by tags
totals = dict()
j = json.loads(body)
for object in j:
  start = datetime.strptime(object['start'], DATEFORMAT)

  if 'end' in object:
    end = datetime.strptime(object['end'], DATEFORMAT)
  else:
    end = datetime.utcnow()

  tracked = (end - start).total_seconds()

   
  if 'tags' in object:
      exit = 0
      key = ""
      #Concat the tags
      for tag in object['tags']:
        stag=u''.join(tag).encode('utf-8').strip()
        key += stag + " / "
        # filter out the +nowork on Shutdown ... tasks
        if stag in ("+nowork","Shutdown","Suspend","pomodoro_timeout"):
          exit = 1
          break

      #eliminate the / and trim the leading/ending spaces
      key=key[:-2].strip()

      if exit == 0:
        if key in totals:
           totals[key] += tracked
        else:
           totals[key] = tracked
  else:
      totals["No tagged"] = tracked


# Determine largest tag width.
max_width = 0


for tag in totals:
  if len(tag) > max_width:
    max_width = len(tag)


if max_width > 0:
  # sane value for 110 columns max = (110 - 15(formatted) )
  max_columns = 92
  if max_width > max_columns:
      max_width = max_columns
  start = datetime.strptime(configuration['temp.report.start'], DATEFORMAT)
  end   = datetime.strptime(configuration['temp.report.end'],   DATEFORMAT)

  # Compose report header.
  print '\nTotal by Tag from %s - %s (sorted by time)\n' % (start, end)

  # Compose table header.
  if configuration['color'] == 'on':
    print '[4m%-*s[0m [4m%15s[0m' % (max_width, 'Tag', 'Total')
  else:
    print '%-*s %10s' % (max_width, 'Tag', 'Total')
    print '-' * max_width, '-------------------'

  grand_total = 0

  # Compose table rows.Sorted by time
  for tag in sorted(totals,key=totals.get,reverse=False):
    formatted = formatSeconds(totals[tag])
    grand_total += totals[tag]
    if max_width == max_columns:
        # left 5 columns between the tag text and the time column
        print '%-*s %10s' % (max_columns, tag[:max_columns-5], formatted)
    else:
        print '%-*s %10s' % (max_width, tag, formatted)

    
  # Compose total.
  if configuration['color'] == 'on':
    print ' ' * max_width, '[4m               [0m'
  else:
    print ' ' * max_width, '-------------------'

  print '%-*s %10s' % (max_width, 'Total', formatSeconds(grand_total))

else:
  print "Nothing found. Check your search "

