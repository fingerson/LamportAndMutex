from concurrent import futures
import threading
import grpc
import sys
import time
import random

from mutex_pb2 import(
    MutexMessage,
)
import mutex_pb2_grpc

class LockedValue:
    def __init__(self, initial):
        self.lock = threading.Lock()
        self.value = initial

def cond(id1, id2, t1, t2):
    if t1 > t2:
        return True
    if t1 == t2 and id2 < id1:
        return True
    return False
class Mutex(mutex_pb2_grpc.MutexSendServicer):
    def __init__(self, id, neighbors):
        super().__init__()
        self.id = id
        self.time = LockedValue(id)
        self.interested = LockedValue(False)
        self.neighbors = neighbors

    def set_interested(self, value):
        self.interested.lock.acquire()
        self.interested.value = value
        self.interested.lock.release()

    def is_interested(self):
        self.interested.lock.acquire()
        value = self.interested.value
        self.interested.lock.release()
        return value

    def update_time(self, new = -1):
        self.time.lock.acquire()
        old_time = self.time.value
        self.time.value = max(old_time, new) + 1
        ret_time = self.time.value
        self.time.lock.release()
        return ret_time, old_time

    def requestAccess(self, id):
        reqTime,_ = self.update_time()
        message = MutexMessage(id = self.id, time=reqTime)
        response = self.neighbors[id].AskForPermission(message)
        self.update_time(response.time)

    def interestLoop(self):
        while True:
            time.sleep(1)#random.randrange(3,10))
            self.set_interested(True)
            open_threads = []
            for i in self.neighbors.keys():
                thr = threading.Thread(target = self.requestAccess, args=(i,))
                open_threads.append(thr)
                thr.start()
            for thread in open_threads:
                thread.join()
            self.update_time()
            print("ID:"+str(self.id)+" started using critical area")
            time.sleep(1)
            print("ID:"+str(self.id)+" stopped using critical area")
            self.set_interested(False)

    def AskForPermission(self, request, context):
        reqTime,old_time = self.update_time(request.time)
        if request.id == self.id or (not self.is_interested()) or cond(self.id, request.id, old_time, request.time):
            reqTime,_ = self.update_time()
            return MutexMessage(id = self.id, time=reqTime)
        else:
            while self.is_interested():
                pass
            reqTime,_ = self.update_time()
            return MutexMessage(id = self.id, time=reqTime)

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

    my_mutex = Mutex(my_id, my_neighbors)

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
