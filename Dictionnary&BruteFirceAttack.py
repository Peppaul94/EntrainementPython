import threading
import time
import random
import string


## Fonction permettant l'affichage du temps (debug)
def print_time(threadName, delay):
   while 1:
      time.sleep(delay)
      print ("%s: %s" % (threadName, time.ctime(time.time())))


## Classe permettant l'exécution de plusieurs tâches en même temps. 
## Pour résumer, plutôt que d'essayer un a un les mots de passe, on fait tourner le script plusieurs fois 
## en même temps. Ainsi, cela devine le mot de passe beaucoup plus vite
class MyThread(threading.Thread):
    def __init__(self, thread_id, password, stop_event, used_strings, lock):
        threading.Thread.__init__(self)
        self.thread_id = thread_id  
        self.password = password
        self.length = len(password)
        self.stop_event = stop_event
        self.used_strings = used_strings  
        self.lock = lock
    
    ## Fonction qui fait l'attaque par force brute
    def brute_force(self, length):
        characters = string.digits + string.ascii_lowercase + string.ascii_uppercase 
        while True:
            random_string = ''.join(random.choice(characters) for _ in range(length))
            with self.lock:  
                if random_string not in self.used_strings:
                    self.used_strings.add(random_string)
                    return random_string


    ## Fonction qui vérifie si on a trouvé le bon mot de passe
    def find_matching_string(self, stop_event):
        start_time = time.time()
        attempts = 0  
        while not stop_event.is_set():  
            random_string = self.brute_force(self.length)
            attempts += 1
            
            if random_string == self.password:
                end_time = time.time()  
                duration = end_time - start_time  
                print(f"{self.name}: Match found after {attempts} attempts: {random_string}")
                print(f"{self.name}: Time taken: {duration:.2f} seconds")
                stop_event.set()  
                break

    ## Lancement du script
    def run(self):
        self.find_matching_string(stop_event)


## Définition de la liste de mot de passe à utiliser et du mot de passe à trouver
file_path = input("Nom du fichier: ")
password="Poussin2000"


## Fonction permettant l'attaque par dictionnaire
def dictionary_attack(file_path, password, stop_event):
        try:
            with open(file_path, 'r', encoding='ISO-8859-1') as file:
                for i, line in enumerate(file):  
                    word = line.strip()
                    if word == password:
                        print(f"Password '{password}' found on line {i + 1}")
                        stop_event.set()
                        return
                print(f"Password '{password}' not found in the file.")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")


used_strings = set()
lock = threading.Lock()
stop_event = threading.Event()


dictionary_attack(file_path, password, stop_event)


threads = []
## Nombre de "scripts" qui seront lancés en même temps
num_threads = 278

## Fonction qui lance les "scripts" et les garde actif tant que le mot de passe n'est pas trouvé
if not stop_event.is_set():
    for i in range(num_threads):
        thread = MyThread(i, password, stop_event, used_strings, lock)
        threads.append(thread)
        thread.start()


for thread in threads:
    thread.join()
