@app.get("/api/admin/datos")
def admin_datos():
    usuarios_dict = PERSONAL_FIJO.copy()
    try:
        res_u = supabase.table("usuarios").select("*").execute()
        if res_u.data:
            for u in res_u.data:
                usuarios_dict[u["usuario"]] = u
    except Exception:
        pass

    asistencias_list = []
    try:
        # Forzar consulta directa y abierta de todas las asistencias ordenadas
        res_a = supabase.table("asistencias").select("*").execute()
        if res_a.data:
            asistencias_list = res_a.data
    except Exception as e:
        print("Error obteniendo asistencias:", e)

    return {"usuarios": usuarios_dict, "asistencias": asistencias_list}
