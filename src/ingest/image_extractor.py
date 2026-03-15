from __future__ import annotations

from pathlib import Path
import hashlib
import zipfile
import fitz

from src.models import ImageAsset, SourceDocument


def extract_images(documents: list[SourceDocument], output_dir: str) -> list[ImageAsset]:
    root = Path(output_dir) / "images"
    root.mkdir(parents=True, exist_ok=True)

    all_assets: list[ImageAsset] = []
    seen_hashes: set[str] = set()

    for doc in documents:
        path = Path(doc.file_path)
        if path.suffix.lower() == ".pdf":
            assets = _extract_pdf_images(doc, root, seen_hashes)
        elif path.suffix.lower() == ".docx":
            assets = _extract_docx_images(doc, root, seen_hashes)
        else:
            assets = []
        all_assets.extend(assets)

    return all_assets


def _extract_pdf_images(doc: SourceDocument, root: Path, seen_hashes: set[str]) -> list[ImageAsset]:
    assets: list[ImageAsset] = []
    pdf = fitz.open(doc.file_path)
    try:
        for page_index, page in enumerate(pdf, start=1):
            for image_index, img in enumerate(page.get_images(full=True), start=1):
                xref = img[0]
                data = pdf.extract_image(xref)
                blob = data.get("image", b"")
                if not blob:
                    continue
                digest = hashlib.sha256(blob).hexdigest()
                if digest in seen_hashes:
                    continue
                seen_hashes.add(digest)
                ext = data.get("ext", "png")
                image_id = f"{doc.doc_id}-p{page_index}-i{image_index}"
                path = root / f"{image_id}.{ext}"
                path.write_bytes(blob)
                assets.append(
                    ImageAsset(
                        image_id=image_id,
                        doc_id=doc.doc_id,
                        page=page_index,
                        file_path=str(path),
                        hash_sha256=digest,
                    )
                )
    finally:
        pdf.close()
    return assets


def _extract_docx_images(doc: SourceDocument, root: Path, seen_hashes: set[str]) -> list[ImageAsset]:
    assets: list[ImageAsset] = []
    index = 0
    with zipfile.ZipFile(doc.file_path, "r") as zf:
        for name in zf.namelist():
            if not name.startswith("word/media/"):
                continue
            blob = zf.read(name)
            digest = hashlib.sha256(blob).hexdigest()
            if digest in seen_hashes:
                continue
            seen_hashes.add(digest)
            index += 1
            ext = Path(name).suffix.lstrip(".") or "png"
            image_id = f"{doc.doc_id}-p1-i{index}"
            path = root / f"{image_id}.{ext}"
            path.write_bytes(blob)
            assets.append(
                ImageAsset(
                    image_id=image_id,
                    doc_id=doc.doc_id,
                    page=1,
                    file_path=str(path),
                    hash_sha256=digest,
                )
            )
    return assets
