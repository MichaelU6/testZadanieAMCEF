Názov aplikácie
Microservice v Pythone, ktorý sprostredkováva RESTful API na manažovanie príspevkov používateľov. 

Inštalácia
Nasledujúce inštrukcie vám ukážu, ako nainštalovať a spustiť aplikáciu v kontajneri pomocou Dockeru.

Najprv si nainštalujte Docker z oficiálnych webových stránok: Docker Install .

Stiahnite si Docker obraz aplikácie [v súbore testzadanie.tar](https://ulozto.sk/tam/e12a2bbd-6d83-4090-b545-01c8b2777d46)

Po úspešnom stiahnutí prejdite v termináli do priečinku kde je obraz uložený a sputite príkaz:
'docker load -i testzadanie.tar'

Po úspešnom natiahnutí obrazu spustite kontajner pomocou nasledujúceho príkazu:
'docker run -p 5000:5000 testzadanie' 
Týmto príkazom spustíte kontajner a prepojíte port 5000 uvnitř kontajneru s portom 5000 na vašom hostiteľskom stroji.

Otvorte webový prehliadač a prejdite na http://localhost:5000, aby ste videli domovskú stránku aplikácie.

Použitie
Aplikácia najprv otovrí domovskú stránku. Pre pridanie príspevku sa použíej talčidlo pridať príspevok. Je potrebné zadať všetky údaje o príspevku a odoslať príspevok.
Pre prezeranie príspevku použíjete tlačidlo príspevky. Následne treba vybrať id príspevku alebo id užívateľa a vyhľadať prísevky. Po vyhľadaní môžeme každý príspevok
vymazať alebo upraviť.


Autor: Michal Uhrin
