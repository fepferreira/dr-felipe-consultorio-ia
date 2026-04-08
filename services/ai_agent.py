"""
Serviço de Agente de IA para atendimento de pacientes
"""

import json
import logging
from typing import Dict, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class AIAgent:
    """Agente de IA para atendimento de pacientes"""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini"):
        """
        Inicializa o agente de IA
        
        Args:
            api_key: Chave de API OpenAI
            model: Modelo a usar
        """
        try:
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            logger.warning(f"Erro ao inicializar OpenAI: {str(e)}, usando client sem proxy")
            self.client = None
        self.model = model
        self.conversation_history = {}
        
        self.system_prompt = """Você é uma assistente médica empática e profissional do Dr. Felipe Mendes, neurocirurgião especialista em cirurgia de coluna e procedimentos minimamente invasivos em Belo Horizonte e Sete Lagoas.

INFORMAÇÕES IMPORTANTES:
- Dr. Felipe Mendes é especialista em neurocirurgia e cirurgia da coluna
- Oferece procedimentos minimamente invasivos como endoscopia de coluna
- Atende em Belo Horizonte (Rua Rio Grande do Norte, 23, 8º andar) e Sete Lagoas (Rua Paulo Frontin, 1172)
- Horário: Segunda a sexta, 8h-18h
- Oferece telemedicina para pacientes de todo o Brasil
- Tem o maior número de avaliações 5 estrelas no Google em BH e Sete Lagoas

SEUS OBJETIVOS:
1. Acolher o paciente com empatia e compreensão
2. Entender a queixa principal (dor, sintomas, etc)
3. Explicar brevemente a abordagem do Dr. Felipe (identificar causa, não apenas sintoma)
4. Coletar informações: nome, telefone, email, cidade
5. Oferecer agendamento de consulta presencial ou telemedicina
6. Se for pós-operatório, fazer triagem de urgência

PROCEDIMENTOS OFERECIDOS:
- Endoscopia de coluna
- Bloqueios e infiltrações
- Tratamento de hérnia de disco
- Cirurgia de coluna
- Segunda opinião médica
- Telemedicina

IMPORTANTE:
- Sempre seja empático e acolhedor
- Nunca faça diagnóstico - apenas ouça e ofereça avaliação com o Dr. Felipe
- Se o paciente relatar sintomas graves (febre alta, sangramento, déficit neurológico), ofereça urgência
- Mantenha conversas curtas e objetivas
- Use linguagem clara e acessível
- Sempre confirme os dados antes de agendar

FLUXO DE CONVERSA:
1. Saudação calorosa
2. Entender o motivo do contato
3. Coletar dados pessoais (se novo paciente)
4. Explicar abordagem do Dr. Felipe
5. Oferecer agendamento ou próximos passos"""
    
    async def processar_mensagem(self, mensagem: str, dados_paciente: Dict = None, perguntas_urgencia: List = None) -> str:
        """
        Processa uma mensagem do paciente e retorna resposta da IA
        
        Args:
            mensagem: Mensagem do paciente
            dados_paciente: Dados do paciente
            perguntas_urgencia: Perguntas de triagem de urgência
            
        Returns:
            Resposta da IA
        """
        try:
            if not self.client:
                return "Desculpe, o serviço de IA não está disponível no momento. Tente novamente em alguns instantes."
            # Prepara contexto adicional
            contexto = ""
            if dados_paciente:
                contexto = f"\nDados do paciente: {json.dumps(dados_paciente, ensure_ascii=False)}"
            
            # Chama OpenAI com nova API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt + contexto},
                    {"role": "user", "content": mensagem}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            resposta = response.choices[0].message.content
            
            logger.info(f"Resposta gerada pela IA")
            
            return resposta
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem com IA: {str(e)}")
            return "Desculpe, tive um problema ao processar sua mensagem. Pode tentar novamente?"
    
    def _extrair_metadata(self, resposta: str, telefone: str) -> Dict:
        """
        Extrai informações úteis da resposta da IA
        
        Args:
            resposta: Resposta da IA
            telefone: Telefone do paciente
            
        Returns:
            Dicionário com metadata
        """
        metadata = {
            "telefone": telefone,
            "tipo_resposta": "conversacao",
            "requer_agendamento": False,
            "requer_urgencia": False,
            "palavras_chave": []
        }
        
        resposta_lower = resposta.lower()
        
        # Detecta se é para agendar
        if any(palavra in resposta_lower for palavra in ["agendar", "agenda", "horário", "disponível", "quando"]):
            metadata["requer_agendamento"] = True
        
        # Detecta se é urgência
        if any(palavra in resposta_lower for palavra in ["urgência", "urgente", "emergência", "risco", "grave"]):
            metadata["requer_urgencia"] = True
        
        # Extrai palavras-chave
        palavras_importantes = ["dor", "coluna", "cirurgia", "hérnia", "endoscopia", "telemedicina"]
        metadata["palavras_chave"] = [p for p in palavras_importantes if p in resposta_lower]
        
        return metadata
    
    def gerar_prompt_triagem_urgencia(self) -> str:
        """
        Gera um prompt para triagem de urgência pós-operatória
        
        Returns:
            Prompt para triagem
        """
        return """Você agora vai fazer uma triagem rápida de urgência pós-operatória. Faça as seguintes perguntas uma por uma, aguardando resposta:

1. "Você realizou sua cirurgia com o Dr. Felipe nos últimos 15 dias?"
2. "Está com dor intensa que não melhora com os medicamentos prescritos?"
3. "Notou alguma dificuldade nova para movimentar os braços ou as pernas?"
4. "Há saída de líquido ou secreção pela ferida operatória?"
5. "O paciente apresenta sonolência excessiva ou confusão mental?"

Para cada pergunta, registre a resposta como SIM ou NÃO.
Se receber 2 ou mais SIMs nas perguntas 2-5, classifique como URGÊNCIA ALTA e avise que o Dr. Felipe será notificado imediatamente."""
    
    def analisar_resposta_triagem(self, respostas: List[str]) -> Dict:
        """
        Analisa respostas da triagem de urgência
        
        Args:
            respostas: Lista com respostas (SIM/NÃO)
            
        Returns:
            Dicionário com análise
        """
        try:
            # Conta SIMs nas perguntas críticas (2-5)
            respostas_criticas = respostas[1:5] if len(respostas) > 4 else []
            count_sim = sum(1 for r in respostas_criticas if "sim" in r.lower())
            
            analise = {
                "respostas": respostas,
                "count_sim": count_sim,
                "eh_urgencia": count_sim >= 2,
                "score_urgencia": min(count_sim * 25, 100),
                "recomendacao": ""
            }
            
            if analise["eh_urgencia"]:
                analise["recomendacao"] = "URGÊNCIA ALTA - Notificar Dr. Felipe imediatamente"
            elif count_sim == 1:
                analise["recomendacao"] = "Urgência moderada - Agendar consulta em breve"
            else:
                analise["recomendacao"] = "Sem sinais de urgência - Agendar consulta de rotina"
            
            return analise
            
        except Exception as e:
            logger.error(f"Erro ao analisar triagem: {str(e)}")
            return {
                "respostas": respostas,
                "count_sim": 0,
                "eh_urgencia": False,
                "score_urgencia": 0,
                "recomendacao": "Erro na análise - Contatar suporte"
            }
    
    def limpar_historico(self, telefone: str):
        """
        Limpa histórico de conversa de um paciente
        
        Args:
            telefone: Telefone do paciente
        """
        if telefone in self.conversation_history:
            del self.conversation_history[telefone]
            logger.info(f"Histórico de conversa limpo para {telefone}")
