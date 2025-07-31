# 🚀 Configuração para Pagamentos Reais - Mercado Pago

## Resumo Executivo

Este documento fornece instruções detalhadas para configurar o sistema AnalisaVet para processar pagamentos reais usando o Mercado Pago em ambiente de produção.

## ⚠️ Importante

**ATENÇÃO:** As instruções abaixo são para ambiente de produção com dinheiro real. Certifique-se de que o sistema foi completamente testado antes de implementar em produção.



## 1. Obtenção das Credenciais de Produção do Mercado Pago

Para processar pagamentos reais, você precisará das credenciais de produção do Mercado Pago. Siga os passos abaixo para obtê-las:

1.  Acesse o [Painel do Desenvolvedor do Mercado Pago](https://www.mercadopago.com.br/developers/panel/credentials).
2.  Certifique-se de que você está na seção de **Credenciais de Produção**.
3.  Copie os valores de:
    *   **Public Key**
    *   **Access Token**

Guarde essas chaves em um local seguro, pois elas são confidenciais.




## 2. Atualização das Credenciais no Código do Projeto

As credenciais do Mercado Pago devem ser configuradas como variáveis de ambiente no ambiente de produção. Isso garante que as chaves não sejam expostas diretamente no código-fonte.

No arquivo `analisavet_nova/analisavet_nova/app/config.py`, as credenciais são carregadas da seguinte forma:

```python
class Config:
    # ... outras configurações ...
    MERCADO_PAGO_ACCESS_TOKEN = os.environ.get("MERCADO_PAGO_ACCESS_TOKEN") or "SEU_ACCESS_TOKEN_DE_TESTE"
    MERCADO_PAGO_PUBLIC_KEY = os.environ.get("MERCADO_PAGO_PUBLIC_KEY") or "SUA_PUBLIC_KEY_DE_TESTE"
    MERCADO_PAGO_WEBHOOK_SECRET = os.environ.get("MERCADO_PAGO_WEBHOOK_SECRET") or "SUA_WEBHOOK_SECRET_DE_TESTE"
    # ...

class ProductionConfig(Config):
    # ... outras configurações ...
    BASE_URL = os.environ.get("BASE_URL") or "https://seuservidor.com.br"
```

Para configurar as credenciais de produção, defina as seguintes variáveis de ambiente no seu servidor de produção:

*   `MERCADO_PAGO_ACCESS_TOKEN`: O Access Token de produção obtido no passo 1.
*   `MERCADO_PAGO_PUBLIC_KEY`: A Public Key de produção obtida no passo 1.
*   `MERCADO_PAGO_WEBHOOK_SECRET`: A chave secreta do webhook que você usará para validar as notificações do Mercado Pago. Você pode gerar uma nova chave segura usando o script `generate_webhook_secret.py` fornecido no projeto.
*   `BASE_URL`: O URL base do seu aplicativo em produção (ex: `https://seuservidor.com.br`). Este URL é crucial para que o Mercado Pago saiba para onde redirecionar o usuário após o pagamento e para onde enviar as notificações de webhook.

**Exemplo de como definir variáveis de ambiente (Linux/macOS):**

```bash
export MERCADO_PAGO_ACCESS_TOKEN="SEU_ACCESS_TOKEN_DE_PRODUCAO"
export MERCADO_PAGO_PUBLIC_KEY="SUA_PUBLIC_KEY_DE_PRODUCAO"
export MERCADO_PAGO_WEBHOOK_SECRET="SUA_WEBHOOK_SECRET_DE_PRODUCAO"
export BASE_URL="https://seuservidor.com.br"
```

Para garantir que essas variáveis sejam carregadas automaticamente, você pode adicioná-las ao arquivo de configuração do seu servidor web (Nginx, Apache) ou ao script de inicialização do seu aplicativo (por exemplo, um arquivo `.env` carregado pelo seu sistema de deployment).




## 3. Configuração dos Webhooks no Painel do Mercado Pago

Os webhooks são essenciais para que o Mercado Pago notifique seu sistema sobre o status dos pagamentos (aprovado, pendente, rejeitado, estornado, etc.).

1.  Acesse o [Painel do Desenvolvedor do Mercado Pago](https://www.mercadopago.com.br/developers/panel/webhooks).
2.  Clique em "Criar um novo webhook" ou edite um existente.
3.  Configure os seguintes campos:
    *   **URL de Notificação**: `https://seuservidor.com.br/api/payment/webhook` (substitua `https://seuservidor.com.br` pelo seu `BASE_URL` de produção).
    *   **Secret**: `SUA_WEBHOOK_SECRET_DE_PRODUCAO` (a mesma chave que você definiu como variável de ambiente `MERCADO_PAGO_WEBHOOK_SECRET`).
4.  Certifique-se de que os eventos de notificação relevantes estejam selecionados (ex: `payment`, `refund`, `chargebacks`).
5.  Salve as configurações.

**Importante:** O Mercado Pago enviará notificações para este URL. Certifique-se de que seu servidor esteja acessível publicamente e que a rota `/api/payment/webhook` esteja configurada para receber e processar essas notificações.




## 4. Considerações de Segurança e Ambiente de Produção

Para um ambiente de produção seguro e confiável, é fundamental:

*   **HTTPS:** Sempre utilize HTTPS para todas as comunicações. Isso garante a criptografia dos dados entre o cliente, seu servidor e o Mercado Pago, protegendo informações sensíveis.
*   **Servidor WSGI:** Utilize um servidor WSGI robusto como Gunicorn ou uWSGI para servir sua aplicação Flask em produção. O `flask run` é apenas para desenvolvimento.
*   **Proxy Reverso:** Configure um proxy reverso (Nginx ou Apache) na frente do seu servidor WSGI. Isso adiciona uma camada extra de segurança, gerencia conexões e pode lidar com certificados SSL/TLS.
*   **Gerenciamento de Variáveis de Ambiente:** Utilize ferramentas de gerenciamento de variáveis de ambiente (como `python-dotenv` para desenvolvimento ou o sistema de variáveis de ambiente do seu provedor de cloud/servidor) para evitar que as credenciais fiquem expostas no código-fonte ou em arquivos de configuração versionados.
*   **Logs e Monitoramento:** Implemente um sistema robusto de logs e monitoramento para acompanhar o desempenho da aplicação, identificar erros e monitorar o fluxo de pagamentos e webhooks.




## Conclusão

Seguindo estas instruções, você poderá configurar o sistema AnalisaVet para processar pagamentos reais com o Mercado Pago de forma segura e eficiente. Lembre-se de sempre testar todas as configurações em um ambiente de homologação antes de aplicar em produção.

---

**Data:** 27/07/2025  
**Versão:** 1.0


