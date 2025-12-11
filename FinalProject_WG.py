import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk

# Defining a color for charts
CHART1_COLOR = '#1F78B4'  # Blue
CHART2_COLOR = '#FF7F00'  # Orange
CHART3_COLOR = '#33A02C'  # Green

# Categorizing meteorite classifications labels into words for dropdown menu
meteorite_class = {
    # CHONDRITES
    # Carbonaceous
    "CB": "Carbonaceous Chondrite", "CH": "Carbonaceous Chondrite",
    "CK": "Carbonaceous Chondrite", "CM": "Carbonaceous Chondrite",
    "CR": "Carbonaceous Chondrite", "CV": "Carbonaceous Chondrite",
    "CO": "Carbonaceous Chondrite", "CI": "Carbonaceous Chondrite",
    # Ordinary
    "H": "Ordinary Chondrite", "L": "Ordinary Chondrite", "LL": "Ordinary Chondrite",
    # Rumuruti
    "R": "Rumuruti Chondrite",
    # Enstatite
    "EH": "Enstatite Chondrite", "EL": "Enstatite Chondrite",
    # ACHONDRITES
    # Primitive Achondrites
    "Lodranite": "Primitive Achondrite", "Acapulcoite": "Primitive Achondrite",
    "Winonaite": "Primitive Achondrite",
    # Martian
    "Shergottite": "Martian", "Nakhlite": "Martian", "Chassignite": "Martian",
    # Aubrites
    "Aubrite": "Aubrite",
    # Eurelites
    "Ureilite": "Ureilite",
    # HED
    "Howardite": "HED", "Eucrite": "HED", "Diogenite": "HED",
    # Angrites
    "Angrite": "Angrite",
    # Brachinites
    "Brachinite": "Brachinite",
    # Lunar
    "Feldspathic Breccia": "Lunar", "Basaltic": "Lunar", "Polymict": "Lunar",
    # IRON METEORITES
    "IAB": "Iron Meteorite", "IIAB": "Iron Meteorite", "IIIAB": "Iron Meteorite", "IVAB": "Iron Meteorite",
    # STONY-IRON METEORITES
    "Pallasite": "Stony-Iron", "Mesosiderite": "Stony-Iron"
}


# [FUNCCALL2]: Counts the number of records (data)
def get_df_count(df):
    return len(df)


# Function: This function returns the DataFrame and the initial record count.
def read_meteorite_date(FILENAME):
    df = pd.read_csv(FILENAME).set_index('id')
    total_records = len(df)  # Stored for return
    # [COLUMNS]
    df = df.drop(columns=['nametype', 'GeoLocation'])  # Drops 2 columns that are not relevant to website
    # Renaming columns for more clarification
    df = df.rename(columns={
        'name': 'Meteorite Name',
        'recclass': 'Classification',
        'mass (g)': 'Mass (g)',
        'fall': 'Discovery Type',
        'year': 'Year',
        'reclat': 'Latitude',
        'reclong': 'Longitude'
    })

    # Cleaning Classification Data (removing numbers)
    df['Classification'] = df['Classification'].str.replace('\d+', '', regex=True).str.strip()
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

    # [FUNCRETURN2]
    return df, total_records


# [MAP]: Utilized PyDeck and Streamline
def map_locations(df):
    # Subheader and Text
    st.subheader("🌎 Interactive Map: Filtered Meteorite Locations 🌍")
    st.caption("Zoom in to explore meteorite discoveries. **Hover over a dot for meteorite information.**")

    # Using Latitude and Longitude for PyDeck data
    df_map = df.dropna(subset=['Latitude', 'Longitude']).copy()  # Create a separate DataFrame with .copy()
    df_map['lat'] = df_map['Latitude']
    df_map['lon'] = df_map['Longitude']

    # Cleaning data for the map
    df_map['Mass (g)'] = df_map['Mass (g)'].round(2)
    df_map['Type'] = df_map['Type'].fillna('Unknown')

    # Defining PyDeck Layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_map,
        get_position=["lon", "lat"],
        get_color=[255, 165, 0, 160],  # Orange
        get_radius=10000,  # Size of dot
        radius_scale=2,  # Scaling dot
        pickable=True,  # Enabling hovering
        auto_highlight=True  # Making the dot highlighted when hovered on
    )

    # Centering the map
    view_state = pdk.ViewState(
        latitude=0,
        longitude=0,
        zoom=1
    )

    # Placing the dots on the map, setting map start position, and using HTML to make pop-up box
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>Name:</b> {Meteorite Name}<br/>"
                    "<b>Mass:</b> {Mass (g)} g<br/>"
                    "<b>Classification:</b> {Type}",
            "style": {
                "backgroundColor": "orange",
                "color": "black"
            }
        }
    )

    st.pydeck_chart(r)


# [CHART1]: Creating a line graph to display found vs.fallen observations
# [FUNC2P]
def chart_landings_over_time(df, found_color=CHART1_COLOR):
    # Subheader and Text
    st.subheader("Chart 1: Meteorite Landings Over Time (Found vs. Fell)")
    st.caption("Shows the time-series distribution of discovered meteorites.")

    yearly_counts = df.dropna(subset=['Year']).groupby(['Year', 'Discovery Type']).size().reset_index(name='Count')

    # [PIVOTTABLE]
    pivot_counts = yearly_counts.pivot(index='Year', columns='Discovery Type', values='Count').fillna(0)

    fig, ax = plt.subplots(figsize=(10, 5))

    # Coloring the points
    color_fell = 'red'
    color_found = found_color

    # If-Statements to categorize the data
    if 'Fell' in pivot_counts.columns:
        ax.plot(pivot_counts.index, pivot_counts['Fell'], label='Fell', marker='.', linestyle='-', color=color_fell)
    if 'Found' in pivot_counts.columns:
        ax.plot(pivot_counts.index, pivot_counts['Found'], label='Found', marker='.', linestyle='-', color=color_found)

    # Creating the table and plotting the points
    ax.set_title('Annual Count of Meteorite Discoveries')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Meteorites')
    ax.legend(title='Discovery Type')
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


# [CHART2]: Creating a bar chart to show the distribution of meteorite classifications
def chart_type_distribution(df, bar_color=CHART2_COLOR):
    # Subheader and Text
    st.subheader("Chart 2: Distribution of Major Meteorite Types")
    st.caption("Displays the total count for each unique meteorite classification type in the filtered dataset.")

    # [SORT]:Calculate the count for each major meteorite classification and sorting them
    type_counts = df["Type"].value_counts().sort_values(ascending=False)

    if type_counts.empty:
        st.warning("No meteorite types found in the filtered data for charting.")
        return

    # Setting the graph plot
    fig, ax = plt.subplots(figsize=(10, 6))

    # Creating the bar chart
    ax.bar(type_counts.index, type_counts.values, color=bar_color)

    ax.set_title('Distribution of Meteorite Types')
    ax.set_xlabel('Meteorite Type')
    ax.set_ylabel('Total Count')
    plt.xticks(rotation=45, ha='right')  # Making sure the text is readable
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


# Function to create a Top 10 Chart of meteorite masses according to the filters
def chart_top_mass_by_year(df, year_range, chart_color=CHART3_COLOR):
    # Subheader and Text
    st.subheader("Chart 3: Top 10 Heaviest Meteorites Filtered by Year")
    st.caption(
        f"Shows the 10 most massive meteorites discovered/fell between the years {year_range[0]} and {year_range[1]}.")

    df_filtered = df.dropna(subset=['Mass (g)', 'Year']).copy()

    # [FILTER2]
    df_filtered = df_filtered[
        (df_filtered['Year'] >= year_range[0]) &
        (df_filtered['Year'] <= year_range[1])
        ]

    # [SORT]
    top_10 = df_filtered.sort_values('Mass (g)', ascending=False).head(10)

    # [COLUMNS]
    top_10['Mass (kg)'] = top_10['Mass (g)'] / 1000
    # [SORT]
    top_10 = top_10.sort_values('Mass (kg)', ascending=True)

    # Setting the plot
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.barh(top_10['Meteorite Name'], top_10['Mass (kg)'], color=chart_color)

    # Creating the bar chart
    ax.set_title(f'Top {len(top_10)} Heaviest Meteorites ({year_range[0]}-{year_range[1]})')
    ax.set_xlabel('Mass (kg)')
    ax.set_ylabel('Meteorite Name')

    ax.ticklabel_format(style='plain', axis='x')

    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


# Function to run the overall program
def main():
    FILENAME = 'Meteorite_Landings.csv'

    # Setting the tab name, title, and other formatting
    st.set_page_config(page_title="Meteorite Landings Explorer", layout="wide")
    st.title("🌠 Meteorite Landings Explorer 🌠")
    st.subheader("Turning Meteorite Landings Data into Information")
    st.markdown("<hr>", unsafe_allow_html=True)

    # Load data and transform it
    meteorite_data, total_records = read_meteorite_date(FILENAME)  # [FUNCRETURN2]
    meteorite_data["Type"] = meteorite_data["Classification"].map(meteorite_class)  # [COLUMNS]

    # [ST3] Sidebar Filters
    st.sidebar.header("Data Filters")

    # [ST1]: Dropdown / Multi-Select Box
    unique_types = meteorite_data["Type"].unique()
    available_types = sorted([t for t in unique_types if pd.notna(t)])  # [LISTCOMP]
    selected_types = st.sidebar.multiselect(
        "Select Meteorite Types",
        available_types,
        default=available_types
    )

    # [ST2]: Double-ended sliders (years)
    slider_min_year = 1399
    slider_max_year = 2025

    selected_year_range = st.sidebar.slider(
        "Filter by Year",
        min_value=slider_min_year,
        max_value=slider_max_year,
        value=(slider_min_year, slider_max_year),
        step=1
    )

    # [ST2]: Double-ended slider (mass)
    mass_data = meteorite_data['Mass (g)'].dropna()
    mass_min = float(mass_data.min())  # #[MAXMIN]: Find minimum value
    mass_max = float(mass_data.max())  # #[MAXMIN]: Find maximum value

    selected_mass_range = st.sidebar.slider(
        "Filter by Mass (g)",
        min_value=mass_min,
        max_value=mass_max,
        value=(mass_min, mass_max),
        step=1000.0
    )

    st.sidebar.markdown("---")

    # [ST3]: Custom colors
    st.sidebar.header("🎨 Chart Color Settings")

    # Color 1
    chart1_color = st.sidebar.color_picker(
        "Chart 1 (Landings Over Time): Found Color",
        CHART1_COLOR
    )

    # Color 2
    chart2_color = st.sidebar.color_picker(
        "Chart 2 (Type Distribution): Bar Color",
        CHART2_COLOR
    )

    # Color 3
    chart3_color = st.sidebar.color_picker(
        "Chart 3 (Top Heaviest): Bar Color",
        CHART3_COLOR
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Classification Mapping Example")

    # [DICTMETHOD1]: Keys
    total_raw_classes = len(meteorite_class.keys())  # #[DICTMETHOD] (keys)
    st.sidebar.caption(f"Aggregated from {total_raw_classes} raw classifications.")

    st.sidebar.markdown("**First 5 Mappings:**")
    count = 0
    # [ITERLOOP] and [DICTMETHOD2]: Items
    for raw_class, major_type in meteorite_class.items():
        if count < 5:
            st.sidebar.text(f"{major_type}: [{raw_class}]")
            count += 1
        else:
            break

    # Apply filters
    filtered_data = meteorite_data.copy()

    #[FILTER1]
    if selected_types:
        filtered_data = filtered_data[filtered_data["Type"].isin(selected_types)]

    #[FILTER2]: Mass
    filtered_data = filtered_data[
        (filtered_data['Mass (g)'] >= selected_mass_range[0]) &
        (filtered_data['Mass (g)'] <= selected_mass_range[1])
        ]

    #[FILTER2]: Year
    filtered_data = filtered_data.dropna(subset=['Year'])
    filtered_data = filtered_data[
        (filtered_data['Year'] >= selected_year_range[0]) &
        (filtered_data['Year'] <= selected_year_range[1])
        ]

    # Cleaning data for display
    filtered_data['Year'] = filtered_data['Year'].astype(int)

    # Calculate filtered data count
    filtered_records = get_df_count(filtered_data)  #[FUNCCALL2]

    # Calculate total data
    total_data_count = get_df_count(meteorite_data)  #[FUNCCALL2]

    # Outputs
    st.info(
        f"The current filters result in **{filtered_records:,}** meteorites being displayed out of **{total_data_count:,}** total records.")
    st.markdown("---")

    # [MAP]
    map_locations(filtered_data)
    st.markdown("---")

    # Display Charts
    if not filtered_data.empty:

        # [CHART1]: Landings Over Time (Line Chart)
        chart_landings_over_time(filtered_data, chart1_color)
        st.markdown("---")

        col1, col2 = st.columns(2)

        # [CHART2]: Classification Distribution(Bar chart)
        with col1:
            chart_type_distribution(filtered_data, chart2_color)

        # Top 10 Masses (Bar chart)
        with col2:
            chart_top_mass_by_year(meteorite_data, selected_year_range, chart3_color)

        st.markdown("---")

    else:
        st.error("No data matches the current filter settings. Please adjust your selections in the sidebar.")

    # Filtered DataSet display
    st.subheader("Filtered Meteorite Data Table")
    st.dataframe(filtered_data)
    st.markdown("<hr>", unsafe_allow_html=True)

    # [ST3]: Displaying a reference image
    st.subheader('Reference: Meteorite Classifications')
    st.caption('Source: https://www.uky.edu/KGS/rocksmineral/meteorite-database.php')
    st.image('meteorite-classification-chart.jpg')


if __name__ == "__main__":
    main()

