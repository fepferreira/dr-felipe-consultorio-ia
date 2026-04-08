"""
Configurações do Sistema de Atendimento - Dr. Felipe Mendes
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== TWILIO ====================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "+1 415 523 8886")  # Sandbox
TWILIO_WEBHOOK_URL = os.getenv("TWILIO_WEBHOOK_URL", "http://localhost:8000/webhook/whatsapp")

# ==================== NOTION ====================
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "9ececefa7126479bbacfb72a175479da")

# ==================== OPENAI ====================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Já configurado no sandbox
OPENAI_MODEL = "gpt-4.1-mini"

# ==================== CONSULTÓRIO ====================
CONSULTORIO_NAME = "Dr. Felipe Mendes - Neurocirurgia"
CONSULTORIO_PHONE = "+55 31 99124-9411"
CONSULTORIO_EMAIL = "contato@drfelipemendes.com.br"
CONSULTORIO_WHATSAPP = "31 99124-9411"

# Horários de funcionamento
HORARIO_FUNCIONAMENTO = {
    "segunda": "08:00-18:00",
    "terca": "08:00-18:00",
    "quarta": "08:00-18:00",
    "quinta": "08:00-18:00",
    "sexta": "08:00-18:00",
    "sabado": "Fechado",
    "domingo": "Fechado"
}

# Locais de atendimento
LOCAIS_ATENDIMENTO = [
    {
        "nome": "Belo Horizonte",
        "endereco": "Rua Rio Grande do Norte, 23, 8º andar - Santa Efigênia",
        "telefone": "+55 31 99124-9411"
    },
    {
        "nome": "Sete Lagoas",
        "endereco": "Rua Paulo Frontin, 1172 - Centro",
        "telefone": "+55 31 99124-9411"
    }
]

# Especialidades e procedimentos
ESPECIALIDADES = [
    "Neurocirurgia",
    "Cirurgia da Coluna",
    "Procedimentos Minimamente Invasivos",
    "Endoscopia de Coluna"
]

PROCEDIMENTOS = [
    "Endoscopia de Coluna",
    "Bloqueios e Infiltrações",
    "Tratamento de Hérnia de Disco",
    "Cirurgia de Coluna",
    "Tratamento de Dor Crônica",
    "Segunda Opinião Médica",
    "Telemedicina"
]

# Canais de aquisição
CANAIS_AQUISICAO = [
    "Google Ads",
    "Google My Business",
    "Instagram",
    "Indicação",
    "Outro"
]

# ==================== SISTEMA DE TRIAGEM ====================
# Perguntas para triagem de urgência pós-operatória
PERGUNTAS_URGENCIA = [
    {
        "id": 1,
        "pergunta": "Você realizou sua cirurgia com o Dr. Felipe nos últimos 15 dias?",
        "tipo": "validacao",
        "critico": True
    },
    {
        "id": 2,
        "pergunta": "Está com dor intensa que não melhora com os medicamentos prescritos?",
        "tipo": "sintoma",
        "critico": True
    },
    {
        "id": 3,
        "pergunta": "Notou alguma dificuldade nova para movimentar os braços ou as pernas?",
        "tipo": "sintoma",
        "critico": True
    },
    {
        "id": 4,
        "pergunta": "Há saída de líquido ou secreção pela ferida operatória?",
        "tipo": "sintoma",
        "critico": True
    },
    {
        "id": 5,
        "pergunta": "O paciente apresenta sonolência excessiva ou confusão mental?",
        "tipo": "sintoma",
        "critico": True
    }
]

# Limiar para considerar urgência
URGENCIA_THRESHOLD = 2  # Se 2 ou mais sintomas críticos = urgência

# ==================== LOGGING ====================
LOG_LEVEL = "INFO"
LOG_FILE = "consultorio.log"

# ==================== AMBIENTE ====================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"
