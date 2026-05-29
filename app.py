import unicodedata

import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Fluxo Solar",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_css():
    st.markdown(
        """
        <style>
        /* ── Oculta elementos nativos ── */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header[data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        section[data-testid="stSidebar"] { display: none !important; }

        /* ── Fundo global ── */
        [data-testid="stAppViewContainer"] {
            background-color: #0F172A;
        }

        /* ── Métricas ── */
        [data-testid="stMetric"] {
            background: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1rem 1.25rem;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #94A3B8;
        }
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
            color: #F1F5F9;
        }

        /* ── Barra de pesquisa ── */
        [data-testid="stTextInput"] input {
            background-color: #1E293B !important;
            border: 1px solid #475569 !important;
            border-radius: 8px !important;
            color: #F1F5F9 !important;
            font-size: 0.95rem;
        }
        [data-testid="stTextInput"] input::placeholder { color: #64748B !important; }
        [data-testid="stTextInput"] input:focus {
            border-color: #F97316 !important;
            box-shadow: 0 0 0 2px rgba(249,115,22,0.2) !important;
        }

        /* ── Filtros estilo AutoFiltro ── */
        /* Labels dos selectboxes na linha de filtros */
        [data-testid="stSelectbox"] > label {
            font-size: 0.68rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            color: #64748B !important;
        }
        /* Container do select */
        [data-testid="stSelectbox"] > div > div {
            background-color: #1E293B !important;
            border: 1px solid #334155 !important;
            border-radius: 6px !important;
            font-size: 0.85rem !important;
            transition: border-color 0.2s;
        }
        [data-testid="stSelectbox"] > div > div:focus-within {
            border-color: #F97316 !important;
            box-shadow: 0 0 0 2px rgba(249,115,22,0.15) !important;
        }

        /* ── Animação de entrada ── */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        [data-testid="stVerticalBlock"] { animation: fadeIn 0.35s ease forwards; }

        /* ── Separador ── */
        hr { border-color: #334155; margin: 1rem 0; }

        /* ── Linha divisória entre filtros e tabela ── */
        .filter-divider {
            height: 2px;
            background: linear-gradient(to right, #F97316, transparent);
            border-radius: 2px;
            margin: 4px 0 0 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data() -> pd.DataFrame:
    path = Path(__file__).parent / "clientes.xlsx"
    df = pd.read_excel(path, dtype=str).fillna("")
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    return df


def find_col(df: pd.DataFrame, *candidates: str) -> str | None:
    for candidate in candidates:
        matches = [col for col in df.columns if candidate.lower() in str(col).lower()]
        if matches:
            return matches[0]
    return None


def normalize(text: str) -> str:
    return (
        unicodedata.normalize("NFD", str(text).lower())
        .encode("ascii", "ignore")
        .decode()
    )


def main():
    inject_css()
    df = load_data()

    col_marca = find_col(df, "marca", "inversor", "fabricante") or df.columns[5]
    col_status = find_col(df, "status") or df.columns[6]
    col_cidade = find_col(df, "cidade", "city", "municipio")
    col_nome = find_col(df, "nome", "cliente", "razao")
    col_numero = find_col(df, "número", "numero", "n°", "n ", "cod", "id")

    # ── Título ────────────────────────────────────────────────────────────────
    st.markdown("## ☀️ Fluxo Solar")

    # Placeholder para métricas (calculadas após filtros)
    metrics_placeholder = st.empty()
    st.markdown("---")

    # ── Barra de pesquisa ─────────────────────────────────────────────────────
    search_query = st.text_input(
        "Pesquisar",
        placeholder="🔍   Buscar por marca, número, nome ou cidade...",
        label_visibility="collapsed",
    )

    # ── Linha de filtros (AutoFiltro) ──────────────────────────────────────────
    fc1, fc2, fc3, _gap = st.columns([1.8, 2.5, 1.5, 4.2])

    with fc1:
        marcas_opts = ["Todas as marcas"] + sorted([m for m in df[col_marca].unique() if m])
        marca_sel = st.selectbox("Marca ▼", options=marcas_opts)

    with fc2:
        if col_cidade:
            cidades_opts = ["Todas as cidades"] + sorted([c for c in df[col_cidade].unique() if c])
            cidade_sel = st.selectbox("Cidade ▼", options=cidades_opts)
        else:
            cidade_sel = "Todas as cidades"

    with fc3:
        status_opts = ["Todos os status"] + sorted([s for s in df[col_status].unique() if s])
        status_sel = st.selectbox("Status ▼", options=status_opts)

    # Divisória laranja abaixo dos filtros (visual de cabeçalho de planilha)
    st.markdown('<div class="filter-divider"></div>', unsafe_allow_html=True)

    # ── Aplicar filtros ────────────────────────────────────────────────────────
    filtered = df.copy()

    if marca_sel != "Todas as marcas":
        filtered = filtered[filtered[col_marca].str.lower() == marca_sel.lower()]

    if col_cidade and cidade_sel != "Todas as cidades":
        filtered = filtered[filtered[col_cidade].str.lower() == cidade_sel.lower()]

    if status_sel != "Todos os status":
        filtered = filtered[filtered[col_status] == status_sel]

    if search_query.strip():
        q = normalize(search_query.strip())
        search_cols = [c for c in [col_marca, col_numero, col_nome, col_cidade] if c]
        mask = pd.Series(False, index=filtered.index)
        for col in search_cols:
            mask |= filtered[col].apply(normalize).str.contains(q, na=False)
        filtered = filtered[mask]

    # ── Preenche métricas com dados filtrados ─────────────────────────────────
    total = len(filtered)
    online = int((filtered[col_status] == "On-line").sum())
    offline = int((filtered[col_status] == "Off-line").sum())
    alarme = int((filtered[col_status] == "Alarme").sum())

    with metrics_placeholder.container():
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total de Clientes", total)
        c2.metric("On-line", online, delta=online, delta_color="normal")
        c3.metric("Off-line", offline, delta=-offline if offline else 0, delta_color="inverse")
        c4.metric("Alarme", alarme, delta=-alarme if alarme else 0, delta_color="inverse")

    # ── Tabela ────────────────────────────────────────────────────────────────
    st.dataframe(filtered, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
