import re
import os
import time
import json
import hashlib
import datetime
import requests
import subprocess
import dns.resolver


app = "live"
stream = "benny"
cdn = "ws"
protocols = ["flv","m3u8"]
secret = "0b365b5a0b64262e62362f3e6dd5f06f"
duration = 2
domain = "pull-ofZhifeng032.bchxny.com"
atxt = "domain_name.txt"
vlc_path = r'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe'


def api():
    url = "https://stream-token-saba.lzmd.info/token-service/server/v1/getToken"

    payload = json.dumps({
      "uip": "220.130.164.129",
      "uid": "op"
    })
    headers = {
      'x-sa-access-token': 'YjNlNTNlZmEtN2I4NC00NjJkLTkyMDAtNTJjZmM3MjEyNGRi',
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    today_json = json.loads(response.text)
    data = today_json['data']
    token = data['token']
    #print(token)
    return token

def getFullStream(cdn, protocol, stream):
  if (protocol == 'flv'):
    return stream+".flv"
  if (protocol == 'm3u8'):
    if (cdn == "ali"):
      return stream+".m3u8"
    if (cdn == "ws"):
      return stream+"/playlist.m3u8"
    if (cdn == "tc"):
      return stream+".m3u8"


def getstream(scheme, domain, app, fullStream, secret, duration):
  timestamp = ((datetime.datetime.now()+datetime.timedelta(days=duration)).strftime('%Y%m%d%H%M%S'))
  time_array = time.strptime(timestamp, '%Y%m%d%H%M%S')
  wsABSTime = hex(int(time.mktime(time_array)))[2:]
  
  token = api()
  m = hashlib.md5()

  if re.search(r'ws', str(cdn)):
    print(cdn)
    raw = '/'+app+'/'+fullStream+secret+wsABSTime
    m.update(raw.encode("utf8"))
    wsSecret = m.hexdigest()
    url = (scheme+domain+'/'+app+'/'+ fullStream+ '?wsSecret='+wsSecret+'&wsABSTime='+wsABSTime+'&token='+token)
    #url = (scheme+domain+'/'+app+'/'+ fullStream+ '?wsSecret='+wsSecret+'&wsABSTime='+wsABSTime)
  if re.search(r'ali', str(cdn)):
    print(cdn)
    raw = '/'+app+'/'+fullStream+'-'+timestamp+'-0-0-'+secret
    m.update(raw.encode("utf8"))
    wsSecret = m.hexdigest()
    url = (scheme+domain+'/'+app+'/'+ fullStream+ '?auth_key='+timestamp+'-0-0-'+wsSecret)
  print(url)
  return (url)

def streamtest(url):
    command = [
    vlc_path,
    url,
    '--sout', '#duplicate{dst=file{dst=output.ts},dst=display}',
    '--run-time', '2',
    '--play-and-exit'
    ]
    print(command)
    subprocess.run(command, check=True)


def DNSchecker(domain):
  try:
      my_resolver = dns.resolver.Resolver(configure=False)
      my_resolver.nameservers = ['1.1.1.1']
      print(str(domain))
      for rdata in my_resolver.resolve(str(domain.strip()), 'CNAME'):
          cdnname = (rdata.target)
          print(cdnname)
          if re.search(r'cdngslb', str(cdnname)):
              print("ali")
              return("ali")
          if re.search(r'gccdn', str(cdnname)):
              print("ws")
              return("ws")
          if re.search(r'wscdns', str(cdnname)):
              print("ws")
              return("ws")
  except Exception as e:
      print(f"解析 {domain} 時出現錯誤: {str(e)}")

f = open(atxt,"r",encoding="UTF-8")
domain_list = []
for line in f:
    domain_list.append(line)

for domain in domain_list:
  cdn = DNSchecker(domain)

  for protocol in protocols:
    print(protocol)
    URL = getstream('https://', domain.replace('\n', ''), app, getFullStream(cdn, protocol, stream), secret, duration)
    streamtest(URL)
    
    if os.path.exists("output.ts") and os.path.getsize("output.ts") > 0:
      print("拉流成功")
    else:
      print("拉流失敗")
      os.remove('output.ts')
      with open("error_streamingURL.txt", 'a',encoding="UTF-8") as output:
        output.write(str("ffplay \'" +URL+'\'\n'))
