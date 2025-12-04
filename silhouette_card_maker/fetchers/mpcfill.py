from pathlib import Path
from base64 import b64decode
import requests
from filetype.filetype import guess_extension
from silhouette_card_maker.models.collections import CardCollection
from silhouette_card_maker.models.faces import NormalizedCardFace
from silhouette_card_maker.fetchers.base import BaseFetcher
import os
from silhouette_card_maker.utils import remove_nonalphanumeric


class MPCFillFetcher(BaseFetcher):
    """
    Fetcher for MPCFill card images.
    Front faces go in 'front', back faces go in 'double_sided'.
    """

    HEADERS: dict[str, str] = {
        "user-agent": "silhouette-card-maker/0.1",
        "accept": "*/*",
    }

    # URL components
    BASE_URL: str = "https://script.google.com/macros/s/"
    SCRIPT_ID: str = "AKfycbw8laScKBfxda2Wb0g63gkYDBdy8NWNxINoC4xDOwnCQ3JMFdruam1MdmNmN4wI5k4"
    EXEC_PATH: str = "exec?id="

    def download_face(self, face: NormalizedCardFace, stem: str, output_dir: Path) -> Path:
        """
        Download a single card face or use a cached file if already exists.
        Returns the full path to the downloaded file (with extension).
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        face_id = self.construct_face_id(face)
        url = f"{self.BASE_URL}{self.SCRIPT_ID}/{self.EXEC_PATH}{face_id}"

        resp = requests.get(url, headers=self.HEADERS)
        resp.raise_for_status()

        image_bytes = b64decode(resp.content)
        ext = guess_extension(image_bytes)
        filepath = output_dir / f"{stem}.{ext}"
        filepath.write_bytes(image_bytes)
        return filepath

    def construct_stem(self, card, idx: int) -> str:
        """
        Return a safe stem for the card's filename: {idx}_{card.front.name}.
        """
        stem = os.path.splitext(card.front.name)[0]
        safe_stem = remove_nonalphanumeric(stem)
        return f"{idx}_{safe_stem}"

    def construct_face_id(self, face: NormalizedCardFace) -> str:
        """
        Return a unique id for caching a face. Requires face.data.id.
        """
        return face.id
