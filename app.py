from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import Response
from io import BytesIO
from pypdf import PdfReader, PdfWriter

app = FastAPI()


@app.post("/unlock-pdf")
async def unlock_pdf(
    password: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        content = await file.read()
        input_buffer = BytesIO(content)

        try:
            reader = PdfReader(input_buffer)
            # Ha a PDF titkosított, próbáljuk megnyitni a jelszóval
            if reader.is_encrypted:
                if reader.decrypt(password) == 0:
                    # 0 = nem sikerült a decrypt
                    raise HTTPException(status_code=400, detail="Hibás jelszó vagy a PDF nem nyitható meg.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Nem sikerült megnyitni a PDF-et: {e}")

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        # Jelszó/enkryptálás eltávolítása
        #writer.remove_encryption()

        output_buffer = BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        filename = file.filename or "unlocked.pdf"

        return Response(
            content=output_buffer.read(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Belső hiba: {e}")
