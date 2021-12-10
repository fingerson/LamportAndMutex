# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: lamport.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='lamport.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\rlamport.proto\"/\n\x0eLamportMessage\x12\x0f\n\x07user_id\x18\x01 \x01(\x04\x12\x0c\n\x04time\x18\x02 \x01(\x04\"\x17\n\tLamportOK\x12\n\n\x02ok\x18\x01 \x01(\x08\x32\x36\n\x0bLamportSend\x12\'\n\x08LampSend\x12\x0f.LamportMessage\x1a\n.LamportOKb\x06proto3'
)




_LAMPORTMESSAGE = _descriptor.Descriptor(
  name='LamportMessage',
  full_name='LamportMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='user_id', full_name='LamportMessage.user_id', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='time', full_name='LamportMessage.time', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=17,
  serialized_end=64,
)


_LAMPORTOK = _descriptor.Descriptor(
  name='LamportOK',
  full_name='LamportOK',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='ok', full_name='LamportOK.ok', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=66,
  serialized_end=89,
)

DESCRIPTOR.message_types_by_name['LamportMessage'] = _LAMPORTMESSAGE
DESCRIPTOR.message_types_by_name['LamportOK'] = _LAMPORTOK
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LamportMessage = _reflection.GeneratedProtocolMessageType('LamportMessage', (_message.Message,), {
  'DESCRIPTOR' : _LAMPORTMESSAGE,
  '__module__' : 'lamport_pb2'
  # @@protoc_insertion_point(class_scope:LamportMessage)
  })
_sym_db.RegisterMessage(LamportMessage)

LamportOK = _reflection.GeneratedProtocolMessageType('LamportOK', (_message.Message,), {
  'DESCRIPTOR' : _LAMPORTOK,
  '__module__' : 'lamport_pb2'
  # @@protoc_insertion_point(class_scope:LamportOK)
  })
_sym_db.RegisterMessage(LamportOK)



_LAMPORTSEND = _descriptor.ServiceDescriptor(
  name='LamportSend',
  full_name='LamportSend',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=91,
  serialized_end=145,
  methods=[
  _descriptor.MethodDescriptor(
    name='LampSend',
    full_name='LamportSend.LampSend',
    index=0,
    containing_service=None,
    input_type=_LAMPORTMESSAGE,
    output_type=_LAMPORTOK,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_LAMPORTSEND)

DESCRIPTOR.services_by_name['LamportSend'] = _LAMPORTSEND

# @@protoc_insertion_point(module_scope)
