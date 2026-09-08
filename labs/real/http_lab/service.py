"""Bounded loopback fixture. No remote targets, file access, or mutation endpoints."""
import argparse
from http.server import HTTPServer,BaseHTTPRequestHandler
import json
import time
from urllib.parse import urlsplit,parse_qs

class Handler(BaseHTTPRequestHandler):
    total=0
    errors=0
    def log_message(self,*args):pass
    def do_GET(self):
        started=time.monotonic();url=urlsplit(self.path);status=200
        scenario=parse_qs(url.query).get('scenario',['healthy'])[0]
        if url.path=='/health':body=b'{"status":"process-running"}'
        elif url.path=='/quotes':
            Handler.total+=1
            if scenario=='degraded':
                time.sleep(.05);status=503;Handler.errors+=1;body=b'{"error":"synthetic upstream timeout"}'
            elif scenario=='healthy':body=b'{"symbol":"DEMO","value":100,"synthetic":true}'
            else:status=400;body=b'{"error":"unknown scenario"}'
        elif url.path=='/metrics':body=f'# TYPE requests_total counter\nrequests_total {Handler.total}\n# TYPE errors_total counter\nerrors_total {Handler.errors}\n'.encode()
        else:status=404;body=b'{}'
        self.send_response(status);self.send_header('Content-Type','text/plain; version=0.0.4' if url.path=='/metrics' else 'application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        print(json.dumps(dict(path=url.path,scenario=scenario,status=status,duration_ms=round((time.monotonic()-started)*1000,2),synthetic=True)),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8877);p.add_argument('--seconds',type=int,default=600);a=p.parse_args()
    if not 0<=a.port<=65535 or not 1<=a.seconds<=600:p.error('port 0..65535; seconds 1..600')
    server=HTTPServer(('127.0.0.1',a.port),Handler);server.timeout=.25
    print(json.dumps(dict(ready=True,port=server.server_port)),flush=True)
    deadline=time.monotonic()+a.seconds
    try:
        while time.monotonic()<deadline:server.handle_request()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
