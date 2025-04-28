import streamlit as st
import pandas as pd
from backend import load_buyers, load_sellers, get_matchings

# --- Seitenwahl ---
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Seite wählen:", ["Übersicht", "Maklerbereich"])

# --- Übersicht ---
if page == "Übersicht":
    st.title("🏡 Immobilienmarkt Zürich – Übersicht")

    try:
        # Daten laden
        population_df_raw = pd.read_csv('data/Cleaned/bevoelkerungZuerichCleaned.csv')
        population_df = population_df_raw[population_df_raw["Year"] == 2024]

        gebaeude_df = pd.read_csv('data/Cleaned/gebauedeZuerich2024Cleaned.csv')

        einkommen_df_raw = pd.read_csv('data/Cleaned/einkommenZuerichCleaned.csv')
        einkommen_df = einkommen_df_raw[einkommen_df_raw["StichtagDatJahr"] == 2022]

        # Charts
        st.subheader("Bevölkerung nach Kreis")
        einwohner_pro_kreis = population_df.groupby("Kreis")["PopulationCount"].sum()
        st.bar_chart(einwohner_pro_kreis)

        st.subheader("Durchschnittliches steuerbares Einkommen pro Kreis (Median, 2022)")
        einkommen_pro_kreis = einkommen_df.groupby("KreisCd")["SteuerEinkommen_p50"].mean()
        st.bar_chart(einkommen_pro_kreis)

        st.subheader("Anzahl Gebäude nach Kreis")
        anzahl_gebaeude_pro_kreis = gebaeude_df.groupby("KreisCd")["AnzGbd"].sum()
        st.bar_chart(anzahl_gebaeude_pro_kreis)

    except FileNotFoundError as e:
        st.error(f"Fehler beim Laden der Daten: {e}")

# --- Maklerbereich ---
elif page == "Maklerbereich":
    st.title("🧑‍💼 Maklerbereich: Marktbeobachtung & Matching")

    # Käufer:innen & Verkäufer:innen laden
    buyers = load_buyers()
    sellers = load_sellers()

    # Session-States initialisieren
    if "market_view" not in st.session_state:
        st.session_state.market_view = "none"

    if "matchings" not in st.session_state:
        st.session_state.matchings = None
        st.session_state.best_matchings = None

    if st.button("👀 Marktbeobachtungen anzeigen"):
        st.session_state.market_view = "active"

    # --- Buttons für Verkäufer:innen ---
    col1, col2 = st.columns(2)

    if st.session_state.market_view != "none":
        st.subheader("Aktive Käufer:innen")
        st.dataframe(buyers)

        with col1:
            if st.button("🔄 Nur aktive Verkäufer:innen anzeigen"):
                st.session_state.market_view = "active"

        with col2:
            if st.button("➕ Nur potenzielle Verkäufer:innen anzeigen"):
                st.session_state.market_view = "potential"

        if st.session_state.market_view == "active":
            st.subheader("Aktive Verkäufer:innen (gelistet)")
            aktive_sellers = sellers[sellers["Gelisted"] == True]
            st.dataframe(aktive_sellers)

        elif st.session_state.market_view == "potential":
            st.subheader("Potenzielle Verkäufer:innen (noch nicht gelistet)")
            potential_sellers = sellers[sellers["Gelisted"] == False]
            st.dataframe(potential_sellers)

    # --- Kaufvorschläge ---
    st.subheader("🏠 Kaufvorschläge")
    matching_threshold = st.slider("Mindest-Matching-Score (%)", 50, 100, 70)

    # Session-Variablen initialisieren
    if "matchings" not in st.session_state:
        st.session_state.matchings = None
    if "best_matchings" not in st.session_state:
        st.session_state.best_matchings = None

    # Button: Vorschläge laden
    if st.button("💬 Kaufvorschläge anzeigen"):
        matchings = get_matchings(threshold=matching_threshold)

        # Alle Matches speichern
        st.session_state.matchings = matchings

        # Nur bestes Match je Käufer:in für Übersicht
        best_matchings = matchings.sort_values("MatchingScore", ascending=False).drop_duplicates(subset=["BuyerID"])
        st.session_state.best_matchings = best_matchings

    # --- Nur wenn Matching vorhanden ist ---
    if st.session_state.best_matchings is not None:
        st.subheader("📋 Übersicht beste Kaufvorschläge")
        st.dataframe(st.session_state.best_matchings)

        # Käufer-Auswahl
        selected_match = st.selectbox("Details zu Käufer:", st.session_state.best_matchings["BuyerID"].unique())

        if selected_match:
            # Käuferprofil holen
            selected_buyer_row = buyers[buyers["BuyerID"] == selected_match]

            if not selected_buyer_row.empty:
                buyer_info = selected_buyer_row.iloc[0]

                st.subheader(f"👤 Käuferprofil: ID {buyer_info['BuyerID']}")
                st.markdown(f"""
                **Alter:** {buyer_info['Alter']}  
                **Wohnort (Kreis):** {buyer_info['Kreis (Wohnort)']}  
                **Budget:** {buyer_info['Budget (CHF)']:,} CHF  
                **Einkommen:** {buyer_info['Einkommen (CHF)']:,} CHF  
                """)

                # Alle passenden Listings dieses Käufers
                detailed_matches = st.session_state.matchings[
                    st.session_state.matchings["BuyerID"] == selected_match
                    ]

                # Nur relevante Spalten anzeigen
                relevant_columns = [
                    "SellerID", "OfferPrice", "SellerKreis", "MatchingScore",
                    "ViaBroker", "FinalPrice", "Comments"
                ]
                detailed_matches_display = detailed_matches[relevant_columns]

                st.subheader("🏠 Passende Immobilienangebote:")
                st.dataframe(detailed_matches_display)

            else:
                st.warning("Kein Käuferprofil gefunden.")
