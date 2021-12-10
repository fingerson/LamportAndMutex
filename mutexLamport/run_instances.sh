#! /bin/bash
ports=" 50051 50052 50053 50054 50055"
python3 -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/mutex.proto
rm resource.txt
echo "" > resource.txt
python3 mutex2.py 0 $ports &
python3 mutex2.py 1 $ports &
python3 mutex2.py 2 $ports &
python3 mutex2.py 3 $ports &
python3 mutex2.py 4 $ports &
