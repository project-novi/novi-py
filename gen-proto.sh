#!/bin/bash
python -m grpc_tools.protoc --python_out src --pyi_out src --grpc_python_out src novi.proto -I novi=.
