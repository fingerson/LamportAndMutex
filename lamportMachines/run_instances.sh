#! /bin/bash
ports="50051 50052 50053 50054 50055 50056"
python3 -m pip install -r requirements.txt
python3 -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/lamport.proto

python3 lamport.py 1 $ports &
python3 lamport.py 2 $ports &
python3 lamport.py 3 $ports &
python3 lamport.py 4 $ports &
python3 lamport.py 5 $ports &
python3 lamport.py 0 $ports &
