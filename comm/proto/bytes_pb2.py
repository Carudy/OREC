# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: bytes.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0b\x62ytes.proto\"\x12\n\x03Msg\x12\x0b\n\x03msg\x18\x01 \x01(\x0c\"\x12\n\x03Res\x12\x0b\n\x03res\x18\x01 \x01(\x0c\x32\x1d\n\x05\x42ytes\x12\x14\n\x04send\x12\x04.Msg\x1a\x04.Res\"\x00\x62\x06proto3')



_MSG = DESCRIPTOR.message_types_by_name['Msg']
_RES = DESCRIPTOR.message_types_by_name['Res']
Msg = _reflection.GeneratedProtocolMessageType('Msg', (_message.Message,), {
  'DESCRIPTOR' : _MSG,
  '__module__' : 'bytes_pb2'
  # @@protoc_insertion_point(class_scope:Msg)
  })
_sym_db.RegisterMessage(Msg)

Res = _reflection.GeneratedProtocolMessageType('Res', (_message.Message,), {
  'DESCRIPTOR' : _RES,
  '__module__' : 'bytes_pb2'
  # @@protoc_insertion_point(class_scope:Res)
  })
_sym_db.RegisterMessage(Res)

_BYTES = DESCRIPTOR.services_by_name['Bytes']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _MSG._serialized_start=15
  _MSG._serialized_end=33
  _RES._serialized_start=35
  _RES._serialized_end=53
  _BYTES._serialized_start=55
  _BYTES._serialized_end=84
# @@protoc_insertion_point(module_scope)