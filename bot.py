import os
import youtube_dl
import telepotpro
from random import randint
from multiprocessing import Process
from youtubesearchpython import VideosSearch
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.environ.get("TOKEN")
bot = telepotpro.Bot(TOKEN)

class Music:
    def __init__(self, user_input, msg):
        self.chat = Chat
        self.user_input = user_input[6:]

    def search_music(self, user_input):
        return VideosSearch(user_input, limit = 1).result()

    def get_link(self, result):
        return result['result'][0]['link']

    def get_title(self, result):
        return result['result'][0]['title']

    def get_duration(self, result):
        result = result['result'][0]['duration'].split(':')
        min_duration = int(result[0])
        split_count = len(result)
        
        return min_duration, split_count

    def download_music(self, file_name, link):
        ydl_opts = {
            'outtmpl': './'+file_name,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '256',
            }],
            'prefer_ffmpeg': True
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)

        pass

class Chat:
    def __init__(self, msg):
        self.chat_id = msg['chat']['id']
        self.user_input = msg['text']
        self.user_input = self.user_input.replace('@TLMusicDownloader_bot', '')
        self.user_name = msg['from']['first_name']
        self.message_id = msg['message_id']

        self.messages = {
            'start':'😁 Oi, '+ self.user_name +', Tudo Bem?\n\n'
                    '📩 Para pedir uma musica, use os seguintes comandos:\n\n'
                    '"*/music* _Nome da musica_"  ou\n'
                    '"*/music* _Artista - Nome da musica_"\n\n'
                    'Eu fasso o download para você!. 🎶',
            
            'spotify_input_error':"‼️ *Ops! o bot não suporta links do spotify!*\n"
                    'Tente: "*/music* _Nome da musica_"\n'
                    'ou: "*/music* _Artista - Nome da musica_"',


            'too_long':'‼️ *Ops! o video e muito longo para converter!*\n'
                    'O limite é de 30minutos.'


        }

        self.check_input(self.user_input, msg)

        pass

    def send_message(self, content):
        return bot.sendMessage(self.chat_id, content, reply_to_message_id=self.message_id, parse_mode='Markdown')

    def delete_message(self, message):
        chat_id = message['chat']['id']
        message_id = message['message_id']
        bot.deleteMessage((chat_id, message_id))

        pass

    def send_audio(self, file_name):
        bot.sendAudio(self.chat_id,audio=open(file_name,'rb'), reply_to_message_id=self.message_id)

        pass

    def process_request(self, user_input):
        result = Music.search_music(self, user_input[6:])

        min_duration, split_count = Music.get_duration(self, result)

        if int(min_duration) < 30 and split_count < 3:
            file_name = Music.get_title(self, result) +' - @TLMusicDownloader_bot '+str(randint(0,999999))+'.mp3'
            file_name = file_name.replace('"', '')

            self.send_message(f"🎵 {Music.get_title(self, result)}\n🔗 {Music.get_link(self, result)}")
            downloading_message = self.send_message('⬇️ Fazendo download, aguarde...')

            Music.download_music(self, file_name, Music.get_link(self, result))

            try:
                self.send_audio(file_name)
                self.delete_message(downloading_message)
                self.send_message('✅ Download Concluído!')
                print ("\nSucess!\n")
            except:
                print("\nError")

            os.remove(file_name)
        pass

    def check_input(self, user_input, msg):
        if user_input.startswith('/start'):
            self.send_message(self.messages['start'])

        elif user_input.startswith('/music') and user_input[6:]!='':
            if 'open.spotify.com' in user_input[6:]:
            	self.send_message(self.messages['spotify_input_error'])

            else:
                #Valid command
                self.process_request(user_input)

        else:
            #Invalid command
            print("\nError")

        pass 

def start_new_chat(msg):
    Process(target=Chat, args=(msg,)).start()
    

bot.message_loop(start_new_chat, run_forever=True)
