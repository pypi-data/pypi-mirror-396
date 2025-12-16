from ...alias import CamelCaseAliasedBaseModel, SnakeCaseAliasedBaseModel


class SnakeCaseOutboundMessage(SnakeCaseAliasedBaseModel):
    pass


class CamelCaseOutboundMessage(CamelCaseAliasedBaseModel):
    pass


class OutboundMessage(CamelCaseOutboundMessage):
    pass
