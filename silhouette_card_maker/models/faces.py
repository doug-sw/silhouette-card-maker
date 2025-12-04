from dataclasses import dataclass, field
from typing import Any
from silhouette_card_maker.utils import to_namespace
from silhouette_card_maker.enums import FaceType


@dataclass
class NormalizedCardFace:
    """
    Represents a single card face.
    Wraps raw data into a recursive SimpleNamespace, so all nested keys
    can be accessed via dot notation (e.g., cardface.foo.bar).
    """
    face_type: FaceType
    data: Any
    _raw_data: Any = field(init=False, repr=False)

    def __post_init__(self):
        self._raw_data = self.data
        self.data = to_namespace(self._raw_data)
    
    def __getattr__(self, item: str) -> Any:
        """
        Allow direct attribute access from data:
        cardface.foo → cardface.data.foo
        """
        try:
            return getattr(self.data, item)
        except AttributeError as e:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{item}'") from e