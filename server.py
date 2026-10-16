@app.get("/api/admin/datos")
def admin_datos():
    usuarios_dict = PERSONAL_FIJO.copy()
    if supabase:
        try:
            res_u = supabase.table("usuarios").select("*").execute()
            if res_u.data:
                for u in res_u.data:
                    tipo = str(u.get("tipo_pago", "")).lower()
                    if tipo in ["fijo", "semanal"]:
                        if not u.get("monto_fijo") or u.get("monto_fijo") == 0:
                            u["monto_fijo"] = u.get("tarifa_hora", 150.0)
                        if not u.get("tarifa_hora") or u.get("tarifa_hora") == 0:
                            u["tarifa_hora"] = u["monto_fijo"]
                    usuarios_dict[u["usuario"]] = u
        except Exception as e:
            print("Error al cargar usuarios desde Supabase:", e)

    asistencias_list = []
    if supabase:
        try:
            res_a = supabase.table("asistencias").select("*").execute()
            if res_a.data is not None:
                asistencias_list = res_a.data
        except Exception as e:
            print("Error al cargar asistencias desde Supabase:", e)

    return {"usuarios": usuarios_dict, "asistencias": asistencias_list}
