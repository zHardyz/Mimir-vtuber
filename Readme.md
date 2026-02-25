# Mimir - Assistente Virtual com Personalidade

para instalar as dependencias:


Mimir é um assistente virtual com personalidade marcante que você pode customizar para interagir com seus espectadores através de texto e voz. Este projeto integra reconhecimento de fala, síntese de voz e processamento de linguagem natural para criar uma experiência de interação natural e envolvente.

## Características Principais

- **Personalidade Customizável**: Configure traços de personalidade, estilo de comunicação e diretrizes de comportamento para combinar com sua VTuber
- **Interação por Voz**: Reconhecimento de fala em português brasileiro usando a API do Google
- **Síntese de Voz Natural**: Conversão de texto para fala usando ElevenLabs
- **Histórico de Conversas**: Armazenamento persistente de conversas em banco de dados SQLite
- **Processamento de Linguagem**: Integração com modelos avançados de IA via Groq

## Requisitos

- Python 3.10 ou superior
- Conexão com internet (para APIs de IA e síntese de voz)
- Microfone (para reconhecimento de fala)
- Alto-falantes (para reprodução de áudio)
- Chaves de API para Groq e ElevenLabs

## Instalação

1. Clone este repositório ou baixe os arquivos

2. Crie e ative um ambiente virtual Python:

```bash
python -m venv mimir-env
cd mimir-env
Scripts\activate
```

3. Instale as dependências necessárias:

```bash
pip install requests pydub SpeechRecognition keyboard
```

4. Instale o PyAudio (necessário para o reconhecimento de fala):

```bash
pip install pyaudio
```

Se encontrar problemas na instalação do PyAudio no Windows, você pode baixar o arquivo wheel apropriado do site [Unofficial Windows Binaries for Python](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) e instalá-lo com:

```bash
pip install caminho/para/o/arquivo/PyAudio-x.x.x-cpxx-cpxx-win_xxx.whl
```

## Configuração

1. Obtenha chaves de API:
   - Crie uma conta na [Groq](https://console.groq.com/) para obter uma chave de API para o modelo LLM
   - Crie uma conta na [ElevenLabs](https://elevenlabs.io/) para obter uma chave de API para síntese de voz

2. Configure o arquivo `config.json` com suas chaves de API e preferências:

```json
{
  "api_keys": {
    "groq": "SUA_CHAVE_API_GROQ",
    "elevenlabs": "SUA_CHAVE_API_ELEVENLABS"
  },
  "llm": {
    "provider": "groq",
    "model": "llama-3.3-70b-versatile",
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 1024
    }
  },
  "tts": {
    "provider": "elevenlabs",
    "voice_id": "SUA_VOICE_ID_ELEVENLABS",
    "model": "eleven_multilingual_v2",
    "settings": {
      "stability": 0.75,
      "similarity_boost": 0.75
    }
  },
  "speech_recognition": {
    "provider": "google",
    "language": "pt-BR",
    "settings": {
      "timeout": 5,
      "phrase_time_limit": 10
    }
  }
}
```

3. Personalize a personalidade do assistente no arquivo `config.json` na seção `personality`:

```json
"personality": {
  "name": "NOME_DO_ASSISTENTE",
  "base_description": "DESCRIÇÃO_BASE_DA_PERSONALIDADE",
  "traits": [
    {
      "category": "CATEGORIA_DO_TRAÇO",
      "attributes": ["TRAÇO_1", "TRAÇO_2", "TRAÇO_3"],
      "intensity": 0.8
    }
  ],
  "communication_style": {
    "language": "[idioma-principal]",
    "formality": "[nível-de-formalidade]",
    "elements": [
      {
        "type": "[elemento-de-comunicação]",
        "usage_frequency": "[frequência-de-uso]"
      }
    ]
  },
  "guidelines": [
    "[diretriz-1]",
    "[diretriz-2]"
  ]
}
```

## Uso

1. Execute o assistente:

```bash
python main.py
```

2. Comandos disponíveis:
   - Digite mensagens de texto e pressione Enter para interagir com o assistente
   - Pressione `Shift+K` (ou a tecla configurada) para ativar o modo de reconhecimento de voz
   - Digite `desativar-fala` para alternar o modo de fala
   - Digite `sair` para encerrar o programa

## Banco de Dados

O histórico de conversas é armazenado em um banco de dados SQLite (`conversation_history.db`). O sistema mantém automaticamente um número limitado de mensagens (configurável) para evitar crescimento excessivo do banco de dados.

## Estrutura do Projeto

- `main.py`: Arquivo principal que contém a classe `AIAssistant` e a lógica de interação
- `db_manager.py`: Gerenciador do banco de dados para armazenamento de conversas
- `config.json`: Arquivo de configuração com chaves de API e preferências
- `audio_storage/`: Diretório onde os arquivos de áudio gerados são armazenados

## Personalização Avançada

### Modificando a Voz

Para alterar a voz do assistente, obtenha um novo `voice_id` da ElevenLabs e atualize o arquivo `config.json`. Recomendamos testar diferentes vozes para encontrar a que melhor combina com a personalidade da sua VTuber.

### Ajustando o Modelo de IA

Você pode experimentar diferentes modelos disponíveis na Groq alterando o campo `model` na seção `llm` do arquivo `config.json`. Teste diferentes modelos para encontrar o equilíbrio ideal entre performance e qualidade das respostas.

### Expandindo Funcionalidades

O código foi projetado de forma modular, facilitando a adição de novas funcionalidades. Você pode expandir o assistente adicionando:

- Integração com APIs externas para consultas específicas
- Controle de dispositivos inteligentes
- Interface gráfica para visualização

## Solução de Problemas

### Problemas com Reconhecimento de Voz

- Verifique se o microfone está funcionando corretamente
- Ajuste o nível de ruído ambiente
- Verifique sua conexão com a internet

### Problemas com Síntese de Voz

- Confirme se sua chave de API da ElevenLabs está correta
- Verifique se o `voice_id` existe em sua conta
- Verifique sua conexão com a internet

### Erros de API

- Verifique os limites de uso das suas chaves de API
- Confirme se as chaves estão inseridas corretamente no arquivo `config.json`

## Licença

Este projeto é distribuído sob a licença MIT. 

## Ferramentas Externas

### VB-Cable

O VB-Cable é uma ferramenta essencial para redirecionar o áudio do assistente para outros programas, permitindo a sincronização labial do seu avatar.

1. Baixe o VB-Cable em [VB-Audio](https://vb-audio.com/Cable/)
2. Execute o instalador como administrador
3. Reinicie o computador após a instalação
4. Configure o VB-Cable como dispositivo de saída de áudio padrão nas configurações de som do Windows
5. No software de avatar (VSeeFace ou VTube Studio), configure o VB-Cable como fonte de entrada de áudio para sincronização labial

### OBS Studio

O OBS Studio permite criar uma câmera virtual para transmitir seu avatar em plataformas de streaming ou videoconferência.

1. Baixe e instale o [OBS Studio](https://obsproject.com/)
2. Instale o plugin de câmera virtual (incluído nas versões recentes do OBS)
3. Configure uma nova cena e adicione seu avatar como fonte
4. Inicie a câmera virtual em OBS (Ferramentas > Iniciar Câmera Virtual)
5. Selecione "OBS Virtual Camera" como câmera em seus aplicativos de streaming ou videoconferência

### VSeeFace

O VSeeFace é um software gratuito para rastreamento facial que anima avatares 3D.

1. Baixe o [VSeeFace](https://www.vseeface.icu/)
2. Extraia os arquivos para uma pasta de sua escolha
3. Execute o VSeeFace.exe
4. Carregue seu modelo 3D (formato .vrm)
5. Configure o rastreamento facial usando webcam
6. Configure o VB-Cable como entrada de áudio para sincronização labial

### VTube Studio

Alternativa ao VSeeFace, o VTube Studio suporta tanto modelos 3D quanto Live2D.

1. Adquira o [VTube Studio](https://denchisoft.com/) na Steam ou App Store
2. Instale e execute o programa
3. Carregue seu modelo (3D ou Live2D)
4. Configure o rastreamento facial e a sincronização labial
5. Use o aplicativo móvel VTube Studio como controle remoto (opcional)

### VRoid Studio

Para criar modelos 3D personalizados compatíveis com VSeeFace:

1. Baixe o [VRoid Studio](https://vroid.com/en/studio/)
2. Crie seu avatar personalizado usando as ferramentas de modelagem
3. Exporte o modelo no formato .vrm
4. Importe o modelo no VSeeFace

### Live2D

Para criar modelos 2D animados compatíveis com VTube Studio:

1. Adquira o [Live2D Cubism](https://www.live2d.com/)
2. Prepare suas ilustrações em camadas usando Photoshop ou similar
3. Importe as ilustrações no Live2D e configure os parâmetros de animação
4. Exporte o modelo no formato .model3.json
5. Importe o modelo no VTube Studio

---
esse projeto foi feito de maneira simples para ser gratuito e leve, pode haver muita coisa faltando.
