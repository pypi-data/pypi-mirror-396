from io import BytesIO
import cbor2
from cbor2 import CBORTag
from cbor2.decoder import CBORDecoder

from . import bindings

# ugly patch to remove default UUID decodeur
cbor2.decoder.semantic_decoders.pop(37)


def tag_hook(decoder, tag, shareable_index=None):
    if tag.tag == 37:
        return bindings.UUID(bytes=tag.value)
    if tag.tag == 32:
        return bindings.URL(tag.value)
    return tag


def default_encoder(encoder, value):
    if isinstance(value, bindings.UUID):
        encoder.encode(CBORTag(37, value.bytes))

    if isinstance(value, bindings.URL):
        encoder.encode(CBORTag(32, value.bytes))


def dumps(obj, **kwargs):
    return cbor2.dumps(obj, default=default_encoder, **kwargs)


def loads(payload, **kwargs):
    # return cbor2.loads(payload,tag_hook=tag_hook,**kwargs)
    return _loads(payload, tag_hook=tag_hook, **kwargs)


def _loads(s, **kwargs):
    with BytesIO(s) as fp:
        return CBORDecoder(fp, **kwargs).decode()


# class CustomDecoder(CBORDecoder):pass


def cleanup(obj):
    """
    recursive walk a object to search for un-wanted CBOR tags.
    Transform this tag in string format, this can be UUID, URL..
    Should be Ok, with list, dicts..
    Warning: This operate in-place changes.
    Warning: This won't work for tags in dict keys.
    """
    if isinstance(obj, list):
        for i in range(0, len(obj)):
            obj[i] = cleanup(obj[i])
        return obj

    if isinstance(obj, dict):
        for k in obj.keys():
            obj.update({k: cleanup(obj[k])})
        return obj

    if type(obj) in bindings.classes:
        return str(obj)
    else:
        return obj
