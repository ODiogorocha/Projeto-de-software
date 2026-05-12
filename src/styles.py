def carregar_estilos():
    return """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a, #111827, #1e293b);
    }

    /* Container dos Gráficos com efeito de vidro */
    .stPlotlyChart {
        background: rgba(30, 41, 59, 0.4);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    [data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 20px;
        border-radius: 18px;
        backdrop-filter: blur(10px);
    }

    .stTabs [role="tab"] {
        background-color: rgba(30,41,59,0.6);
        border-radius: 12px;
        margin-right: 8px;
        padding: 10px 20px;
        color: white;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    h1, h2, h3 { color: white; font-weight: 700; }
    </style>
    """