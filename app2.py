import streamlit as st
import pandas as pd
import numpy as np
import itertools
import altair as alt

def load_coefficient_data(csv_path):
    """
    Carga y estructura los coeficientes desde el archivo CSV.
    Retorna un diccionario de diccionarios por año.
    """
    # Leer el CSV
    df = pd.read_csv(csv_path)
    
    # Obtener los años únicos
    years = [col for col in df.columns if col.isdigit()]
    
    # Diccionario para almacenar coeficientes por año
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
    """
    Calcula probabilidades para todos los años, provincias y trimestres.
    """
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
    
    results_df = pd.DataFrame(all_results).sort_values(
        by=['Year', 'Probability'], 
        ascending=[True, False]
    )
    return results_df

def initialize_session_state():
    """
    Inicializa el estado de la sesión si no existe.
    """
    if 'results_calculated' not in st.session_state:
        st.session_state.results_calculated = False
    if 'results_df' not in st.session_state:
        st.session_state.results_df = None
    if 'show_trends' not in st.session_state:
        st.session_state.show_trends = False
    if 'selected_year' not in st.session_state:
        st.session_state.selected_year = 'Todos'
    if 'selected_province' not in st.session_state:
        st.session_state.selected_province = 'Todas'

def calculate_and_store_results():
    """
    Calcula los resultados y los almacena en el estado de la sesión.
    """
    st.session_state.results_df = calculate_probability(
        st.session_state.selected_profile,
        st.session_state.coefficients_by_year
    )
    st.session_state.results_calculated = True

def main():
    st.title("Recomendador histórico de oportunidades laborales")
    
    # Inicializar el estado de la sesión
    initialize_session_state()
    
    try:
        # Cargar datos solo una vez y almacenarlos en session_state
        if 'coefficients_by_year' not in st.session_state:
            st.session_state.coefficients_by_year = load_coefficient_data('Book2.csv')
        
        # Obtener coeficientes del primer año
        first_year = list(st.session_state.coefficients_by_year.keys())[0]
        coefficients = st.session_state.coefficients_by_year[first_year]
        
        # Crear selectores para el perfil del usuario
        st.subheader("Perfil del usuario")
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.selectbox("Edad", list(coefficients['Age'].keys()), key='age')
            gender = st.selectbox("Género", list(coefficients['Gender'].keys()), key='gender')
            marstat = st.selectbox("Estado civil", list(coefficients['MarStat'].keys()), key='marstat')
        
        with col2:
            educ = st.selectbox("Nivel educativo", list(coefficients['Educ'].keys()), key='educ')
            inmig = st.selectbox("Estatus migratorio", list(coefficients['Inmig'].keys()), key='inmig')
            noc = st.selectbox("Ocupación (NOC)", list(coefficients['NOC'].keys()), key='noc')
        
        # Almacenar el perfil seleccionado en session_state
        st.session_state.selected_profile = {
            'Age': age,
            'Gender': gender,
            'MarStat': marstat,
            'Educ': educ,
            'Inmig': inmig,
            'NOC': noc
        }
        
        if st.button("Calcular probabilidades históricas"):
            calculate_and_store_results()
        
        # Mostrar resultados si se han calculado
        if st.session_state.results_calculated:
            st.subheader("Resultados históricos")
            
            # Filtros con estado persistente
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.selected_year = st.selectbox(
                    "Filtrar por año",
                    ['Todos'] + sorted(st.session_state.results_df['Year'].unique().tolist()),
                    key='year_filter'
                )
            with col2:
                st.session_state.selected_province = st.selectbox(
                    "Filtrar por provincia",
                    ['Todas'] + sorted(st.session_state.results_df['Province'].unique().tolist()),
                    key='province_filter'
                )
            
            # Aplicar filtros
            filtered_df = st.session_state.results_df.copy()
            if st.session_state.selected_year != 'Todos':
                filtered_df = filtered_df[filtered_df['Year'] == st.session_state.selected_year]
            if st.session_state.selected_province != 'Todas':
                filtered_df = filtered_df[filtered_df['Province'] == st.session_state.selected_province]
            
            # Mostrar resultados filtrados
            st.dataframe(filtered_df)
            
            # Checkbox para mostrar tendencias con estado persistente
            st.session_state.show_trends = st.checkbox(
                "Mostrar gráfico de tendencias",
                value=st.session_state.show_trends,
                key='show_trends_checkbox'
            )
            
            if st.session_state.show_trends:
                # Crear columna combinada de 'Year_Quarter'
                st.session_state.results_df['Year_Quarter'] = (
                    st.session_state.results_df['Year'].astype(str) + 
                    " Q" + st.session_state.results_df['Quarter'].astype(str)
                )
                
                # Crear gráfico con Altair
                chart = alt.Chart(st.session_state.results_df).mark_line().encode(
                    x='Year_Quarter:N',
                    y='Probability:Q',
                    color='Province:N',
                    tooltip=['Year', 'Quarter', 'Province', 'Probability']
                ).properties(
                    title="Tendencias de Probabilidad por Provincia"
                )
                
                st.altair_chart(chart, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error al cargar o procesar los datos: {str(e)}")
        st.write("Por favor, verifica que el archivo CSV está en el formato correcto y accesible.")

if __name__ == "__main__":
    main()
