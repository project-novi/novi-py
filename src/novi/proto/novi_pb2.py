# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: novi/proto/novi.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15novi/proto/novi.proto\x12\x04novi\"\x84\x01\n\x05\x45rror\x12\x0c\n\x04kind\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12+\n\x08metadata\x18\x03 \x03(\x0b\x32\x19.novi.Error.MetadataEntry\x1a/\n\rMetadataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x1e\n\x04UUID\x12\n\n\x02hi\x18\x01 \x01(\x06\x12\n\n\x02lo\x18\x02 \x01(\x06\"9\n\x08TagValue\x12\x12\n\x05value\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x0f\n\x07updated\x18\x02 \x01(\x03\x42\x08\n\x06_value\"w\n\x04Tags\x12.\n\nproperties\x18\x01 \x03(\x0b\x32\x1a.novi.Tags.PropertiesEntry\x12\x0c\n\x04tags\x18\x02 \x03(\t\x1a\x31\n\x0fPropertiesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\xd3\x01\n\x06Object\x12\x16\n\x02id\x18\x01 \x01(\x0b\x32\n.novi.UUID\x12$\n\x04tags\x18\x02 \x03(\x0b\x32\x16.novi.Object.TagsEntry\x12 \n\x07\x63reator\x18\x03 \x01(\x0b\x32\n.novi.UUIDH\x00\x88\x01\x01\x12\x0f\n\x07updated\x18\x04 \x01(\x03\x12\x0f\n\x07\x63reated\x18\x05 \x01(\x03\x1a;\n\tTagsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1d\n\x05value\x18\x02 \x01(\x0b\x32\x0e.novi.TagValue:\x02\x38\x01\x42\n\n\x08_creator\"\x18\n\x06Scopes\x12\x0e\n\x06scopes\x18\x01 \x03(\t\"2\n\x0cLoginRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"\x1e\n\nLoginReply\x12\x10\n\x08identity\x18\x01 \x01(\t\"=\n\x0eLoginAsRequest\x12\x18\n\x04user\x18\x01 \x01(\x0b\x32\n.novi.UUID\x12\x11\n\ttemporary\x18\x02 \x01(\x08\" \n\x0cLoginAsReply\x12\x10\n\x08identity\x18\x01 \x01(\t\"\"\n\x13UseMasterKeyRequest\x12\x0b\n\x03key\x18\x01 \x01(\t\"%\n\x11UseMasterKeyReply\x12\x10\n\x08identity\x18\x01 \x01(\t\"/\n\x11NewSessionRequest\x12\x11\n\x04lock\x18\x01 \x01(\x08H\x00\x88\x01\x01\x42\x07\n\x05_lock\" \n\x0fNewSessionReply\x12\r\n\x05token\x18\x01 \x01(\t\"#\n\x11\x45ndSessionRequest\x12\x0e\n\x06\x63ommit\x18\x01 \x01(\x08\"\x11\n\x0f\x45ndSessionReply\"/\n\x13\x43reateObjectRequest\x12\x18\n\x04tags\x18\x01 \x01(\x0b\x32\n.novi.Tags\"1\n\x11\x43reateObjectReply\x12\x1c\n\x06object\x18\x01 \x01(\x0b\x32\x0c.novi.Object\"*\n\x10GetObjectRequest\x12\x16\n\x02id\x18\x01 \x01(\x0b\x32\n.novi.UUID\".\n\x0eGetObjectReply\x12\x1c\n\x06object\x18\x01 \x01(\x0b\x32\x0c.novi.Object\"V\n\x13UpdateObjectRequest\x12\x16\n\x02id\x18\x01 \x01(\x0b\x32\n.novi.UUID\x12\x18\n\x04tags\x18\x02 \x01(\x0b\x32\n.novi.Tags\x12\r\n\x05\x66orce\x18\x03 \x01(\x08\"1\n\x11UpdateObjectReply\x12\x1c\n\x06object\x18\x01 \x01(\x0b\x32\x0c.novi.Object\"\x85\x01\n\x14ReplaceObjectRequest\x12\x16\n\x02id\x18\x01 \x01(\x0b\x32\n.novi.UUID\x12\x18\n\x04tags\x18\x02 \x01(\x0b\x32\n.novi.Tags\x12!\n\x06scopes\x18\x03 \x01(\x0b\x32\x0c.novi.ScopesH\x00\x88\x01\x01\x12\r\n\x05\x66orce\x18\x04 \x01(\x08\x42\t\n\x07_scopes\"2\n\x12ReplaceObjectReply\x12\x1c\n\x06object\x18\x01 \x01(\x0b\x32\x0c.novi.Object\"?\n\x17\x44\x65leteObjectTagsRequest\x12\x16\n\x02id\x18\x01 \x01(\x0b\x32\n.novi.UUID\x12\x0c\n\x04tags\x18\x02 \x03(\t\"5\n\x15\x44\x65leteObjectTagsReply\x12\x1c\n\x06object\x18\x01 \x01(\x0b\x32\x0c.novi.Object\"-\n\x13\x44\x65leteObjectRequest\x12\x16\n\x02id\x18\x01 \x01(\x0b\x32\n.novi.UUID\"\x13\n\x11\x44\x65leteObjectReply\"\x98\x03\n\x0cQueryRequest\x12\x0e\n\x06\x66ilter\x18\x01 \x01(\t\x12\x17\n\ncheckpoint\x18\x02 \x01(\x03H\x00\x88\x01\x01\x12\x1a\n\rupdated_after\x18\x03 \x01(\x03H\x01\x88\x01\x01\x12\x1b\n\x0eupdated_before\x18\x04 \x01(\x03H\x02\x88\x01\x01\x12\x1a\n\rcreated_after\x18\x05 \x01(\x03H\x03\x88\x01\x01\x12\x1b\n\x0e\x63reated_before\x18\x06 \x01(\x03H\x04\x88\x01\x01\x12\'\n\x05order\x18\x07 \x01(\x0e\x32\x18.novi.QueryRequest.Order\x12\x12\n\x05limit\x18\x08 \x01(\rH\x05\x88\x01\x01\"M\n\x05Order\x12\x10\n\x0c\x43REATED_DESC\x10\x00\x12\x0f\n\x0b\x43REATED_ASC\x10\x01\x12\x10\n\x0cUPDATED_DESC\x10\x02\x12\x0f\n\x0bUPDATED_ASC\x10\x03\x42\r\n\x0b_checkpointB\x10\n\x0e_updated_afterB\x11\n\x0f_updated_beforeB\x10\n\x0e_created_afterB\x11\n\x0f_created_beforeB\x08\n\x06_limit\"+\n\nQueryReply\x12\x1d\n\x07objects\x18\x01 \x03(\x0b\x32\x0c.novi.Object\"q\n\x10SubscribeRequest\x12\x0e\n\x06\x66ilter\x18\x01 \x01(\t\x12\x17\n\ncheckpoint\x18\x02 \x01(\x03H\x00\x88\x01\x01\x12%\n\x0c\x61\x63\x63\x65pt_kinds\x18\x03 \x03(\x0e\x32\x0f.novi.EventKindB\r\n\x0b_checkpoint\"M\n\x0eSubscribeReply\x12\x1c\n\x06object\x18\x01 \x01(\x0b\x32\x0c.novi.Object\x12\x1d\n\x04kind\x18\x02 \x01(\x0e\x32\x0f.novi.EventKind\"I\n\x0bObjectEdits\x12\x0f\n\x07\x64\x65letes\x18\x01 \x03(\t\x12\x1a\n\x06update\x18\x02 \x01(\x0b\x32\n.novi.Tags\x12\r\n\x05\x63lear\x18\x03 \x01(\x08\"\xd8\x03\n\x12RegCoreHookRequest\x12\x35\n\x08initiate\x18\x01 \x01(\x0b\x32!.novi.RegCoreHookRequest.InitiateH\x00\x12\x35\n\x06result\x18\x02 \x01(\x0b\x32#.novi.RegCoreHookRequest.CallResultH\x00\x1aM\n\x08Initiate\x12\x31\n\x05point\x18\x01 \x01(\x0e\x32\".novi.RegCoreHookRequest.HookPoint\x12\x0e\n\x06\x66ilter\x18\x02 \x01(\t\x1al\n\nCallResult\x12\x0f\n\x07\x63\x61ll_id\x18\x01 \x01(\x04\x12%\n\x08response\x18\x02 \x01(\x0b\x32\x11.novi.ObjectEditsH\x00\x12\x1c\n\x05\x65rror\x18\x03 \x01(\x0b\x32\x0b.novi.ErrorH\x00\x42\x08\n\x06result\"\x8b\x01\n\tHookPoint\x12\x11\n\rBEFORE_CREATE\x10\x00\x12\x10\n\x0c\x41\x46TER_CREATE\x10\x01\x12\x11\n\rBEFORE_UPDATE\x10\x02\x12\x10\n\x0c\x41\x46TER_UPDATE\x10\x03\x12\x11\n\rBEFORE_DELETE\x10\x04\x12\x10\n\x0c\x41\x46TER_DELETE\x10\x05\x12\x0f\n\x0b\x42\x45\x46ORE_VIEW\x10\x06\x42\t\n\x07message\"\xab\x01\n\x10RegCoreHookReply\x12\x0f\n\x07\x63\x61ll_id\x18\x01 \x01(\x04\x12\x1c\n\x06object\x18\x02 \x01(\x0b\x32\x0c.novi.Object\x12%\n\nold_object\x18\x03 \x01(\x0b\x32\x0c.novi.ObjectH\x00\x88\x01\x01\x12\x14\n\x07session\x18\x04 \x01(\tH\x01\x88\x01\x01\x12\x10\n\x08identity\x18\x05 \x01(\tB\r\n\x0b_old_objectB\n\n\x08_session\"Q\n\nHookAction\x12\x13\n\x0bupdate_args\x18\x01 \x01(\x08\x12\x1b\n\x0eresult_or_args\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x11\n\x0f_result_or_args\"\x9c\x02\n\x0eRegHookRequest\x12\x31\n\x08initiate\x18\x01 \x01(\x0b\x32\x1d.novi.RegHookRequest.InitiateH\x00\x12\x31\n\x06result\x18\x02 \x01(\x0b\x32\x1f.novi.RegHookRequest.CallResultH\x00\x1a,\n\x08Initiate\x12\x10\n\x08\x66unction\x18\x01 \x01(\t\x12\x0e\n\x06\x62\x65\x66ore\x18\x02 \x01(\x08\x1ak\n\nCallResult\x12\x0f\n\x07\x63\x61ll_id\x18\x01 \x01(\x04\x12$\n\x08response\x18\x02 \x01(\x0b\x32\x10.novi.HookActionH\x00\x12\x1c\n\x05\x65rror\x18\x03 \x01(\x0b\x32\x0b.novi.ErrorH\x00\x42\x08\n\x06resultB\t\n\x07message\"\x87\x01\n\x0cRegHookReply\x12\x0f\n\x07\x63\x61ll_id\x18\x01 \x01(\x04\x12\x11\n\targuments\x18\x02 \x01(\t\x12\x1c\n\x0foriginal_result\x18\x03 \x01(\tH\x00\x88\x01\x01\x12\x0f\n\x07session\x18\x04 \x01(\t\x12\x10\n\x08identity\x18\x05 \x01(\tB\x12\n\x10_original_result\"\xaa\x02\n\x12RegFunctionRequest\x12\x35\n\x08initiate\x18\x01 \x01(\x0b\x32!.novi.RegFunctionRequest.InitiateH\x00\x12\x35\n\x06result\x18\x02 \x01(\x0b\x32#.novi.RegFunctionRequest.CallResultH\x00\x1a@\n\x08Initiate\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x17\n\npermission\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\r\n\x0b_permission\x1aY\n\nCallResult\x12\x0f\n\x07\x63\x61ll_id\x18\x01 \x01(\x04\x12\x12\n\x08response\x18\x02 \x01(\tH\x00\x12\x1c\n\x05\x65rror\x18\x03 \x01(\x0b\x32\x0b.novi.ErrorH\x00\x42\x08\n\x06resultB\t\n\x07message\"Y\n\x10RegFunctionReply\x12\x0f\n\x07\x63\x61ll_id\x18\x01 \x01(\x04\x12\x11\n\targuments\x18\x02 \x01(\t\x12\x0f\n\x07session\x18\x03 \x01(\t\x12\x10\n\x08identity\x18\x04 \x01(\t\"6\n\x13\x43\x61llFunctionRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\targuments\x18\x02 \x01(\t\"#\n\x11\x43\x61llFunctionReply\x12\x0e\n\x06result\x18\x01 \x01(\t\";\n\x16\x43heckPermissionRequest\x12\x13\n\x0bpermissions\x18\x01 \x03(\t\x12\x0c\n\x04\x62\x61il\x18\x02 \x01(\x08\"\"\n\x14\x43heckPermissionReply\x12\n\n\x02ok\x18\x01 \x01(\x08*/\n\tEventKind\x12\n\n\x06\x43REATE\x10\x00\x12\n\n\x06UPDATE\x10\x01\x12\n\n\x06\x44\x45LETE\x10\x02\x32\x99\t\n\x04Novi\x12-\n\x05Login\x12\x12.novi.LoginRequest\x1a\x10.novi.LoginReply\x12\x33\n\x07LoginAs\x12\x14.novi.LoginAsRequest\x1a\x12.novi.LoginAsReply\x12\x42\n\x0cUseMasterKey\x12\x19.novi.UseMasterKeyRequest\x1a\x17.novi.UseMasterKeyReply\x12>\n\nNewSession\x12\x17.novi.NewSessionRequest\x1a\x15.novi.NewSessionReply0\x01\x12<\n\nEndSession\x12\x17.novi.EndSessionRequest\x1a\x15.novi.EndSessionReply\x12\x42\n\x0c\x43reateObject\x12\x19.novi.CreateObjectRequest\x1a\x17.novi.CreateObjectReply\x12\x39\n\tGetObject\x12\x16.novi.GetObjectRequest\x1a\x14.novi.GetObjectReply\x12\x42\n\x0cUpdateObject\x12\x19.novi.UpdateObjectRequest\x1a\x17.novi.UpdateObjectReply\x12\x45\n\rReplaceObject\x12\x1a.novi.ReplaceObjectRequest\x1a\x18.novi.ReplaceObjectReply\x12N\n\x10\x44\x65leteObjectTags\x12\x1d.novi.DeleteObjectTagsRequest\x1a\x1b.novi.DeleteObjectTagsReply\x12\x42\n\x0c\x44\x65leteObject\x12\x19.novi.DeleteObjectRequest\x1a\x17.novi.DeleteObjectReply\x12-\n\x05Query\x12\x12.novi.QueryRequest\x1a\x10.novi.QueryReply\x12;\n\tSubscribe\x12\x16.novi.SubscribeRequest\x1a\x14.novi.SubscribeReply0\x01\x12H\n\x10RegisterCoreHook\x12\x18.novi.RegCoreHookRequest\x1a\x16.novi.RegCoreHookReply(\x01\x30\x01\x12<\n\x0cRegisterHook\x12\x14.novi.RegHookRequest\x1a\x12.novi.RegHookReply(\x01\x30\x01\x12H\n\x10RegisterFunction\x12\x18.novi.RegFunctionRequest\x1a\x16.novi.RegFunctionReply(\x01\x30\x01\x12\x42\n\x0c\x43\x61llFunction\x12\x19.novi.CallFunctionRequest\x1a\x17.novi.CallFunctionReply\x12K\n\x0f\x43heckPermission\x12\x1c.novi.CheckPermissionRequest\x1a\x1a.novi.CheckPermissionReplyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'novi.proto.novi_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_ERROR_METADATAENTRY']._loaded_options = None
  _globals['_ERROR_METADATAENTRY']._serialized_options = b'8\001'
  _globals['_TAGS_PROPERTIESENTRY']._loaded_options = None
  _globals['_TAGS_PROPERTIESENTRY']._serialized_options = b'8\001'
  _globals['_OBJECT_TAGSENTRY']._loaded_options = None
  _globals['_OBJECT_TAGSENTRY']._serialized_options = b'8\001'
  _globals['_EVENTKIND']._serialized_start=4184
  _globals['_EVENTKIND']._serialized_end=4231
  _globals['_ERROR']._serialized_start=32
  _globals['_ERROR']._serialized_end=164
  _globals['_ERROR_METADATAENTRY']._serialized_start=117
  _globals['_ERROR_METADATAENTRY']._serialized_end=164
  _globals['_UUID']._serialized_start=166
  _globals['_UUID']._serialized_end=196
  _globals['_TAGVALUE']._serialized_start=198
  _globals['_TAGVALUE']._serialized_end=255
  _globals['_TAGS']._serialized_start=257
  _globals['_TAGS']._serialized_end=376
  _globals['_TAGS_PROPERTIESENTRY']._serialized_start=327
  _globals['_TAGS_PROPERTIESENTRY']._serialized_end=376
  _globals['_OBJECT']._serialized_start=379
  _globals['_OBJECT']._serialized_end=590
  _globals['_OBJECT_TAGSENTRY']._serialized_start=519
  _globals['_OBJECT_TAGSENTRY']._serialized_end=578
  _globals['_SCOPES']._serialized_start=592
  _globals['_SCOPES']._serialized_end=616
  _globals['_LOGINREQUEST']._serialized_start=618
  _globals['_LOGINREQUEST']._serialized_end=668
  _globals['_LOGINREPLY']._serialized_start=670
  _globals['_LOGINREPLY']._serialized_end=700
  _globals['_LOGINASREQUEST']._serialized_start=702
  _globals['_LOGINASREQUEST']._serialized_end=763
  _globals['_LOGINASREPLY']._serialized_start=765
  _globals['_LOGINASREPLY']._serialized_end=797
  _globals['_USEMASTERKEYREQUEST']._serialized_start=799
  _globals['_USEMASTERKEYREQUEST']._serialized_end=833
  _globals['_USEMASTERKEYREPLY']._serialized_start=835
  _globals['_USEMASTERKEYREPLY']._serialized_end=872
  _globals['_NEWSESSIONREQUEST']._serialized_start=874
  _globals['_NEWSESSIONREQUEST']._serialized_end=921
  _globals['_NEWSESSIONREPLY']._serialized_start=923
  _globals['_NEWSESSIONREPLY']._serialized_end=955
  _globals['_ENDSESSIONREQUEST']._serialized_start=957
  _globals['_ENDSESSIONREQUEST']._serialized_end=992
  _globals['_ENDSESSIONREPLY']._serialized_start=994
  _globals['_ENDSESSIONREPLY']._serialized_end=1011
  _globals['_CREATEOBJECTREQUEST']._serialized_start=1013
  _globals['_CREATEOBJECTREQUEST']._serialized_end=1060
  _globals['_CREATEOBJECTREPLY']._serialized_start=1062
  _globals['_CREATEOBJECTREPLY']._serialized_end=1111
  _globals['_GETOBJECTREQUEST']._serialized_start=1113
  _globals['_GETOBJECTREQUEST']._serialized_end=1155
  _globals['_GETOBJECTREPLY']._serialized_start=1157
  _globals['_GETOBJECTREPLY']._serialized_end=1203
  _globals['_UPDATEOBJECTREQUEST']._serialized_start=1205
  _globals['_UPDATEOBJECTREQUEST']._serialized_end=1291
  _globals['_UPDATEOBJECTREPLY']._serialized_start=1293
  _globals['_UPDATEOBJECTREPLY']._serialized_end=1342
  _globals['_REPLACEOBJECTREQUEST']._serialized_start=1345
  _globals['_REPLACEOBJECTREQUEST']._serialized_end=1478
  _globals['_REPLACEOBJECTREPLY']._serialized_start=1480
  _globals['_REPLACEOBJECTREPLY']._serialized_end=1530
  _globals['_DELETEOBJECTTAGSREQUEST']._serialized_start=1532
  _globals['_DELETEOBJECTTAGSREQUEST']._serialized_end=1595
  _globals['_DELETEOBJECTTAGSREPLY']._serialized_start=1597
  _globals['_DELETEOBJECTTAGSREPLY']._serialized_end=1650
  _globals['_DELETEOBJECTREQUEST']._serialized_start=1652
  _globals['_DELETEOBJECTREQUEST']._serialized_end=1697
  _globals['_DELETEOBJECTREPLY']._serialized_start=1699
  _globals['_DELETEOBJECTREPLY']._serialized_end=1718
  _globals['_QUERYREQUEST']._serialized_start=1721
  _globals['_QUERYREQUEST']._serialized_end=2129
  _globals['_QUERYREQUEST_ORDER']._serialized_start=1953
  _globals['_QUERYREQUEST_ORDER']._serialized_end=2030
  _globals['_QUERYREPLY']._serialized_start=2131
  _globals['_QUERYREPLY']._serialized_end=2174
  _globals['_SUBSCRIBEREQUEST']._serialized_start=2176
  _globals['_SUBSCRIBEREQUEST']._serialized_end=2289
  _globals['_SUBSCRIBEREPLY']._serialized_start=2291
  _globals['_SUBSCRIBEREPLY']._serialized_end=2368
  _globals['_OBJECTEDITS']._serialized_start=2370
  _globals['_OBJECTEDITS']._serialized_end=2443
  _globals['_REGCOREHOOKREQUEST']._serialized_start=2446
  _globals['_REGCOREHOOKREQUEST']._serialized_end=2918
  _globals['_REGCOREHOOKREQUEST_INITIATE']._serialized_start=2578
  _globals['_REGCOREHOOKREQUEST_INITIATE']._serialized_end=2655
  _globals['_REGCOREHOOKREQUEST_CALLRESULT']._serialized_start=2657
  _globals['_REGCOREHOOKREQUEST_CALLRESULT']._serialized_end=2765
  _globals['_REGCOREHOOKREQUEST_HOOKPOINT']._serialized_start=2768
  _globals['_REGCOREHOOKREQUEST_HOOKPOINT']._serialized_end=2907
  _globals['_REGCOREHOOKREPLY']._serialized_start=2921
  _globals['_REGCOREHOOKREPLY']._serialized_end=3092
  _globals['_HOOKACTION']._serialized_start=3094
  _globals['_HOOKACTION']._serialized_end=3175
  _globals['_REGHOOKREQUEST']._serialized_start=3178
  _globals['_REGHOOKREQUEST']._serialized_end=3462
  _globals['_REGHOOKREQUEST_INITIATE']._serialized_start=3298
  _globals['_REGHOOKREQUEST_INITIATE']._serialized_end=3342
  _globals['_REGHOOKREQUEST_CALLRESULT']._serialized_start=3344
  _globals['_REGHOOKREQUEST_CALLRESULT']._serialized_end=3451
  _globals['_REGHOOKREPLY']._serialized_start=3465
  _globals['_REGHOOKREPLY']._serialized_end=3600
  _globals['_REGFUNCTIONREQUEST']._serialized_start=3603
  _globals['_REGFUNCTIONREQUEST']._serialized_end=3901
  _globals['_REGFUNCTIONREQUEST_INITIATE']._serialized_start=3735
  _globals['_REGFUNCTIONREQUEST_INITIATE']._serialized_end=3799
  _globals['_REGFUNCTIONREQUEST_CALLRESULT']._serialized_start=3801
  _globals['_REGFUNCTIONREQUEST_CALLRESULT']._serialized_end=3890
  _globals['_REGFUNCTIONREPLY']._serialized_start=3903
  _globals['_REGFUNCTIONREPLY']._serialized_end=3992
  _globals['_CALLFUNCTIONREQUEST']._serialized_start=3994
  _globals['_CALLFUNCTIONREQUEST']._serialized_end=4048
  _globals['_CALLFUNCTIONREPLY']._serialized_start=4050
  _globals['_CALLFUNCTIONREPLY']._serialized_end=4085
  _globals['_CHECKPERMISSIONREQUEST']._serialized_start=4087
  _globals['_CHECKPERMISSIONREQUEST']._serialized_end=4146
  _globals['_CHECKPERMISSIONREPLY']._serialized_start=4148
  _globals['_CHECKPERMISSIONREPLY']._serialized_end=4182
  _globals['_NOVI']._serialized_start=4234
  _globals['_NOVI']._serialized_end=5411
# @@protoc_insertion_point(module_scope)
