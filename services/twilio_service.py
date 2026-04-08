"""
Serviço de integração com Twilio WhatsApp
"""

import logging
from typing import Optional
from twilio.rest import Client

logger = logging.getLogger(__name__)


class TwilioService:
    """Serviço para enviar e receber mensagens via Twilio WhatsApp"""
    
    def __init__(self, account_sid: str, auth_token: str, whatsapp_number: str):
        """
        Inicializa o serviço Twilio
        
        Args:
            account_sid: SID da conta Twilio
            auth_token: Token de autenticação Twilio
            whatsapp_number: Número de WhatsApp do Twilio (ex: +1 415 523 8886)
        """
        self.client = Client(account_sid, auth_token)
        self.whatsapp_number = whatsapp_number
    
    def enviar_mensagem(self, para: str, mensagem: str, media_url: Optional[str] = None) -> Optional[str]:
        """
        Envia uma mensagem via WhatsApp
        
        Args:
            para: Número do destinatário (formato: +55 31 99124-9411)
            mensagem: Conteúdo da mensagem
            media_url: URL de mídia opcional (imagem, documento, etc)
            
        Returns:
            SID da mensagem se enviada com sucesso, None caso contrário
        """
        try:
            # Remove espaços e caracteres especiais
            numero_limpo = para.replace(" ", "").replace("-", "")
            # Formata o número para o padrão Twilio (com whatsapp: prefix)
            numero_formatado = f"whatsapp:{numero_limpo}"
            # Formata o número de origem (também precisa de whatsapp: prefix)
            from_number = f"whatsapp:{self.whatsapp_number}" if not self.whatsapp_number.startswith("whatsapp:") else self.whatsapp_number
            
            # Prepara payload
            kwargs = {
                "body": mensagem,
                "from_": from_number,
                "to": numero_formatado
            }
            
            # Adiciona mídia se fornecida
            if media_url:
                kwargs["media_url"] = [media_url]
            
            # Envia mensagem
            message = self.client.messages.create(**kwargs)
            
            logger.info(f"Mensagem enviada para {para} - SID: {message.sid}")
            
            return message.sid
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {para}: {str(e)}")
            return None
    
    def enviar_alerta_urgencia(self, telefone_paciente: str, nome_paciente: str, 
                               sintomas: str, telefone_medico: str) -> bool:
        """
        Envia alerta de urgência para o médico
        
        Args:
            telefone_paciente: Telefone do paciente
            nome_paciente: Nome do paciente
            sintomas: Descrição dos sintomas
            telefone_medico: Telefone do médico para receber alerta
            
        Returns:
            True se alerta enviado com sucesso
        """
        try:
            mensagem_alerta = f"""
🚨 ALERTA DE URGÊNCIA - Pós-operatório 🚨

Paciente: {nome_paciente}
Telefone: {telefone_paciente}
Sintomas: {sintomas}

⚠️ Este paciente foi triado como URGÊNCIA e requer atenção imediata.

Responda ao paciente ou entre em contato direto.
"""
            
            # Envia para o médico
            self.enviar_mensagem(telefone_medico, mensagem_alerta)
            
            logger.info(f"Alerta de urgência enviado para {telefone_medico}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta de urgência: {str(e)}")
            return False
    
    def enviar_confirmacao_agendamento(self, telefone: str, data: str, hora: str, 
                                      local: str, tipo_consulta: str) -> Optional[str]:
        """
        Envia confirmação de agendamento
        
        Args:
            telefone: Telefone do paciente
            data: Data do agendamento
            hora: Hora do agendamento
            local: Local da consulta
            tipo_consulta: Tipo (Presencial ou Telemedicina)
            
        Returns:
            SID da mensagem ou None
        """
        try:
            mensagem = f"""
✅ AGENDAMENTO CONFIRMADO

Data: {data}
Hora: {hora}
Local: {local}
Tipo: {tipo_consulta}

Consultório Dr. Felipe Mendes
📱 WhatsApp: 31 99124-9411
🌐 www.drfelipemendes.com.br

Qualquer dúvida, entre em contato!
"""
            
            return self.enviar_mensagem(telefone, mensagem)
            
        except Exception as e:
            logger.error(f"Erro ao enviar confirmação de agendamento: {str(e)}")
            return None
    
    def enviar_lembretes_consulta(self, telefone: str, data: str, hora: str) -> Optional[str]:
        """
        Envia lembrete de consulta
        
        Args:
            telefone: Telefone do paciente
            data: Data da consulta
            hora: Hora da consulta
            
        Returns:
            SID da mensagem ou None
        """
        try:
            mensagem = f"""
📅 LEMBRETE DE CONSULTA

Sua consulta com o Dr. Felipe Mendes está marcada para:

Data: {data}
Hora: {hora}

Não esqueça! Chegue com 10 minutos de antecedência.

Dúvidas? Responda este WhatsApp ou ligue: 31 99124-9411
"""
            
            return self.enviar_mensagem(telefone, mensagem)
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete: {str(e)}")
            return None
    
    def enviar_instrucoes_pos_operatorio(self, telefone: str) -> Optional[str]:
        """
        Envia instruções pós-operatórias
        
        Args:
            telefone: Telefone do paciente
            
        Returns:
            SID da mensagem ou None
        """
        try:
            mensagem = """
📋 INSTRUÇÕES PÓS-OPERATÓRIAS

Cuidados importantes após sua cirurgia:

✅ Repouso adequado
✅ Tomar medicamentos conforme prescrito
✅ Manter a ferida limpa e seca
✅ Evitar esforços físicos nos primeiros dias
✅ Fazer acompanhamento conforme agendado

⚠️ PROCURE ATENDIMENTO URGENTE SE:
- Febre acima de 38°C
- Sangramento excessivo
- Dificuldade para movimentar braços/pernas
- Saída de líquido pela ferida
- Sonolência excessiva ou confusão

📱 Qualquer dúvida, entre em contato: 31 99124-9411
"""
            
            return self.enviar_mensagem(telefone, mensagem)
            
        except Exception as e:
            logger.error(f"Erro ao enviar instruções pós-operatórias: {str(e)}")
            return None
