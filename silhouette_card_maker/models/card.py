from dataclasses import dataclass, field
from typing import List
from silhouette_card_maker.models.faces import NormalizedCardFace
from silhouette_card_maker.enums import FaceType

@dataclass
class Card:
    """
    Represents a single card with one or more faces.
    """
    faces: List[NormalizedCardFace] = field(default_factory=list)

    def add_face(self, face: NormalizedCardFace) -> None:
        """
        Add a card face. If a face of the same type exists, replace it.
        """
        for i, existing in enumerate(self.faces):
            if existing.face_type == face.face_type:
                self.faces[i] = face
                return
        self.faces.append(face)

    @property
    def front(self) -> NormalizedCardFace | None:
        """
        Return the front face, or None if missing.
        """
        for face in self.faces:
            if face.face_type == FaceType.FRONT:
                return face
        return None

    @property
    def back(self) -> NormalizedCardFace | None:
        """
        Return the back face, or None if missing.
        """
        for face in self.faces:
            if face.face_type == FaceType.BACK:
                return face
        return None

    @property
    def doublesided(self) -> bool:
        """
        Returns True if the card has both front and back faces.
        """
        return self.front is not None and self.back is not None

    def __len__(self) -> int:
        """
        Return the number of faces in this card.
        """
        return len(self.faces)
