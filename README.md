# Documentação da API - Freddie Mercury AI (Backend)

## 1. Descrição da Aplicação e Funcionalidades

Esta é uma API desenvolvida com **FastAPI** que funciona como um assistente de inteligência artificial chamado **Freddie Mercury**, destinado para **transpor músicas para outras tonalidades**. O usuário interage com o sistema por meio de perguntas e envio de arquivos contendo letras de músicas em **formato `.pdf` ou `.png`** ou apenas digitando.

### Funcionalidades principais:

- Upload de arquivos com letras de músicas.
- Processamento de imagens e PDFs para extrair o texto.
- Recebimento de mensagens com pedidos para mudar o tom da música.
- Respostas geradas via modelo de IA da Google Gemini.
- AI contextualizada - através do armazenamento do histórico de conversa em um arquivo local `context.txt`.

---

## 2. Dependências Necessárias

As bibliotecas utilizadas no projeto são:

```bash
fastapi
uvicorn
pydantic
google-generativeai
pymupdf
pillow
```

Para instalar todas elas é necessário rodar o comando abaixo:

```bash
pip install fastapi uvicorn pydantic google-generativeai pymupdf pillow
```

---

## 3. Instruções para Rodar a Aplicação

**Pré-requisitos**:

- Python 3.8 ou superior

**Executando a API**:

Após instalar as bibliotecas basta estar no diretório do projeto e rodar o comando abaixo:

```bash
uvicorn main_gemini:app --reload
```

**Endpoints disponíveis**:

- `POST /upload/` – envia um arquivo `.pdf`, `.txt` ou `.png`.
- `POST /message/` – envia uma mensagem solicitando a alteração de tom da música.

---

## 4. Integração com Modelos Locais ou APIs Externas

A aplicação integra com a **API do modelo Gemini da Google**, utilizando o SDK oficial `google-generativeai`.

- Modelo utilizado: `'gemini-1.5-flash'`.
- A chave da API é configurada diretamente no código (não recomendado para produção).
- O prompt enviado à IA inclui:
  - Histórico salvo no `context.txt`.
  - Letra da música (texto extraído do arquivo enviado).
  - Instruções para transpor a música para a tonalidade desejada.
- A resposta é enviada ao cliente e salva no histórico.

---
