from fastapi_query.filtering import WithPrefix
from .examples.schemas import UserFilters


def test_with_prefix():
    model = WithPrefix(UserFilters, prefix="test_prefix")

    assert model.Settings.prefix == "test_prefix"
