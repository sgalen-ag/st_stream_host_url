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
cdn = "ali"
protocol = "m3u8"
secret = "0b365b5a0b64262e62362f3e6dd5f06f"
duration = 2
domain = "push-gaia.88jnb.cn"
atxt = "domain_name.txt"
ffplay_path = r'C:\Users\s9308\Documents\st_stream_host_url\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe'



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

def getALI(scheme, domain, app, fullStream, secret, duration):
    timestamp = ((datetime.datetime.now()+datetime.timedelta(days=duration)).strftime('%Y%m%d%H%M%S'))

    raw = '/'+app+'/'+fullStream+'-'+timestamp+'-0-0-'+secret
    m = hashlib.md5()
    m.update(raw.encode("utf8"))
    wsSecret = m.hexdigest()

    url = (scheme+domain+'/'+app+'/'+ fullStream+ '?auth_key='+timestamp+'-0-0-'+wsSecret)
    print(url)
    return (url)

def getWS(scheme, domain, app, fullStream, secret, duration):
    timestamp = ((datetime.datetime.now()+datetime.timedelta(days=duration)).strftime('%Y%m%d%H%M%S'))
    time_array = time.strptime(timestamp, '%Y%m%d%H%M%S')
    wsABSTime = hex(int(time.mktime(time_array)))[2:]


    raw = '/'+app+'/'+fullStream+secret+wsABSTime
    m = hashlib.md5()
    m.update(raw.encode("utf8"))
    wsSecret = m.hexdigest()

    #token = api()
    #url = (scheme+domain+'/'+app+'/'+ fullStream+ '?wsSecret='+wsSecret+'&wsABSTime='+wsABSTime+'&token='+token)
    url = (scheme+domain+'/'+app+'/'+ fullStream+ '?wsSecret='+wsSecret+'&wsABSTime='+wsABSTime)

    print(url)
    return (url)

def streamtest(url):
    command = [
    ffplay_path,
    '-hide_banner', '-re', '-f', 'lavfi', '-i', 'testsrc', 
    '-f', 'lavfi', '-i', 'sine=frequency=1000', '-c:v', 'libx264', 
    '-b:v', '1600k', '-preset', 'ultrafast', '-bufsize', '3000k', 
    '-acodec', 'aac', '-ac', '2', '-ar', '44100', '-b:a', '128k', 
    '-s', '854?480','-x264opts', 'bframes=5:b-adapt=0', '-g', '50', 
    '-sc_threshold', '0', '-pix_fmt', 'yuv420p', '-f', 'flv', 
    url
    ]
    
    print(command)
    try:
      subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
      raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
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
    except Exception as e:
      print(f"解析 {domain} 時出現錯誤: {str(e)}")


cdn = DNSchecker(domain)
if re.search(r'ws', str(cdn)):
  print("ws")
  streamtest(getWS('rtmp://', domain.replace('\n', ''), app, stream, secret, duration))
  
elif re.search(r'ali', str(cdn)):
  print("ali")
  streamtest(getALI('rtmp://', domain.replace('\n', ''), app, stream, secret, duration))