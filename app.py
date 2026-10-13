    <div class="aportes-finca-summary-title compact">
        🏠 Detalle de Finca Raíz conjunta
    </div>

    <div class="aportes-finca-summary-sub compact">
        Sin registros disponibles.
    </div>

</div>
""")

        # --------------------------------------------------------
        # FINCA RAÍZ ADICIONAL + DEUDA INDIVIDUAL
        # --------------------------------------------------------
        # Aquí salen únicamente los activos de Finca Raíz que quedan
        # fuera del patrimonio principal. Comercio y Vehículos ya están
        # integrados en "Activos" y no se repiten aquí.
        if not activos_finca_adicional.empty:

            # Consolidar activos adicionales por inmueble, sin desglosar por socio.
            # El valor corresponde a la suma de las participaciones registradas
            # para cada activo en la vista patrimonial.
            adicionales_tabla = (
                activos_finca_adicional
                .groupby(
                    ["ID_Activo", "Nombre_Entidad", "Ciudad"],
                    as_index=False
                )["Valor_Mercado_Socio"]
                .sum()
                .rename(columns={"Valor_Mercado_Socio": "Valor_Activo"})
            )

            if not creditos_prorrateados.empty:
                deuda_individual_tabla = (
                    creditos_prorrateados[
                        ~creditos_prorrateados["Es_Principal"]
                    ]
                    .groupby("ID_Activo", as_index=False)["Saldo_Actual_Prorrateado"]
                    .sum()
                    .rename(columns={"Saldo_Actual_Prorrateado": "Deuda"})
                )
                adicionales_tabla = adicionales_tabla.merge(
                    deuda_individual_tabla, on="ID_Activo", how="left"
                )
            else:
                adicionales_tabla["Deuda"] = 0

            adicionales_tabla["Deuda"] = pd.to_numeric(
                adicionales_tabla["Deuda"], errors="coerce"
            ).fillna(0)
            adicionales_tabla["Patrimonio_Neto"] = (
                adicionales_tabla["Valor_Activo"] - adicionales_tabla["Deuda"]
            )
            adicionales_tabla = adicionales_tabla.sort_values(
                "Valor_Activo", ascending=False
            )

            valor_adicional_tabla = float(adicionales_tabla["Valor_Activo"].sum())
            deuda_adicional_tabla = float(adicionales_tabla["Deuda"].sum())
            neto_adicional_tabla = float(adicionales_tabla["Patrimonio_Neto"].sum())

            adicional_table_html = f"""
<div class="aportes-otros-panel" style="margin-top:16px;">
    <div class="aportes-card-title2">🏠 Finca Raíz adicional y deuda</div>
    <div class="aportes-card-sub2">
        Activos fuera de la finca raíz conjunta · consolidados por inmueble
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:18px;margin:10px 0 12px;padding:10px 12px;background:#F7F9FC;border:1px solid #E4EAF0;border-radius:10px;">
        <div><span style="font-size:9px;color:#71839A;">Valor agregado</span><br><b style="font-size:14px;color:#17345E;">{dinero_corto(valor_adicional_tabla)}</b></div>
        <div><span style="font-size:9px;color:#71839A;">Deuda atribuible</span><br><b style="font-size:14px;color:#E84235;">-{dinero_corto(deuda_adicional_tabla)}</b></div>
        <div><span style="font-size:9px;color:#71839A;">Patrimonio neto</span><br><b style="font-size:14px;color:#17345E;">{dinero_corto(neto_adicional_tabla)}</b></div>
    </div>
    <table class="aportes-table2">
        <thead>
            <tr>
                <th>Activo</th>
                <th>Ciudad</th>
                <th>Valor agregado</th>
                <th>Deuda</th>
                <th>Neto</th>
            </tr>
        </thead>
        <tbody>
"""
            for _, row in adicionales_tabla.iterrows():
                adicional_table_html += f"""
            <tr>
                <td>{escape_html(row["Nombre_Entidad"])}</td>
                <td>{escape_html(row["Ciudad"])}</td>
                <td><span class="aportes-finca-value compact">{dinero_corto(float(row["Valor_Activo"]))}</span></td>
                <td><span class="aportes-finca-debt compact">-{dinero_corto(float(row["Deuda"]))}</span></td>
                <td><span class="aportes-finca-value compact">{dinero_corto(float(row["Patrimonio_Neto"]))}</span></td>
            </tr>
"""
            adicional_table_html += """
        </tbody>
    </table>
    <div class="aportes-note2">
        Estos inmuebles se muestran separados de los activos conjuntos. El valor agregado suma las participaciones registradas en la vista patrimonial; no representa necesariamente el valor bruto total de cada inmueble.
    </div>
</div>
"""
            render_aportes_html(adicional_table_html)

