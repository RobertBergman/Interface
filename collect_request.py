#!/usr/bin/python

# __author__ = 'Rbergma'
import httplib
conn = httplib.HTTPConnection('127.0.0.1:5000')

conn.request("GET", "/collect/")
r1 = conn.getresponse()
print r1.status, r1.reason

data1 = r1.read()
print(data1)
