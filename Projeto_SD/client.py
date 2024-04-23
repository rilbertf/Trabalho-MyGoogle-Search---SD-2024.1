import streamlit as st
import requests
import numpy as np
import time

# URL do backend, ajuste conforme necessário
BACKEND_URL = "http://localhost:8000"


def perform_requests(rate, duration=60):
    """ Executa requisições HTTP a uma taxa específica e mede os tempos de resposta. """
    interval = 1 / rate
    response_times = []
    start_time = time.time()
    while time.time() - start_time < duration:
        request_start = time.time()
        response = requests.get(f"{BACKEND_URL}/search/?query=example")
        request_end = time.time()
        response_times.append(request_end - request_start)
        time.sleep(max(0, interval - (request_end - request_start)))
    return response_times


def calculate_statistics(times):
    """ Calcula estatísticas sobre os tempos de resposta filtrando os 5% maiores e menores valores. """
    times = np.array(times)
    q_low = np.percentile(times, 5)
    q_high = np.percentile(times, 95)
    filtered_times = times[(times >= q_low) & (times <= q_high)]
    mean_time = np.mean(filtered_times)
    median_time = np.median(filtered_times)
    std_dev = np.std(filtered_times)
    return mean_time, median_time, std_dev


# Interface do usuário com guias
tab1, tab2 = st.tabs(["Uso Regular", "Teste de Desempenho"])

with tab1:
    st.header("MyGoogle Search - Interface de Uso Regular")

    # Upload de artigos e arquivos
    with st.form("upload_form"):
        title = st.text_input("Título do Artigo:")
        text = st.text_area("Texto do Artigo:")
        uploaded_file = st.file_uploader("Ou escolha um arquivo para upload (texto):", type=['txt'])
        submit_button = st.form_submit_button("Upload")

        if submit_button:
            if uploaded_file is not None:
                file_content = uploaded_file.getvalue().decode("utf-8")
                data = {"title": title, "text": file_content}
            else:
                data = {"title": title, "text": text}

            response = requests.post(f"{BACKEND_URL}/upload/", json=data)
            if response.status_code == 200:
                response_data = response.json()
                st.success(f"Artigo enviado com sucesso! ID: {response_data['id']}")
            else:
                st.error("Falha ao enviar o artigo.")

    # Remoção de artigos
    article_id_to_delete = st.text_input("Digite o ID do artigo para remover:")
    if st.button("Remover Artigo"):
        response = requests.delete(f"{BACKEND_URL}/delete/{article_id_to_delete}")
        if response.status_code == 200:
            st.success("Artigo removido com sucesso!")
        else:
            st.error("Falha ao remover o artigo. Verifique o ID e tente novamente.")

    # Busca de palavras-chave
    query = st.text_input("Digite a palavra chave para busca:")
    if st.button('Buscar'):
        response = requests.get(f"{BACKEND_URL}/search/", params={"query": query})
        if response.ok:
            results = response.json()
            st.write(f"Total de artigos encontrados: {results['total']}")
            for result in results['results']:
                st.write(f"ID: {result['id']} - {result['title']} - {result['text']}")

    # Listar artigos
    if st.button('Listar Artigos'):
        response = requests.get(f"{BACKEND_URL}/articles/")
        if response.ok:
            articles = response.json()
            st.write(f"Total de artigos listados: {len(articles)}")
            for article in articles:
                st.write(f"ID: {article['id']} - {article['title']} - {article['text']}")

with tab2:
    st.header("MyGoogle Search - Teste de Desempenho")
    rate = st.selectbox('Escolha a taxa de requisição por segundo:', options=[50, 100, 200, 400])
    if st.button('Iniciar Teste'):
        with st.spinner(f'Executando teste de carga a {rate} reqs/segundo...'):
            times = perform_requests(rate)
            mean_time, median_time, std_dev = calculate_statistics(times)
            st.write(f"Tempo médio de resposta: {mean_time:.4f} segundos")
            st.write(f"Mediana do tempo de resposta: {median_time:.4f} segundos")
            st.write(f"Desvio padrão do tempo de resposta: {std_dev:.4f} segundos")
