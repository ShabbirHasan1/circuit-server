# #!/usr/bin/env python3 server.py
# from http.server import HTTPServer, SimpleHTTPRequestHandler, test
# import sys
# from http import HTTPStatus
# import json

# class CORSRequestHandler (SimpleHTTPRequestHandler):
#     def end_headers (self):
#         self.send_header('Access-Control-Allow-Origin', '*')
#         SimpleHTTPRequestHandler.end_headers(self)

#     def do_GET(req):
       
#         req.send_response(HTTPStatus.OK)
       

#         req.send_header("Content-Type","application/json; charset=utf-8")
#         req.end_headers()
#         req.wfile.write((json.dumps('alerts')).encode())


# if __name__ == '__main__':
#     test(CORSRequestHandler, HTTPServer, port=int(sys.argv[1]) if len(sys.argv) > 1 else 8000)
#     # test_orig(*args, port=int(sys.argv[1]) if len(sys.argv) > 1 else 80), bind="0.0.0.0"

# try:
#     # try to use Python 3
#     from http.server import HTTPServer, SimpleHTTPRequestHandler, test as test_orig
#     import sys
#     def test (*args):
#         test_orig(*args, port=int(sys.argv[1]) if len(sys.argv) > 1 else 80)
# except ImportError: # fall back to Python 2
#     from BaseHTTPServer import HTTPServer, test
#     from SimpleHTTPServer import SimpleHTTPRequestHandler

# class CORSRequestHandler (SimpleHTTPRequestHandler):
#     def end_headers (self):
#         self.send_header('Access-Control-Allow-Origin', '*')
#         SimpleHTTPRequestHandler.end_headers(self)

# if __name__ == '__main__':
#     test(CORSRequestHandler, HTTPServer)

#!/usr/bin/env python3
# encoding: utf-8
# """Use instead of `python3 -m http.server` when you need CORS"""

# from http.server import HTTPServer, SimpleHTTPRequestHandler


# class CORSRequestHandler(SimpleHTTPRequestHandler):
#     def end_headers(self):
#         self.send_header('Access-Control-Allow-Origin', '*')
#         self.send_header('Access-Control-Allow-Methods', 'GET')
#         self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
#         return super(CORSRequestHandler, self).end_headers()


# httpd = HTTPServer(('localhost', 8000), CORSRequestHandler)
# httpd.serve_forever()