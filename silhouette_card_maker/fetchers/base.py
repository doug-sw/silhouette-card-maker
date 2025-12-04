from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from ..models.card import Card
from collections import namedtuple


FaceRecord = namedtuple('FaceRecord', ['face', 'card', 'stem', 'folder'])


class BaseFetcher:
    """
    Base fetcher for card images using two-pass parallel downloading.
    """

    def fetch_parallel(self, collection, output_dir: str, max_workers: int | None = None) -> None:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        face_map: dict[str, FaceRecord] = {}
        for idx, card in enumerate(collection.cards):
            for face, folder in ((card.front, "front"), (card.back, "double_sided")):
                if face is None:
                    continue
                face_id = self.construct_face_id(face)
                if face_id in face_map:
                    continue
                stem = self.construct_stem(card, idx)
                face_map[face_id] = FaceRecord(face, card, stem, folder)

        max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4, len(face_map))
        cache: dict[str, Path] = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(self.download_face, record.face, record.stem, output_path / record.folder): face_id
                for face_id, record in face_map.items()
            }
            for future in as_completed(future_map):
                face_id = future_map[future]
                cache[face_id] = future.result()

        for idx, card in enumerate(collection.cards):
            for face, folder in ((card.front, "front"), (card.back, "double_sided")):
                if face is None:
                    continue

                face_id = self.construct_face_id(face)
                src_path = cache[face_id]
                stem = self.construct_stem(card, idx)
                dst_dir = output_path / folder
                dst_dir.mkdir(parents=True, exist_ok=True)
                dst_path = dst_dir / (stem + os.path.splitext(src_path)[1])

                if not dst_path.exists():
                    try:
                        dst_path.hardlink_to(src_path)
                    except AttributeError:
                        os.link(src_path, dst_path)


    def fetch(self, collection, output_dir: str):
        """Serial fallback."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        cache: dict[str, Path] = {}

        for idx, card in enumerate(collection.cards):
            for face, folder in ((card.front, "front"), (card.back, "double_sided")):
                if face is None:
                    continue

                face_id = self.construct_face_id(face)
                dst_dir = output_path / folder
                dst_dir.mkdir(parents=True, exist_ok=True)
                stem = self.construct_stem(card, idx)

                if face_id not in cache:
                    cache[face_id] = self.download_face(face, stem, dst_dir)
                else:
                    src_path = cache[face_id]
                    dst_path = dst_dir / (stem + os.path.splitext(src_path)[1])
                    if not dst_path.exists():
                        try:
                            dst_path.hardlink_to(src_path)
                        except AttributeError:
                            os.link(src_path, dst_path)

    def download_face(self, face: Any, stem: str, output_dir: Path) -> Path:
        """Download a single card face. Must return the full Path (with extension)."""
        raise NotImplementedError("Subclasses must implement download_face(face, stem, output_dir) -> Path")

    def construct_stem(self, card: Any, idx: int) -> str:
        """Return a safe filename stem for the card face."""
        raise NotImplementedError("Subclasses must implement construct_stem(card, idx) -> str")

    def construct_face_id(self, face: Any) -> str:
        """Return a unique identifier for caching purposes."""
        raise NotImplementedError("Subclasses must implement construct_face_id(face)")