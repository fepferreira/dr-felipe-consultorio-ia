"""
Aplicação principal FastAPI para o sistema de atendimento
Dr. Felipe Mendes - Consultório de Neurocirurgia
"""

import logging
import json
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from config import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER,
    NOTION_API_KEY, NOTION_DATABASE_ID, OPENAI_API_KEY, OPENAI_MODEL,
    LOG_LEVEL, CONSULTORIO_NAME, PERGUNTAS_URGENCIA,
    URGENCIA_THRESHOLD, CONSULTORIO_PHONE
)
from services.twilio_service import TwilioService
from services.ai_agent import AIAgent
from services.notion_service import NotionService

# ==================== CONFIGURAÇÃO ====================

# Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI
app = FastAPI(
    title="Sistema de Atendimento Dr. Felipe Mendes",
    description="API para atendimento de pacientes via WhatsApp com IA",
    version="1.0.0"
)

# Serviços
twilio_service = TwilioService(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    "+1 415 523 8886"  # Número do sandbox do Twilio
)

ai_agent = AIAgent(OPENAI_API_KEY, OPENAI_MODEL)

notion_service = NotionService(NOTION_API_KEY, NOTION_DATABASE_ID)

# Estado da conversa (em memória)
conversas_ativas = {}  # {telefone: {"estado": "triagem|agendamento|urgencia", "dados": {...}}}
pacientes_db = {}  # {telefone: {dados do paciente}}

# ==================== ROTAS ====================

@app.get("/health")
async def health_check():
    """Verifica saúde da aplicação"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": CONSULTORIO_NAME
    }


@app.post("/webhook/whatsapp")
async def webhook_whatsapp(request: Request):
    """
    Webhook para receber mensagens do Twilio WhatsApp
    """
    try:
        # Recebe dados do Twilio
        form_data = await request.form()
        
        telefone = form_data.get("From", "").replace("whatsapp:", "")
        mensagem_texto = form_data.get("Body", "").strip()
        message_sid = form_data.get("MessageSid", "")
        
        logger.info(f"Mensagem recebida de {telefone}: {mensagem_texto[:50]}...")
        
        # Processa a mensagem
        resposta = await processar_mensagem_paciente(
            telefone, mensagem_texto, message_sid
        )
        
        # Envia resposta via Twilio
        if resposta:
            twilio_service.enviar_mensagem(telefone, resposta)
            logger.info(f"Resposta enviada para {telefone}")
        
        return JSONResponse({"status": "success"})
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}", exc_info=True)
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.get("/api/pacientes/{telefone}")
async def obter_paciente(telefone: str):
    """Obtém informações de um paciente"""
    try:
        telefone_limpo = telefone.replace("%2B", "+")
        
        if telefone_limpo in pacientes_db:
            return pacientes_db[telefone_limpo]
        else:
            return JSONResponse({"error": "Paciente não encontrado"}, status_code=404)
            
    except Exception as e:
        logger.error(f"Erro ao buscar paciente: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/conversas/{telefone}")
async def obter_conversa(telefone: str):
    """Obtém histórico de conversa com um paciente"""
    try:
        telefone_limpo = telefone.replace("%2B", "+")
        
        if telefone_limpo in conversas_ativas:
            return conversas_ativas[telefone_limpo]
        else:
            return JSONResponse({"error": "Conversa não encontrada"}, status_code=404)
            
    except Exception as e:
        logger.error(f"Erro ao buscar conversa: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/agendamentos")
async def criar_agendamento(request: Request):
    """Cria um novo agendamento"""
    try:
        dados = await request.json()
        
        # Valida dados
        telefone = dados.get("telefone")
        data = dados.get("data")
        hora = dados.get("hora")
        
        if not all([telefone, data, hora]):
            return JSONResponse(
                {"error": "Dados incompletos"},
                status_code=400
            )
        
        # Salva agendamento
        agendamento = {
            "telefone": telefone,
            "data": data,
            "hora": hora,
            "status": "confirmado",
            "criado_em": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Agendamento criado para {telefone}: {data} às {hora}")
        
        return JSONResponse(agendamento)
        
    except Exception as e:
        logger.error(f"Erro ao criar agendamento: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)


# ==================== FUNÇÕES AUXILIARES ====================

async def processar_mensagem_paciente(
    telefone: str,
    mensagem: str,
    message_sid: str
) -> Optional[str]:
    """Processa mensagem de um paciente e retorna resposta"""
    
    try:
        # Inicializa conversa se não existe
        if telefone not in conversas_ativas:
            conversas_ativas[telefone] = {
                "estado": "triagem",
                "mensagens": [],
                "dados": {}
            }
        
        conversa = conversas_ativas[telefone]
        
        # Adiciona mensagem do paciente
        conversa["mensagens"].append({
            "role": "user",
            "content": mensagem,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Verifica se é urgência pós-operatória
        if await detectar_urgencia(telefone, mensagem, conversa):
            resposta = await processar_urgencia(telefone, conversa)
        else:
            # Processa com IA
            resposta = await ai_agent.processar_mensagem(
                mensagem,
                conversa.get("dados", {}),
                PERGUNTAS_URGENCIA
            )
        
        # Adiciona resposta do bot
        if resposta:
            conversa["mensagens"].append({
                "role": "assistant",
                "content": resposta,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Sincroniza com Notion
            await sincronizar_notion(telefone, conversa)
        
        return resposta
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)
        return "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."


async def detectar_urgencia(
    telefone: str,
    mensagem: str,
    conversa: Dict
) -> bool:
    """Detecta se a mensagem indica urgência pós-operatória"""
    
    try:
        # Palavras-chave de urgência
        palavras_urgencia = [
            "febre", "sangramento", "dor", "dificuldade",
            "secreção", "sonolência", "urgência", "emergência"
        ]
        
        mensagem_lower = mensagem.lower()
        
        # Verifica se contém palavras de urgência
        tem_urgencia = any(palavra in mensagem_lower for palavra in palavras_urgencia)
        
        # Verifica se está em período pós-operatório
        em_pos_op = conversa.get("dados", {}).get("em_pos_operatorio", False)
        
        return tem_urgencia and em_pos_op
        
    except Exception as e:
        logger.error(f"Erro ao detectar urgência: {str(e)}")
        return False


async def processar_urgencia(telefone: str, conversa: Dict) -> str:
    """Processa caso de urgência"""
    
    try:
        # Envia alerta para o médico
        mensagem_alerta = f"""
        ⚠️ URGÊNCIA PÓS-OPERATÓRIA
        
        Paciente: {telefone}
        Dados: {json.dumps(conversa.get('dados', {}), indent=2)}
        
        Últimas mensagens:
        {json.dumps(conversa.get('mensagens', [])[-3:], indent=2)}
        """
        
        logger.warning(f"URGÊNCIA DETECTADA: {telefone}")
        
        # Envia SMS/WhatsApp para o médico
        try:
            twilio_service.enviar_mensagem(
                CONSULTORIO_PHONE,
                mensagem_alerta
            )
        except Exception as e:
            logger.error(f"Erro ao enviar alerta: {str(e)}")
        
        return "Detectamos sintomas que requerem atenção imediata. O Dr. Felipe foi notificado e entrará em contato em breve."
        
    except Exception as e:
        logger.error(f"Erro ao processar urgência: {str(e)}")
        return "Erro ao processar sua solicitação de urgência."


async def sincronizar_notion(telefone: str, conversa: Dict) -> bool:
    """Sincroniza dados com Notion"""
    
    try:
        # Prepara dados para Notion
        dados_notion = {
            "Nome": conversa.get("dados", {}).get("nome", "Desconhecido"),
            "Telefone": telefone,
            "Última mensagem": conversa.get("mensagens", [])[-1].get("content", "") if conversa.get("mensagens") else "",
            "Data último contato": datetime.utcnow().isoformat(),
            "Status": conversa.get("estado", "triagem")
        }
        
        # Sincroniza com Notion
        resultado = notion_service.criar_pagina(dados_notion)
        
        if resultado:
            logger.info(f"Dados sincronizados com Notion para {telefone}")
            return True
        else:
            logger.warning(f"Falha ao sincronizar com Notion para {telefone}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao sincronizar com Notion: {str(e)}")
        return False


# ==================== INICIALIZAÇÃO ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
