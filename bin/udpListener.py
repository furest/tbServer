import socketserver

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 1501

class nullUDPHandler(socketserver.DatagramRequestHandler):
    
    # Override the handle() method
    def handle(self):
        print(self.client_address)
        self.wfile.write("".encode())
if __name__ == "__main__":
    server = socketserver.ThreadingUDPServer((LISTEN_IP, LISTEN_PORT), nullUDPHandler)
    server.serve_forever()

