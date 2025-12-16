from ..alias import CamelCaseAliasedBaseModel, SnakeCaseAliasedBaseModel

__all__ = [
    "CamelCaseRequest",
    "InboundRequest",
    "OutboundRequest",
    "SnakeCaseRequest",
]


class SnakeCaseRequest(SnakeCaseAliasedBaseModel):
    pass


class CamelCaseRequest(CamelCaseAliasedBaseModel):
    pass


class InboundRequest(CamelCaseAliasedBaseModel):
    pass


class OutboundRequest(CamelCaseAliasedBaseModel):
    pass
