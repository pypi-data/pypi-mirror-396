from ...alias import CamelCaseAliasedBaseModel, SnakeCaseAliasedBaseModel


class SnakeCaseInboundMessage(SnakeCaseAliasedBaseModel):
    pass


class CamelCaseInboundMessage(CamelCaseAliasedBaseModel):
    pass


class InboundMessage(CamelCaseAliasedBaseModel):
    pass
