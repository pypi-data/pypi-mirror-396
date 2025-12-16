import pickle
import zmq


class PickleClient:
    """Minimal ZeroMQ pickle-based RPC client."""

    def __init__(self, hostname: str, port: int):
        self.hostname = hostname
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{self.hostname}:{self.port}")

    def send_data(self, data):
        self.socket.send(pickle.dumps(data))
        response = pickle.loads(self.socket.recv())
        return response

    def close(self):
        self.socket.close()
        self.context.term()
