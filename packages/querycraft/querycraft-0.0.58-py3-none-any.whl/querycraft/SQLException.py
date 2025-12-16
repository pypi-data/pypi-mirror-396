import os
import sys
from querycraft.LLM import *
import json
from pathlib import Path
from querycraft.tools import existFile,diff_dates_iso

class SQLException(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message

    def __unicode__(self):
        return self.message

class SQLQueryException(SQLException):
    model = "gemma3:1b"
    service = "ollama"
    api_key = None
    url = None
    ia_on = False

    #cache = dict()
    cache_file = ""

    @classmethod
    def set_model(cls, service, model, api_key=None, url=None, ia_on=True):
        cls.model = model
        cls.api_key = api_key
        cls.service = service
        cls.url = url
        cls.ia_on = ia_on
        cls.cache_file = (cls.service+"_"+cls.model).replace(':','_')+'.json'

    @classmethod
    def get_model(cls):
        return cls.model

    def loadCache(self,cacheName):
        cache = dict()
        with importlib.resources.path("querycraft.cache", cacheName) as file:
            if existFile(file):
                with file.open("r", encoding="utf-8") as fichier:
                    cache = json.load(fichier)
        return cache

    def saveCache(self, cacheName, cache, cle, val):
        cache[cle] = (val, datetime.now().date().isoformat())
        with importlib.resources.path("querycraft.cache", cacheName) as file:
            with file.open("w", encoding="utf-8") as fichier:
                json.dump(cache, fichier, ensure_ascii=False, indent=2)

    def __init__(self,verbose, message, sqlhs, sqlok, sgbd, bd = "", duree = 3):
        super().__init__(message)
        self.sqlhs = sqlhs
        if sqlok is None : self.sqlok = ""
        else: self.sqlok = sqlok
        self.sgbd = sgbd
        self.hints = ""
        print(
            f"Erreur doSBS = {RED}Erreur sur la requête SQL avec {self.sgbd} :\n -> Requête proposée : {self.sqlhs}\n -> Message {self.sgbd} :\n{self.message}{RESET}")  # Affichage de l'erreur de base
        if SQLQueryException.ia_on :
            #print(f"{SQLQueryException.model},{SQLQueryException.api_key}, {SQLQueryException.url}")
            input("Appuyez sur Entrée pour avoir une explication de l'erreur par IA ou Ctrl + Z pour quitter.")
            self.clear_line()
            print("Construction de l'explication. Veuillez patienter.")
            new = False
            maintenant = datetime.now().date().isoformat()
            cache = self.loadCache(SQLQueryException.cache_file)

            if self.sqlhs+self.sqlok in cache:
                (self.hints, date) = cache[self.sqlhs + self.sqlok]
                if not diff_dates_iso(date,maintenant,duree) :
                    self.hints = self.hints + " (cache)"
                    self.clear_line()
                else : self.hints = ""

            if self.hints == "":
                new = True
                if SQLQueryException.service == "ollama" :
                    #print("Appel ollama")
                    self.hints = OllamaLLM(verbose,self.sgbd,SQLQueryException.get_model(),
                                           bd).run(str(self.message), self.sqlok, self.sqlhs)
                elif SQLQueryException.service == "poe" :
                    #print("Appel POE")
                    self.hints = PoeLLM(verbose, self.sgbd, modele=SQLQueryException.model,
                                        api_key=SQLQueryException.api_key, base_url='https://api.poe.com/v1',#SQLQueryException.url,
                                        bd=bd).run(str(self.message), self.sqlok, self.sqlhs)
                elif SQLQueryException.service == "openai":
                    # print("Appel Open AI")
                    self.hints = OpenaiLLM(verbose, self.sgbd, modele=SQLQueryException.model,
                                        api_key=SQLQueryException.api_key, base_url='https://api.openai.com/v1/chat/completions',#SQLQueryException.url,
                                        bd=bd).run(str(self.message), self.sqlok, self.sqlhs)
                elif SQLQueryException.service == "google":
                    # print("Appel Google Gemini")
                    self.hints = GoogleLLM(verbose, self.sgbd, modele=SQLQueryException.model,
                                           api_key=SQLQueryException.api_key, base_url='https://generativelanguage.googleapis.com/v1beta/openai/',#SQLQueryException.url,
                                           bd=bd).run(str(self.message), self.sqlok, self.sqlhs)
                elif SQLQueryException.service == "generic":
                    # print("Appel API Générique")
                    self.hints = GenericLLM(verbose, self.sgbd, modele=SQLQueryException.model,
                                           api_key=SQLQueryException.api_key,
                                           base_url=SQLQueryException.url,
                                           bd=bd).run(str(self.message), self.sqlok, self.sqlhs)
                else :
                    self.hints = ""

                self.clear_line()
                if self.hints:
                    if new:
                        self.saveCache(SQLQueryException.cache_file, cache,self.sqlhs+self.sqlok, self.hints )
                else:
                    print("Modèle pas accessible, utilisation du modèle par défaut")
                    cache = self.loadCache("default.json")
                    if self.sqlhs + self.sqlok in cache:
                        (self.hints, date) = cache[self.sqlhs+ self.sqlok]
                        if not diff_dates_iso(date, maintenant, duree):
                            self.hints = self.hints +" (cache)"
                            new = False
                        else : self.hints = ""

                    if self.hints == "":
                        # gpt-4.1-nano ; gpt-5-nano ; gpt-5.1-codex
                        #print("Appel POE 2")
                        self.hints = PoeLLM(verbose,self.sgbd,
                                        "gpt-4.1-nano", "umnm9e2VrXsAX6FDurYa8ThkRTcYSHuQMzb22xjnh0A","https://api.poe.com/v1",
                                        bd).run(str(self.message), self.sqlok, self.sqlhs)

                    self.clear_line()
                    if new:
                        self.saveCache("default.json", cache, self.sqlhs + self.sqlok, self.hints)

    def __str__(self):
        #mssg = f"{RED}Erreur sur la requête SQL avec {self.sgbd} :\n -> Requête proposée : {self.sqlhs}\n -> Message {self.sgbd} :\n{self.message}{RESET}"
        mssg = ""
        if self.hints != "":
            mssg += f"\n{GREEN} -> Aide :{RESET} {self.hints}"
        return mssg

    def __repr__(self):
        return self.__str__()
    def __unicode__(self):
        return self.__str__()

    def clear_line(self):
        # Windows
        if os.name == 'nt':
            os.system('cls')
        # Unix/Linux/MacOS
        else:
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")