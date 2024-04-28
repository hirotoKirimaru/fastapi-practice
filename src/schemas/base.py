from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CustomModel(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        strict=True,
    )
