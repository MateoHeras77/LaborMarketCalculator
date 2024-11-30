import streamlit as st
import pandas as pd
import numpy as np
import itertools
import plotly.express as px
import json
from urllib.request import urlopen

def load_coefficient_data(csv_path):
    df = pd.read_csv(csv_path)
    years = [col for col in df.columns if col.isdigit()]
    coefficients_by_year = {}
    for year in years:
        coefficients = {
            'Intercept': df[df['Base Category'] == 'Intercept'][year].iloc[0]
        }
        for base_category in df['Base Category'].unique():
            if base_category != 'Intercept':
                category_data = df[df['Base Category'] == base_category]
                coefficients[base_category] = dict(zip(category_data['Categories'], 
                                                     category_data[year]))
        coefficients_by_year[year] = coefficients
    return coefficients_by_year

def calculate_probability(selected_profile, coefficients_by_year):
    all_results = []
    for year, coefficients in coefficients_by_year.items():
        combinations = list(itertools.product(
            coefficients['Province'].keys(),
            coefficients['Quarter'].keys()
        ))
        for combo in combinations:
            logit = coefficients['Intercept']
            for feature, category in selected_profile.items():
                logit += coefficients[feature][category]
            logit += coefficients['Province'][combo[0]]
            logit += coefficients['Quarter'][combo[1]]
            probability = np.round((np.exp(logit) / (1 + np.exp(logit))) * 100, 2)
            all_results.append({
                'Year': year,
                'Province': combo[0],
                'Quarter': combo[1],
                'Probability': probability
            })
    
    results_df = pd.DataFrame(all_results).sort_values(by=['Year', 'Probability'], ascending=[True, False])
    return results_df

def initialize_session_state():
    if 'results_calculated' not in st.session_state:
        st.session_state.results_calculated = False
    if 'results_df' not in st.session_state:
        st.session_state.results_df = None
    if 'show_trends' not in st.session_state:
        st.session_state.show_trends = False
    if 'selected_year' not in st.session_state:
        st.session_state.selected_year = 'All'
    if 'selected_province' not in st.session_state:
        st.session_state.selected_province = 'All'
    if 'graph_province' not in st.session_state:
        st.session_state.graph_province = 'All'

def calculate_and_store_results():
    st.session_state.results_df = calculate_probability(
        st.session_state.selected_profile,
        st.session_state.coefficients_by_year
    )
    st.session_state.results_calculated = True

@st.cache_data
def load_canada_geojson():
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/canada.geojson"
    with urlopen(geojson_url) as response:
        canada_geojson = json.load(response)
    return canada_geojson

def main():
    st.title("Historical Job Opportunities Recommender")

    st.sidebar.title("About the Author")
    st.sidebar.markdown(""" 
    **Author**: Wilmer Mateo Heras Vera  
    **University**: University of Niagara Falls  
    **Email**: [wmateohv@hotmail.com](mailto:wmateohv@hotmail.com)  
    **LinkedIn**: [linkedin.com/in/mateoheras](https://www.linkedin.com/in/mateoheras/)  
    ![Logo](https://unfc.ca/wp-content/uploads/2023/04/UNF-logo-full.svg)
    """, unsafe_allow_html=True)

    initialize_session_state()
    
    try:
        if 'coefficients_by_year' not in st.session_state:
            st.session_state.coefficients_by_year = load_coefficient_data('Book2.csv')
        
        first_year = list(st.session_state.coefficients_by_year.keys())[0]
        coefficients = st.session_state.coefficients_by_year[first_year]
        
        st.subheader("User Profile")
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.selectbox("Age", list(coefficients['Age'].keys()), key='age')
            gender = st.selectbox("Gender", list(coefficients['Gender'].keys()), key='gender')
            marstat = st.selectbox("Marital Status", list(coefficients['MarStat'].keys()), key='marstat')
        
        with col2:
            educ = st.selectbox("Education Level", list(coefficients['Educ'].keys()), key='educ')
            inmig = st.selectbox("Migration Status", list(coefficients['Inmig'].keys()), key='inmig')
            noc = st.selectbox("Occupation (NOC)", list(coefficients['NOC'].keys()), key='noc')
        
        st.session_state.selected_profile = {
            'Age': age,
            'Gender': gender,
            'MarStat': marstat,
            'Educ': educ,
            'Inmig': inmig,
            'NOC': noc
        }
        
        if st.button("Calculate Historical Probabilities"):
            calculate_and_store_results()
        
        if st.session_state.results_calculated:
            st.subheader("Historical Results")
            
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.selected_year = st.selectbox(
                    "Filter by Year",
                    ['All'] + sorted(st.session_state.results_df['Year'].unique().tolist()),
                    key='year_filter'
                )
            with col2:
                st.session_state.selected_province = st.selectbox(
                    "Filter by Province in Table",
                    ['All'] + sorted(st.session_state.results_df['Province'].unique().tolist()),
                    key='province_filter'
                )
            
            filtered_df = st.session_state.results_df.copy()
            if st.session_state.selected_year != 'All':
                filtered_df = filtered_df[filtered_df['Year'] == st.session_state.selected_year]
            if st.session_state.selected_province != 'All':
                filtered_df = filtered_df[filtered_df['Province'] == st.session_state.selected_province]

            filtered_df_styled = filtered_df[['Year', 'Province', 'Quarter', 'Probability']]
            st.dataframe(filtered_df_styled.style.format({'Probability': "{:.2f}%"}))

            # Choropleth Map Section
            st.subheader("Provincial Employment Probability Map")
            
            # Calculate average probability by province for choropleth map
            if st.session_state.selected_year != 'All':
                map_data = filtered_df[filtered_df['Year'] == st.session_state.selected_year]
            else:
                map_data = filtered_df

            # Create a complete list of all Canadian provinces
            all_provinces = [
                'Alberta', 'British Columbia', 'Manitoba', 'New Brunswick',
                'Newfoundland and Labrador', 'Northwest Territories', 'Nova Scotia',
                'Nunavut', 'Ontario', 'Prince Edward Island', 'Quebec', 'Saskatchewan',
                'Yukon'
            ]

            # Calculate averages for provinces with data
            avg_prob_by_province = map_data.groupby('Province')['Probability'].mean().reset_index()
            
            # Create a complete DataFrame with all provinces
            complete_provinces_df = pd.DataFrame({'Province': all_provinces})
            avg_prob_by_province = pd.merge(
                complete_provinces_df,
                avg_prob_by_province,
                on='Province',
                how='left'
            )

            # Get min and max values for color scale (only from provinces with data)
            min_prob = avg_prob_by_province['Probability'].min()
            max_prob = avg_prob_by_province['Probability'].max()
            
            # Load GeoJSON data
            canada_geojson = load_canada_geojson()

            # Create choropleth map with updated settings
            fig_choropleth = px.choropleth(
                avg_prob_by_province,
                geojson=canada_geojson,
                locations='Province',
                featureidkey='properties.name',
                color='Probability',
                color_continuous_scale=['red', 'yellow', 'green'],  # Red to Green scale
                range_color=[min_prob, max_prob],  # Dynamic range based on data
                labels={'Probability': 'Average Probability (%)'},
                title=f"Employment Probability by Province {st.session_state.selected_year}"
            )

            # Update map layout
            fig_choropleth.update_geos(
                fitbounds="locations",
                visible=False,
            )

            fig_choropleth.update_layout(
                margin={"r":0,"t":30,"l":0,"b":0},
                height=500
            )

            # Update missing values to be transparent
            fig_choropleth.update_traces(
                marker_line_color='darkgray',
                marker_line_width=1,
                showscale=True
            )

            # Display the choropleth map
            st.plotly_chart(fig_choropleth, use_container_width=True)

            # Trends Graph Section
            st.session_state.graph_province = st.selectbox(
                "Select Province for Trend Graph",
                ['All'] + sorted(st.session_state.results_df['Province'].unique().tolist()),
                key='graph_province_filter'
            )

            st.session_state.show_trends = st.checkbox(
                "Show Trends Graph",
                value=st.session_state.show_trends,
                key='show_trends_checkbox'
            )
            
            if st.session_state.show_trends:
                graph_df = st.session_state.results_df.copy()
                if st.session_state.graph_province != 'All':
                    graph_df = graph_df[graph_df['Province'] == st.session_state.graph_province]
                
                graph_df['Year_Quarter'] = graph_df['Year'] + "-Q" + graph_df['Quarter'].astype(str)
                
                fig = px.line(
                    graph_df, 
                    x='Year_Quarter', 
                    y='Probability', 
                    color='Province', 
                    line_group='Province', 
                    title="Probability Trends by Province",
                    labels={"Year_Quarter": "Year and Quarter", "Probability": "Probability (%)"},
                    markers=False
                )
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error loading or processing data: {str(e)}")
        st.write("Please verify that the CSV file is correctly formatted and accessible.")

    st.markdown("""
    <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f5f5f5;
            color: black;
            text-align: center;
            padding: 10px;
            font-size: 12px;
        }
    </style>
    <div class="footer">
        Developed by Wilmer Mateo Heras Vera | © 2024 Niagara Falls University
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
