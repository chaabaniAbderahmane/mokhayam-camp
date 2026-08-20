# -*- coding: utf-8 -*-
"""Utility helpers: QR generation, CSV/Excel export."""
import io
import qrcode
import pandas as pd


def make_qr_image(data: str) -> bytes:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0b0b0b", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def participant_portal_url(app_url: str, token: str) -> str:
    app_url = (app_url or "").strip().rstrip("/")
    if app_url:
        return f"{app_url}/?p={token}"
    return token  # fallback: raw token, participant pastes it into the portal search box


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return buf.getvalue()
