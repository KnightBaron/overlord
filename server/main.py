from bottle import request, route, post, run
import bottle
import datetime
from pymongo import MongoClient
import logging

import common
import config
import scheduler_idlewait as scheduler

def authen(hostname, authkey):
  return True

def change_host_status(hostname, status, dt):
  conn = MongoClient(config.MONGO_SERVER)[config.MONGO_DB]
  host = conn.host.find_one({'hostname': hostname})
  host['last_dt'] = dt
  host['status'] = 'idle'
  conn.host.update({'_id':host['_id']}, host)

def record_values(src_hostname, values, dt):
  conn = MongoClient(config.MONGO_SERVER)[config.MONGO_DB]
  logging.error("values : %s" %str(values))
  src_host = conn.host.find_one({'hostname': src_hostname})
  for r in values:
    flow_query = {'src': src_hostname, 'dest': r["dest"]}
    flow = conn.flow.find_one(flow_query)
    row = dict()
    row["src"] = src_hostname
    row["dt"] = dt
    row["dest"] = r["dest"]
    row["type"] = r["type"]
    if row["type"] == 'ping':
      row["min"] = float(r["min"])
      row["max"] = float(r["max"])
      row["avg"] = float(r["avg"])
      flow["last_ping_dt"] = dt
    elif row["type"] == 'iperf':
      row["bandwidth"] = float(r["bandwidth"])
      flow["last_iperf_dt"] = dt
    else:
      logging.error("invalid value type: %s" %srow["type"])
      return False
    conn.flow.update({'_id': flow["_id"]}, flow)

    conn.values.insert(row)
    logging.error("recording : %s" %str(row['src']))
    conn.flow.update({'_id': flow["_id"]}, flow)
    logging.error("updating flow time:"+  str(flow['last_iperf_dt']) +" : "+ str(type(flow['src'])) + "->" + str(type(flow['dest'])))

  src_host["status"] = 'idle'
  conn.host.update({'_id':src_host["_id"]}, src_host)
 

@post('/listen')
def index(hostname=0):
  d = request.json
  logging.error('POST request:' +str(d))
  if not authen(d["hostname"], d["authkey"]):
    return {'error': 'authenticate fail'}
  dt = datetime.datetime.now()
  change_host_status(d["hostname"], "idle", dt)
  record_values(d["hostname"], d["results"], dt)
  jobs = scheduler.getJobForHost(d["hostname"], dt)
  result = dict()
  result['jobs'] = jobs
  logging.error(str(result))
  return result

if __name__ == '__main__':
  scheduler.initialize()
  run(server='paste', host='0.0.0.0', port=8081)
