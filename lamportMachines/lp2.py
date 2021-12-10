from concurrent import futures
import threading
import grpc
import sys
import random
import time

from lamport_pb2 import(
    LamportMessage,
    LamportOK,
)
import lamport_pb2_grpc

my_neighbors = {}
my_id = 0
time_lock = threading.Lock()
process_time = 0
log_lock = threading.Lock()
log = []

def update_time(new = -1):
    time_lock.acquire()
    global process_time
    process_time = max(process_time, new) + 1
    ret_time = process_time
    time_lock.release()
    return ret_time

def log_write(message):
    global my_id
    global log
    global log_lock
    print("esperando")
    log_lock.acquire(1)
    log.append(message)
    my_file = open("log"+str(my_id)+".txt", "a")
    my_file.write(message+"\n")
    my_file.close()
    log_lock.release()

def receive_log(id, time):
    print("aqui?")
    message = "Received message from id:"+str(id)+" at time:"+str(time)
    log_write(message)

def send_log(id, time):
    message = "Sent message to id:"+str(id)+" at time:"+str(time)
    #print(message)
    log_write(message)

def LampAnother(last = -1):
    global my_neighbors

    time.sleep(1)
    reqTime = update_time()
    lampRequest = LamportMessage(user_id = my_id, time = reqTime)

    possible_targets = [i for i in my_neighbors.keys()]
    print(possible_targets)
    if my_id in possible_targets:
        possible_targets.remove(my_id)
    if len(possible_targets) > 1 and last in possible_targets:
        possible_targets.remove(last)

    target_id = random.choice(possible_targets)
    send_log(target_id, reqTime)

    target_client = my_neighbors[target_id]
    response = target_client.LampSend(lampRequest)

class Lamport(lamport_pb2_grpc.LamportSendServicer):
    def LampSend(self, request, context):

        reqTime = update_time(request.time)

        receive_log(request.user_id, reqTime)

        callThread = threading.Thread(target = LampAnother, args = (request.user_id,))
        callThread.start()

        return LamportOK(ok=True)


def serve():
    global my_id
    global my_neighbors

    my_neighbors = {}

    my_id = int(sys.argv[1])

    neigh_ports = sys.argv[2:]

    for i in range(len(neigh_ports)):
        channel = grpc.insecure_channel("localhost:"+neigh_ports[i])
        client = lamport_pb2_grpc.LamportSendStub(channel)
        my_neighbors[i] = client

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    lamport_pb2_grpc.add_LamportSendServicer_to_server(
        Lamport(), server
    )

    my_file = open("log"+str(my_id)+".txt", "w")
    my_file.write("process "+str(my_id)+" log start\n")
    my_file.close()

    server.add_insecure_port("[::]:"+neigh_ports[my_id])
    print("[::]:"+neigh_ports[my_id])
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
