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

my_neighbors = {}
my_id = 0
process_time = LockedValue(0)
log = LockedValue([])
want = LockedValue(False)
my_queue = LockedValue([])
pending_permissions = LockedValue([])
#currently_using_resource = LockedValue(False)

def wantStatus():
    global want
    want.lock.acquire()
    res = want.value
    want.lock.release()
    return res

def setWant(newVal):
    global want
    want.lock.acquire()
    want.value = newVal
    want.lock.release()


def update_time(new = -1):
    global time
    process_time.lock.acquire()
    old_time = process_time.value
    process_time.value = max(old_time, new) + 1
    ret_time = process_time.value
    process_time.lock.release()
    return ret_time, old_time

def log_write(message):
    global my_id
    global log
    global log_lock
    log.lock.acquire()
    log.value.append(message)
    my_file = open("log"+str(my_id)+".txt", "a")
    my_file.write(message+"\n")
    my_file.close()
    log.lock.release()

def received_permission(id, ltime):
    message = "Permitted by id:"+str(id)+" at time:"+str(ltime)
    log_write(message)

def asked_permission(id, ltime):
    message = "Asked id:"+str(id)+" for permission at time:"+str(ltime)
    log_write(message)

def received_request(id, ltime):
    message = "Received permission request from id:"+str(id)+" at time:"+str(ltime)
    log_write(message)

def granted_permission(id, ltime):
    message = "Granted id:"+str(id)+" at time:"+str(ltime)+" my permission"
    log_write(message)

def using_resource(ltime):
    message = "Using resource at time:"+str(ltime)
    log_write(message)

def finished_resource(ltime):
    message = "Finished using resource at time:"+str(ltime)
    log_write(message)

def grant_permission_to_id(id):
    global my_id
    global my_neighbors
    neigh = my_neighbors[id]
    print(str(my_id)+" b3")
    reqTime,_ = update_time()
    request = MutexMessage(id = my_id, time=reqTime)
    neigh.GrantPermission(request)
    granted_permission(id, reqTime)

def add_to_queue(id):
    my_queue.lock.acquire()
    my_queue.value.append(id)
    my_queue.lock.release()

def received_permission_from_id(id, time):
    print(str(my_id)+" b6")
    pending_permissions.lock.acquire()
    if id in pending_permissions.value:
        pending_permissions.value.remove(id)
        received_permission(id, time)
    else:
        print("permission not asked for")
        pending_permissions.lock.release()
        return False
    print(str(my_id)+" b7")
    res = False
    if len(pending_permissions.value) == 0:
        res = True
    pending_permissions.lock.release()

    if res:
        start_use_resource()

def start_use_resource():
    #currently_using_resource.lock().acquire()
    #if currently_using_resource.value:
    #    currently_using_resource.lock().release()
    #    return
    #currently_using_resource.value = True
    #currently_using_resource.lock().release()
    reqTime,_ = update_time()
    using_resource(reqTime)
    resource = open("resource.txt","a")
    resource.write("Being used by:"+str(my_id)+" at time+"+str(reqTime)+"\n")
    resource.close()
    time.sleep(3)
    reqTime,_ = update_time()
    resource = open("resource.txt","a")
    resource.write("Finished use by:"+str(my_id)+" at time+"+str(reqTime)+"\n")
    resource.close()

    #urrently_using_resource.lock().acquire()
    #currently_using_resource.value = False
    #currently_using_resource.lock().release()

    finished_using()

def finished_using():
    reqTime,_ = update_time()
    setWant(False)
    finished_resource(reqTime)
    global my_queue
    my_queue.lock.acquire()
    q = my_queue.value
    my_queue.value = []
    my_queue.lock.release()

    for id in q:
        grant_permission_to_id(id)

    thr = threading.Thread(target = waiter)
    thr.start()

def waiter():
    wait_time = 1#random.randrange(3,10)
    time.sleep(wait_time)
    if wantStatus():
        return
    setWant(True)
    global my_neighbors
    global my_id



    global pending_permissions
    pending_permissions.lock.acquire()
    for id in my_neighbors.keys():
        pending_permissions.value.append(id)
    pending_permissions.lock.release()
    for id in my_neighbors.keys():
        reqTime,_ = update_time()
        request = MutexMessage(id = my_id, time=reqTime)
        asked_permission(id, reqTime)
        my_neighbors[id].AskForPermission(request)


def check_priority(id1, id2, t1, t2):
    if t1 > t2:
        return True
    elif t1 == t2 and id2 < id1:
        return True
    return False

class Mutex(mutex_pb2_grpc.MutexSendServicer):
    def AskForPermission(self, request, context):
        global my_id
        reqTime,old_time = update_time(request.time)
        received_request(request.id, reqTime)
        if request.id == my_id or wantStatus() == False or check_priority(my_id,request.id,old_time,request.time):
            thr = threading.Thread(target = grant_permission_to_id, args = (request.id,))
            thr.start()
        else:
            thr = threading.Thread(target = add_to_queue, args = (request.id,))
            thr.start()
        return Void()

    def GrantPermission(self, request, context):
        reqTime,_ = update_time(request.time)

        thr = threading.Thread(target = received_permission_from_id, args = (request.id, reqTime,))
        thr.start()


        return Void()
    def Ping(self, request, context):
        return Void()


def serve():
    global my_id
    global my_neighbors

    my_neighbors = {}

    my_id = int(sys.argv[1])

    neigh_ports = sys.argv[2:]
    print(my_id)
    print(neigh_ports)
    for i in range(len(neigh_ports)):
        channel = grpc.insecure_channel("localhost:"+neigh_ports[i])
        client = mutex_pb2_grpc.MutexSendStub(channel)
        my_neighbors[i] = client

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mutex_pb2_grpc.add_MutexSendServicer_to_server(
        Mutex(), server
    )

    my_file = open("log"+str(my_id)+".txt", "w")
    my_file.write("process "+str(my_id)+" log start\n")
    my_file.close()

    thr = threading.Thread(target = waiter)
    thr.start()

    server.add_insecure_port("[::]:"+neigh_ports[my_id])
    print("[::]:"+neigh_ports[my_id])
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
