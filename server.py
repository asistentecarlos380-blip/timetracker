@app.get("/api/admin/exportar-excel")
def exportar_excel():
    data = load_data()
    usuarios_list = list(data["usuarios"].keys())
    
    # Construir una estructura por días basada en las asistencias registradas
    # Agruparemos por trabajador y por fecha de inicio del turno
    registros_por_usuario = {u: {} for u in usuarios_list}
    
    for reg in data["asistencias"]:
        u = reg["usuario"]
        if u not in registros_por_usuario:
            registros_por_usuario[u] = {}
        
        # Extraer fecha de entrada (YYYY-MM-DD)
        if reg.get("entrada"):
            partes = reg["entrada"].split(' ')[0]
            # Formatear la hora de entrada y salida de forma limpia (ej. 13:08)
            def limpiar_hora(h_str):
                if not h_str: return "00:00"
                try:
                    p = h_str.split(' ')
                    t = p[1].split(':')
                    hh = int(t[0])
                    if p[2] == 'PM' and hh < 12: hh += 12
                    if p[2] == 'AM' and hh == 12: hh = 0
                    return f"{hh:02d}:{t[1]}"
                except:
                    return "00:00"

            h_ent = limpiar_hora(reg["entrada"])
            h_sal = limpiar_hora(reg["salida"]) if reg.get("salida") else "00:00"
            
            # Calcular horas
            hrs = 0.0
            if reg.get("salida"):
                d1 = parse_fh_excel(reg["entrada"])
                d2 = parse_fh_excel(reg["salida"])
                if d1 and d2:
                    diff = (d2 - d1).total_seconds() / 3600.0
                    if reg.get("receso_inicio") and reg.get("receso_fin"):
                        dr1 = parse_fh_excel(reg["receso_inicio"])
                        dr2 = parse_fh_excel(reg["receso_fin"])
                        if dr1 and dr2:
                            diff -= (dr2 - dr1).total_seconds() / 3600.0
                    hrs = max(0.0, diff)

            registros_por_usuario[u][partes] = {
                "entrada": h_ent if reg.get("entrada") else "00:00",
                "salida": h_sal if reg.get("salida") else "00:00",
                "horas": round(hrs, 2)
            }

    # Recopilar todas las fechas únicas ordenadas
    todas_fechas = set()
    for u in registros_por_usuario:
        for f in registros_por_usuario[u]:
            todas_fechas.add(f)
    fechas_ordenadas = sorted(list(todas_fechas))

    # Armar filas para el DataFrame de Excel con formato de matriz
    filas_excel = []
    for u in usuarios_list:
        fila = {"Trabajador": u}
        total_horas_global = 0.0
        for f in fechas_ordenadas:
            info = registros_por_usuario[u].get(f, {"entrada": "00:00", "salida": "00:00", "horas": 0.0})
            fila[f"{f} Entr"] = info["entrada"]
            fila[f"{f} Sal"] = info["salida"]
            fila[f"{f} Horas"] = info["horas"]
            total_horas_global += info["horas"]
        fila["Total Horas"] = round(total_horas_global, 2)
        filas_excel.append(fila)

    df_matriz = pd.DataFrame(filas_excel)

    # También mantenemos las hojas de Usuarios y Asistencias brutas para respaldo completo
    df_usuarios = pd.DataFrame([{
        "Usuario": u, "PIN": info.get("pin"), "Tipo_Pago": info.get("tipo_pago"),
        "Monto_Fijo": info.get("monto_fijo"), "Tarifa_Hora": info.get("tarifa_hora"),
        "Area": info.get("area"), "Rol_Sistema": info.get("rol_sistema")
    } for u, info in data["usuarios"].items()])

    df_asistencias = pd.DataFrame(data["asistencias"] if data["asistencias"] else [{"id": "", "usuario": "", "entrada": "", "receso_inicio": "", "receso_fin": "", "salida": ""}])

    file_path = "respaldo_nomina.xlsx"
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df_matriz.to_excel(writer, sheet_name="Resumen Matriz Dias", index=False)
        df_usuarios.to_excel(writer, sheet_name="Usuarios", index=False)
        df_asistencias.to_excel(writer, sheet_name="Asistencias Brutas", index=False)

    return FileResponse(file_path, filename=f"Respaldo_Matriz_Nomina_{datetime.now().strftime('%Y-%m-%d')}.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def parse_fh_excel(str_fh):
    try:
        partes = str_fh.split(' ')
        f = partes[0].split('-')
        h = partes[1].split(':')
        ampm = partes[2]
        hh = int(h[0])
        if ampm == 'PM' and hh < 12: hh += 12
        if ampm == 'AM' and hh == 12: hh = 0
        return datetime(int(f[0]), int(f[1]), int(f[2]), hh, int(h[1]), int(h[2]))
    except:
        return None
