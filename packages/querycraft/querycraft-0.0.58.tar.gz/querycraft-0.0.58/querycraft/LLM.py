# https://github.com/ollama/ollama-python
import importlib.resources

import openai
# https://github.com/Soulter/hugging-chat-api
from hugchat import hugchat
from hugchat.login import Login
from ollama import chat, ChatResponse
from datetime import datetime

BdD = '''
create table etudiants(
	noetu  varchar(6)      not null,
	nom     varchar(10)     not null,
	prenom  varchar(10)     not null,
	primary key (noetu)) ;

create table matieres(
	codemat        varchar(8)      not null primary key,
	titre           varchar(10),
	responsable     varchar(4),
	diplome         varchar(20));

create table notes(
	noetu          varchar(6),
	codemat        varchar(8) ,
	noteex          numeric         check (noteex between 0 and 20),
	notecc          numeric         check (notecc between 0 and 20),
	primary key (noetu, codemat),
	CONSTRAINT FK_noe       FOREIGN KEY (noetu)       REFERENCES etudiants (noetu),
	CONSTRAINT FK_codemat   FOREIGN KEY (codemat)   REFERENCES matieres (codemat));
'''

sql1 = "select * from etudiants ;"
sql1e = "select * from etudiant ;"
erreur1 = '''
ERROR:  relation "etudiant" does not exist
LIGNE 1 : select * from etudiant;
                        ^
'''

sql2 = "select * from notes where noteex = 12;"
sql2e = "select * from notes where notex = 12;"
erreur2 = '''
ERROR:  column "notex" does not exist
LIGNE 1 : select * from notes where notex = 12;
                                        ^
'''

# Définir les codes de couleur
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"


class LLM():
    def __init__(self, verbose, sgbd, modele, bd=None):
        self.prompt = str()
        self.modele = modele
        self.bd = bd
        self.sgbd = sgbd
        self.prompt_systeme = self.__build_prompt_contexte(sgbd, bd)
        self.verbose = verbose

    def __build_prompt_contexte(self, sgbd, bd=None):
        instruction_contexte = f'''
# Contexte 
Tu parles en français.
Tu es un assistant pour un élève en informatique qui apprend les fondements des bases de données relationnelles et le langage SQL.
Les élèves cherchent à apprendre SQL. Ils ne peuvent ni créer de tables ni modifier leur structure. 
Ils peuvent uniquement proposer des requêtes du langage de manipulation des données (MLD) en SQL. 
Ils te proposent des erreurs de requêtes SQL, tu es chargé de les aider à comprendre leurs erreurs.
'''

        instruction_sgbd = f'''
# Description de la base de données relationnelle

## SGBD

Le SGBD utilisé est {sgbd}.
'''
        if bd is None:
            instruction_base_de_donnees = ""
        else:
            instruction_base_de_donnees = f'''
## Schéma relationnel de la base de données 

{bd}
'''
        instruction_systeme = f'''
# Instructions

L'élève te propose *une erreur SQL*, prends le soin de l'expliquer *en français*.
Réponds en français et uniquement à la question posée. 
Réponds directement, sans faire de préambule, en t'appuyant sur les informations de la description de la base de données et sur l'erreur.
La base de données est *bien construite*. Les *noms des tables et des attributs sont corrects*. Toutes les *tables ont bien été créées*.
S'il y a des erreurs, elles viennent *nécessairement* de la requête. 
'''
        instruction = instruction_contexte + instruction_sgbd + instruction_base_de_donnees + instruction_systeme
        return instruction

    def set_prompt(self, erreur, sql_attendu, sql_soumis):
        self.prompt = "Expliquer l'erreur suivante :\n```sql\n" + erreur + '\n```\n'
        self.prompt += f"Voici la requête SQL qui a généré cette erreur : \n```sql\n{sql_soumis}\n```\n"
        if sql_attendu != "" and sql_attendu != None:
            self.prompt += f"Voici la requête SQL corrigée : \n```sql\n{sql_attendu}\n```\n"

    def run(self, erreur, sql_attendu, sql_soumis):
        return ""

    def set_reponse(self, rep, llm, link, modele, date):
        return (f"{GREEN} {rep} {RESET}\n---\n"
                + f"{BLUE}Source : {llm} ({link}) avec {modele} {RESET}"
                + f"{BLUE} le {date.date()} à {date.time()}. {RESET}\n"
                + f"{BLUE}Attention, {llm}/{modele} ne garantit pas la validité de l'aide. "
                + f"Veuillez vérifier la réponse et vous rapprocher de vos enseignants si nécessaire.{RESET}\n"
                )

class OllamaLLM(LLM):
    def __init__(self, verbose, sgbd, modele="gemma3:1b", bd=None):
        super().__init__(verbose, sgbd, modele, bd)

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            self.set_prompt(erreur, sql_attendu, sql_soumis)
            response: ChatResponse = chat(model=self.modele, options={"temperature": 0.0, "top-p": 0.9}, messages=[
                {'role': 'system', 'content': self.prompt_systeme},
                {'role': 'user', 'content': self.prompt},
            ])
            if self.verbose:
                print(f"{CYAN}{self.prompt_systeme}{RESET}")
                print(f"{CYAN}{self.prompt}{RESET}")
            return self.set_reponse(response.message.content, "Ollama", "https://ollama.com/",
                                    self.modele, datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)

class GenericLLM(LLM):
    def __init__(self, verbose, sgbd, modele, api_key, base_url, bd=None):
        super().__init__(verbose, sgbd, modele, bd)
        self.api_key = api_key
        self.base_url= base_url
        self.client = openai.OpenAI(api_key=self.api_key,base_url=self.base_url,)

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            response = self.query(erreur, sql_attendu, sql_soumis)
            return self.set_reponse(response.choices[0].message.content, "Generic LLM", "API Reference - OpenAI",
                                    self.modele, datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)

    def query(self, erreur, sql_attendu, sql_soumis):
        try:
            self.set_prompt(erreur, sql_attendu, sql_soumis)
            response = self.client.chat.completions.create(model=self.modele, temperature= 0.0, messages=[
                {'role': 'system', 'content': self.prompt_systeme},
                {'role': 'user', 'content': self.prompt},
            ])
            if self.verbose:
                print(f"{CYAN}{self.prompt_systeme}{RESET}")
                print(f"{CYAN}{self.prompt}{RESET}")
            return response
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)


class PoeLLM(GenericLLM):
    def __init__(self, verbose, sgbd, modele, api_key, base_url = 'https://api.poe.com/v1', bd=None):
        super().__init__(verbose, sgbd, modele,api_key, 'https://api.poe.com/v1', bd)

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            response = self.query(erreur, sql_attendu, sql_soumis)
            return self.set_reponse(response.choices[0].message.content, "POE", "https://poe.com/",
                                    self.modele, datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)

class GoogleLLM(GenericLLM):
    def __init__(self, verbose, sgbd, modele, api_key, base_url = 'https://generativelanguage.googleapis.com/v1beta/openai/', bd=None):
        super().__init__(verbose, sgbd, modele, bd)
        self.api_key = api_key
        self.base_url= base_url
        self.client = openai.OpenAI(api_key=self.api_key)

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            response = self.query(erreur, sql_attendu, sql_soumis)
            return self.set_reponse(response.choices[0].message.content,
                                    "Google", "https://ai.google.dev/gemini-api/",
                                    self.modele, datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)


class OpenaiLLM(GenericLLM):
    def __init__(self, verbose, sgbd, modele, api_key, base_url = 'https://api.openai.com/v1/chat/completions', bd=None):
        super().__init__(verbose, sgbd, modele, bd)
        self.api_key = api_key
        self.base_url= base_url
        self.client = openai.OpenAI(api_key=self.api_key)

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            response = self.query(erreur, sql_attendu, sql_soumis)
            return self.set_reponse(response.choices[0].message.content, "Open AI", "https://openai.com/",
                                    self.modele, datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)

class HuggingLLM(LLM):
    def __init__(self, verbose, sgbd, modele, bd=None):
        super().__init__(verbose, sgbd, modele, bd)

    def run(self, erreur, sql_attendu, sql_soumis):
        try:
            EMAIL = "emmanuel.desmontils@univ-nantes.fr"
            PASSWD = ""
            with importlib.resources.files("querycraft.cookies").joinpath('') as cookie_path_dir:
                cpd = str(cookie_path_dir) + '/'
                # print(cpd)
                # cookie_path_dir = "./cookies/"  # NOTE: trailing slash (/) is required to avoid errors
                sign = Login(EMAIL, PASSWD)
                cookies = sign.login(cookie_dir_path=cpd, save_cookies=True)

                chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

                # Create a new conversation with an assistant
                ASSISTANT_ID = self.modele  # get the assistant id from https://huggingface.co/chat/assistants
                chatbot.new_conversation(assistant=ASSISTANT_ID, switch_to=True)
                self.set_prompt(erreur, sql_attendu, sql_soumis)
                if self.verbose:
                    print(f"{CYAN}{self.prompt_systeme}\n\n{self.prompt}{RESET}")
                return (f"{GREEN}" + chatbot.chat(self.prompt).wait_until_done() + f"{RESET}\n---\n"
                        + f"{BLUE}Source : HuggingChat (https://huggingface.co/chat/), assistant Mia-DB (https://hf.co/chat/assistant/{self.modele}) {RESET}\n"
                        + f"{BLUE}Attention, HuggingChat/Mia-DB ne garantit pas la validité de l'aide. Veuillez vérifier la réponse et vous rapprocher de vos enseignants si nécessaire.{RESET}")
                #return self.set_reponse(chatbot.chat(self.prompt).wait_until_done(), "HuggingChat", "https://huggingface.co/chat/", self.modele,
                #                        datetime.now())
        except Exception as e:
            print(e)
            return super().run(erreur, sql_attendu, sql_soumis)  # + f"\nPb HuggingChat : {e}"


def main():
    mess = HuggingLLM(True, "PostgreSQL", "67bc5132aea628b3325f2f8b", BdD).run(erreur2, sql2, sql2e)
    print(mess)


if __name__ == '__main__':
    main()
