# Sistema de Atendimento com IA - Dr. Felipe Mendes

Sistema completo de atendimento automatizado para consultório de neurocirurgia, integrando WhatsApp (via Twilio), Inteligência Artificial (OpenAI) e CRM (Notion).

## 🎯 Funcionalidades

- **Atendimento 24/7 via WhatsApp**: Agente de IA responde pacientes automaticamente
- **Triagem Inteligente**: Detecta casos de urgência pós-operatória
- **Agendamento Automático**: Oferece horários disponíveis e confirma agendamentos
- **Sincronização Notion**: Todos os dados são salvos automaticamente no CRM
- **Histórico de Conversas**: Rastreia todas as interações com pacientes
- **Alertas de Urgência**: Notifica o médico em casos críticos via WhatsApp

## 📋 Requisitos

- Python 3.8+
- Conta Twilio (com WhatsApp Sandbox)
- Conta OpenAI (API key)
- Integração Notion (API key)
- Banco de dados SQLite (incluído)

## 🚀 Instalação

### 1. Clonar/Preparar o projeto

```bash
cd /home/ubuntu/dr_felipe_consultorio
```

### 2. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
TWILIO_ACCOUNT_SID=seu_account_sid
TWILIO_AUTH_TOKEN=seu_auth_token
NOTION_API_KEY=seu_api_key_notion
OPENAI_API_KEY=sua_chave_openai
```

## 🏃 Executar a aplicação

### Desenvolvimento local

```bash
python main.py
```

A API estará disponível em: `http://localhost:8000`

### Documentação interativa

Acesse: `http://localhost:8000/docs`

## 🔌 Configuração do Twilio Webhook

Para que o Twilio envie mensagens para sua aplicação:

1. Acesse o dashboard Twilio
2. Vá para **Messaging** → **WhatsApp** → **Sandbox settings**
3. Em "When a message comes in", configure:
   - URL: `https://seu-dominio.com/webhook/whatsapp`
   - Método: POST

## 📊 Estrutura do Banco de Dados

### Tabelas principais

- **pacientes**: Dados dos pacientes
- **conversas**: Histórico de mensagens
- **agendamentos**: Agendamentos confirmados
- **urgencias**: Casos de urgência detectados
- **sincronizacao_notion**: Rastreamento de sincronizações

## 🤖 Fluxo de Atendimento

### 1. Novo Paciente

```
Paciente envia mensagem
    ↓
IA recebe e saudação calorosa
    ↓
IA coleta: nome, telefone, email, cidade
    ↓
IA entende motivo do contato
    ↓
IA explica abordagem do Dr. Felipe
    ↓
IA oferece agendamento
```

### 2. Triagem de Urgência (Pós-operatório)

```
Paciente relata pós-operatório
    ↓
IA faz 5 perguntas de triagem
    ↓
Se 2+ respostas SIM → URGÊNCIA ALTA
    ↓
Alerta enviado para Dr. Felipe via WhatsApp
    ↓
Caso registrado no Notion com prioridade
```

## 📱 Exemplos de Uso

### Enviar mensagem de teste

```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -d "From=whatsapp:%2B5531991249411" \
  -d "Body=Olá, tenho uma dor na coluna" \
  -d "MessageSid=SM123456789"
```

### Criar agendamento

```bash
curl -X POST http://localhost:8000/api/agendamento/criar \
  -H "Content-Type: application/json" \
  -d '{
    "paciente_id": 1,
    "telefone": "+55 31 99124-9411",
    "data_agendamento": "2026-04-10T14:00:00",
    "local": "Belo Horizonte",
    "tipo_consulta": "Presencial"
  }'
```

### Obter dados do paciente

```bash
curl http://localhost:8000/api/pacientes/%2B5531991249411
```

## 🔐 Segurança

- Nunca compartilhe suas credenciais
- Use variáveis de ambiente para dados sensíveis
- Mantenha o `.env` fora do controle de versão
- Use HTTPS em produção
- Implemente rate limiting para APIs

## 🚀 Deploy em Produção

### Opção 1: Render.com (Recomendado - Gratuito)

1. Crie conta em https://render.com
2. Conecte seu repositório GitHub
3. Crie novo "Web Service"
4. Configure:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Adicione variáveis de ambiente no painel

### Opção 2: Heroku

```bash
heroku login
heroku create seu-app-name
git push heroku main
```

### Opção 3: AWS/Google Cloud/Azure

Siga documentação oficial de cada plataforma para deploy de aplicações Python.

## 📊 Monitoramento

A aplicação registra logs em `consultorio.log`:

```bash
tail -f consultorio.log
```

## 🐛 Troubleshooting

### Mensagens não chegam

- Verifique se o webhook está configurado corretamente
- Confirme que a URL é acessível publicamente
- Verifique logs: `tail -f consultorio.log`

### IA não responde

- Verifique se `OPENAI_API_KEY` está configurada
- Confirme se tem créditos na OpenAI
- Verifique limite de tokens

### Notion não sincroniza

- Verifique se `NOTION_API_KEY` está correta
- Confirme que a integração tem permissão na database
- Verifique se os nomes das propriedades correspondem

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique os logs
2. Consulte a documentação da API: `http://localhost:8000/docs`
3. Abra uma issue no repositório

## 📝 Roadmap

- [ ] Dashboard web para gerenciar agendamentos
- [ ] Integração com Google Calendar
- [ ] SMS como canal alternativo
- [ ] Análise de sentimento nas conversas
- [ ] Relatórios de performance
- [ ] Integração com sistemas de pagamento
- [ ] App mobile para pacientes

## 📄 Licença

Propriedade do Consultório Dr. Felipe Mendes

## 👨‍⚕️ Sobre

Sistema desenvolvido para o Consultório Dr. Felipe Mendes - Neurocirurgia e Cirurgia da Coluna.

- 📍 Belo Horizonte e Sete Lagoas
- 🌐 www.drfelipemendes.com.br
- 📱 31 99124-9411
