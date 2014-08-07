from pyasn1.type import univ, tag, namedtype, namedval
from pysnmp.proto import rfc1155

class VarBind(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('name', rfc1155.ObjectName()),
        namedtype.NamedType('value', rfc1155.ObjectSyntax())
        )
class VarBindList(univ.SequenceOf):
    componentType = VarBind()

_errorStatus = univ.Integer(namedValues=namedval.NamedValues(('noError', 0), ('tooBig', 1), ('noSuchName', 2), ('badValue', 3), ('readOnly', 4), ('genErr', 5)))
    
class _RequestBase(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('request-id', univ.Integer()),
        namedtype.NamedType('error-status', _errorStatus),
        namedtype.NamedType('error-index', univ.Integer()),
        namedtype.NamedType('variable-bindings', VarBindList())
        )

class GetRequestPDU(_RequestBase):
    tagSet = _RequestBase.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0)
        )    
class GetNextRequestPDU(_RequestBase):
    tagSet = _RequestBase.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1)
        )
class GetResponsePDU(_RequestBase):
    tagSet = _RequestBase.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 2)
        )
class SetRequestPDU(_RequestBase):
    tagSet = _RequestBase.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 3)
        )

_genericTrap = univ.Integer().clone(namedValues=namedval.NamedValues(('coldStart', 0), ('warmStart', 1), ('linkDown', 2), ('linkUp', 3), ('authenticationFailure', 4), ('egpNeighborLoss', 5), ('enterpriseSpecific', 6)))

class TrapPDU(univ.Sequence):
    tagSet = univ.Sequence.tagSet.tagImplicitly(
        tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 4)
        )    
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('enterprise', univ.ObjectIdentifier()),
        namedtype.NamedType('agent-addr', rfc1155.NetworkAddress()),
        namedtype.NamedType('generic-trap', _genericTrap),
        namedtype.NamedType('specific-trap', univ.Integer()),
        namedtype.NamedType('time-stamp', rfc1155.TimeTicks()),
        namedtype.NamedType('variable-bindings', VarBindList())
        )

class PDUs(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('get-request', GetRequestPDU()),
        namedtype.NamedType('get-next-request', GetNextRequestPDU()),
        namedtype.NamedType('get-response', GetResponsePDU()),
        namedtype.NamedType('set-request', SetRequestPDU()),
        namedtype.NamedType('trap', TrapPDU())
        )

_version =  univ.Integer(namedValues = namedval.NamedValues(('version-1', 0)))

class Message(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('version', _version),
        namedtype.NamedType('community', univ.OctetString()),
        namedtype.NamedType('data', PDUs())        
        )
