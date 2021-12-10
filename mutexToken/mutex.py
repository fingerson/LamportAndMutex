from concurrent import futures
import threading
import grpc
import sys
import time
import random

from mutex_pb2 import(
    MutexMessage,
    Void,
)
import mutex_pb2_grpc

def process(mutexObj, startingID):
    time.sleep(1)
    id = mutexObj.id
    if id == startingID:
        mutexObj.forwardToken()
    while True:
        time.sleep(random.randrange(5,10))
        mutexObj.interested = True
        mutexObj.token.acquire()
        print("ID:"+str(id)+" started using critical area")
        time.sleep(1)
        print("ID:"+str(id)+" stopped using critical area")
        mutexObj.interested = False
        mutexObj.forwardToken()

class LockedValue:
    def __init__(self, initial):
        self.lock = threading.Lock()
        self.value = initial

class Mutex(mutex_pb2_grpc.MutexSendServicer):
    def __init__(self, id, neighbors, next_id):
        super().__init__()
        self.next_id = next_id
        self.id = id
        self.interested = False
        self.neighbors = neighbors
        self.token = threading.Lock()
        self.token.acquire()

    def forwardToken(self):
        next = self.neighbors[self.next_id]
        message = MutexMessage(id = self.id)
        next.SendToken(message)

    def SendToken(self, request, context):
        if self.interested:
            self.token.release()
        else:
            thr = threading.Thread(target=self.forwardToken)
            thr.start()
        return Void()

def serve():
    my_id = int(sys.argv[1])
    neigh_ports = sys.argv[2:]

    my_neighbors = {}
    for i in range(len(neigh_ports)):
        channel = grpc.insecure_channel("localhost:"+neigh_ports[i])
        client = mutex_pb2_grpc.MutexSendStub(channel)
        my_neighbors[i] = client

    next_id = my_id+1
    if next_id == len(neigh_ports):
        next_id = 0

    my_mutex = Mutex(my_id, my_neighbors, next_id)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mutex_pb2_grpc.add_MutexSendServicer_to_server(
        my_mutex, server
    )

    thr = threading.Thread(target = process, args = (my_mutex,0,))
    thr.start()

    server.add_insecure_port("[::]:"+neigh_ports[my_id])
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
