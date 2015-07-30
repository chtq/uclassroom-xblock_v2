#!/usr/bin/python

import pymongo
import json
conn=pymongo.Connection("192.168.122.115", 27017)
db=conn.test
user=db.user

result=user.find_one({"username":"chtq2", "dockername":"aaaa"})
print result
print '\n'.join(result["result"]["result"][0]["result"]["output"])
