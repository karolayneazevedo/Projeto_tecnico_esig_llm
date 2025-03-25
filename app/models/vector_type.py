from sqlalchemy.types import UserDefinedType

class Vector(UserDefinedType):
    def get_col_spec(self, **kw):
        return "vector(1536)"
