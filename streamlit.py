import plotly.graph_objects as go
import json
import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

st.set_page_config(
    page_title="Sloterdijk Noord",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

zonuren_per_jaar = 1750 # zonuren per jaar in sloterdijk gemiddeld
performance_ratio = 0.825  # performance ratio van zonnepanelen
gemiddelde_wp_per_paneel = 320.53  # gemiddelde watt piek van zonnepanelen
kwh_paneel_per_jaar = gemiddelde_wp_per_paneel * zonuren_per_jaar * performance_ratio / 1000  # omrekenen naar kWh
aantal_kwh_per_hectare = 289616  # kWh per hectare
oppervlakte_zonnepaneel = 1.65  #(1 paneel = 1.65 m²)

afstand_per_werknemer_per_dag = 44  # in kilometers
aantal_werkdagen_per_jaar = 230
energieverbruik_per_km = 0.2  # in kWh per kilometer


# Initialize variables to calculate the average
total_lat = 0
total_lon = 0
count = 0

# data format: 'company':(m2, nummeraanduiding, aantal zonnepanelen, watt piek)
#Groothandel data met koeling (True of False)
groothandel = {
    'sligro': (51226, "0363200011872485", 1260, 415800, True),  # true
    'bilal_chicken_centre': (3390, "0363200012110968", 0, 0, True),  # true
    'Jansen_Houtimport_BV': (6765, "0363200000486527", 222, 73260, False),  # false
    'wenzel_bv': (6765, "0363200000486527", 0, 0, False),  # false
    'Scania Amsterdam': (1849, "0363200000508212", 0, 0, False),  # false
    'Euromaster Amsterdam': (1499, "0363200003766943", 0, 0, False),  # false
    'Advion B.V.': (15278, "0363200012110531", 0, 0, False),  # false
    'Decorum Kantoormeubelen': (9277, "0363200000496878", 0, 0, False),  # false
    'Anker Amsterdam Spirits': (7686, "0363200012080084", 1289, 406035, True),  # true
    'dronk bedrijfswagen onderdelen': (2654, "0363200001988473", 0, 0, False),  # false
}

dienstverlening = {
    'cws_hygiene_amsterdam': (2741, "0363200000492527",0,0),
}

vervoer_opslag = {
    'apollo_verhuizingen': (1808, "0363200000538631",483,147315),
    'warehouse_company_freight_company': (799,"0363200012118068",0,0),
    'nipparts': (15941,"0363200000484308",0,0),
    'ap_logistics': (15941,"0363200000484308",0,0),
    "PostNL Crossdock Amsterdam"  : (11080,"0363200000455959",0,0),
    "PostNL - ScB Amsterdam" : (31074,"0363200000455961",3003,990990),
    "skynet_worldwide_express" : (2400,"0363200000486614",0,0),
    "fietsendepot_amsterdam" : (16042,"0363200000348278",1841,579915),
    "hulshoff projectverhuizingen" : (1360,"0363200012137295",2782,876330),
    "truckwash1_amsterdam" : (831,"0363200012133402",0,0)
}
industrie_nutsbedrijven = {
    "anamet_europe" : (4591,"0363200012107486",580,177180),
    "IGT europe gaming" : (10150,"0363200000497168",0,0)
}

openbaar_bestuur = {
    "gezamenlijke_brandweer_amsterdam" : (5755,"0363200012147107",687,226710)
}
ict = {
    "SOCIALDATABASE" : (799,"0363200012118068",0,0)
}
detailhandel = {
    "Shell tankstation" : (101,"0363200001970483",0,0)
}

all_sectors = [groothandel, dienstverlening, vervoer_opslag, industrie_nutsbedrijven, openbaar_bestuur, detailhandel, ict]

##########################
##########################
tab1, tab2,tab3,tab4,tab5  = st.tabs(['data', 'zonnepanelen', "personenauto's", 'bestelbussen', 'energievraag'])

with tab1:
    # Title of the app
    st.title("Data van Sloterdijk Noord")

    code="""
    #Data format: 'company':(m2, nummeraanduiding, aantal zonnepanelen, watt piek) Groothandel data met koeling (True of False)

groothandel = {
    'sligro': (51226, "0363200011872485", 1260, 415800, True),
    'bilal_chicken_centre': (3390, "0363200012110968", 0, 0, True),
    'Jansen_Houtimport_BV': (6765, "0363200000486527", 222, 73260, False),
    'wenzel_bv': (6765, "0363200000486527", 0, 0, False),
    'Scania Amsterdam': (1849, "0363200000508212", 0, 0, False),
    'Euromaster Amsterdam': (1499, "0363200003766943", 0, 0, False),
    'Advion B.V.': (15278, "0363200012110531", 0, 0, False),  # false
    'Decorum Kantoormeubelen': (9277, "0363200000496878", 0, 0, False),
    'Anker Amsterdam Spirits': (7686, "0363200012080084", 1289, 406035, True),
    'dronk bedrijfswagen onderdelen': (2654, "0363200001988473", 0, 0, False),
}

dienstverlening = {
    'cws_hygiene_amsterdam': (2741, "0363200000492527",0,0),
}

vervoer_opslag = {
    'apollo_verhuizingen': (1808, "0363200000538631",483,147315),
    'warehouse_company_freight_company': (799,"0363200012118068",0,0),
    'nipparts': (15941,"0363200000484308",0,0),
    'ap_logistics': (15941,"0363200000484308",0,0),
    "PostNL Crossdock Amsterdam"  : (11080,"0363200000455959",0,0),
    "PostNL - ScB Amsterdam" : (31074,"0363200000455961",3003,990990),
    "skynet_worldwide_express" : (2400,"0363200000486614",0,0),
    "fietsendepot_amsterdam" : (16042,"0363200000348278",1841,579915),
    "hulshoff projectverhuizingen" : (1360,"0363200012137295",2782,876330),
    "truckwash1_amsterdam" : (831,"0363200012133402",0,0)
}
industrie_nutsbedrijven = {
    "anamet_europe" : (4591,"0363200012107486",580,177180),
    "IGT europe gaming" : (10150,"0363200000497168",0,0)
}

openbaar_bestuur = {
    "gezamenlijke_brandweer_amsterdam" : (5755,"0363200012147107",687,226710)
}
ict = {
    "SOCIALDATABASE" : (799,"0363200012118068",0,0)
}
detailhandel = {
    "Shell tankstation" : (101,"0363200001970483",0,0)
}

all_sectors = [groothandel, dienstverlening, vervoer_opslag, industrie_nutsbedrijven, openbaar_bestuur, detailhandel, ict]

"""
    st.code(code, language='python')


    st.image('bag.png')
    # Load the GeoJSON data
    geojson_data = json.load(open('geojson.json'))

    # Loop through each feature in the GeoJSON data
    for feature in geojson_data['features']:
        # Extract geometry coordinates (assuming they are polygons)
        coordinates = feature['geometry']['coordinates'][0]  # Get the first ring of the polygon
        for coord in coordinates:
            # Each coord is in the form (longitude, latitude)
            lon, lat = coord  # Note: the order is (longitude, latitude)
            total_lat += lat
            total_lon += lon
            count += 1

    # Calculate averages
    if count > 0:
        avg_lat = total_lat / count
        avg_lon = total_lon / count
    else:
        avg_lat = avg_lon = None  # Handle case where there are no coordinates

    # Create a Folium map (in WGS84)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=15)  # Amsterdam coordinates

    # Add geometries to the map
    for feature in geojson_data['features']:
        bedrijven = feature['properties']['bedrijven']
        oppervlakte = feature['properties']['oppervlakte']
        zonnepanelen = feature['properties']['zonnepanelen']
        wp = feature['properties']['wp']
        sectors = feature['properties']['sectors']  # Get the sectors

        # Create a popup with company and sector information
        popup_text = (
            f"<strong>Oppervlakte:</strong> {oppervlakte} m²<br>"
            f"<strong>Zonnepanelen:</strong> {zonnepanelen}<br>"
            f"<strong>Watt piek:</strong> {wp} Wp<br>"
            f"<strong>Bedrijven:</strong><br>" + "<br>".join(bedrijven) + "<br>"
            f"<strong>Sectors:</strong><br>" + "<br>".join(sectors)  # Add sectors to popup
        )

        
        # Add the polygon and popup to the map
        folium.GeoJson(
            feature['geometry'],
            tooltip=folium.Tooltip(popup_text)
        ).add_to(m)

    st.subheader('Map van Sloterdijk Noord')
    # Display the map in Streamlit
    folium_static(m)
###################
###################

with tab2:
# Extracting the total number of solar panels (zonnepanelen) for each sector
    sectors_total = {
        'Groothandel': sum(value[2] for value in groothandel.values()),
        'Dienstverlening': sum(value[2] for value in dienstverlening.values()),
        'Vervoer & Opslag': sum(value[2] for value in vervoer_opslag.values()),
        'Industrie & Nutsbedrijven': sum(value[2] for value in industrie_nutsbedrijven.values()),
        'Openbaar Bestuur': sum(value[2] for value in openbaar_bestuur.values()),
        'ICT': sum(value[2] for value in ict.values()),
        'Detailhandel': sum(value[2] for value in detailhandel.values()),
    }

    st.title('Totaal aantal zonnepanelen per sector')

    st.image('zonnepanelen.png')
    # Create a bar chart
    fig = go.Figure()

    # Add bar for each sector
    fig.add_trace(go.Bar(
        x=list(sectors_total.keys()),  # Sector names
        y=list(sectors_total.values()),  # Total solar panels
        marker=dict(line=dict(width=1)),  # Border styling for bars
    ))

    # Update layout
    fig.update_layout(
        title='Total Number of Solar Panels by Sector',
        xaxis_title='Sector',
        yaxis_title='Total Number of Solar Panels',
        template='plotly_white'
    )

    # Show the figure in Streamlit
    st.plotly_chart(fig)

    ###################
    ###################
    st.write('---')

    def calculate_kwh(zonuren_per_jaar, total_kwp):
        kwh = zonuren_per_jaar * total_kwp * 0.825
        return kwh

    total_wp = sum(value[3] for sector in all_sectors for value in sector.values())
    total_kwp = total_wp / 1000

    oplevering_zonnepanelen_per_jaar = int(calculate_kwh(zonuren_per_jaar, total_kwp))


    print(f"Total kWh per year: {oplevering_zonnepanelen_per_jaar}")

    solar_code ="""
    def calculate_kwh(zonuren_per_jaar, total_kwp):
        kwh = zonuren_per_jaar * total_kwp * 0.825
        return kwh

    total_wp = sum(value[3] for sector in all_sectors for value in sector.values())
    total_kwp = total_wp / 1000

    oplevering_zonnepanelen_per_jaar = int(calculate_kwh(zonuren_per_jaar, total_kwp))

    """
    # calculate the total oppervlakte, but only unique values
    totale_oppervlakte = (value[0] for sector in all_sectors for value in sector.values())

    # get unique values from the generator
    unique_oppervlakte = set(totale_oppervlakte)

    # get the hectare:
    hectare = sum(unique_oppervlakte) / 10000

    kwh_verbruik_per_jaar = int(aantal_kwh_per_hectare * hectare)

    print(f"Total kWh per year for the total oppervlakte: {kwh_verbruik_per_jaar}")
    usage_code = """
    # calculate the total oppervlakte, but only unique values
    totale_oppervlakte = (value[0] for sector in all_sectors for value in sector.values())

    # get unique values from the generator
    unique_oppervlakte = set(totale_oppervlakte)

    # get the hectare:
    hectare = sum(unique_oppervlakte) / 10000

    kwh_verbruik_per_jaar = int(aantal_kwh_per_hectare * hectare)
    """
    # write subtitle for calculation
    col1, col2 = st.columns(2)
    with col1:
        st.write('### oplevering zonnepanelen per jaar')
        st.code(solar_code, language='python')
        # write the answer
        st.write(f'Totale kwh oplevering per jaar in Sloterdijk Noord: {oplevering_zonnepanelen_per_jaar}')
    with col2:
        st.write('### energie verbruik per jaar')
        st.code(usage_code, language='python')
        st.write(f'Totale kwh verbruik per jaar in Sloterdijk Noord: {kwh_verbruik_per_jaar}')

    # Calculate the remaining energy consumption
    remaining_kwh = kwh_verbruik_per_jaar - oplevering_zonnepanelen_per_jaar

    # Prepare data for the pie chart
    labels = ['Oplevering Zonnepanelen per Jaar', 'Overige Energie Levering per Jaar']
    values = [oplevering_zonnepanelen_per_jaar, remaining_kwh]

    # Create a Streamlit app
    st.title('Energie Verbruik en Zonnepanelen Oplevering')

    # Create a pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])  # Create a donut chart with hole size

    # Update layout
    fig.update_layout(
        title='Annual Energy Consumption and Solar Panel Output',
        template='plotly_white'
    )

    # Show the figure in Streamlit
    st.plotly_chart(fig)

###################
###################


    #Dataset omzetten naar een DataFrame voor gebruik met Plotly
    df = pd.DataFrame.from_dict(groothandel, orient='index', columns=['Oppervlakte', 'Kamer', 'Zonnepanelen', 'Watt_Piek', 'Koeling'])
    df['Bedrijf'] = df.index

    #Staafdiagram maken
    fig = px.bar(df, x='Bedrijf', y='Zonnepanelen', color='Koeling',
                title='Aantal Zonnepanelen in Groothandel met Koeling of Geen Koeling',
                labels={'Zonnepanelen': 'Aantal Zonnepanelen', 'Bedrijf': 'Bedrijf'},
                color_discrete_map={True: 'blue', False: 'orange'})  # Kleur aanpassen

    #Layout aanpassen
    fig.update_layout(
        xaxis_title='Bedrijf',
        yaxis_title='Aantal Zonnepanelen',
        template='plotly_white',
        xaxis_tickangle=-45,  # Draai de labels op de x-as
        width=1000,  # Breder maken voor betere zichtbaarheid
        height=600   # Hoogte van de grafiek
    )

    #Grafiek weergeven in Streamlit
    st.plotly_chart(fig)

    st.write('---')

    #Bereken totale oppervlakte in vierkante meters
    unique_oppervlakten = set()  # To track unique areas

    # do the same with all_sectors:
    for sector in all_sectors:
        for value in sector.values():
            unique_oppervlakten.add(value[0])

    # Sum the unique areas
    totaal_oppervlakte_m2 = sum(unique_oppervlakten)

    totaal_aantal_zonnepanelen = int(totaal_oppervlakte_m2 / oppervlakte_zonnepaneel)

    code = """
    #Bereken totale oppervlakte in vierkante meters
    unique_oppervlakten = set()  # To track unique areas

    # do the same with all_sectors:
    for sector in all_sectors:
        for value in sector.values():
            unique_oppervlakten.add(value[0])

    # Sum the unique areas
    totaal_oppervlakte_m2 = sum(unique_oppervlakten)

    totaal_aantal_zonnepanelen = int(totaal_oppervlakte_m2 / oppervlakte_zonnepaneel)
    """
    st.code(code, language='python')

    #Resultaat tonen
    st.write(f'Aantal zonnepanelen dat op de daken kan worden geplaatst: {totaal_aantal_zonnepanelen:.0f}')
    
    #Lijst om zonnepanelen van alle sectoren op te slaan
    zonnepanelen_per_sector = []

    #Doorloop alle sectoren en voeg zonnepanelen toe aan de lijst
    for sector in all_sectors:
        zonnepanelen_per_sector.extend([value[2] for value in sector.values()])

    #Totale aantal zonnepanelen berekenen
    totaal_zonnepanelen = int(sum(zonnepanelen_per_sector))

    code = """
    #Lijst om zonnepanelen van alle sectoren op te slaan
    zonnepanelen_per_sector = []

    #Doorloop alle sectoren en voeg zonnepanelen toe aan de lijst
    for sector in all_sectors:
        zonnepanelen_per_sector.extend([value[2] for value in sector.values()])

    #Totale aantal zonnepanelen berekenen
    totaal_zonnepanelen = int(sum(zonnepanelen_per_sector))

    """
    st.code(code, language='python')
    #Resultaat tonen
    st.write(f"Het totale aantal zonnepanelen dat momenteel op de daken ligt: {totaal_zonnepanelen}")

    #Totale energie berekenen in kWh, rekening houdend met de performance ratio
    totaal_energie_kwh = int((totaal_aantal_zonnepanelen * gemiddelde_wp_per_paneel * zonuren_per_jaar * performance_ratio))/1000

    code = """
    #Totale energie berekenen in kWh, rekening houdend met de performance ratio
    totaal_energie_kwh = int((totaal_aantal_zonnepanelen * gemiddelde_wp_per_paneel * zonuren_per_jaar * performance_ratio))/1000
    """
    st.code(code, language='python')
    #Resultaat tonen
    st.write(f"Het totale energieproductie per jaar met {totaal_aantal_zonnepanelen} zonnepanelen is: {int(totaal_energie_kwh)} kWh")

###################
###################

with tab3:
    # Aantal werknemers per bedrijf
    werknemers_data = {
        "groothandel": {
            "Sligro": 1024,
            "Bilal Chicken Centre": 68,
            "Jansen Houtimport BV": 135,
            "Wenzel BV": 135,
            "Scania Amsterdam": 37,
            "Euromaster Amsterdam": 30,
            "Advion B.V.": 306,
            "Decorum Kantoormeubelen": 185,
            "Anker Amsterdam Spirits": 154,
            "Dronk Bedrijfswagen Onderdelen": 53,
        },
        "dienstverlening": {
            "CWS Hygiene Amsterdam": 73,
        },
        "vervoer_en_opslag": {
            "Apollo Verhuizingen": 24,
            "Warehouse Company Freight Company": 11,
            "Nipparts": 212,
            "AP Logistics": 212,
            "PostNL Crossdock Amsterdam": 147,
            "PostNL - ScB Amsterdam": 414,
            "Skynet Worldwide Express": 32,
            "Fietsendepot Amsterdam": 214,
            "Hulshoff Projectverhuizingen": 18,
            "Truckwash1 Amsterdam": 11,
        },
        "industrie_nutsbedrijven": {
            "Anamet Europe": 74,
            "IGT Europe Gaming": 162,
        },
        "openbaar_bestuur": {
            "Gezamenlijke Brandweer Amsterdam": 153,
        },
        "ict": {
            "Socialdatabase": 32,
        },
        "detailhandel": {
            "Shell Tankstation": 2,
        },
    }

    # show dictionary werknemers_data in a table
    st.title("Energieverbruik van personenauto's")
    st.write(werknemers_data)

    st.write('---')
    st.subheader('bereken het energieverbruik van de werknemers per bedrijf')
    
    code = """
    afstand_per_werknemer_per_dag = 44  # in kilometers
    aantal_werkdagen_per_jaar = 230
    energieverbruik_per_km = 0.2  # in kWh per kilometer

    energie_data = {}
    totaal_kwh = 0

    # Bereken energie en afstand per bedrijf
    for categorie, bedrijven in werknemers_data.items():
        energie_data[categorie] = {}
        for naam, aantal_werknemers in bedrijven.items():
            totale_afstand = aantal_werknemers * afstand_per_werknemer_per_dag * aantal_werkdagen_per_jaar
            totale_energie = totale_afstand * energieverbruik_per_km / 2  # Deel de energie door 2
            energie_data[categorie][naam] = (totale_afstand, totale_energie)
            totaal_kwh += totale_energie

    # Print resultaten
    print("Totale Afstand en Energieverbruik per Bedrijf per Jaar:")
    bedrijven, energieverbruik = [], []

    for categorie, bedrijven_data in energie_data.items():
        print(categorie.capitalize())
        for naam, (afstand, energie) in bedrijven_data.items():
            print(f"{naam}: {afstand:,.0f} km, {energie:,.2f} kWh")
            bedrijven.append(naam)
            energieverbruik.append(energie)

    print(f"\nTotale Energieverbruik van alle bedrijven: {totaal_kwh:,.2f} kWh")

    # Genereer grafiek
    plt.figure(figsize=(12, 6))
    plt.barh(bedrijven, energieverbruik, color='skyblue')
    plt.xlabel('Energieverbruik (kWh) in 2035')
    plt.title('Energieverbruik per Bedrijf van Personenauto per Jaar in 2035')
    plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()

    st.pyplot(plt)
    """
    st.code(code, language='python')

    energie_data = {}
    totaal_personenauto_kwh = 0

    # Bereken energie en afstand per bedrijf
    for categorie, bedrijven in werknemers_data.items():
        energie_data[categorie] = {}
        for naam, aantal_werknemers in bedrijven.items():
            totale_afstand = aantal_werknemers * afstand_per_werknemer_per_dag * aantal_werkdagen_per_jaar
            totale_energie = totale_afstand * energieverbruik_per_km / 2  # Deel de energie door 2
            energie_data[categorie][naam] = (totale_afstand, totale_energie)
            totaal_personenauto_kwh += totale_energie

    # Print resultaten
    print("Totale Afstand en Energieverbruik per Bedrijf per Jaar:")
    bedrijven, energieverbruik = [], []

    for categorie, bedrijven_data in energie_data.items():
        print(categorie.capitalize())
        for naam, (afstand, energie) in bedrijven_data.items():
            print(f"{naam}: {afstand:,.0f} km, {energie:,.2f} kWh")
            bedrijven.append(naam)
            energieverbruik.append(energie)

    print(f"\nTotale Energieverbruik van alle bedrijven: {int(totaal_personenauto_kwh) } kWh")

    # Genereer grafiek
    plt.figure(figsize=(12, 6))
    plt.barh(bedrijven, energieverbruik, color='skyblue')
    plt.xlabel('Energieverbruik (kWh) in 2035')
    plt.title('Energieverbruik per Bedrijf van Personenauto per Jaar in 2035')
    plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()

    st.pyplot(plt)

    st.write(f'Totale Energieverbruik van alle bedrijven: {totaal_personenauto_kwh} kWh')
###################
###################
with tab4:

    # put png in streamlit
    st.image('westpoort.png')
    st.image('wagenparkdfp.png')


    # Data arrays
    sloterdijk3 = np.array([31, 187, 435])
    sloterdijknoord = np.array([3, 18, 42])

    # Years array
    years = np.array([2025, 2030, 2035])

    # Create a Plotly figure for the comparison of Sloterdijk 3 and Sloterdijk Noord
    fig1 = go.Figure()

    # Add Sloterdijk 3 trace
    fig1.add_trace(go.Scatter(x=years, y=sloterdijk3, mode='lines+markers', name='Sloterdijk 3', line=dict(color='blue')))

    # Add Sloterdijk Noord trace
    fig1.add_trace(go.Scatter(x=years, y=sloterdijknoord, mode='lines+markers', name='Sloterdijk Noord', line=dict(color='green')))

    # Set titles and labels for the first plot
    fig1.update_layout(
        title='Data Comparison of Sloterdijk 3 and Sloterdijk Noord',
        xaxis_title='Year',
        yaxis_title='Values',
        showlegend=True
    )

    # Create another Plotly figure for Sloterdijk Noord only
    fig2 = go.Figure()

    # Add Sloterdijk Noord trace
    fig2.add_trace(go.Scatter(x=years, y=sloterdijknoord, mode='lines+markers', name='Sloterdijk Noord', line=dict(color='green')))

    # Set titles and labels for the second plot
    fig2.update_layout(
        title='Data for Sloterdijk Noord',
        xaxis_title='Year',
        yaxis_title='Values',
        showlegend=True
    )

    code = """
# Data arrays
    sloterdijk3 = np.array([31, 187, 435])
    sloterdijknoord = np.array([3, 18, 42])

    # Years array
    years = np.array([2025, 2030, 2035])

    # Create a Plotly figure for the comparison of Sloterdijk 3 and Sloterdijk Noord
    fig1 = go.Figure()

    # Add Sloterdijk 3 trace
    fig1.add_trace(go.Scatter(x=years, y=sloterdijk3, mode='lines+markers', name='Sloterdijk 3', line=dict(color='blue')))

    # Add Sloterdijk Noord trace
    fig1.add_trace(go.Scatter(x=years, y=sloterdijknoord, mode='lines+markers', name='Sloterdijk Noord', line=dict(color='green')))

    # Set titles and labels for the first plot
    fig1.update_layout(
        title='Data Comparison of Sloterdijk 3 and Sloterdijk Noord',
        xaxis_title='Year',
        yaxis_title='Values',
        showlegend=True
    )

    # Create another Plotly figure for Sloterdijk Noord only
    fig2 = go.Figure()

    # Add Sloterdijk Noord trace
    fig2.add_trace(go.Scatter(x=years, y=sloterdijknoord, mode='lines+markers', name='Sloterdijk Noord', line=dict(color='green')))

    # Set titles and labels for the second plot
    fig2.update_layout(
        title='Data for Sloterdijk Noord',
        xaxis_title='Year',
        yaxis_title='Values',
        showlegend=True
    )
    """
    st.code(code, language='python')
    # Display the second plot
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)

###################
###################

with tab5:

    bussen = 42 #2030
    e_bus_verbruik_in_kwh = 60 #1 volle e-bestelbus = 300 km = 60 kwh
    e_bus_afstand_met_volle_accu = 300 #km
    gemiddelde_e_bus_afstand_per_jaar = 30000 #km
    kwh_per_bus = (gemiddelde_e_bus_afstand_per_jaar / e_bus_afstand_met_volle_accu) * e_bus_verbruik_in_kwh
    totaal_bestelauto_energie = kwh_per_bus * (bussen/2) # ervan uitgaande dat de helft van de bussen op het terrein is tijdens het opladen

    totaal_bus_en_persoonauto_verbruik = totaal_bestelauto_energie + totaal_personenauto_kwh

    #Bereken het aantal zonnepanelen
    aantal_nodige_zonnepanelen = totaal_bus_en_persoonauto_verbruik / kwh_paneel_per_jaar

    code = """
    bussen = 42 #2030
    e_bus_verbruik_in_kwh = 60 #1 volle e-bestelbus = 300 km = 60 kwh
    e_bus_afstand_met_volle_accu = 300 #km
    gemiddelde_e_bus_afstand_per_jaar = 30000 #km
    kwh_per_bus = (gemiddelde_e_bus_afstand_per_jaar / e_bus_afstand_met_volle_accu) * e_bus_verbruik_in_kwh
    totaal_bestelauto_energie = kwh_per_bus * (bussen/2) # ervan uitgaande dat de helft van de bussen op het terrein is tijdens het opladen

    totaal_bus_en_persoonauto_verbruik = totaal_bestelauto_energie + totaal_personenauto_kwh

    #Bereken het aantal zonnepanelen
    aantal_nodige_zonnepanelen = totaal_bus_en_persoonauto_verbruik / kwh_paneel_per_jaar
    """
    st.subheader('Hoe veel zonnepanelen zijn er nodig?')
    st.code(code, language='python')

    st.write(f"aantal  zonnepanelen om aan energievraag voor bussen en personenauto's te voldoen in 2035: {np.ceil(aantal_nodige_zonnepanelen)}")