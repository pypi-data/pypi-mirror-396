from ..alias import CamelCaseAliasedBaseModel, SnakeCaseAliasedBaseModel

__all__ = [
    "CamelCaseResponse",
    "InboundResponse",
    "OutboundResponse",
    "SnakeCaseRespose",
]


class SnakeCaseRespose(SnakeCaseAliasedBaseModel):
    pass


class CamelCaseResponse(CamelCaseAliasedBaseModel):
    pass


class InboundResponse(CamelCaseAliasedBaseModel):
    pass


class OutboundResponse(CamelCaseAliasedBaseModel):
    pass
