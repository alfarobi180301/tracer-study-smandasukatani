import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import os

# Google Sheets URL (Diubah otomatis menjadi format ekspor CSV)
SHEETS_URL = "https://docs.google.com/spreadsheets/d/1Zt24-BXfXXuvDR7j79BTJy1UdTrXfTgBI9kg8ok01t8/export?format=csv"

# Inisialisasi Aplikasi Dash
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Tracer Study SMAN 2 Sukatani"
)
server = app.server

# Custom CSS Stylesheet (Inline)
COLORS = {
    "maroon": "#8B0000",
    "gold": "#DAA520",
    "background": "#F9F9F9",
    "card_bg": "#FFFFFF",
    "text": "#333333"
}

def load_data():
    try:
        df_raw = pd.read_csv(SHEETS_URL)
        kolom_map = {
            "NAMA LENGKAP": "Nama",
            "KELAS": "Kelas",
            "KARIER": "Karier",
            "UNIVERSITAS/INSTANSI/PERUSAHAAN": "Universitas/Instansi/Perusahaan",
            "JURUSAN": "Jurusan",
            "TAHUN LULUS": "Tahun Lulus"
        }
        
        # Penyelarasan nama kolom
        df_columns = {col.upper().strip(): col for col in df_raw.columns}
        clean_cols = {}
        for k_key, v_val in kolom_map.items():
            if k_key in df_columns:
                clean_cols[df_columns[k_key]] = v_val
                
        df = df_raw.rename(columns=clean_cols)
        
        # Buat kolom kosong jika tidak ada
        for col in kolom_map.values():
            if col not in df.columns:
                df[col] = "-"
                
        df = df[list(kolom_map.values())]
        
        # Standarisasi nilai Karier
        df["Karier"] = df["Karier"].astype(str).str.upper().str.strip()
        df["Karier"] = df["Karier"].replace({
            "BEBEKERJA": "BEKERJA",
            "KERJA": "BEKERJA",
            "WIRASWASTA": "WIRAUSAHA",
            "MEMBANTU ORANG TUA": "WIRAUSAHA"
        })
        
        df = df.fillna("-")
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"nan": "-", "": "-"})
        return df
    except Exception as e:
        print(f"Error load data: {e}")
        # Return fallback empty dataframe
        return pd.DataFrame(columns=["Nama", "Kelas", "Karier", "Universitas/Instansi/Perusahaan", "Jurusan", "Tahun Lulus"])

df_all = load_data()

# Layout Aplikasi
app.layout = html.Div(
    style={
        "backgroundColor": COLORS["background"],
        "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        "margin": "0",
        "padding": "0 20px 20px 20px"
    },
    children=[
        # HEADER SECTION (Logo & Title)
        html.Div(
            style={
                "textAlign": "center",
                "padding": "25px 0",
                "borderBottom": f"3px solid {COLORS['gold']}",
                "backgroundColor": COLORS['card_bg'],
                "marginBottom": "20px",
                "borderRadius": "0 0 10px 10px",
                "boxShadow": "0 4px 6px rgba(0,0,0,0.05)"
            },
            children=[
                # Menampilkan logo jika ada di folder assets, jika tidak tampilkan default logo
                html.Img(
                    src="/assets/logo.png" if os.path.exists("assets/logo.png") else "https://upload.wikimedia.org/wikipedia/commons/0/09/Logo_SMAN_2_Sukatani.png",
                    style={"height": "120px", "marginBottom": "10px"}
                ),
                html.H1(
                    "TRACER STUDY ALUMNI SMAN 2 SUKATANI",
                    style={"color": COLORS["maroon"], "fontWeight": "bold", "margin": "0", "fontSize": "2.2rem"}
                ),
                html.P(
                    "Sistem Pemantauan Perkembangan Karier, Perguruan Tinggi, dan Kewirausahaan Alumni",
                    style={"color": COLORS["gold"], "fontSize": "1.1rem", "marginTop": "5px"}
                )
            ]
        ),

        # MAIN CONTENT (Two Columns: Sidebar Filters & Metrics/Charts)
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px"},
            children=[
                # SIDEBAR (FILTERS)
                html.Div(
                    style={
                        "flex": "1 1 300px",
                        "backgroundColor": COLORS['card_bg'],
                        "padding": "20px",
                        "borderRadius": "10px",
                        "boxShadow": "0 4px 6px rgba(0,0,0,0.05)",
                        "borderLeft": f"5px solid {COLORS['maroon']}"
                    },
                    children=[
                        html.H3("⚙️ Filter Alumni", style={"color": COLORS["maroon"], "marginBottom": "15px", "borderBottom": "1px solid #ddd", "paddingBottom": "8px"}),
                        
                        # Filter Nama
                        html.Div(
                            style={"marginBottom": "15px"},
                            children=[
                                html.Label("Cari Nama Alumni:", style={"fontWeight": "600"}),
                                dcc.Input(
                                    id="search-name",
                                    type="text",
                                    placeholder="Masukkan nama...",
                                    style={"width": "100%", "padding": "8px", "marginTop": "5px", "borderRadius": "4px", "border": "1px solid #ccc"}
                                )
                            ]
                        ),
                        
                        # Filter Tahun Lulus
                        html.Div(
                            style={"marginBottom": "15px"},
                            children=[
                                html.Label("Tahun Lulus:", style={"fontWeight": "600"}),
                                dcc.Dropdown(
                                    id="filter-tahun",
                                    options=[{"label": str(t), "value": str(t)} for t in sorted(df_all["Tahun Lulus"].unique(), reverse=True)],
                                    multi=True,
                                    placeholder="Pilih Tahun...",
                                    style={"marginTop": "5px"}
                                )
                            ]
                        ),

                        # Filter Kelas
                        html.Div(
                            style={"marginBottom": "15px"},
                            children=[
                                html.Label("Kelas:", style={"fontWeight": "600"}),
                                dcc.Dropdown(
                                    id="filter-kelas",
                                    options=[{"label": k, "value": k} for k in sorted(df_all["Kelas"].unique())],
                                    multi=True,
                                    placeholder="Pilih Kelas...",
                                    style={"marginTop": "5px"}
                                )
                            ]
                        ),

                        # Filter Karier
                        html.Div(
                            style={"marginBottom": "15px"},
                            children=[
                                html.Label("Karier:", style={"fontWeight": "600"}),
                                dcc.Dropdown(
                                    id="filter-karier",
                                    options=[{"label": kr, "value": kr} for kr in sorted(df_all["Karier"].unique()) if kr != "-"],
                                    multi=True,
                                    placeholder="Pilih Status...",
                                    style={"marginTop": "5px"}
                                )
                            ]
                        ),

                        # Tombol Reset / Refresh Data
                        html.Button(
                            "🔄 Sinkronisasi Data Google Sheets",
                            id="btn-sync",
                            n_clicks=0,
                            style={
                                "width": "100%",
                                "backgroundColor": COLORS["maroon"],
                                "color": "white",
                                "border": "none",
                                "padding": "10px",
                                "borderRadius": "5px",
                                "fontWeight": "bold",
                                "cursor": "pointer",
                                "marginTop": "10px"
                            }
                        ),
                        html.Div(id="sync-status", style={"fontSize": "0.85rem", "color": "green", "marginTop": "5px", "textAlign": "center"})
                    ]
                ),

                # METRICS & CHARTS (RIGHT SECTION)
                html.Div(
                    style={"flex": "3 1 600px", "display": "flex", "flexDirection": "column", "gap": "20px"},
                    children=[
                        # KPI Cards
                        html.Div(
                            id="kpi-cards-container",
                            style={"display": "flex", "flexWrap": "wrap", "gap": "15px"}
                        ),

                        # Charts (2 Columns)
                        html.Div(
                            style={"display": "flex", "flexWrap": "wrap", "gap": "20px"},
                            children=[
                                # Chart 1: Pie Karier
                                html.Div(
                                    style={"flex": "1 1 300px", "backgroundColor": COLORS['card_bg'], "padding": "15px", "borderRadius": "10px", "boxShadow": "0 4px 6px rgba(0,0,0,0.05)"},
                                    children=[
                                        html.H4("Persentase Karier Alumni", style={"color": COLORS["maroon"], "textAlign": "center"}),
                                        dcc.Graph(id="chart-karier")
                                    ]
                                ),
                                # Chart 2: Bar Universitas
                                html.Div(
                                    style={"flex": "1 1 300px", "backgroundColor": COLORS['card_bg'], "padding": "15px", "borderRadius": "10px", "boxShadow": "0 4px 6px rgba(0,0,0,0.05)"},
                                    children=[
                                        html.H4("Top Perguruan Tinggi Tujuan", style={"color": COLORS["maroon"], "textAlign": "center"}),
                                        dcc.Graph(id="chart-universitas")
                                    ]
                                )
                            ]
                        ),

                        # Data Table
                        html.Div(
                            style={"backgroundColor": COLORS['card_bg'], "padding": "20px", "borderRadius": "10px", "boxShadow": "0 4px 6px rgba(0,0,0,0.05)"},
                            children=[
                                html.H4("📋 Daftar Alumni Terfilter", style={"color": COLORS["maroon"], "marginBottom": "15px"}),
                                dash_table.DataTable(
                                    id="alumni-table",
                                    columns=[
                                        {"name": "Nama Lengkap", "id": "Nama"},
                                        {"name": "Kelas", "id": "Kelas"},
                                        {"name": "Status Karier", "id": "Karier"},
                                        {"name": "Universitas / Instansi / Perusahaan", "id": "Universitas/Instansi/Perusahaan"},
                                        {"name": "Program Studi / Jurusan", "id": "Jurusan"},
                                        {"name": "Tahun Lulus", "id": "Tahun Lulus"}
                                    ],
                                    page_size=10,
                                    style_table={"overflowX": "auto"},
                                    style_header={
                                        "backgroundColor": COLORS["maroon"],
                                        "color": "white",
                                        "fontWeight": "bold",
                                        "textAlign": "left"
                                    },
                                    style_cell={
                                        "padding": "10px",
                                        "textAlign": "left",
                                        "fontFamily": "inherit"
                                    },
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "#f9f9f9"
                                        }
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        
        # Footer
        html.Div(
            style={"textAlign": "center", "marginTop": "40px", "color": "gray", "fontSize": "0.85rem"},
            children="Dashboard Tracer Study SMAN 2 Sukatani © 2026. Dikembangkan menggunakan Dash Plotly."
        )
    ]
)

# Callbacks untuk Filter, Sinkronisasi Google Sheets, dan Visualisasi
@app.callback(
    [
        Output("alumni-table", "data"),
        Output("kpi-cards-container", "children"),
        Output("chart-karier", "figure"),
        Output("chart-universitas", "figure"),
        Output("sync-status", "children")
    ],
    [
        Input("search-name", "value"),
        Input("filter-tahun", "value"),
        Input("filter-kelas", "value"),
        Input("filter-karier", "value"),
        Input("btn-sync", "n_clicks")
    ]
)
def update_dashboard(name, tahun, kelas, karier, sync_clicks):
    # Logika Trigger Sinkronisasi
    global df_all
    sync_msg = ""
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]["prop_id"] == "btn-sync.n_clicks":
        df_all = load_data()
        sync_msg = "✓ Data Google Sheets berhasil dimuat ulang!"

    df_filtered = df_all.copy()

    # Filter Nama
    if name:
        df_filtered = df_filtered[df_filtered["Nama"].str.contains(name, case=False, na=False)]
        
    # Filter Tahun Lulus
    if tahun:
        df_filtered = df_filtered[df_filtered["Tahun Lulus"].astype(str).isin(tahun)]
        
    # Filter Kelas
    if kelas:
        df_filtered = df_filtered[df_filtered["Kelas"].isin(kelas)]
        
    # Filter Karier
    if karier:
        df_filtered = df_filtered[df_filtered["Karier"].isin(karier)]

    # --- HITUNG METRIK KPI ---
    total_alumni = len(df_filtered)
    pct_kuliah = 0.0
    pct_bekerja = 0.0
    pct_wirausaha = 0.0
    
    kuliah_count = len(df_filtered[df_filtered["Karier"] == "KULIAH"])
    bekerja_count = len(df_filtered[df_filtered["Karier"] == "BEKERJA"])
    wirausaha_count = len(df_filtered[df_filtered["Karier"] == "WIRAUSAHA"])

    if total_alumni > 0:
        pct_kuliah = (kuliah_count / total_alumni) * 100
        pct_bekerja = (bekerja_count / total_alumni) * 100
        pct_wirausaha = (wirausaha_count / total_alumni) * 100

    kpi_cards = [
        # Total Card
        html.Div(
            style={"flex": "1 1 180px", "backgroundColor": COLORS["card_bg"], "padding": "15px", "borderRadius": "8px", "boxShadow": "0 2px 4px rgba(0,0,0,0.05)", "borderLeft": "5px solid gray", "textAlign": "center"},
            children=[
                html.Div("TOTAL TERFILTER", style={"fontSize": "0.85rem", "fontWeight": "bold", "color": "gray"}),
                html.Div(str(total_alumni), style={"fontSize": "1.8rem", "fontWeight": "bold", "color": COLORS["text"], "margin": "5px 0"}),
                html.Div("Alumni", style={"fontSize": "0.75rem", "color": "gray"})
            ]
        ),
        # Kuliah Card
        html.Div(
            style={"flex": "1 1 180px", "backgroundColor": COLORS["card_bg"], "padding": "15px", "borderRadius": "8px", "boxShadow": "0 2px 4px rgba(0,0,0,0.05)", "borderLeft": "5px solid #8B0000", "textAlign": "center"},
            children=[
                html.Div("🎓 KULIAH", style={"fontSize": "0.85rem", "fontWeight": "bold", "color": COLORS["maroon"]}),
                html.Div(f"{pct_kuliah:.1f}%", style={"fontSize": "1.8rem", "fontWeight": "bold", "color": COLORS["maroon"], "margin": "5px 0"}),
                html.Div(f"{kuliah_count} Alumni", style={"fontSize": "0.75rem", "color": "gray"})
            ]
        ),
        # Bekerja Card
        html.Div(
            style={"flex": "1 1 180px", "backgroundColor": COLORS["card_bg"], "padding": "15px", "borderRadius": "8px", "boxShadow": "0 2px 4px rgba(0,0,0,0.05)", "borderLeft": "5px solid #DAA520", "textAlign": "center"},
            children=[
                html.Div("💼 BEKERJA", style={"fontSize": "0.85rem", "fontWeight": "bold", "color": COLORS["gold"]}),
                html.Div(f"{pct_bekerja:.1f}%", style={"fontSize": "1.8rem", "fontWeight": "bold", "color": COLORS["gold"], "margin": "5px 0"}),
                html.Div(f"{bekerja_count} Alumni", style={"fontSize": "0.75rem", "color": "gray"})
            ]
        ),
        # Wirausaha Card
        html.Div(
            style={"flex": "1 1 180px", "backgroundColor": COLORS["card_bg"], "padding": "15px", "borderRadius": "8px", "boxShadow": "0 2px 4px rgba(0,0,0,0.05)", "borderLeft": "5px solid #32CD32", "textAlign": "center"},
            children=[
                html.Div("🚀 WIRAUSAHA", style={"fontSize": "0.85rem", "fontWeight": "bold", "color": "#32CD32"}),
                html.Div(f"{pct_wirausaha:.1f}%", style={"fontSize": "1.8rem", "fontWeight": "bold", "color": "#32CD32", "margin": "5px 0"}),
                html.Div(f"{wirausaha_count} Alumni", style={"fontSize": "0.75rem", "color": "gray"})
            ]
        )
    ]

    # --- FIG 1: PIE KARIER ---
    if total_alumni > 0:
        karier_counts = df_filtered["Karier"].value_counts().reset_index()
        karier_counts.columns = ["Karier", "Jumlah"]
        fig_pie = px.pie(
            karier_counts,
            values="Jumlah",
            names="Karier",
            color_discrete_sequence=["#8B0000", "#DAA520", "#32CD32", "#808080"],
            hole=0.4
        )
        fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300, showlegend=True, legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))
    else:
        fig_pie = px.pie(title="Tidak ada data")

    # --- FIG 2: BAR UNIVERSITAS ---
    kuliah_only = df_filtered[
        (df_filtered["Karier"] == "KULIAH") & 
        (~df_filtered["Universitas/Instansi/Perusahaan"].isin(["-", "_", "secret", ""]))
    ]
    if len(kuliah_only) > 0:
        univ_counts = kuliah_only["Universitas/Instansi/Perusahaan"].value_counts().reset_index()
        univ_counts.columns = ["Universitas", "Jumlah Alumni"]
        total_kuliah_valid = univ_counts["Jumlah Alumni"].sum()
        univ_counts["Persentase"] = (univ_counts["Jumlah Alumni"] / total_kuliah_valid) * 100
        
        # Ambil 8 Perguruan Tinggi Teratas
        top_univ = univ_counts.head(8).sort_values(by="Jumlah Alumni", ascending=True)
        
        fig_bar = px.bar(
            top_univ,
            x="Jumlah Alumni",
            y="Universitas",
            orientation="h",
            color_discrete_sequence=["#DAA520"],
            text=top_univ.apply(lambda row: f"{row['Jumlah Alumni']} ({row['Persentase']:.1f}%)", axis=1)
        )
        fig_bar.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300, xaxis_title="Jumlah Alumni", yaxis_title="")
        fig_bar.update_traces(textposition="inside")
    else:
        fig_bar = px.bar(title="Pilih kategori KULIAH untuk menampilkan universitas.")

    table_data = df_filtered.to_dict("records")
    
    return table_data, kpi_cards, fig_pie, fig_bar, sync_msg

# Menjalankan aplikasi
if __name__ == "__main__":
    app.run_server(debug=True)
