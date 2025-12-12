from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING


class StringDataSchema(Schema):
    """Сервисный класс генерации схемы post запросов с параметрами"""

    def __init__(self, body_params: list[tuple[str, str]]):
        self.properties = self.get_properties(body_params)
        super().__init__(type=TYPE_OBJECT, properties=self.properties)

    def get_properties(
            self, params: list[tuple[str, str]]
    ) -> dict[str, Schema]:
        """Возвращается список параметров для post запроса"""
        return {
            param: Schema(type=TYPE_STRING, description=description)
            for param, description in params
        }
