import socket
import threading

class BattleshipServer:
    def __init__(self, host='localhost', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)  #max is 2 players like normal battlehisp or player vs computer
        print("Server started on", host, ":", port)
        self.clients = []
        self.lock = threading.Lock()

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print("Received:", message)
                self.broadcast(message, client_socket)
            except ConnectionResetError:
                break
        with self.lock:
            self.clients.remove(client_socket)
        client_socket.close()

    def broadcast(self, message, sender_socket):
        with self.lock:
            for client in self.clients:
                if client != sender_socket:
                    client.send(message.encode('utf-8'))

    def start(self):
        while True:
            client_socket, addr = self.server.accept()
            print(f"Connection from {addr}")
            with self.lock:
                self.clients.append(client_socket)
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.start()

if __name__ == "__main__":
    server = BattleshipServer()
    server.start()
