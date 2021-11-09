###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Zerodha technologies Pvt. Ltd.
#
# This example shows how to run KiteTicker in threaded mode.
# KiteTicker runs in seprate thread and main thread is blocked to juggle between
# different modes for current subscribed tokens. In real world web apps
# the main thread will be your web server and you can access WebSocket object
# in your main thread while running KiteTicker in separate thread.
###############################################################################

import time
import logging
from kiteconnect import KiteTicker
import os
import http.server
import socketserver
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler, test
import sys
import json
import threading
import requests
from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



# Initialise.
kws = KiteTicker("26ud7j6qh471oabu", "C1qsdnQDDKXqL8GGMGE22ZZ21p9Qd7Kx")

# ********GMAIL API CONFIGURATION*************
CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
# ********GMAIL API CONFIGURATION*************

# RELIANCE BSE
tokens = [  4451329 ]

# authorization_string 
authorization_string = 'token 26ud7j6qh471oabu:C1qsdnQDDKXqL8GGMGE22ZZ21p9Qd7Kx'


alerts = [
   
    {
        "instrument_token": 4451329,
        "instrument_name": "ADANIPOWER",
        "volume_alert": {
            "value": 3500000,
            "triggered": 0
        },
        "type": "UPPER",
        "quantity_alert": {
            "value": 1000000,
            "triggered": 0
        },
        "exchange": "BSE",
        "quantity": 2791,
        "place_order": 1,
        "price": 109.8
    }
]

def expo_notification(trigger_type, instrument_name):
  url = "https://exp.host/--/api/v2/push/send"
  body_tejas = [
              {"to": "ExponentPushToken[hkyQJJPFZX_R3VBUrcvJlD]","title":f'{instrument_name} {trigger_type} Triggered',"body":f'{instrument_name} {trigger_type} Triggered',"sound": "default"}
              ]
  body_saksham = [
                {"to": "ExponentPushToken[4qqOxCPVOBVFAt8z9I0-Pz]","title":f'{instrument_name} {trigger_type} Triggered',"body":f'{instrument_name} {trigger_type} Triggered',"sound": "default"}
              ]
  headers = {'content-type': 'application/json'}
  requests.post(url,data=json.dumps(body_tejas),headers=headers)
  requests.post(url,data=json.dumps(body_saksham),headers=headers)

def send_email(trigger_type, instrument_name):
  emailMsg = f'{instrument_name} {trigger_type} Triggered'

  mimeMessage = MIMEMultipart()
  mimeMessage['to'] = 'f20190562@pilani.bits-pilani.ac.in, agarwalsaksham32@gmail.com'
#   mimeMessage['to'] = 'f20190562@pilani.bits-pilani.ac.in'
  mimeMessage['subject'] = f'{instrument_name} {trigger_type} Triggered'
  mimeMessage.attach(MIMEText(emailMsg, 'plain'))
  raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
  message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()

def check_alerts(ticks): 
    # print(ticks)

    for tick in ticks:

    
        for item in alerts: 
        
            if tick['instrument_token'] == item['instrument_token']:
                #check alerts
               
                if tick['volume'] >= int(item['volume_alert']['value']) and (not item['volume_alert']['triggered']):
                    item['volume_alert']['triggered'] = True
                    
                    expo_notification('Volume',item['instrument_name'])
                    send_email('Volume',item['instrument_name'])
                

               
                qty = 0
                order_type = 'SELL'

                if item['type'] == 'LOWER':
                    qty = tick['depth']['sell'][0]['quantity']
                    order_type = 'BUY'
                else:
                    qty = tick['depth']['buy'][0]['quantity']  
                    order_type = 'SELL' 

                if qty <= int(item['quantity_alert']['value']) and ( not item['quantity_alert']['triggered']):
                  item['quantity_alert']['triggered'] = True

                  if item['place_order']:
                
                    

                    order = {
                        'tradingsymbol':item['instrument_name'],
                        'exchange':item['exchange'],
                        'transaction_type':order_type,
                        'order_type':'LIMIT',
                        'quantity':item['quantity'],
                        'product':'CNC',
                        'validity':'DAY',
                        'price':item['price']
                        
                    }

                    print(order)

                    url = f'https://api.kite.trade/orders/regular'
                    resp = requests.post(url, data = order,headers={'X-Kite-Version': '3','Authorization':authorization_string})
                    parsed_response = json.loads(resp.content.decode("UTF-8"))
                    print(parsed_response)



                  print(alerts)
                  expo_notification('Qty Alert',item['instrument_name'])
                  send_email('Qty Alert',item['instrument_name'])
                  print(f'send quantity alert') 


# Callback for tick reception.
def on_ticks(ws, ticks):
    # print(ticks)
   
    if len(ticks) > 0:
        t = threading.Thread(name='t',target=check_alerts,args=(ticks,))
        t.start()
        


# Callback for successful connection.
def on_connect(ws, response):
    print("Successfully connected. Response: {}".format(response))
    ws.subscribe(tokens)
    print(tokens)
    ws.set_mode(ws.MODE_FULL, tokens)
    print("Subscribe to tokens in Full mode: {}".format(tokens))


# Callback when current connection is closed.
def on_close(ws, code, reason):
    print("Connection closed: {code} - {reason}".format(code=code, reason=reason))
    ws.stop()



# Callback when connection closed with error.
def on_error(ws, code, reason):
    # print("Connection error: {code} - {reason}".format(code=code, reason=reason))
    return


# Callback when reconnect is on progress
def on_reconnect(ws, attempts_count):
    print("Reconnecting: {}".format(attempts_count))


# Callback when all reconnect failed (exhausted max retries)
def on_noreconnect(ws):
    print("Reconnect failed.")


# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_close = on_close
kws.on_error = on_error
kws.on_connect = on_connect
kws.on_reconnect = on_reconnect
kws.on_noreconnect = on_noreconnect

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect(threaded=True)

# Block main thread
print("This is main thread. Will change webosocket mode every 5 seconds.")


class CORSRequestHandler (SimpleHTTPRequestHandler):
    def do_OPTIONS(self):           
        self.send_response(200, "ok")       
        self.send_header('Access-Control-Allow-Origin', '*')                
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "*")        
        self.end_headers()

    def end_headers (req):
        req.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(req)

    def do_GET(req):
        global alerts
        req.send_response(HTTPStatus.OK)


        req.send_header("Content-Type","application/json; charset=utf-8")
        req.end_headers()
        req.wfile.write((json.dumps(alerts)).encode())

    def do_POST(req):
        global tokens
        global alerts

        req.send_response(HTTPStatus.OK)
        req.end_headers()
        content_length = int(req.headers['Content-Length']) # <--- Gets the size of data
        post_data = req.rfile.read(content_length) # <--- Gets the data itreq
        print(post_data)
        alerts = json.loads(post_data.decode('utf-8'))
        tokens = [int(alert['instrument_token']) for alert in alerts]
        print(tokens)

        if kws.is_connected():
           kws.set_mode(kws.MODE_FULL, tokens)

if __name__ == '__main__':
    test(CORSRequestHandler, HTTPServer, port=int(sys.argv[1]) if len(sys.argv) > 1 else 9000)
   





