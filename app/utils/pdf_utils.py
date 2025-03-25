import fitz
import os
from typing import Dict


def extract_images_from_pdf(pdf_path: str, output_dir: str) -> Dict[int, list]:
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_map = {}

    for page_number in range(len(doc)):
        images = doc[page_number].get_images(full=True)
        page_images = []

        for img_index, img in enumerate(images):
            try:
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)

                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                image_filename = f"page{page_number + 1}_img{img_index + 1}.png"
                image_path = os.path.join(output_dir, image_filename)
                pix.save(image_path)
                page_images.append(image_path)

            except Exception as e:
                print(f"Erro ao extrair imagem da página {page_number + 1}: {e}")

        if page_images:
            image_map[page_number] = page_images

    return image_map
