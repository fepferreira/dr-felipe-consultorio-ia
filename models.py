"""
Modelos de dados para o sistema de atendimento
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Paciente(Base):
    """Modelo para armazenar dados dos pacientes"""
    __tablename__ = "pacientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    telefone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    cidade = Column(String(100), nullable=True)
    
    # Informações de contato
    canal_aquisicao = Column(String(50), nullable=True)  # Google Ads, Instagram, etc
    motivo_contato = Column(Text, nullable=True)
    data_primeiro_contato = Column(DateTime, default=datetime.utcnow)
    data_ultimo_contato = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status do atendimento
    agendou_consulta = Column(Boolean, default=False)
    consulta_realizada = Column(Boolean, default=False)
    data_consulta = Column(DateTime, nullable=True)
    
    # Informações médicas
    valor_potencial = Column(Float, nullable=True)
    convenio = Column(String(100), nullable=True)
    motivo_negativa = Column(Text, nullable=True)
    
    # Pós-operatório
    em_pos_operatorio = Column(Boolean, default=False)
    data_cirurgia = Column(DateTime, nullable=True)
    dias_pos_operatorio = Column(Integer, default=0)
    
    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Paciente(id={self.id}, nome={self.nome}, telefone={self.telefone})>"


class Conversa(Base):
    """Modelo para armazenar histórico de conversas"""
    __tablename__ = "conversas"
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, nullable=False, index=True)
    telefone = Column(String(20), nullable=False, index=True)
    
    # Conteúdo da mensagem
    tipo = Column(String(20), nullable=False)  # "usuario" ou "assistente"
    mensagem = Column(Text, nullable=False)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    sessao_id = Column(String(100), nullable=True, index=True)
    
    def __repr__(self):
        return f"<Conversa(id={self.id}, paciente_id={self.paciente_id}, tipo={self.tipo})>"


class Agendamento(Base):
    """Modelo para armazenar agendamentos"""
    __tablename__ = "agendamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, nullable=False, index=True)
    telefone = Column(String(20), nullable=False)
    
    # Detalhes do agendamento
    data_agendamento = Column(DateTime, nullable=False, index=True)
    local = Column(String(100), nullable=False)  # BH ou Sete Lagoas
    tipo_consulta = Column(String(50), nullable=False)  # Presencial ou Telemedicina
    
    # Status
    confirmado = Column(Boolean, default=False)
    compareceu = Column(Boolean, default=False)
    cancelado = Column(Boolean, default=False)
    motivo_cancelamento = Column(Text, nullable=True)
    
    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Agendamento(id={self.id}, paciente_id={self.paciente_id}, data={self.data_agendamento})>"


class Urgencia(Base):
    """Modelo para armazenar casos de urgência detectados"""
    __tablename__ = "urgencias"
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, nullable=False, index=True)
    telefone = Column(String(20), nullable=False, index=True)
    
    # Informações da urgência
    tipo = Column(String(50), nullable=False)  # "pos_operatorio", "dor_aguda", etc
    descricao = Column(Text, nullable=False)
    sintomas = Column(Text, nullable=False)  # JSON com sintomas relatados
    
    # Respostas às perguntas de triagem
    respostas_triagem = Column(Text, nullable=True)  # JSON com respostas
    score_urgencia = Column(Integer, default=0)  # 0-10
    
    # Status
    notificado_medico = Column(Boolean, default=False)
    data_notificacao = Column(DateTime, nullable=True)
    resolvido = Column(Boolean, default=False)
    data_resolucao = Column(DateTime, nullable=True)
    
    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow, index=True)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Urgencia(id={self.id}, paciente_id={self.paciente_id}, tipo={self.tipo})>"


class SincronizacaoNotion(Base):
    """Modelo para rastrear sincronizações com Notion"""
    __tablename__ = "sincronizacao_notion"
    
    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, nullable=False, index=True)
    notion_page_id = Column(String(100), nullable=True)
    
    # Status da sincronização
    sincronizado = Column(Boolean, default=False)
    ultima_sincronizacao = Column(DateTime, nullable=True)
    proxima_sincronizacao = Column(DateTime, nullable=True)
    
    # Dados sincronizados
    dados_sincronizados = Column(Text, nullable=True)  # JSON
    
    # Timestamps
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SincronizacaoNotion(id={self.id}, paciente_id={self.paciente_id})>"
