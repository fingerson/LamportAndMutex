import grpc
import lamport_pb2
import lamport_pb2_grpc
request=lamport_pb2.LamportMessage(user_id=1,time=2)
channel = grpc.insecure_channel("localhost:50051")
client = lamport_pb2_grpc.LamportSendStub(channel)
print(client.LampSend(request))
