def build_verify_email_content(verify_link: str) -> tuple[str, str, str]:
    subject = "Potvrďte svoj e-mail | HireCrackr"
    text_body = (
        "Ahoj,\n\n"
        "ďakujeme za registráciu na HireCrackr.\n"
        "Pre aktiváciu účtu prosím potvrďte svoj e-mail kliknutím na odkaz:\n\n"
        f"{verify_link}\n\n"
        "Odkaz je platný 24 hodín.\n\n"
        "Ak ste sa neregistrovali vy, tento e-mail môžete ignorovať.\n\n"
        "S pozdravom,\n"
        "tím HireCrackr"
    )

    html_body = f"""
        <html>
            <body style="margin:0;padding:0;background:#f6f8fb;font-family:Arial,sans-serif;color:#1f2937;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding:24px;">
                <tr>
                    <td align="left">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px;background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
                        <tr>
                        <td style="padding:24px 24px 8px 24px;">
                            <h1 style="margin:0;font-size:22px;line-height:1.3;color:#111827;text-align:left;">Potvrďte svoj e-mail</h1>
                        </td>
                        </tr>
                        <tr>
                        <td style="padding:8px 24px 0 24px;font-size:15px;line-height:1.6;color:#374151;text-align:left;">
                            Ďakujeme za registráciu na <strong>HireCrackr</strong>.
                            Pre aktiváciu účtu kliknite na tlačidlo nižšie.
                        </td>
                        </tr>
                        <tr>
                        <td style="padding:24px;text-align:left;">
                            <a href="{verify_link}"
                            style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;font-weight:600;padding:12px 20px;border-radius:8px;">
                            Overiť e-mail
                            </a>
                        </td>
                        </tr>
                        <tr>
                        <td style="padding:0 24px 16px 24px;font-size:13px;line-height:1.6;color:#6b7280;text-align:left;">
                            Odkaz je platný <strong>24 hodín</strong>.
                            Ak tlačidlo nefunguje, skopírujte tento odkaz do prehliadača:
                            <br>
                            <a href="{verify_link}" style="color:#2563eb;word-break:break-all;">{verify_link}</a>
                        </td>
                        </tr>
                        <tr>
                        <td style="padding:0 24px 24px 24px;font-size:13px;line-height:1.6;color:#6b7280;text-align:left;">
                            Ak ste sa neregistrovali vy, tento e-mail môžete bezpečne ignorovať.
                        </td>
                        </tr>
                    </table>
                    <p style="margin:12px 0 0 0;font-size:12px;color:#9ca3af;text-align:left;">© HireCrackr</p>
                    </td>
                </tr>
                </table>
            </body>
        </html>
    """
    return subject, text_body, html_body