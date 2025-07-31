// Carrega as variáveis do .env
require('dotenv').config();

// Importa os módulos
const express = require('express');
const bodyParser = require('body-parser');

// Cria a aplicação
const app = express();

// Permite que o app leia JSON
app.use(bodyParser.json());

// Rota principal só pra testar
app.get('/', (req, res) => {
  res.send('AnalisaVet no ar!');
});

// Rota do webhook do Mercado Pago
app.post('/api/payment/webhook', (req, res) => {
  const secret = req.headers['x-signature-secret'];

  if (secret !== process.env.MP_WEBHOOK_SECRET) {
    return res.status(403).send('Acesso negado.');
  }

  console.log('🔔 Webhook recebido:', req.body);
  res.sendStatus(200);
});

// Define a porta
const PORT = process.env.PORT || 3000;

// Inicia o servidor
app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});

