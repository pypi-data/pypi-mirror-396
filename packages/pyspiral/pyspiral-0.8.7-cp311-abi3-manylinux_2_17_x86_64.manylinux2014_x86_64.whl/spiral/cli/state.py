from spiral import Spiral
from spiral.settings import settings


@property
def spiral() -> Spiral:
    return Spiral(settings())
