from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x19sentencepiece_model.proto\x12\rsentencepiece"\x80\x0c\n\x0bTrainerSpec\x12\r\n\x05input\x18\x01 \x03(\t\x12\x14\n\x0cinput_format\x18\x07 \x01(\t\x12\x14\n\x0cmodel_prefix\x18\x02 \x01(\t\x12\x41\n\nmodel_type\x18\x03 \x01(\x0e\x32$.sentencepiece.TrainerSpec.ModelType:\x07UNIGRAM\x12\x18\n\nvocab_size\x18\x04 \x01(\x05:\x04\x38\x30\x30\x30\x12\x17\n\x0f\x61\x63\x63\x65pt_language\x18\x05 \x03(\t\x12 \n\x15self_test_sample_size\x18\x06 \x01(\x05:\x01\x30\x12*\n\x1b\x65nable_differential_privacy\x18\x32 \x01(\x08:\x05\x66\x61lse\x12+\n differential_privacy_noise_level\x18\x33 \x01(\x02:\x01\x30\x12\x32\n\'differential_privacy_clipping_threshold\x18\x34 \x01(\x04:\x01\x30\x12"\n\x12\x63haracter_coverage\x18\n \x01(\x02:\x06\x30.9995\x12\x1e\n\x13input_sentence_size\x18\x0b \x01(\x04:\x01\x30\x12$\n\x16shuffle_input_sentence\x18\x13 \x01(\x08:\x04true\x12 \n\x14mining_sentence_size\x18\x0c \x01(\x05\x42\x02\x18\x01\x12"\n\x16training_sentence_size\x18\r \x01(\x05\x42\x02\x18\x01\x12(\n\x17seed_sentencepiece_size\x18\x0e \x01(\x05:\x07\x31\x30\x30\x30\x30\x30\x30\x12\x1e\n\x10shrinking_factor\x18\x0f \x01(\x02:\x04\x30.75\x12!\n\x13max_sentence_length\x18\x12 \x01(\x05:\x04\x34\x31\x39\x32\x12\x17\n\x0bnum_threads\x18\x10 \x01(\x05:\x02\x31\x36\x12\x1d\n\x12num_sub_iterations\x18\x11 \x01(\x05:\x01\x32\x12$\n\x18max_sentencepiece_length\x18\x14 \x01(\x05:\x02\x31\x36\x12%\n\x17split_by_unicode_script\x18\x15 \x01(\x08:\x04true\x12\x1d\n\x0fsplit_by_number\x18\x17 \x01(\x08:\x04true\x12!\n\x13split_by_whitespace\x18\x16 \x01(\x08:\x04true\x12)\n\x1atreat_whitespace_as_suffix\x18\x18 \x01(\x08:\x05\x66\x61lse\x12+\n\x1c\x61llow_whitespace_only_pieces\x18\x1a \x01(\x08:\x05\x66\x61lse\x12\x1b\n\x0csplit_digits\x18\x19 \x01(\x08:\x05\x66\x61lse\x12
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "sentencepiece_model_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS is False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"H\003"
    _globals["_TRAINERSPEC"]._serialized_start = 45
    _globals["_TRAINERSPEC"]._serialized_end = 1581
    _globals["_TRAINERSPEC_MODELTYPE"]._serialized_start = 1517
    _globals["_TRAINERSPEC_MODELTYPE"]._serialized_end = 1570
    _globals["_NORMALIZERSPEC"]._serialized_start = 1584
    _globals["_NORMALIZERSPEC"]._serialized_end = 1793
    _globals["_SELFTESTDATA"]._serialized_start = 1795
    _globals["_SELFTESTDATA"]._serialized_end = 1916
    _globals["_SELFTESTDATA_SAMPLE"]._serialized_start = 1864
    _globals["_SELFTESTDATA_SAMPLE"]._serialized_end = 1905
    _globals["_MODELPROTO"]._serialized_start = 1919
    _globals["_MODELPROTO"]._serialized_end = 2429
    _globals["_MODELPROTO_SENTENCEPIECE"]._serialized_start = 2208
    _globals["_MODELPROTO_SENTENCEPIECE"]._serialized_end = 2418
    _globals["_MODELPROTO_SENTENCEPIECE_TYPE"]._serialized_start = 2323
    _globals["_MODELPROTO_SENTENCEPIECE_TYPE"]._serialized_end = 2407