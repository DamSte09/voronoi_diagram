
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import io
import csv
import sys
import os

# Importy modułów projektu
# Sprawdź czy moduły są dostępne lokalnie lub w uploads
try:
    from src.structures.QE import EventsQueue, SiteEvent, CircleEvent
    from src.structures.BST import Root, Node, Leaf
    from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
    from src.algorithms.site import handle_site_event
    from src.algorithms.circle import handle_circle_event
except ImportError:
    # Jeśli nie ma lokalnie, spróbuj z uploads
    sys.path.insert(0, '/mnt/user-data/uploads')
    from src.structures.QE import EventsQueue, SiteEvent, CircleEvent
    from src.structures.BST import Root, Node, Leaf
    from src.structures.DCEL import DCEL, Vertex, HalfEdge, Face
    from src.algorithms.site import handle_site_event
    from src.algorithms.circle import handle_circle_event
import folium
from folium import plugins
from streamlit_folium import st_folium


# Konfiguracja strony
st.set_page_config(
    page_title="Interaktywny Diagram Voronoi",
    page_icon="🗺️",
    layout="wide"
)

# Inicjalizacja session state
if 'points' not in st.session_state:
    st.session_state.points = []
if 'diagram_generated' not in st.session_state:
    st.session_state.diagram_generated = False
if 'dcel' not in st.session_state:
    st.session_state.dcel = None
if 'map_mode' not in st.session_state:
    st.session_state.map_mode = 'matplotlib'  # 'matplotlib' or 'folium'
if 'geo_points' not in st.session_state:
    st.session_state.geo_points = []  # [(lat, lon, name), ...]
if 'map_clicks' not in st.session_state:
    st.session_state.map_clicks = []

def lat_lon_to_xy(lat, lon, center_lat=52.0, center_lon=19.0):
    """Konwertuje współrzędne geograficzne na płaszczyznę XY dla algorytmu Voronoi"""
    # Przybliżona projekcja Mercatora dla małych obszarów
    # 1 stopień szerokości ≈ 111 km
    # 1 stopień długości ≈ 111 * cos(lat) km
    x = (lon - center_lon) * 111.0 * np.cos(np.radians(center_lat))
    y = (lat - center_lat) * 111.0
    return [x, y]

def xy_to_lat_lon(x, y, center_lat=52.0, center_lon=19.0):
    """Konwertuje współrzędne XY z powrotem na lat/lon"""
    lat = center_lat + (y / 111.0)
    lon = center_lon + (x / (111.0 * np.cos(np.radians(center_lat))))
    return lat, lon

def plot_voronoi_diagram(points, dcel=None, show_voronoi=True):
    """Rysuje punkty i opcjonalnie diagram Voronoi w matplotlib"""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    if points:
        px, py = zip(*points) if len(points) > 0 else ([], [])
        
        if show_voronoi and dcel:
            seen_edges = set()
            for he in dcel.half_edges:
                if he.origin and he.twin and he.twin.origin:
                    edge_id = tuple(sorted([id(he), id(he.twin)]))
                    if edge_id not in seen_edges:
                        x_vals = [he.origin.x, he.twin.origin.x]
                        y_vals = [he.origin.y, he.twin.origin.y]
                        ax.plot(x_vals, y_vals, color="forestgreen", linewidth=1.5, zorder=1)
                        seen_edges.add(edge_id)
            
            vx = [v.x for v in dcel.vertices]
            vy = [v.y for v in dcel.vertices]
            ax.scatter(vx, vy, c="red", s=20, label="Wierzchołki Voronoi", zorder=2)
        
        ax.scatter(px, py, c="blue", s=100, marker="o", label="Punkty generujące", zorder=3)
        
        for i, (x, y) in enumerate(points):
            ax.annotate(f'{i+1}', (x, y), xytext=(5, 5), textcoords='offset points', 
                       fontsize=8, color='darkblue')
        
        if px and py:
            margin = 1
            ax.set_xlim(min(px) - margin, max(px) + margin)
            ax.set_ylim(min(py) - margin, max(py) + margin)
    else:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
    
    ax.set_aspect("equal")
    ax.set_title("Diagram Voronoi" if show_voronoi else "Rozmieszczenie punktów", fontsize=14)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", frameon=True, shadow=True)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    
    return fig

def create_folium_map(geo_points, dcel=None, show_voronoi=True, center_lat=52.0, center_lon=19.0):
    """Tworzy mapę Folium z punktami i opcjonalnie diagramem Voronoi"""
    
    # Wyznacz centrum mapy
    if geo_points:
        lats = [p[0] for p in geo_points]
        lons = [p[1] for p in geo_points]
        center_lat = np.mean(lats)
        center_lon = np.mean(lons)
        zoom_start = 6
    else:
        zoom_start = 5
    
    # Stwórz mapę
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles='OpenStreetMap'
    )
    
    # Dodaj możliwość klikania na mapę
    m.add_child(folium.LatLngPopup())
    
    # Rysuj diagram Voronoi jeśli istnieje
    if show_voronoi and dcel and geo_points:
        # Rysuj krawędzie Voronoi
        seen_edges = set()
        for he in dcel.half_edges:
            if he.origin and he.twin and he.twin.origin:
                edge_id = tuple(sorted([id(he), id(he.twin)]))
                if edge_id not in seen_edges:
                    # Konwertuj XY z powrotem na lat/lon
                    lat1, lon1 = xy_to_lat_lon(he.origin.x, he.origin.y, center_lat, center_lon)
                    lat2, lon2 = xy_to_lat_lon(he.twin.origin.x, he.twin.origin.y, center_lat, center_lon)
                    
                    folium.PolyLine(
                        locations=[[lat1, lon1], [lat2, lon2]],
                        color='green',
                        weight=2,
                        opacity=0.7
                    ).add_to(m)
                    seen_edges.add(edge_id)
        
        # Rysuj wierzchołki Voronoi
        for v in dcel.vertices:
            lat, lon = xy_to_lat_lon(v.x, v.y, center_lat, center_lon)
            folium.CircleMarker(
                location=[lat, lon],
                radius=3,
                color='red',
                fill=True,
                fillColor='red',
                fillOpacity=0.7,
                popup='Wierzchołek Voronoi'
            ).add_to(m)
    
    # Dodaj markery dla punktów generujących
    for i, point in enumerate(geo_points):
        lat, lon = point[0], point[1]
        name = point[2] if len(point) > 2 else f"Punkt {i+1}"
        
        folium.Marker(
            location=[lat, lon],
            popup=f"<b>{name}</b><br>Lat: {lat:.4f}<br>Lon: {lon:.4f}",
            tooltip=name,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
        
        # Dodaj okrąg wokół punktu
        if show_voronoi:
            folium.Circle(
                location=[lat, lon],
                radius=5000,  # 5km
                color='blue',
                fill=False,
                opacity=0.3
            ).add_to(m)
    
    # Dodaj plugin do pełnego ekranu
    plugins.Fullscreen().add_to(m)
    
    # Dodaj kontrolkę warstw
    folium.LayerControl().add_to(m)
    
    return m

def generate_voronoi(points):
    """Generuje diagram Voronoi dla podanych punktów"""
    if len(points) < 3:
        return None
    
    try:
        Q = EventsQueue(points)    
        root = Root()
        dcel = DCEL()
        sweepline = None
        
        while Q.all_events:
            event = Q.all_events.pop(0)
        
            if isinstance(event, SiteEvent):
                sweepline = event.centre[1]
                root = handle_site_event(root, event, queue=Q, dcel=dcel, y_sweep=sweepline)
            elif isinstance(event, CircleEvent) and event.is_valid:
                sweepline = event.centre[1]
                root = handle_circle_event(event, sweepline, root, Q, dcel)
            else:
                continue

        dcel.close_halfedges(points)
        return dcel
    except Exception as e:
        st.error(f"Błąd podczas generowania diagramu: {str(e)}")
        return None

def save_points_to_csv(points, mode='matplotlib'):
    """Zapisuje punkty do pliku CSV"""
    if mode == 'matplotlib':
        df = pd.DataFrame(points, columns=['x', 'y'])
    else:  # folium
        df = pd.DataFrame(points, columns=['lat', 'lon', 'name'])
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, sep=';')
    return csv_buffer.getvalue()

def load_points_from_csv(uploaded_file, mode='matplotlib'):
    """Wczytuje punkty z pliku CSV"""
    try:
        content = uploaded_file.getvalue().decode('utf-8')
        reader = csv.reader(io.StringIO(content), delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        points = []
        header = next(reader, None)  # Skip header
        
        for row in reader:
            if mode == 'matplotlib' and len(row) >= 2:
                try:
                    points.append([float(row[0]), float(row[1])])
                except (ValueError, IndexError):
                    continue
            elif mode == 'folium' and len(row) >= 2:
                try:
                    lat = float(row[0])
                    lon = float(row[1])
                    name = str(row[2]) if len(row) > 2 else f"Punkt {len(points)+1}"
                    points.append([lat, lon, name])
                except (ValueError, IndexError):
                    continue
        return points
    except Exception as e:
        st.error(f"Błąd podczas wczytywania pliku: {str(e)}")
        return []

# Tytuł aplikacji
st.title("🗺️ Interaktywny Generator Diagramu Voronoi")
st.markdown("---")

# Wybór trybu
col_mode1, col_mode2 = st.columns(2)
with col_mode1:
    if st.button("📊 Tryb Wykres (Matplotlib)", use_container_width=True, 
                 type="primary" if st.session_state.map_mode == 'matplotlib' else "secondary"):
        st.session_state.map_mode = 'matplotlib'
        st.session_state.diagram_generated = False
        st.rerun()

with col_mode2:
    if st.button("🌍 Tryb Mapa Świata (Folium)", use_container_width=True,
                 type="primary" if st.session_state.map_mode == 'folium' else "secondary"):
        st.session_state.map_mode = 'folium'
        st.session_state.diagram_generated = False
        st.rerun()

st.markdown("---")

# Sidebar z kontrolkami
with st.sidebar:
    st.header("⚙️ Ustawienia")
    
    # Wyświetl aktualny tryb
    mode_icon = "📊" if st.session_state.map_mode == 'matplotlib' else "🌍"
    mode_name = "Wykres" if st.session_state.map_mode == 'matplotlib' else "Mapa Świata"
    st.info(f"{mode_icon} **Aktualny tryb:** {mode_name}")
    
    st.markdown("---")
    
    # Sekcja dodawania punktów - różna dla każdego trybu
    if st.session_state.map_mode == 'matplotlib':
        st.subheader("➕ Dodaj punkt (XY)")
        col1, col2 = st.columns(2)
        with col1:
            x_coord = st.number_input("X:", value=5.0, step=0.1, format="%.2f", key="x_matplotlib")
        with col2:
            y_coord = st.number_input("Y:", value=5.0, step=0.1, format="%.2f", key="y_matplotlib")
        
        if st.button("➕ Dodaj punkt XY", use_container_width=True):
            st.session_state.points.append([x_coord, y_coord])
            st.session_state.diagram_generated = False
            st.success(f"Dodano punkt ({x_coord:.2f}, {y_coord:.2f})")
    else:  # folium mode
        st.subheader("➕ Dodaj punkt (Geo)")
        lat_coord = st.number_input("Szerokość (Lat):", value=52.2297, min_value=-90.0, max_value=90.0, 
                                     step=0.01, format="%.4f", key="lat_folium")
        lon_coord = st.number_input("Długość (Lon):", value=21.0122, min_value=-180.0, max_value=180.0, 
                                     step=0.01, format="%.4f", key="lon_folium")
        point_name = st.text_input("Nazwa punktu:", value=f"Punkt {len(st.session_state.geo_points)+1}", 
                                   key="name_folium")
        
        if st.button("➕ Dodaj punkt Geo", use_container_width=True):
            st.session_state.geo_points.append([lat_coord, lon_coord, point_name])
            st.session_state.diagram_generated = False
            st.success(f"Dodano {point_name} ({lat_coord:.4f}, {lon_coord:.4f})")
    
    # Generowanie losowych punktów
    st.subheader("🎲 Losowe punkty")
    num_random = st.number_input("Liczba punktów:", min_value=1, max_value=50, value=10, key="num_random")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 Generuj", use_container_width=True):
            if st.session_state.map_mode == 'matplotlib':
                random_points = np.random.uniform(0, 10, size=(num_random, 2)).tolist()
                st.session_state.points = random_points
            else:  # folium - generuj punkty w Polsce/Europie
                # Zakres dla Polski: lat 49-54.5, lon 14-24
                random_lats = np.random.uniform(49.0, 54.5, size=num_random)
                random_lons = np.random.uniform(14.0, 24.0, size=num_random)
                st.session_state.geo_points = [[lat, lon, f"Losowy {i+1}"] 
                                               for i, (lat, lon) in enumerate(zip(random_lats, random_lons))]
            st.session_state.diagram_generated = False
            st.success(f"Wygenerowano {num_random} punktów")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Wyczyść", use_container_width=True):
            st.session_state.points = []
            st.session_state.geo_points = []
            st.session_state.diagram_generated = False
            st.session_state.dcel = None
            st.success("Usunięto wszystkie punkty")
            st.rerun()
    
    st.markdown("---")
    
    # Zarządzanie punktami
    current_points = st.session_state.points if st.session_state.map_mode == 'matplotlib' else st.session_state.geo_points
    
    if current_points:
        st.subheader("📋 Lista punktów")
        
        if st.session_state.map_mode == 'matplotlib':
            points_df = pd.DataFrame(current_points, columns=['X', 'Y'])
        else:
            points_df = pd.DataFrame(current_points, columns=['Lat', 'Lon', 'Nazwa'])
        
        points_df.index = points_df.index + 1
        st.dataframe(points_df, use_container_width=True)
        
        # Usuwanie punktu
        if st.session_state.map_mode == 'matplotlib':
            point_to_remove = st.selectbox(
                "Wybierz punkt do usunięcia:",
                options=range(len(current_points)),
                format_func=lambda i: f"Punkt {i+1}: ({current_points[i][0]:.2f}, {current_points[i][1]:.2f})"
            )
        else:
            point_to_remove = st.selectbox(
                "Wybierz punkt do usunięcia:",
                options=range(len(current_points)),
                format_func=lambda i: f"{current_points[i][2]}: ({current_points[i][0]:.4f}, {current_points[i][1]:.4f})"
            )
        
        if st.button("🗑️ Usuń wybrany punkt", use_container_width=True):
            if st.session_state.map_mode == 'matplotlib':
                st.session_state.points.pop(point_to_remove)
            else:
                st.session_state.geo_points.pop(point_to_remove)
            st.session_state.diagram_generated = False
            st.success("Usunięto punkt")
            st.rerun()
    
    st.markdown("---")
    
    # Operacje na plikach
    st.subheader("💾 Pliki")
    
    # Zapisywanie
    if current_points:
        csv_data = save_points_to_csv(current_points, st.session_state.map_mode)
        filename = "voronoi_points_xy.csv" if st.session_state.map_mode == 'matplotlib' else "voronoi_points_geo.csv"
        st.download_button(
            label="⬇️ Pobierz punkty (CSV)",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )
    
    # Wczytywanie
    uploaded_file = st.file_uploader("⬆️ Wczytaj punkty (CSV)", type=['csv'])
    if uploaded_file is not None:
        loaded_points = load_points_from_csv(uploaded_file, st.session_state.map_mode)
        if loaded_points:
            if st.session_state.map_mode == 'matplotlib':
                st.session_state.points = loaded_points
            else:
                st.session_state.geo_points = loaded_points
            st.session_state.diagram_generated = False
            st.success(f"Wczytano {len(loaded_points)} punktów")
            st.rerun()

# Główna część aplikacji
col_left, col_right = st.columns([2, 1])

with col_left:
    st.header("📊 Wizualizacja" if st.session_state.map_mode == 'matplotlib' else "🌍 Mapa")
    
    # Przycisk generowania diagramu
    current_points = st.session_state.points if st.session_state.map_mode == 'matplotlib' else st.session_state.geo_points
    
    if len(current_points) >= 3:
        if st.button("🎯 Generuj Diagram Voronoi", type="primary", use_container_width=True):
            with st.spinner("Generowanie diagramu Voronoi..."):
                # Konwersja punktów geo na XY jeśli potrzeba
                if st.session_state.map_mode == 'folium':
                    center_lat = np.mean([p[0] for p in current_points])
                    center_lon = np.mean([p[1] for p in current_points])
                    xy_points = [lat_lon_to_xy(p[0], p[1], center_lat, center_lon) for p in current_points]
                else:
                    xy_points = current_points
                
                dcel = generate_voronoi(xy_points)
                if dcel:
                    st.session_state.dcel = dcel
                    st.session_state.diagram_generated = True
                    st.success("✅ Diagram wygenerowany!")
    elif current_points:
        st.warning("⚠️ Potrzebujesz co najmniej 3 punktów do wygenerowania diagramu Voronoi")
    
    # Wyświetlanie diagramu
    if st.session_state.map_mode == 'matplotlib':
        if st.session_state.points:
            show_voronoi = st.session_state.diagram_generated and st.session_state.dcel is not None
            fig = plot_voronoi_diagram(
                st.session_state.points, 
                st.session_state.dcel if show_voronoi else None,
                show_voronoi
            )
            st.pyplot(fig)
            
            # Opcja zapisu obrazu
            if show_voronoi:
                buf = io.BytesIO()
                fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                buf.seek(0)
                st.download_button(
                    label="⬇️ Pobierz diagram (PNG)",
                    data=buf,
                    file_name="voronoi_diagram.png",
                    mime="image/png"
                )
        else:
            st.info("👆 Dodaj punkty używając panelu po lewej stronie")
    
    else:  # folium mode
        if st.session_state.geo_points:
            show_voronoi = st.session_state.diagram_generated and st.session_state.dcel is not None
            
            # Przygotuj centrum mapy
            center_lat = np.mean([p[0] for p in st.session_state.geo_points])
            center_lon = np.mean([p[1] for p in st.session_state.geo_points])
            
            folium_map = create_folium_map(
                st.session_state.geo_points,
                st.session_state.dcel if show_voronoi else None,
                show_voronoi,
                center_lat,
                center_lon
            )
            
            # Wyświetl mapę
            map_data = st_folium(folium_map, width=800, height=600)
            
            # Obsługa kliknięć na mapie
            if map_data and map_data.get('last_clicked'):
                clicked_lat = map_data['last_clicked']['lat']
                clicked_lon = map_data['last_clicked']['lng']
                
                # Sprawdź czy to nowe kliknięcie
                if st.session_state.map_clicks != [clicked_lat, clicked_lon]:
                    st.session_state.map_clicks = [clicked_lat, clicked_lon]
                    
                    with st.expander("➕ Dodaj punkt z kliknięcia na mapie", expanded=True):
                        st.write(f"**Kliknięto:** Lat: {clicked_lat:.4f}, Lon: {clicked_lon:.4f}")
                        new_name = st.text_input("Nazwa punktu:", 
                                                 value=f"Kliknięty {len(st.session_state.geo_points)+1}",
                                                 key="clicked_name")
                        if st.button("✅ Dodaj ten punkt"):
                            st.session_state.geo_points.append([clicked_lat, clicked_lon, new_name])
                            st.session_state.diagram_generated = False
                            st.success(f"Dodano punkt {new_name}")
                            st.rerun()
            
            # Opcja zapisu mapy
            if show_voronoi:
                map_html = folium_map._repr_html_()
                st.download_button(
                    label="⬇️ Pobierz mapę (HTML)",
                    data=map_html,
                    file_name="voronoi_map.html",
                    mime="text/html"
                )
        else:
            st.info("👆 Dodaj punkty używając panelu po lewej stronie lub klikając na mapę poniżej")
            
            # Pokaż pustą mapę Polski
            empty_map = folium.Map(location=[52.0, 19.0], zoom_start=6)
            empty_map.add_child(folium.LatLngPopup())
            plugins.Fullscreen().add_to(empty_map)
            
            map_data = st_folium(empty_map, width=800, height=600)
            
            if map_data and map_data.get('last_clicked'):
                clicked_lat = map_data['last_clicked']['lat']
                clicked_lon = map_data['last_clicked']['lng']
                
                with st.expander("➕ Dodaj punkt z kliknięcia na mapie", expanded=True):
                    st.write(f"**Kliknięto:** Lat: {clicked_lat:.4f}, Lon: {clicked_lon:.4f}")
                    new_name = st.text_input("Nazwa punktu:", 
                                             value=f"Punkt {len(st.session_state.geo_points)+1}",
                                             key="clicked_name_empty")
                    if st.button("✅ Dodaj ten punkt"):
                        st.session_state.geo_points.append([clicked_lat, clicked_lon, new_name])
                        st.session_state.diagram_generated = False
                        st.success(f"Dodano punkt {new_name}")
                        st.rerun()

with col_right:
    st.header("ℹ️ Informacje")
    
    if current_points:
        st.metric("Liczba punktów", len(current_points))
        
        if st.session_state.diagram_generated and st.session_state.dcel:
            st.metric("Wierzchołki Voronoi", len(st.session_state.dcel.vertices))
            st.metric("Krawędzie", len(st.session_state.dcel.half_edges) // 2)
            st.metric("Regiony", len(st.session_state.dcel.faces))
    
    st.markdown("---")
    st.subheader("📖 Instrukcja")
    
    if st.session_state.map_mode == 'matplotlib':
        st.markdown("""
        **Tryb Wykres (XY):**
        1. Dodaj punkty po współrzędnych X, Y
        2. Lub wygeneruj losowe punkty
        3. Kliknij "Generuj Diagram Voronoi"
        4. Zapisz punkty lub diagram
        
        **Zakres:** 0-10 dla X i Y
        """)
    else:
        st.markdown("""
        **Tryb Mapa Świata:**
        1. **Kliknij na mapie** aby dodać punkt
        2. Lub dodaj ręcznie (Lat/Lon)
        3. Lub wygeneruj losowe (Polska)
        4. Kliknij "Generuj Diagram Voronoi"
        5. Zapisz punkty lub mapę HTML
        
        **Wskazówki:**
        - Kliknij mapę dla szybkiego dodania
        - Użyj pełnego ekranu (ikona w rogu)
        - Mapa używa projekcji Mercatora
        """)
    
    st.markdown("---")
    st.subheader("🔧 O trybach")
    st.markdown("""
    **📊 Wykres:** Klasyczna płaszczyzna XY, 
    idealna do nauki i eksperymentów
    
    **🌍 Mapa:** Rzeczywiste współrzędne 
    geograficzne, do analiz przestrzennych
    
    *Algorytm Fortune'a działa w obu trybach!*
    """)
    
    if st.session_state.map_mode == 'folium':
        st.markdown("---")
        st.subheader("🌍 Przykłady geo")
        st.markdown("""
        **Polskie miasta:**
        - Warszawa: 52.2297, 21.0122
        - Kraków: 50.0647, 19.9450
        - Gdańsk: 54.3520, 18.6466
        - Wrocław: 51.1079, 17.0385
        - Poznań: 52.4064, 16.9252
        """)

# Stopka
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Interaktywny Generator Diagramu Voronoi | "
    "Algorytm Fortune'a | Tryby: Wykres & Mapa Świata"
    "</div>", 
    unsafe_allow_html=True
)