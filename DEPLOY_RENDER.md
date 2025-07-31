# Guia de Deploy do AnalisaVet no Render

Este guia irá te ajudar a fazer o deploy da aplicação AnalisaVet no Render.

## Pré-requisitos

1. Conta no [Render](https://render.com)
2. Conta no GitHub (para hospedar o código)
3. Tokens do Mercado Pago (para funcionalidade de pagamentos)

## Passo 1: Preparar o Repositório

1. Faça upload deste projeto para um repositório no GitHub
2. Certifique-se de que todos os arquivos estão incluídos, especialmente:
   - `run.py` (arquivo principal)
   - `requirements.txt` (dependências)
   - `Procfile` (comando de inicialização)
   - `render.yaml` (configuração do Render)
   - Toda a pasta `app/` com o código da aplicação

## Passo 2: Criar o Banco de Dados

1. No dashboard do Render, clique em "New +"
2. Selecione "PostgreSQL"
3. Configure:
   - **Name**: `analisavet-db`
   - **Database**: `analisavet`
   - **User**: `analisavet`
   - **Plan**: Free (ou pago conforme necessário)
4. Clique em "Create Database"
5. **IMPORTANTE**: Anote a URL de conexão que será gerada

## Passo 3: Criar o Web Service

1. No dashboard do Render, clique em "New +"
2. Selecione "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: `analisavet` (ou nome de sua escolha)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT run:app`

## Passo 4: Configurar Variáveis de Ambiente

No painel do Web Service, vá para "Environment" e adicione:

### Variáveis Obrigatórias:
- `FLASK_ENV`: `production`
- `SECRET_KEY`: (gere uma chave secreta aleatória)
- `DATABASE_URL`: (URL do PostgreSQL criado no Passo 2)

### Variáveis do Mercado Pago:
- `MERCADO_PAGO_ACCESS_TOKEN`: Seu token de acesso
- `MERCADO_PAGO_PUBLIC_KEY`: Sua chave pública
- `MERCADO_PAGO_WEBHOOK_SECRET`: Seu secret do webhook

### Variável Opcional:
- `BASE_URL`: `https://seu-app-name.onrender.com`

## Passo 5: Deploy

1. Clique em "Create Web Service"
2. O Render irá automaticamente:
   - Fazer o build da aplicação
   - Instalar as dependências
   - Iniciar o servidor
3. Aguarde o deploy completar (pode levar alguns minutos)

## Passo 6: Configurar Webhooks (Opcional)

Se você usar pagamentos via Mercado Pago:

1. No painel do Mercado Pago, configure o webhook para:
   `https://seu-app-name.onrender.com/api/payment/webhook`

## Estrutura de Arquivos Importantes

```
analisavet_project/
├── run.py                 # Arquivo principal de inicialização
├── requirements.txt       # Dependências Python
├── Procfile              # Comando de inicialização
├── render.yaml           # Configuração do Render
├── runtime.txt           # Versão do Python
├── .env.example          # Exemplo de variáveis de ambiente
├── app/                  # Código da aplicação
│   ├── app.py           # Aplicação Flask principal
│   ├── config.py        # Configurações
│   ├── models/          # Modelos do banco de dados
│   ├── routes/          # Rotas da API
│   ├── services/        # Lógica de negócio
│   ├── static/          # Arquivos estáticos (CSS, JS, imagens)
│   ├── templates/       # Templates HTML
│   └── utils/           # Utilitários
└── instance/            # Banco de dados local (não usar em produção)
```

## Solução de Problemas

### Erro de Build
- Verifique se o `requirements.txt` está correto
- Certifique-se de que o `runtime.txt` especifica Python 3.11

### Erro de Conexão com Banco
- Verifique se a `DATABASE_URL` está configurada corretamente
- Certifique-se de que o banco PostgreSQL está rodando

### Erro 500 na Aplicação
- Verifique os logs no dashboard do Render
- Certifique-se de que todas as variáveis de ambiente estão configuradas

### Problemas com Pagamentos
- Verifique se os tokens do Mercado Pago estão corretos
- Configure o webhook corretamente

## URLs Importantes

Após o deploy, sua aplicação estará disponível em:
- **URL Principal**: `https://seu-app-name.onrender.com`
- **API de Autenticação**: `https://seu-app-name.onrender.com/api/auth/`
- **API de Análise**: `https://seu-app-name.onrender.com/api/analysis/`
- **API de Pagamentos**: `https://seu-app-name.onrender.com/api/payment/`

## Monitoramento

- Use o dashboard do Render para monitorar logs e métricas
- Configure alertas se necessário
- Monitore o uso do banco de dados

## Backup

- Configure backups automáticos do PostgreSQL no Render
- Mantenha uma cópia do código sempre atualizada no GitHub

---

**Nota**: Este projeto foi configurado e testado para funcionar perfeitamente no Render. Se você encontrar algum problema, verifique primeiro os logs no dashboard do Render.

