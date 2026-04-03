"""
Serviço de integração com Notion
"""

import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class NotionService:
    """Serviço para integração com Notion API"""
    
    def __init__(self, api_key: str, database_id: str):
        """
        Inicializa o serviço Notion
        
        Args:
            api_key: Chave de API do Notion
            database_id: ID da database do Notion
        """
        self.api_key = api_key
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def criar_ou_atualizar_paciente(self, paciente_data: Dict[str, Any]) -> Optional[str]:
        """
        Cria ou atualiza um registro de paciente no Notion
        
        Args:
            paciente_data: Dicionário com dados do paciente
            
        Returns:
            ID da página criada/atualizada ou None se falhar
        """
        try:
            # Primeiro, procura se o paciente já existe
            page_id = self._buscar_paciente_por_telefone(paciente_data.get("telefone"))
            
            if page_id:
                # Atualiza página existente
                return self._atualizar_pagina(page_id, paciente_data)
            else:
                # Cria nova página
                return self._criar_pagina(paciente_data)
                
        except Exception as e:
            logger.error(f"Erro ao criar/atualizar paciente no Notion: {str(e)}")
            return None
    
    def _buscar_paciente_por_telefone(self, telefone: str) -> Optional[str]:
        """
        Busca um paciente pelo telefone
        
        Args:
            telefone: Número de telefone do paciente
            
        Returns:
            ID da página se encontrado, None caso contrário
        """
        try:
            url = f"{self.base_url}/databases/{self.database_id}/query"
            
            payload = {
                "filter": {
                    "property": "WhatsApp",
                    "rich_text": {
                        "contains": telefone
                    }
                }
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            results = response.json().get("results", [])
            if results:
                return results[0]["id"]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar paciente no Notion: {str(e)}")
            return None
    
    def _criar_pagina(self, paciente_data: Dict[str, Any]) -> Optional[str]:
        """
        Cria uma nova página no Notion
        
        Args:
            paciente_data: Dados do paciente
            
        Returns:
            ID da página criada ou None
        """
        try:
            url = f"{self.base_url}/pages"
            
            payload = {
                "parent": {
                    "database_id": self.database_id
                },
                "properties": self._mapear_propriedades(paciente_data)
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            page_id = response.json().get("id")
            logger.info(f"Página criada no Notion: {page_id}")
            
            return page_id
            
        except Exception as e:
            logger.error(f"Erro ao criar página no Notion: {str(e)}")
            return None
    
    def _atualizar_pagina(self, page_id: str, paciente_data: Dict[str, Any]) -> Optional[str]:
        """
        Atualiza uma página existente no Notion
        
        Args:
            page_id: ID da página
            paciente_data: Dados atualizados
            
        Returns:
            ID da página atualizada ou None
        """
        try:
            url = f"{self.base_url}/pages/{page_id}"
            
            payload = {
                "properties": self._mapear_propriedades(paciente_data)
            }
            
            response = requests.patch(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Página atualizada no Notion: {page_id}")
            
            return page_id
            
        except Exception as e:
            logger.error(f"Erro ao atualizar página no Notion: {str(e)}")
            return None
    
    def _mapear_propriedades(self, paciente_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapeia dados do paciente para propriedades do Notion
        
        Args:
            paciente_data: Dados do paciente
            
        Returns:
            Dicionário com propriedades formatadas para Notion
        """
        propriedades = {}
        
        # Nome
        if "nome" in paciente_data:
            propriedades["Nome"] = {
                "title": [
                    {
                        "text": {
                            "content": paciente_data["nome"]
                        }
                    }
                ]
            }
        
        # WhatsApp
        if "telefone" in paciente_data:
            propriedades["WhatsApp"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": paciente_data["telefone"]
                        }
                    }
                ]
            }
        
        # Email
        if "email" in paciente_data:
            propriedades["Email"] = {
                "email": paciente_data["email"]
            }
        
        # Cidade
        if "cidade" in paciente_data:
            propriedades["Cidade"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": paciente_data["cidade"]
                        }
                    }
                ]
            }
        
        # Canal
        if "canal_aquisicao" in paciente_data:
            propriedades["Canal"] = {
                "select": {
                    "name": paciente_data["canal_aquisicao"]
                }
            }
        
        # Motivo do contato
        if "motivo_contato" in paciente_data:
            propriedades["Motivo do contato"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": paciente_data["motivo_contato"][:2000]  # Limite Notion
                        }
                    }
                ]
            }
        
        # Data primeiro contato
        if "data_primeiro_contato" in paciente_data:
            propriedades["Data primeiro contato"] = {
                "date": {
                    "start": paciente_data["data_primeiro_contato"]
                }
            }
        
        # Data último contato
        if "data_ultimo_contato" in paciente_data:
            propriedades["Data ultimo contato"] = {
                "date": {
                    "start": paciente_data["data_ultimo_contato"]
                }
            }
        
        # Agendou consulta
        if "agendou_consulta" in paciente_data:
            propriedades["Agendou consulta"] = {
                "checkbox": paciente_data["agendou_consulta"]
            }
        
        # Consulta realizada
        if "consulta_realizada" in paciente_data:
            propriedades["Consulta realizada"] = {
                "checkbox": paciente_data["consulta_realizada"]
            }
        
        # Valor potencial
        if "valor_potencial" in paciente_data:
            propriedades["Valor potencial"] = {
                "number": paciente_data["valor_potencial"]
            }
        
        # Convênio
        if "convenio" in paciente_data:
            propriedades["Convenio"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": paciente_data["convenio"]
                        }
                    }
                ]
            }
        
        # Motivo da negativa
        if "motivo_negativa" in paciente_data and paciente_data["motivo_negativa"]:
            propriedades["Motivo da negativa"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": paciente_data["motivo_negativa"][:2000]
                        }
                    }
                ]
            }
        
        return propriedades
    
    def registrar_urgencia(self, telefone: str, tipo: str, descricao: str, sintomas: list) -> bool:
        """
        Registra um caso de urgência no Notion
        
        Args:
            telefone: Telefone do paciente
            tipo: Tipo de urgência
            descricao: Descrição da urgência
            sintomas: Lista de sintomas
            
        Returns:
            True se registrado com sucesso, False caso contrário
        """
        try:
            paciente_data = {
                "telefone": telefone,
                "motivo_contato": f"🚨 URGÊNCIA: {tipo}\n\nDescrição: {descricao}\n\nSintomas: {', '.join(sintomas)}"
            }
            
            self.criar_ou_atualizar_paciente(paciente_data)
            logger.info(f"Urgência registrada para {telefone}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar urgência no Notion: {str(e)}")
            return False
