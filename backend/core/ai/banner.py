def inject_banner(html: str, archive_url: str, original_url: str, mode: str = "historical") -> str:
    ts = ""
    try:
        parts = archive_url.split("/web/")
        if len(parts) > 1:
            t = parts[1].split("/")[0].replace("id_","")
            if len(t) >= 8:
                ts = f"{t[6:8]}/{t[4:6]}/{t[:4]}"
    except: pass

    labels = {
        "historical":    ("RECOVERED",       "#68d391"),
        "raw":           ("RAW ARCHIVE",      "#f6ad55"),
        "reconstructed": ("AI RECONSTRUCTED", "#a78bfa"),
    }
    label, color = labels.get(mode, labels["historical"])

    banner = f"""<div id="dwn-bar" style="position:fixed;top:0;left:0;right:0;z-index:2147483647;background:linear-gradient(135deg,#05050a,#0d0d18);border-bottom:1px solid rgba(99,179,237,0.18);padding:9px 16px;display:flex;align-items:center;gap:12px;font-family:monospace;font-size:11px;color:#718096;box-shadow:0 2px 20px rgba(0,0,0,.6);">
<span style="color:#63b3ed;font-weight:700;letter-spacing:.08em;flex-shrink:0;">◈ DEAD WEB</span>
<span style="color:#2d3748;">│</span>
<span style="color:{color};font-size:10px;letter-spacing:.1em;flex-shrink:0;">{label}</span>
<span style="color:#2d3748;">│</span>
<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;color:#4a5568;">{original_url[:70]}</span>
{"<span style='color:#4a5568;font-size:10px;flex-shrink:0;'>📅 "+ts+"</span>" if ts else ""}
<a href="/" style="flex-shrink:0;padding:4px 12px;background:rgba(99,179,237,.08);border:1px solid rgba(99,179,237,.25);border-radius:5px;color:#63b3ed;text-decoration:none;font-size:10px;font-weight:700;">← NAVIGATOR</a>
</div><div style="height:44px;"></div>"""

    if "<body" in html:
        i = html.find("<body")
        e = html.find(">", i)
        return html[:e+1] + banner + html[e+1:]
    return banner + html
