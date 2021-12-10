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

class LockedValue:
    def __init__(self, initial):
        self.lock = threading.Lock()
        self.value = initial

class Mutex(mutex_pb2_grpc.MutexSendServicer):
    def __init__(self, id, neighbors, nextId, startingID):
        super().__init__()
        self.startingID = startingID
        self.nextId = nextId
        self.id = id
        self.time = LockedValue(id)
        self.interested = True
        self.neighbors = neighbors
        self.token = threading.Lock()
        self.finished = threading.Lock()
        self.token.acquire()


    def update_time(self, new = -1):
        self.time.lock.acquire()
        self.time.value = max(self.time.value, new) + 1
        ret_time = self.time.value
        self.time.lock.release()
        return ret_time

    def forwardToken(self):
        next = self.neighbors[self.nextId]
        reqTime = self.update_time()
        message = MutexMessage(id = self.id, time = reqTime)
        next.SendToken(message)
        pass
    def interestLoop(self):
        if self.id == self.startingID:
            time.sleep(1)
            self.forwardToken()
        while True:
            time.sleep(random.randrange(5,10))
            self.interested = True
            self.token.acquire()
            self.update_time()
            print("ID:"+str(self.id)+" started using critical area")
            time.sleep(1)
            print("ID:"+str(self.id)+" stopped using critical area")
            self.interested = False
            self.forwardToken()

    def SendToken(self, request, context):
        self.update_time(request.time)
        if self.interested:
            self.token.release()
        else:
            thr = threading.Thread(target=self.forwardToken)
            thr.start()
        return Void()

def waitStart(mutex):
    time.sleep(1)
    mutex.forwardToken()

def serve():
    my_neighbors = {}

    my_id = int(sys.argv[1])

    neigh_ports = sys.argv[2:]
    print(my_id)
    print(neigh_ports)
    for i in range(len(neigh_ports)):
        channel = grpc.insecure_channel("localhost:"+neigh_ports[i])
        client = mutex_pb2_grpc.MutexSendStub(channel)
        my_neighbors[i] = client

    nextId = my_id+1
    if nextId == len(neigh_ports):
        nextId = 0

    my_mutex = Mutex(my_id, my_neighbors, nextId, 0)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mutex_pb2_grpc.add_MutexSendServicer_to_server(
        my_mutex, server
    )

    thr = threading.Thread(target = my_mutex.interestLoop)
    thr.start()

    server.add_insecure_port("[::]:"+neigh_ports[my_id])
    print("[::]:"+neigh_ports[my_id])
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
