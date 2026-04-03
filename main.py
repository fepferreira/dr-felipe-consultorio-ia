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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER,
    NOTION_API_KEY, NOTION_DATABASE_ID, OPENAI_API_KEY, OPENAI_MODEL,
    DATABASE_URL, LOG_LEVEL, CONSULTORIO_NAME, PERGUNTAS_URGENCIA,
    URGENCIA_THRESHOLD, CONSULTORIO_PHONE
)
from models import Base, Paciente, Conversa, Agendamento, Urgencia, SincronizacaoNotion
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

# Banco de dados
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Serviços
twilio_service = TwilioService(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER
)

ai_agent = AIAgent(OPENAI_API_KEY, OPENAI_MODEL)

notion_service = NotionService(NOTION_API_KEY, NOTION_DATABASE_ID)

# Estado da conversa
conversas_ativas = {}  # {telefone: {"estado": "triagem|agendamento|urgencia", "dados": {...}}}

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
        
        # Inicializa banco de dados
        db = SessionLocal()
        
        try:
            # Processa a mensagem
            resposta = await processar_mensagem_paciente(
                db, telefone, mensagem_texto, message_sid
            )
            
            # Envia resposta via Twilio
            if resposta:
                twilio_service.enviar_mensagem(telefone, resposta)
                logger.info(f"Resposta enviada para {telefone}")
            
            return JSONResponse({"status": "success"})
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}", exc_info=True)
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.post("/webhook/whatsapp/status")
async def webhook_status(request: Request):
    """
    Webhook para receber status de mensagens do Twilio
    """
    try:
        form_data = await request.form()
        message_sid = form_data.get("MessageSid", "")
        message_status = form_data.get("MessageStatus", "")
        
        logger.info(f"Status da mensagem {message_sid}: {message_status}")
        
        return JSONResponse({"status": "success"})
        
    except Exception as e:
        logger.error(f"Erro ao processar status: {str(e)}")
        return JSONResponse({"status": "error"}, status_code=500)


@app.post("/api/agendamento/criar")
async def criar_agendamento(dados: Dict):
    """
    Cria um novo agendamento
    """
    try:
        db = SessionLocal()
        
        try:
            # Cria agendamento
            agendamento = Agendamento(
                paciente_id=dados.get("paciente_id"),
                telefone=dados.get("telefone"),
                data_agendamento=datetime.fromisoformat(dados.get("data_agendamento")),
                local=dados.get("local"),
                tipo_consulta=dados.get("tipo_consulta"),
                confirmado=True
            )
            
            db.add(agendamento)
            db.commit()
            db.refresh(agendamento)
            
            logger.info(f"Agendamento criado: {agendamento.id}")
            
            return {
                "status": "success",
                "agendamento_id": agendamento.id,
                "message": "Agendamento confirmado com sucesso!"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro ao criar agendamento: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/pacientes/{telefone}")
async def obter_paciente(telefone: str):
    """
    Obtém dados de um paciente pelo telefone
    """
    try:
        db = SessionLocal()
        
        try:
            paciente = db.query(Paciente).filter(Paciente.telefone == telefone).first()
            
            if not paciente:
                raise HTTPException(status_code=404, detail="Paciente não encontrado")
            
            return {
                "id": paciente.id,
                "nome": paciente.nome,
                "telefone": paciente.telefone,
                "email": paciente.email,
                "cidade": paciente.cidade,
                "canal_aquisicao": paciente.canal_aquisicao,
                "agendou_consulta": paciente.agendou_consulta,
                "em_pos_operatorio": paciente.em_pos_operatorio
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro ao obter paciente: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== FUNÇÕES AUXILIARES ====================

async def processar_mensagem_paciente(db: Session, telefone: str, mensagem: str, message_sid: str) -> Optional[str]:
    """
    Processa mensagem de um paciente
    
    Args:
        db: Sessão do banco de dados
        telefone: Telefone do paciente
        mensagem: Conteúdo da mensagem
        message_sid: ID da mensagem no Twilio
        
    Returns:
        Resposta a enviar para o paciente
    """
    try:
        # Busca ou cria paciente
        paciente = db.query(Paciente).filter(Paciente.telefone == telefone).first()
        
        if not paciente:
            # Novo paciente
            paciente = Paciente(
                nome="",  # Será preenchido pela IA
                telefone=telefone,
                data_primeiro_contato=datetime.utcnow()
            )
            db.add(paciente)
            db.commit()
            db.refresh(paciente)
            logger.info(f"Novo paciente criado: {telefone}")
        
        # Atualiza último contato
        paciente.data_ultimo_contato = datetime.utcnow()
        
        # Registra conversa
        conversa = Conversa(
            paciente_id=paciente.id,
            telefone=telefone,
            tipo="usuario",
            mensagem=mensagem,
            sessao_id=message_sid
        )
        db.add(conversa)
        
        # Processa com IA
        resposta_ia, metadata = ai_agent.processar_mensagem(telefone, mensagem)
        
        # Registra resposta da IA
        conversa_resposta = Conversa(
            paciente_id=paciente.id,
            telefone=telefone,
            tipo="assistente",
            mensagem=resposta_ia,
            sessao_id=message_sid
        )
        db.add(conversa_resposta)
        
        # Verifica se precisa triagem de urgência
        if "pós-operatório" in mensagem.lower() or "cirurgia" in mensagem.lower():
            paciente.em_pos_operatorio = True
        
        # Sincroniza com Notion
        dados_paciente = {
            "telefone": telefone,
            "motivo_contato": mensagem[:500]
        }
        
        if paciente.nome:
            dados_paciente["nome"] = paciente.nome
        
        notion_service.criar_ou_atualizar_paciente(dados_paciente)
        
        db.commit()
        
        logger.info(f"Mensagem processada para {telefone}")
        
        return resposta_ia
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)
        return "Desculpe, tive um problema ao processar sua mensagem. Pode tentar novamente?"


# ==================== INICIALIZAÇÃO ====================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Iniciando {CONSULTORIO_NAME}")
    logger.info(f"Ambiente: production")
    logger.info(f"Webhook URL: /webhook/whatsapp")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=LOG_LEVEL.lower()
    )
