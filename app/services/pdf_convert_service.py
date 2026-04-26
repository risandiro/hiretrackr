import os
import subprocess
import tempfile


def convert_to_pdf_bytes(file_bytes: bytes, original_filename: str) -> bytes:
    
    # Znormalizuj príponu vstupného súboru (napr. .DOCX -> .docx)
    ext = "." + original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else ""

     # Vytvor dočasný adresár pre vstupný súbor a výsledné PDF
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, f"input{ext}")
        output_path = os.path.join(tmpdir, "input.pdf")

        # Ulož prijaté bytes
        with open(input_path, "wb") as f:
            f.write(file_bytes)

        # Priprav príkaz na konverziu
        cmd = [
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            tmpdir,
            input_path,
        ]

        # LibreOffice headless konverzia
        proc = subprocess.run(cmd, capture_output=True, text=True)
        print("soffice returncode:", proc.returncode)
        print("soffice stdout:", proc.stdout)
        print("soffice stderr:", proc.stderr)

        if proc.returncode != 0:
            raise RuntimeError(f"PDF conversion failed: {proc.stderr or proc.stdout}")

        if not os.path.exists(output_path):
            raise RuntimeError("PDF conversion failed: output file not found")

        # Načítaj a vráť výsledné PDF bytes
        with open(output_path, "rb") as f:
            return f.read()