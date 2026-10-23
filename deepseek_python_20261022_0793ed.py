def fila_html(p):
    mensaje = generar_mensaje(p)
    enlace = generar_enlace_whatsapp(p.telefono, mensaje)
    etiqueta_nicho = ETIQUETA_NICHO[p.nicho]
    
    # sublinea: teléfono · tipo_contacto [· email]
    tipo_label = "contacto directo" if p.tipo_contacto == "directo" else "atención general"
    sub_partes = [p.telefono, tipo_label]
    if p.email:
        sub_partes.append(f'<a class="mailto" href="mailto:{html.escape(p.email)}">{html.escape(p.email)}</a>')
    sub = " · ".join(sub_partes)
    
    # web cell
    if p.web == "Con Web" and p.url:
        web_cell = f'<a class="link-web" href="{html.escape(p.url, quote=True)}" target="_blank" rel="noopener">Ver web</a>'
    else:
        web_cell = '<span class="sin-web">Sin web</span>'
    
    # estado cell
    if p.estado_contacto == "correo_enviado":
        estado_cell = "<span class='estado estado-enviado'>Correo enviado</span>"
    else:
        estado_cell = "<span class='estado estado-pendiente'>Pendiente</span>"
    
    return (
        "<tr>"
        f"<td><div class='empresa'>{html.escape(p.nombre)}</div><div class='sub'>{sub}</div></td>"
        f"<td>{html.escape(etiqueta_nicho)}</td>"
        f"<td><span class='badge'>{html.escape(p.web)}</span></td>"
        f"<td>{web_cell}</td>"
        f"<td>{estado_cell}</td>"
        f"<td><a class='btn-wa' href='{html.escape(enlace, quote=True)}' target='_blank' rel='noopener'>Enviar WhatsApp</a></td>"
        "</tr>"
    )