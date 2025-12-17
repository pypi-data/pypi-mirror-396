import os
from pypdf import PdfWriter, PdfReader
from PIL import Image


def create_pdf_from_folder(folder_path: str, output_pdf: str) -> None:
    pdf_writer = PdfWriter()

    files = sorted(os.listdir(folder_path))

    for file_name in files:
        file_path = os.path.join(folder_path, file_name)

        if file_name.lower().endswith(".pdf"):
            with open(file_path, "rb") as f:
                pdf_reader = PdfReader(f)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)

        elif file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            image = Image.open(file_path).convert("RGB")
            # Convert image to a single-page PDF in memory
            with open(f"{file_path}.pdf", "wb") as temp_pdf:
                image.save(temp_pdf, "PDF")
            # Add the single-page PDF we just created
            with open(f"{file_path}.pdf", "rb") as temp_f:
                try:
                    pdf_reader = PdfReader(temp_f)
                    pdf_writer.add_page(pdf_reader.pages[0])
                except Exception as e:
                    print(f"Error processing {file_name}: {e}")

            # Clean up temp file
            if os.path.exists(f"{file_path}.pdf"):
                os.remove(f"{file_path}.pdf")

    # Write out the combined PDF for the folder
    with open(output_pdf, "wb") as out_f:
        pdf_writer.write(out_f)
