import streamlit as st
import pandas as pd
import numpy as np
import itertools

# Configuración de los coeficientes (igual al código anterior)
coefficients = {
    'Intercept': -2.74,
    'Province': {
        'Newfoundland and Labrador':0.0,'Alberta': 0.32, 'British Columbia': 0.30, 'Manitoba': 0.37,
        'New Brunswick': 0.14, 'Nova Scotia': 0.14, 'Ontario': 0.23,
        'Prince Edward Island': 0.38, 'Quebec': 0.44, 'Saskatchewan': 0.38
    },
    'Age': {
        '15 to 19 years':0.0,'20 to 24 years': 0.48, '25 to 29 years': 0.97, '30 to 34 years': 1.08,
        '35 to 39 years': 1.12, '40 to 44 years': 1.17, '45 to 49 years': 1.14,
        '50 to 54 years': 0.94, '55 to 59 years': 0.37, '60 to 64 years': -0.40,
        '65 to 69 years': -1.42, '70 and over': -2.55
    },
    'Gender': {'Female':0.0,'Male': 0.39},
    'MarStat': {
        'Separated':0.0,'Divorced': 0.27, 'Living in common-law': 0.42,
        'Married': 0.44, 'Single, never married': -0.22, 'Widowed': -0.16
    },
    'Educ': {
        '0 to 8 years':0.0,"Above bachelor's degree": 1.48, "Bachelor's degree": 1.32,
        'High school graduate': 0.80, 'Postsecondary certificate or diploma': 1.18,
        'Some high school': -0.10, 'Some postsecondary': 0.69
    },
    'Inmig': {
        'Non-immigrant':0.0,'Immigrant, landed 10 or less years earlier': -0.35,
        'Immigrant, landed more than 10 years earlier': 0.07
    },
    'NOC': {
        'Occupations in art, culture, recreation and sport, except management':0.0,'Business, finance and administration occupations, except management': 3.14,
        'Health occupations, except management': 3.44, 'Management occupations': 1.83,
        'Natural and applied sciences and related occupations, except management': 0.74,
        'Natural resources, agriculture and related production occupations, except management': -0.18,
        'Occupations in education, law and social, community and government services, except management': 1.47,
        'Occupations in manufacturing and utilities, except management': 0.37,
        'Sales and service occupations, except management': 2.25,
        'Trades, transport and equipment operators and related occupations, except management': 2.83
    },
    'Quarter': {'Q1':0.0,'Q2': 0.10, 'Q3': 0.10, 'Q4': 0.04}
}

# Definir función para calcular la probabilidad
def calculate_probability(selected_profile):
    # Crear combinaciones de Province y Quarter, ya que NOC es elegido por el usuario
    combinations = list(itertools.product(
        coefficients['Province'].keys(),
        coefficients['Quarter'].keys()
    ))
    
    # Lista para almacenar resultados
    results = []
    
    for combo in combinations:
        logit = coefficients['Intercept']  # Empezar con el intercepto

        # Sumar coeficientes del perfil seleccionado
        for feature, category in selected_profile.items():
            logit += coefficients[feature][category]
        
        # Sumar coeficientes de la combinación
        logit += coefficients['Province'][combo[0]]
        logit += coefficients['Quarter'][combo[1]]
        
        # Calcular probabilidad
        probability = np.round((np.exp(logit) / (1 + np.exp(logit)))*100,2)        
        # Guardar resultado
        results.append({
            'Province': combo[0], 'Quarter': combo[1],
            'Logit': logit, 'Probability': probability
        })
    
    # Convertir a DataFrame y ordenar por probabilidad descendente
    results_df = pd.DataFrame(results).sort_values(by='Probability', ascending=False)
    return results_df

# Interfaz de usuario en Streamlit
st.title("Recomendador de oportunidades laborales")

# Listas desplegables para el perfil del usuario
age = st.selectbox("Selecciona tu edad", list(coefficients['Age'].keys()))
gender = st.selectbox("Selecciona tu género", list(coefficients['Gender'].keys()))
marstat = st.selectbox("Selecciona tu estado civil", list(coefficients['MarStat'].keys()))
educ = st.selectbox("Selecciona tu nivel educativo", list(coefficients['Educ'].keys()))
inmig = st.selectbox("Selecciona tu estatus migratorio", list(coefficients['Inmig'].keys()))
noc = st.selectbox("Selecciona el tipo de ocupación (NOC)", list(coefficients['NOC'].keys()))

# Almacenar el perfil seleccionado
selected_profile = {
    'Age': age,
    'Gender': gender,
    'MarStat': marstat,
    'Educ': educ,
    'Inmig': inmig,
    'NOC': noc
}

# Calcular y mostrar las recomendaciones
if st.button("Calcular mejores oportunidades"):
    results_df = calculate_probability(selected_profile)
    st.write("Recomendaciones basadas en tu perfil (ordenadas por probabilidad):")
    st.write(results_df)  # Mostrar todas las combinaciones sin limitar el número de resultados
