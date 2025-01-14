import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
import os
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Obter a chave da API do ambiente
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("A chave da API não foi encontrada. Defina a variável GOOGLE_API_KEY no ambiente.")
else:
    genai.configure(api_key=api_key)  # Configuração da API

# Configuração do Streamlit
st.set_page_config(page_title="kakttus IA", layout="wide")

st.title("🤖 MODELO HEMOSTASYS V1")
st.markdown("""
**Bem-vindo à HEMOSTASYS!**

Converse perfeitamente com os modelos avançados KAKTTUS SOLUTIONS, suportando entradas de texto e imagem.
Siga-me para mais projetos inovadores e atualizações!
""")

# Função para converter a imagem em Base64
def encode_image(image):
    """Converte uma imagem PIL para uma string base64"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    return encoded_image

# Função para extrair dados do gráfico
def extract_data_from_image(image):
    """Envia a imagem para o modelo e extrai os dados do gráfico"""
    base64_image = encode_image(image)
    
    prompt = """
    Extraia os valores do gráfico na imagem e retorne um JSON **estritamente** no seguinte formato, sem explicações adicionais:

    {
        "identificacao_paciente": {
            "nome": "Paciente",
            "ID": "0000000"
        },
        "datas_horarios": {
            "data_exame": "ST",  # ST representa a data do exame no gráfico
            "hora_exame": "RT"   # RT representa a hora do exame no gráfico
        },
        "resultados_metricas": {
            "FIBTEM C": {
                "data_exame": "ST",
                "hora_exame": "RT",
                "CT": "0",
                "CFT": "0",
                "A5": "0",
                "A10": "0",
                "A20": "0",
                "A30": "0",
                "MCF": "0"
            },
            "EXTEM C": {
                "data_exame": "ST",
                "hora_exame": "RT",
                "CT": "0",
                "CFT": "0",
                "A5": "0",
                "A10": "0",
                "A20": "0",
                "A30": "0",
                "MCF": "0"
            },
            "INTEM C": {
                "data_exame": "ST",
                "hora_exame": "RT",
                "CT": "0",
                "CFT": "0",
                "A5": "0",
                "A10": "0",
                "A20": "0",
                "A30": "0",
                "MCF": "0"
            },
            "HEPTEM C": {
                "data_exame": "ST",
                "hora_exame": "RT",
                "CT": "0",
                "CFT": "0",
                "A5": "0",
                "A10": "0",
                "A20": "0",
                "A30": "0",
                "MCF": "0"
            }
        }
    }

    - **A saída deve ser 100% JSON válido.**
    - **Não inclua explicações nem texto extra, apenas o JSON puro.**
    - **Se houver erro ao ler os valores, retorne "0" ao invés de valores ausentes.**
    - **A resposta não pode conter código formatado ou markdown, apenas JSON.**
    """

    model_instance = genai.GenerativeModel(model_name="gemini-1.5-flash")
    content = [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}]

    try:
        response = model_instance.generate_content(
            content,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1000
            )
        )

        # Verifica se a resposta contém um JSON válido
        response_text = response.text if hasattr(response, "text") else None
        if response_text:
            response_text = response_text.strip()
            # Remove possível formatação extra de markdown ou código ```json
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            if response_text.startswith("{") and response_text.endswith("}"):
                return json.loads(response_text)  # Converte para JSON e retorna
            else:
                return {"error": "A resposta não está no formato JSON esperado."}
        else:
            return {"error": "Resposta da API vazia."}

    except json.JSONDecodeError:
        return {"error": "Erro ao converter resposta da API para JSON."}
    except Exception as e:
        return {"error": f"Erro na extração dos dados: {str(e)}"}


# Carregador de arquivos para imagens
uploaded_file = st.file_uploader("Carregar uma imagem (exames)", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    uploaded_image = Image.open(uploaded_file).convert('RGB')
    st.image(uploaded_image, caption="Imagem Carregada", use_container_width=True)
    
    # Extração automática de dados assim que a imagem é carregada
    extracted_json = extract_data_from_image(uploaded_image)
    st.json(extracted_json)

# Instruções na barra lateral
with st.sidebar:
    st.markdown("""
    ## 📝 KAKTTUS - HEMOSTASYS V1:
    1. A extração das informalões foi desenvolvida apenas para o exame ROTEM
    2. O modelo utilizado foi treinado com as informações do processo do app HEMOSTASYS
    3. Ajuste a temperatura e o máximo de tokens, se necessário
    4. Carregue uma imagem contendo gráficos de exames
    ### Direitos Autorais
    Kakttus Soluções
    """)
