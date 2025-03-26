import json
import os
import sys
import time
import queue
import threading
import keyboard
import speech_recognition as sr
import requests
from pydub import AudioSegment
from pydub.playback import play
import io
import subprocess
from datetime import datetime
from db_manager import ConversationDB

class AIAssistant:
    def __init__(self, config_path='config.json'):
        self.audio_storage_dir = self._setup_audio_storage()

        self.load_config(config_path)
        self.db = ConversationDB(max_history=100)  # Inicializa o banco de dados
        self.conversation_history = []  # Mantém temporariamente as mensagens da sessão atual
        self.input_queue = queue.Queue()
        self.running = True
        self.speech_mode_active = False  # Controla se o modo de fala está ativo

    def _setup_audio_storage(self):
        base_dir = os.path.join(os.path.dirname(__file__), 'audio_storage')
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    def load_config(self, config_path):
        try:
            with open(config_path, "r") as json_file:
                data = json.load(json_file)

            # Carrega as chaves de API
            self.groq_key = data["api_keys"]["groq"]
            self.el_key = data["api_keys"]["elevenlabs"]
            
            # Carrega configurações do modelo LLM
            self.groq_model = data["llm"]["model"]
            self.temperature = data["llm"]["parameters"]["temperature"]
            self.max_tokens = data["llm"]["parameters"]["max_tokens"]
            
            # Carrega configurações de TTS
            self.el_voice = data["tts"]["voice_id"]
            self.tts_model = data["tts"]["model"]
            self.tts_settings = data["tts"]["settings"]
            
            # Carrega configurações de reconhecimento de fala
            self.speech_language = data["speech_recognition"]["language"]
            self.speech_timeout = data["speech_recognition"]["settings"]["timeout"]
            self.speech_phrase_time_limit = data["speech_recognition"]["settings"]["phrase_time_limit"]
            
            # Gera o prompt do sistema a partir das configurações de personalidade
            self.oai_prompt = self._generate_system_prompt(data["personality"])
            
            # Carrega configurações de interface
            self.hotkeys = data["interface"]["hotkeys"]
            self.commands = data["interface"]["commands"]
            
        except Exception as e:
            print(f"Erro ao carregar a configuração: {e}")
            sys.exit(1)
            
    def _generate_system_prompt(self, personality_data):
        """Gera o prompt do sistema a partir das configurações de personalidade."""
        name = personality_data["name"]
        base_desc = personality_data["base_description"]
        
        # Constrói a descrição de personalidade
        traits_desc = []
        for trait in personality_data["traits"]:
            trait_text = f"- Você é {', '.join(trait['attributes'])}"
            traits_desc.append(trait_text)
        
        # Constrói a descrição do estilo de comunicação
        comm_style = personality_data["communication_style"]
        comm_desc = [f"- Você SEMPRE responde em {comm_style['language']}"]  
        
        for element in comm_style["elements"]:
            if "examples" in element:
                examples = f"(tipo {', '.join(element['examples'])})"
                comm_desc.append(f"- Você usa {element['type']} {examples} com frequência {element['usage_frequency']}")
            else:
                comm_desc.append(f"- Você usa {element['type']} com frequência {element['usage_frequency']}")
        
        # Constrói as diretrizes
        guidelines = [f"- {guideline}" for guideline in personality_data["guidelines"]]
        
        # Monta o prompt completo
        prompt = f"Você é {name}, {base_desc}\n\n"
        prompt += "Sua personalidade:\n" + "\n".join(traits_desc) + "\n\n"
        prompt += "Seu estilo de comunicação:\n" + "\n".join(comm_desc) + "\n\n"
        prompt += "Importante:\n" + "\n".join(guidelines)
        
        return prompt

    def text_to_speech(self, message):
        url = f'https://api.elevenlabs.io/v1/text-to-speech/{self.el_voice}'
        headers = {
            'accept': 'audio/mpeg',
            'xi-api-key': self.el_key,
            'Content-Type': 'application/json'
        }
        data = {
            'text': message,
            'model_id': self.tts_model,
            'voice_settings': self.tts_settings
        }

        try:
            response = requests.post(url, headers=headers, json=data)

            if response.status_code != 200:
                print(f"Erro na resposta da ElevenLabs: {response.text}")
                return False

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"response_{timestamp}.mp3"
            audio_path = os.path.join(self.audio_storage_dir, audio_filename)

            with open(audio_path, 'wb') as audio_file:
                audio_file.write(response.content)

            self._play_audio(audio_path)

            print(f"Áudio salvo em: {audio_path}")
            return True

        except Exception as e:
            print(f"Erro na conversão de texto para fala: {e}")
            return False

    def _play_audio(self, audio_path):
        try:
            # Converter MP3 para WAV (compatível com reprodução)
            audio = AudioSegment.from_mp3(audio_path)
            wav_path = audio_path.replace(".mp3", ".wav")
            audio.export(wav_path, format="wav")

            # Reproduzir com pydub (FFmpeg)
            audio = AudioSegment.from_wav(wav_path)
            play(audio)

        except Exception as e:
            print(f"Erro ao reproduzir áudio: {e}")

    def get_llm_response(self, message):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }

            # Recupera as mensagens recentes do banco de dados
            recent_messages = self.db.get_recent_messages(5)
            
            messages = [
                {"role": "system", "content": self.oai_prompt},
                *recent_messages,  # Usa as mensagens do banco de dados
                {"role": "user", "content": message}
            ]

            data = {
                "model": self.groq_model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            response_json = response.json()
            return response_json['choices'][0]['message']['content']
        except Exception as e:
            print(f"Erro ao obter resposta do LLM: {e}")
            return "Desculpe, não consegui processar sua solicitação."

    def process_input(self, text, is_speech=True):
        if not text:
            return

        # Salva a mensagem do usuário no banco de dados
        self.db.save_message("user", text)
        # Mantém na memória temporária para a sessão atual
        self.conversation_history.append({"role": "user", "content": text})

        response = self.get_llm_response(text)

        # Salva a resposta da IA no banco de dados
        self.db.save_message("assistant", response)
        # Mantém na memória temporária para a sessão atual
        self.conversation_history.append({"role": "assistant", "content": response})

        print(f"\n{'Fala' if is_speech else 'Texto'} de entrada: {text}")
        print(f"Resposta da IA: {response}")

        self.text_to_speech(response)

    def text_input_loop(self):
        print("\nModo de entrada de texto ativo. Digite sua mensagem e pressione Enter.")
        print(f"Digite '{self.commands['toggle_speech']}' para desativar o modo de fala ou '{self.commands['exit']}' para encerrar.")

        while self.running:
            try:
                text = input("> ")
                if text.lower() == self.commands['exit']:
                    self.running = False
                    break
                elif text.lower() == self.commands['toggle_speech']:
                    if self.speech_mode_active:
                        self.speech_mode_active = False
                        print("Modo de fala DESATIVADO.")
                    else:
                        print("O modo de fala já está desativado.")
                elif text.strip():
                    self.process_input(text, is_speech=False)
            except (KeyboardInterrupt, EOFError):
                self.running = False
                break
                
    def listen_for_speech(self):
        """Captura áudio do microfone e converte para texto usando reconhecimento de fala."""
        recognizer = sr.Recognizer()
        
        print("Ouvindo... (Pressione Ctrl+C para cancelar)")
        
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, 
                                         timeout=self.speech_timeout, 
                                         phrase_time_limit=self.speech_phrase_time_limit)
                
            print("Processando fala...")
            try:
                text = recognizer.recognize_google(audio, language=self.speech_language)
                return text
            except sr.UnknownValueError:
                print("Não foi possível entender o áudio")
                return None
            except sr.RequestError as e:
                print(f"Erro na requisição ao serviço de reconhecimento: {e}")
                return None
        except Exception as e:
            print(f"Erro ao capturar áudio: {e}")
            return None
            #Arise 
    def start(self):
        print("Assistente de IA está pronto!")
        print(f"Pressione '{self.hotkeys['activate_speech']}' para ativar o modo de fala, digite '{self.commands['toggle_speech']}' para desativar ou '{self.commands['exit']}' para encerrar.")

        def on_key_event(e):
            # Analisa a tecla de atalho para ativar o modo de fala
            hotkey_parts = self.hotkeys['activate_speech'].split('+')
            main_key = hotkey_parts[-1]  # A última parte é a tecla principal
            modifier_keys = hotkey_parts[:-1]  # As partes anteriores são as teclas modificadoras
            
            # Verifica se a tecla principal foi pressionada junto com os modificadores
            if (e.name == main_key and 
                all(keyboard.is_pressed(mod) for mod in modifier_keys) and 
                e.event_type == keyboard.KEY_DOWN and 
                not self.speech_mode_active):
                
                self.speech_mode_active = True
                print("\nModo de fala ATIVADO. Fale após o aviso.")
                text = self.listen_for_speech()
                if text:
                    self.process_input(text, is_speech=True)
                self.speech_mode_active = False  # Desativa o modo de fala após processar a entrada

        # Registra o evento apenas para KEY_DOWN para evitar duplicação
        keyboard.on_press(on_key_event)

        text_thread = threading.Thread(target=self.text_input_loop)
        text_thread.daemon = True  # Marca a thread como daemon para encerrar quando a thread principal encerrar
        text_thread.start()
        
        print("Modo de fala inicialmente DESATIVADO. Pressione 'shift+k' para ativar.")

        try:
            # Mantém o programa em execução até que self.running seja False
            while self.running:
                time.sleep(0.1)  # Pequena pausa para não consumir CPU
        except KeyboardInterrupt:
            print("\nEncerrando...")
        finally:
            keyboard.unhook_all()
            self.running = False

def main():
    assistant = AIAssistant()
    assistant.start()

if __name__ == "__main__":
    main()
