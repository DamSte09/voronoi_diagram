"""
Interaktywny generator diagramu Voronoi (algorytm Fortune'a).

Dwa tryby pracy:
  * Płaszczyzna XY  – wykres matplotlib, punkty ręczne lub losowe,
  * Mapa świata     – mapa Folium, punkty geograficzne (klikanie, ręcznie, losowo).

W obu trybach punkty można zapisać do / wczytać z pliku CSV (separator ';').

Uruchomienie (z katalogu głównego projektu):
    streamlit run src/streamlit_app/app.py
"""

from __future__ import annotations

import io
import sys
from dataclasses import dataclass
from pathlib import Path

import folium
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from folium import plugins
from matplotlib.collections import LineCollection
from streamlit_folium import st_folium

# Pozwala uruchamiać aplikację z dowolnego katalogu (import pakietu `src`).
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithms.fortune import compute_fortune  # noqa: E402


# --------------------------------------------------------------------------- #
# Stałe
# --------------------------------------------------------------------------- #
PLANE = "plane"
MAP = "map"
MODE_LABELS = {PLANE: "📊 Płaszczyzna XY", MAP: "🌍 Mapa świata"}

KM_PER_DEG = 111.0                 # ~długość 1° szerokości geograficznej
DEFAULT_MAP_CENTER = (52.0, 19.0)  # Polska
POLAND_BOUNDS = {"lat": (49.0, 54.5), "lon": (14.0, 24.0)}
MIN_POINTS = 3
CSV_SEP = ";"

EXAMPLE_CITIES = [
    ("Warszawa", 52.2297, 21.0122),
    ("Kraków", 50.0647, 19.9450),
    ("Gdańsk", 54.3520, 18.6466),
    ("Wrocław", 51.1079, 17.0385),
    ("Poznań", 52.4064, 16.9252),
    ("Łódź", 51.7592, 19.4560),
    ("Szczecin", 53.4285, 14.5528),
    ("Lublin", 51.2465, 22.5684),
]


# --------------------------------------------------------------------------- #
# Wynik obliczeń
# --------------------------------------------------------------------------- #
@dataclass
class VoronoiResult:
    """Gotowy do narysowania wynik algorytmu (niezależny od struktury DCEL)."""

    segments: list[tuple[tuple[float, float], tuple[float, float]]]
    vertices: list[tuple[float, float]]
    n_faces: int
    n_internal_vertices: int
    projection_center: tuple[float, float] | None = None  # tylko tryb mapy


# --------------------------------------------------------------------------- #
# Stan sesji
# --------------------------------------------------------------------------- #
def init_state() -> None:
    defaults = {
        "mode": PLANE,
        "plane_points": [],          # [[x, y], ...]
        "geo_points": [],            # [[lat, lon, nazwa], ...]
        "results": {PLANE: None, MAP: None},
        "pending_click": None,       # (lat, lon) ostatniego kliknięcia na mapie
        "last_click": None,
        "auto_generate": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def mode() -> str:
    return st.session_state.mode


def points_key(m: str | None = None) -> str:
    return "plane_points" if (m or mode()) == PLANE else "geo_points"


def get_points(m: str | None = None) -> list:
    return st.session_state[points_key(m)]


def set_points(points: list, m: str | None = None) -> None:
    st.session_state[points_key(m)] = points
    invalidate(m)


def add_point(point: list, m: str | None = None) -> None:
    get_points(m).append(point)
    invalidate(m)


def invalidate(m: str | None = None) -> None:
    """Każda zmiana punktów unieważnia diagram w danym trybie."""
    st.session_state.results[m or mode()] = None


def get_result() -> VoronoiResult | None:
    return st.session_state.results[mode()]


# --------------------------------------------------------------------------- #
# Geometria / projekcja
# --------------------------------------------------------------------------- #
def lat_lon_to_xy(lat: float, lon: float, center: tuple[float, float]) -> list[float]:
    """Projekcja równoodległościowa (equirectangular) wokół `center`, wynik w km."""
    c_lat, c_lon = center
    x = (lon - c_lon) * KM_PER_DEG * np.cos(np.radians(c_lat))
    y = (lat - c_lat) * KM_PER_DEG
    return [float(x), float(y)]


def xy_to_lat_lon(x: float, y: float, center: tuple[float, float]) -> tuple[float, float]:
    c_lat, c_lon = center
    lat = c_lat + y / KM_PER_DEG
    lon = c_lon + x / (KM_PER_DEG * np.cos(np.radians(c_lat)))
    return float(lat), float(lon)


def geo_center(geo_points: list) -> tuple[float, float]:
    if not geo_points:
        return DEFAULT_MAP_CENTER
    return (float(np.mean([p[0] for p in geo_points])),
            float(np.mean([p[1] for p in geo_points])))


def unique_xy(points: list[list[float]]) -> list[list[float]]:
    """Usuwa duplikaty – powtarzające się punkty psują algorytm Fortune'a."""
    seen, out = set(), []
    for x, y in points:
        key = (round(x, 9), round(y, 9))
        if key not in seen:
            seen.add(key)
            out.append([float(x), float(y)])
    return out


# --------------------------------------------------------------------------- #
# Algorytm
# --------------------------------------------------------------------------- #
def dcel_to_result(dcel, center=None) -> VoronoiResult:
    segments, seen = [], set()
    for he in dcel.half_edges:
        twin = he.twin
        if he.origin is None or twin is None or twin.origin is None:
            continue
        edge_id = frozenset((id(he), id(twin)))
        if edge_id in seen:
            continue
        seen.add(edge_id)
        segments.append(((he.origin.x, he.origin.y), (twin.origin.x, twin.origin.y)))

    vertices = [(v.x, v.y) for v in dcel.vertices]
    # Atrybut `internal` nie istnieje w każdej wersji DCEL – bezpieczny odczyt.
    n_internal = sum(1 for v in dcel.vertices if getattr(v, "internal", True))

    return VoronoiResult(
        segments=segments,
        vertices=vertices,
        n_faces=len(dcel.faces),
        n_internal_vertices=n_internal,
        projection_center=center,
    )


def generate_voronoi() -> bool:
    """Liczy diagram dla bieżącego trybu. Zwraca True przy sukcesie."""
    pts = get_points()
    center = None

    if mode() == MAP:
        center = geo_center(pts)
        xy = [lat_lon_to_xy(p[0], p[1], center) for p in pts]
    else:
        xy = [[p[0], p[1]] for p in pts]

    xy = unique_xy(xy)
    if len(xy) < MIN_POINTS:
        st.error(f"Potrzeba co najmniej {MIN_POINTS} różnych punktów.")
        return False

    try:
        dcel = compute_fortune(xy)
    except Exception as exc:  # błąd algorytmu nie może wywrócić aplikacji
        st.error(f"Błąd podczas generowania diagramu: {exc}")
        return False

    if dcel is None:
        st.error("Algorytm nie zwrócił wyniku.")
        return False

    st.session_state.results[mode()] = dcel_to_result(dcel, center)
    return True


# --------------------------------------------------------------------------- #
# CSV
# --------------------------------------------------------------------------- #
def points_to_csv(points: list, m: str) -> str:
    columns = ["x", "y"] if m == PLANE else ["lat", "lon", "name"]
    return pd.DataFrame(points, columns=columns).to_csv(index=False, sep=CSV_SEP)


def read_csv_flexible(raw: bytes) -> pd.DataFrame:
    """Czyta CSV z ';' lub ',' – z nagłówkiem albo bez."""
    text = raw.decode("utf-8-sig")
    for sep in (CSV_SEP, ","):
        df = pd.read_csv(io.StringIO(text), sep=sep, header=None, dtype=str,
                         skipinitialspace=True)
        if df.shape[1] >= 2:
            return df
    raise ValueError("Plik musi mieć co najmniej 2 kolumny (separator ';' lub ',').")


def csv_to_points(raw: bytes, m: str) -> list:
    df = read_csv_flexible(raw)
    a = pd.to_numeric(df[0].str.strip().str.strip('"'), errors="coerce")
    b = pd.to_numeric(df[1].str.strip().str.strip('"'), errors="coerce")
    valid = a.notna() & b.notna()  # odrzuca nagłówek i błędne wiersze

    if m == PLANE:
        return [[float(x), float(y)] for x, y in zip(a[valid], b[valid])]

    names = df[2] if df.shape[1] > 2 else pd.Series([None] * len(df))
    points = []
    for lat, lon, name in zip(a[valid], b[valid], names[valid]):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        name = str(name).strip().strip('"') if isinstance(name, str) and name.strip() else None
        points.append([float(lat), float(lon), name or f"Punkt {len(points) + 1}"])
    return points


# --------------------------------------------------------------------------- #
# Rysowanie – płaszczyzna
# --------------------------------------------------------------------------- #
def plot_plane(points: list, result: VoronoiResult | None, show_vertices: bool,
               show_labels: bool):
    fig, ax = plt.subplots(figsize=(9, 9))

    if points:
        arr = np.asarray(points, dtype=float)
        span = max(np.ptp(arr[:, 0]), np.ptp(arr[:, 1]), 1.0)
        margin = 0.15 * span
        ax.set_xlim(arr[:, 0].min() - margin, arr[:, 0].max() + margin)
        ax.set_ylim(arr[:, 1].min() - margin, arr[:, 1].max() + margin)

        if result:
            ax.add_collection(LineCollection(result.segments, colors="forestgreen",
                                             linewidths=1.5, zorder=1,
                                             label="Krawędzie Voronoi"))
            if show_vertices and result.vertices:
                vx, vy = zip(*result.vertices)
                ax.scatter(vx, vy, c="red", s=18, zorder=2, label="Wierzchołki Voronoi")

        ax.scatter(arr[:, 0], arr[:, 1], c="royalblue", s=70, zorder=3,
                   edgecolors="white", linewidths=0.8, label="Punkty generujące")

        if show_labels:
            for i, (x, y) in enumerate(arr, start=1):
                ax.annotate(str(i), (x, y), xytext=(5, 5), textcoords="offset points",
                            fontsize=8, color="darkblue")
        ax.legend(loc="upper right", frameon=True)
    else:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)

    ax.set_aspect("equal")
    ax.set_title("Diagram Voronoi" if result else "Rozmieszczenie punktów", fontsize=14)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------- #
# Rysowanie – mapa
# --------------------------------------------------------------------------- #
def build_map(geo_points: list, result: VoronoiResult | None,
              show_vertices: bool) -> folium.Map:
    fmap = folium.Map(location=geo_center(geo_points), zoom_start=6,
                      tiles="OpenStreetMap", control_scale=True)

    if result and result.projection_center:
        c = result.projection_center
        edges = folium.FeatureGroup(name="Krawędzie Voronoi")
        for (x1, y1), (x2, y2) in result.segments:
            folium.PolyLine([xy_to_lat_lon(x1, y1, c), xy_to_lat_lon(x2, y2, c)],
                            color="green", weight=2, opacity=0.8).add_to(edges)
        edges.add_to(fmap)

        if show_vertices:
            verts = folium.FeatureGroup(name="Wierzchołki Voronoi")
            for x, y in result.vertices:
                folium.CircleMarker(xy_to_lat_lon(x, y, c), radius=3, color="red",
                                    fill=True, fill_opacity=0.8).add_to(verts)
            verts.add_to(fmap)

    sites = folium.FeatureGroup(name="Punkty generujące")
    for lat, lon, name in geo_points:
        folium.Marker(
            [lat, lon],
            tooltip=name,
            popup=folium.Popup(f"<b>{name}</b><br>{lat:.4f}, {lon:.4f}", max_width=200),
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(sites)
    sites.add_to(fmap)

    if len(geo_points) >= 2:
        lats = [p[0] for p in geo_points]
        lons = [p[1] for p in geo_points]
        fmap.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=(30, 30))

    plugins.Fullscreen().add_to(fmap)
    folium.LayerControl(collapsed=True).add_to(fmap)
    return fmap


# --------------------------------------------------------------------------- #
# UI – pasek boczny
# --------------------------------------------------------------------------- #
def sidebar_add_plane_point() -> None:
    st.subheader("➕ Dodaj punkt (XY)")
    with st.form("add_xy", clear_on_submit=False, border=False):
        c1, c2 = st.columns(2)
        x = c1.number_input("X", value=5.0, step=0.1, format="%.2f")
        y = c2.number_input("Y", value=5.0, step=0.1, format="%.2f")
        if st.form_submit_button("Dodaj punkt", width="stretch"):
            add_point([float(x), float(y)])
            st.toast(f"Dodano punkt ({x:.2f}, {y:.2f})")


def sidebar_add_geo_point() -> None:
    st.subheader("➕ Dodaj punkt (geo)")
    with st.form("add_geo", clear_on_submit=False, border=False):
        lat = st.number_input("Szerokość (lat)", value=52.2297, min_value=-90.0,
                              max_value=90.0, step=0.01, format="%.4f")
        lon = st.number_input("Długość (lon)", value=21.0122, min_value=-180.0,
                              max_value=180.0, step=0.01, format="%.4f")
        name = st.text_input("Nazwa", placeholder=f"Punkt {len(get_points()) + 1}")
        if st.form_submit_button("Dodaj punkt", width="stretch"):
            label = name.strip() or f"Punkt {len(get_points()) + 1}"
            add_point([float(lat), float(lon), label])
            st.toast(f"Dodano {label}")

    if st.button("🏙️ Wstaw przykładowe miasta", width="stretch"):
        set_points([[lat, lon, n] for n, lat, lon in EXAMPLE_CITIES])
        st.rerun()


def sidebar_random() -> None:
    st.subheader("🎲 Losowe punkty")
    n = st.number_input("Liczba punktów", min_value=1, max_value=200, value=10)

    if mode() == PLANE:
        c1, c2 = st.columns(2)
        lo = c1.number_input("Min", value=0.0, step=1.0)
        hi = c2.number_input("Max", value=10.0, step=1.0)
    else:
        st.caption("Zakres: obszar Polski")
        lo = hi = None

    replace = st.checkbox("Zastąp istniejące punkty", value=True)

    if st.button("🎲 Generuj losowe", width="stretch"):
        if mode() == PLANE:
            if hi <= lo:
                st.error("Max musi być większe od Min.")
                return
            new = np.random.uniform(lo, hi, size=(int(n), 2)).round(4).tolist()
        else:
            start = 0 if replace else len(get_points())
            lats = np.random.uniform(*POLAND_BOUNDS["lat"], size=int(n))
            lons = np.random.uniform(*POLAND_BOUNDS["lon"], size=int(n))
            new = [[round(float(a), 4), round(float(b), 4), f"Losowy {start + i + 1}"]
                   for i, (a, b) in enumerate(zip(lats, lons))]

        set_points(new if replace else get_points() + new)
        st.rerun()


def sidebar_point_list() -> None:
    pts = get_points()
    st.subheader(f"📋 Punkty ({len(pts)})")
    if not pts:
        st.caption("Brak punktów.")
        return

    cols = ["X", "Y"] if mode() == PLANE else ["Lat", "Lon", "Nazwa"]
    df = pd.DataFrame(pts, columns=cols)
    df.index = df.index + 1
    st.dataframe(df, width="stretch", height=min(35 * len(df) + 38, 250))

    def label(i: int) -> str:
        p = pts[i]
        if mode() == PLANE:
            return f"{i + 1}: ({p[0]:.2f}, {p[1]:.2f})"
        return f"{i + 1}: {p[2]} ({p[0]:.4f}, {p[1]:.4f})"

    to_remove = st.multiselect("Usuń punkty", options=range(len(pts)), format_func=label)
    c1, c2 = st.columns(2)
    if c1.button("🗑️ Usuń zaznaczone", width="stretch", disabled=not to_remove):
        set_points([p for i, p in enumerate(pts) if i not in set(to_remove)])
        st.rerun()
    if c2.button("🧹 Wyczyść wszystko", width="stretch"):
        set_points([])
        st.session_state.pending_click = None
        st.rerun()


def sidebar_files() -> None:
    st.subheader("💾 Pliki CSV")
    pts = get_points()

    st.download_button(
        "⬇️ Zapisz punkty (CSV)",
        data=points_to_csv(pts, mode()),
        file_name="voronoi_points_xy.csv" if mode() == PLANE else "voronoi_points_geo.csv",
        mime="text/csv",
        width="stretch",
        disabled=not pts,
    )

    fmt = "`x;y`" if mode() == PLANE else "`lat;lon;nazwa`"
    uploaded = st.file_uploader(f"Wczytaj punkty – format {fmt}", type=["csv", "txt"],
                                key=f"uploader_{mode()}")
    if uploaded is not None:
        append = st.checkbox("Dołącz do istniejących", value=False, key=f"append_{mode()}")
        if st.button("📥 Wczytaj plik", width="stretch"):
            try:
                loaded = csv_to_points(uploaded.getvalue(), mode())
            except Exception as exc:
                st.error(f"Nie udało się odczytać pliku: {exc}")
                return
            if not loaded:
                st.warning("W pliku nie znaleziono poprawnych punktów.")
                return
            set_points(get_points() + loaded if append else loaded)
            st.toast(f"Wczytano {len(loaded)} punktów")
            st.rerun()


def sidebar_options() -> tuple[bool, bool]:
    st.subheader("🎨 Widok")
    show_vertices = st.checkbox("Pokaż wierzchołki Voronoi", value=True)
    show_labels = st.checkbox("Numeruj punkty", value=True) if mode() == PLANE else False
    st.checkbox("Generuj diagram automatycznie", key="auto_generate",
                help="Diagram przelicza się przy każdej zmianie punktów.")
    return show_vertices, show_labels


def render_sidebar() -> tuple[bool, bool]:
    with st.sidebar:
        st.header("⚙️ Ustawienia")
        if mode() == PLANE:
            sidebar_add_plane_point()
        else:
            sidebar_add_geo_point()
        st.divider()
        sidebar_random()
        st.divider()
        sidebar_point_list()
        st.divider()
        sidebar_files()
        st.divider()
        return sidebar_options()


# --------------------------------------------------------------------------- #
# UI – część główna
# --------------------------------------------------------------------------- #
def generate_controls() -> None:
    pts = get_points()
    enough = len(pts) >= MIN_POINTS

    if st.session_state.auto_generate and enough and get_result() is None:
        generate_voronoi()

    c1, c2 = st.columns([3, 1])
    if c1.button("🎯 Generuj diagram Voronoi", type="primary",
                 width="stretch", disabled=not enough):
        with st.spinner("Liczę diagram..."):
            if generate_voronoi():
                st.toast("✅ Diagram wygenerowany")
    if c2.button("✖️ Ukryj diagram", width="stretch",
                 disabled=get_result() is None):
        invalidate()
        st.rerun()

    if pts and not enough:
        st.warning(f"Potrzebujesz co najmniej {MIN_POINTS} punktów "
                   f"(masz {len(pts)}).")


def render_plane_view(show_vertices: bool, show_labels: bool) -> None:
    pts = get_points()
    if not pts:
        st.info("👈 Dodaj punkty w panelu bocznym, wygeneruj losowe albo wczytaj CSV.")

    result = get_result()
    fig = plot_plane(pts, result, show_vertices, show_labels)
    st.pyplot(fig, width="stretch")

    if result:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        st.download_button("⬇️ Pobierz diagram (PNG)", data=buf.getvalue(),
                           file_name="voronoi_diagram.png", mime="image/png")
    plt.close(fig)


def handle_map_click(map_state: dict | None) -> None:
    click = (map_state or {}).get("last_clicked")
    if not click or click == st.session_state.last_click:
        return
    st.session_state.last_click = click
    lat, lon = round(click["lat"], 6), round(click["lng"], 6)

    if st.session_state.get("quick_add"):
        add_point([lat, lon, f"Punkt {len(get_points()) + 1}"])
        st.rerun()  # odśwież mapę, by pokazać nowy marker
    else:
        st.session_state.pending_click = (lat, lon)


def render_pending_click_form() -> None:
    """Formularz dodania klikniętego punktu – poza warunkiem 'nowe kliknięcie',
    dzięki czemu przycisk działa także po przeładowaniu strony."""
    pending = st.session_state.pending_click
    if not pending:
        return
    lat, lon = pending
    with st.form("add_clicked"):
        st.markdown(f"**📍 Kliknięto:** {lat:.4f}, {lon:.4f}")
        name = st.text_input("Nazwa punktu", value=f"Punkt {len(get_points()) + 1}")
        c1, c2 = st.columns(2)
        add = c1.form_submit_button("✅ Dodaj punkt", type="primary",
                                    width="stretch")
        cancel = c2.form_submit_button("Anuluj", width="stretch")
    if add:
        add_point([lat, lon, name.strip() or f"Punkt {len(get_points()) + 1}"])
        st.session_state.pending_click = None
        st.rerun()
    if cancel:
        st.session_state.pending_click = None
        st.rerun()


def render_map_view(show_vertices: bool) -> None:
    st.toggle("⚡ Dodawaj punkt od razu po kliknięciu", key="quick_add",
              help="Wyłączone: po kliknięciu pojawi się formularz z nazwą.")

    pts = get_points()
    if not pts:
        st.info("🖱️ Kliknij na mapie, aby dodać punkt, albo użyj panelu bocznego.")

    result = get_result()
    fmap = build_map(pts, result, show_vertices)
    map_state = st_folium(fmap, key="voronoi_map", height=600,
                          use_container_width=True, returned_objects=["last_clicked"])
    handle_map_click(map_state)
    render_pending_click_form()

    if result:
        st.download_button("⬇️ Pobierz mapę (HTML)",
                           data=fmap.get_root().render(),
                           file_name="voronoi_map.html", mime="text/html")


def render_info_panel() -> None:
    st.header("ℹ️ Informacje")
    pts = get_points()
    result = get_result()

    st.metric("Punkty", len(pts))
    if result:
        c1, c2 = st.columns(2)
        c1.metric("Wierzchołki", result.n_internal_vertices)
        c2.metric("Krawędzie", len(result.segments))
        st.metric("Regiony", result.n_faces)
    else:
        st.caption("Diagram nie jest wygenerowany.")

    st.divider()
    st.subheader("📖 Instrukcja")
    if mode() == PLANE:
        st.markdown(
            "1. Dodaj punkty (X, Y) w panelu bocznym\n"
            "2. …albo wygeneruj losowe / wczytaj CSV\n"
            "3. Kliknij **Generuj diagram Voronoi**\n"
            "4. Pobierz punkty (CSV) lub obraz (PNG)\n\n"
            "Format CSV: `x;y` (nagłówek opcjonalny)"
        )
    else:
        st.markdown(
            "1. **Kliknij na mapie**, aby dodać punkt\n"
            "2. …albo dodaj ręcznie, losowo (Polska) lub z CSV\n"
            "3. Kliknij **Generuj diagram Voronoi**\n"
            "4. Pobierz punkty (CSV) lub mapę (HTML)\n\n"
            "Format CSV: `lat;lon;nazwa` (nagłówek opcjonalny)"
        )
        st.caption("Współrzędne są rzutowane na płaszczyznę (projekcja równoodległościowa "
                   "wokół środka punktów) – dokładne dla obszarów rzędu kraju.")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    st.set_page_config(page_title="Diagram Voronoi", page_icon="🗺️", layout="wide")
    init_state()

    st.title("🗺️ Interaktywny generator diagramu Voronoi")
    st.radio("Tryb", options=[PLANE, MAP], format_func=MODE_LABELS.get,
             key="mode", horizontal=True, label_visibility="collapsed")

    show_vertices, show_labels = render_sidebar()

    left, right = st.columns([3, 1])
    with left:
        generate_controls()
        if mode() == PLANE:
            render_plane_view(show_vertices, show_labels)
        else:
            render_map_view(show_vertices)
    with right:
        render_info_panel()

    st.divider()
    st.caption("Interaktywny generator diagramu Voronoi · algorytm Fortune'a · "
               "tryby: płaszczyzna XY i mapa świata")


if __name__ == "__main__":
    main()
