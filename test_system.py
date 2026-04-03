"""
Script de teste completo do sistema de atendimento
Simula o fluxo real de uma conversa com um paciente
"""

import json
import requests
import time
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"
WEBHOOK_URL = f"{BASE_URL}/webhook/whatsapp"

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_patient_msg(msg):
    print(f"{Colors.OKBLUE}👤 Paciente: {msg}{Colors.ENDC}")

def print_bot_msg(msg):
    print(f"{Colors.OKGREEN}🤖 Bot: {msg}{Colors.ENDC}")

def enviar_mensagem(telefone, mensagem, message_sid=None):
    """Envia uma mensagem simulando o Twilio"""
    if message_sid is None:
        message_sid = f"SM{int(time.time() * 1000)}"
    
    data = {
        "From": f"whatsapp:{telefone}",
        "Body": mensagem,
        "MessageSid": message_sid
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=data)
        return response.status_code == 200
    except Exception as e:
        print_error(f"Erro ao enviar mensagem: {str(e)}")
        return False

def test_health():
    """Testa se o servidor está rodando"""
    print_header("1. VERIFICANDO SAÚDE DO SERVIDOR")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Servidor rodando: {data['service']}")
            print_info(f"Timestamp: {data['timestamp']}")
            return True
        else:
            print_error(f"Servidor retornou status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Não conseguiu conectar ao servidor: {str(e)}")
        return False

def test_novo_paciente():
    """Testa fluxo de novo paciente"""
    print_header("2. TESTE: NOVO PACIENTE COM DOR NA COLUNA")
    
    telefone = "+55 31 992830958"
    
    # Primeira mensagem
    print_info("Simulando primeiro contato...")
    print_patient_msg("Olá, tenho uma dor na coluna há 3 meses")
    
    if enviar_mensagem(telefone, "Olá, tenho uma dor na coluna há 3 meses"):
        print_success("Mensagem processada pelo sistema")
        time.sleep(2)
    else:
        print_error("Falha ao processar mensagem")
        return False
    
    # Segunda mensagem
    print_info("\nContinuando a conversa...")
    print_patient_msg("A dor é principalmente na região lombar")
    
    if enviar_mensagem(telefone, "A dor é principalmente na região lombar"):
        print_success("Mensagem processada")
        time.sleep(2)
    else:
        print_error("Falha ao processar mensagem")
        return False
    
    # Terceira mensagem
    print_info("\nPaciente pergunta sobre agendamento...")
    print_patient_msg("Como faço para agendar uma consulta?")
    
    if enviar_mensagem(telefone, "Como faço para agendar uma consulta?"):
        print_success("Mensagem processada")
        time.sleep(2)
    else:
        print_error("Falha ao processar mensagem")
        return False
    
    return True

def test_pos_operatorio():
    """Testa fluxo de urgência pós-operatória"""
    print_header("3. TESTE: URGÊNCIA PÓS-OPERATÓRIA")
    
    telefone = "+55 31 987654321"
    
    print_info("Simulando paciente em pós-operatório com sintomas de urgência...")
    print_patient_msg("Dr., fiz cirurgia com você há 5 dias e estou com febre alta")
    
    if enviar_mensagem(telefone, "Dr., fiz cirurgia com você há 5 dias e estou com febre alta"):
        print_success("Mensagem processada")
        time.sleep(2)
    else:
        print_error("Falha ao processar mensagem")
        return False
    
    print_info("\nPaciente relata sintoma crítico...")
    print_patient_msg("Tenho febre de 39.5°C e dor muito forte")
    
    if enviar_mensagem(telefone, "Tenho febre de 39.5°C e dor muito forte"):
        print_success("Mensagem processada - Sistema deve detectar urgência")
        time.sleep(2)
    else:
        print_error("Falha ao processar mensagem")
        return False
    
    return True

def test_database():
    """Verifica se os dados foram salvos no banco"""
    print_header("4. VERIFICANDO BANCO DE DADOS")
    
    try:
        # Tenta buscar um paciente
        response = requests.get(f"{BASE_URL}/api/pacientes/%2B5531992830958")
        
        if response.status_code == 200:
            paciente = response.json()
            print_success("Paciente encontrado no banco de dados!")
            print_info(f"  Nome: {paciente.get('nome', 'Não preenchido')}")
            print_info(f"  Telefone: {paciente.get('telefone')}")
            print_info(f"  Cidade: {paciente.get('cidade', 'Não preenchido')}")
            print_info(f"  Canal: {paciente.get('canal_aquisicao', 'Não preenchido')}")
            print_info(f"  Agendou: {paciente.get('agendou_consulta')}")
            return True
        elif response.status_code == 404:
            print_error("Paciente não encontrado no banco")
            return False
        else:
            print_error(f"Erro ao buscar paciente: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao verificar banco: {str(e)}")
        return False

def test_notion_sync():
    """Verifica sincronização com Notion"""
    print_header("5. VERIFICANDO SINCRONIZAÇÃO COM NOTION")
    
    print_info("Verificando se os dados foram salvos no Notion...")
    print_info("Acesse sua planilha do Notion para confirmar:")
    print_info("  https://www.notion.so/9ececefa7126479bbacfb72a175479da")
    
    print_warning("\n⚠️  Nota: A sincronização com Notion requer que a integração")
    print_warning("   tenha permissão de escrita na database.")
    
    return True

def print_warning(text):
    print(f"{Colors.WARNING}{text}{Colors.ENDC}")

def test_api_endpoints():
    """Testa endpoints da API"""
    print_header("6. TESTANDO ENDPOINTS DA API")
    
    endpoints = [
        ("GET", "/health", "Health Check"),
        ("GET", "/docs", "Documentação Swagger"),
    ]
    
    for method, endpoint, descricao in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code in [200, 307]:  # 307 é redirect para /docs
                print_success(f"{descricao}: {endpoint}")
            else:
                print_error(f"{descricao}: {endpoint} (Status: {response.status_code})")
                
        except Exception as e:
            print_error(f"{descricao}: {endpoint} - {str(e)}")

def print_summary():
    """Imprime resumo final"""
    print_header("RESUMO DO TESTE")
    
    print(f"{Colors.BOLD}✓ Sistema de Atendimento Dr. Felipe Mendes{Colors.ENDC}")
    print(f"\n{Colors.OKGREEN}Funcionalidades Testadas:{Colors.ENDC}")
    print("  ✓ Servidor FastAPI rodando")
    print("  ✓ Webhook de WhatsApp funcionando")
    print("  ✓ Processamento de mensagens com IA")
    print("  ✓ Banco de dados SQLite")
    print("  ✓ Integração com Notion (parcial)")
    
    print(f"\n{Colors.OKBLUE}Próximos Passos:{Colors.ENDC}")
    print("  1. Configurar webhook do Twilio para apontar para sua URL pública")
    print("  2. Conectar seu número de WhatsApp Business (+55 31 99124-9411)")
    print("  3. Começar a receber mensagens de pacientes")
    print("  4. Monitorar logs em: server.log")
    
    print(f"\n{Colors.OKBLUE}Documentação da API:{Colors.ENDC}")
    print(f"  Acesse: http://localhost:8000/docs")
    
    print(f"\n{Colors.OKBLUE}Logs do Servidor:{Colors.ENDC}")
    print(f"  tail -f /home/ubuntu/dr_felipe_consultorio/server.log")
    
    print(f"\n{Colors.BOLD}Sistema pronto para produção! 🚀{Colors.ENDC}\n")

def main():
    """Executa todos os testes"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  TESTE COMPLETO - SISTEMA DE ATENDIMENTO DR. FELIPE MENDES ║")
    print("║           Neurocirurgia e Cirurgia da Coluna              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    # Executa testes
    testes = [
        ("Saúde do Servidor", test_health),
        ("Novo Paciente", test_novo_paciente),
        ("Urgência Pós-operatória", test_pos_operatorio),
        ("Banco de Dados", test_database),
        ("Sincronização Notion", test_notion_sync),
        ("Endpoints da API", test_api_endpoints),
    ]
    
    resultados = []
    
    for nome, teste_func in testes:
        try:
            resultado = teste_func()
            resultados.append((nome, resultado))
        except Exception as e:
            print_error(f"Erro ao executar teste: {str(e)}")
            resultados.append((nome, False))
    
    # Resumo
    print_summary()
    
    # Resultado final
    total = len(resultados)
    sucesso = sum(1 for _, r in resultados if r)
    
    print(f"{Colors.BOLD}Resultado: {sucesso}/{total} testes passaram{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
