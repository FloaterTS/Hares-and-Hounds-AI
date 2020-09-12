import time

INF = 2 ** 30  # Pe post de infinit


def board(lista_poz):  # Formatul afisarii tablei
    return (f"\n  {lista_poz[1]}-{lista_poz[4]}-{lista_poz[7]}\n" + " /|\\|/|\\\n" +
            f"{lista_poz[0]}-{lista_poz[2]}-{lista_poz[5]}-{lista_poz[8]}-{lista_poz[10]}\n" +
            " \\|/|\\|/\n" + f"  {lista_poz[3]}-{lista_poz[6]}-{lista_poz[9]}")


class Joc:          # Clasa statica ce detine informatiile cunoscute de la inceput despre joc
    HARE = 'i'
    HOUNDS = 'c'
    # Vecinii la care poate ajunge iepurele din oricare loc
    NEIGHBOURS_HARE = [[1, 2, 3], [0, 2, 4, 5], [0, 1, 3, 5], [0, 2, 5, 6], [1, 5, 7], [1, 2, 3, 4, 6, 7, 8, 9],
                       [3, 5, 9], [4, 5, 8, 10], [5, 7, 9, 10], [5, 6, 8, 10], [7, 8, 9]]
    # Vecinii la care poate ajunge un caine din oricare loc
    NEIGHBOURS_HOUNDS = [[1, 2, 3], [2, 4, 5], [1, 3, 5], [2, 5, 6], [5, 7], [4, 6, 7, 8, 9], [5, 9], [8, 10],
                         [7, 9, 10], [8, 10], []]
    DISTANCE_FROM_HSTART = [40, 30, 30, 30, 20, 25, 20, 10, 10, 10, 0]  # Distanta fata de punctul de start al iepurelui
    ADANCIME_MAX = None  # inmultita cu 10, folosita pt euristica (scor)

    @staticmethod
    def stare_initiala():  # Functie ce creaza starea initiala a jocului
        hare_poz = 10
        hounds_poz = [0, 1, 3]
        jucator_init = Joc.HOUNDS
        return StareJoc(jucator_init, hare_poz, hounds_poz, Joc.ADANCIME_MAX)


class StareJoc:  # Clasa ce retine starea jocului intr un moment dat sau intr o anumita situatie

    def __init__(self, jucator, hare_poz, hounds_poz, adancime, scor=None):

        self.jucator = jucator  # Jucatorul al carui rand e (iepure sau caini)

        self.hare_poz = hare_poz  # Pozitia iepurelui pe tabla
        self.hounds_poz = hounds_poz.copy()  # Pozitia cainilor pe tabla

        # Adancimea in arborele de stari
        # (scade cu cate o unitate din „tata” in „fiu”)
        self.adancime = adancime

        # Scorul starii (daca e finala, adica frunza a arborelui)
        # sau scorul celei mai bune stari-fiu - pentru jucatorul curent
        self.scor = scor

        # Lista de mutari posibile din starea curenta
        self.mutari_posibile = []  # Lista va contine obiecte de tip StareJoc

        # Cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

    def is_hare_escaped(self):  # Functie care verif daca iepurele a ajuns la dest (a scapat de caini - a castigat)
        return self.hare_poz == 0

    def is_hare_cornered(self):  # Functie care verifica daca iepurele a fost incoltit de caini (a pierdut)
        return ((self.hare_poz == 10 and set(self.hounds_poz) == {7, 8, 9}) or
                (self.hare_poz == 4 and set(self.hounds_poz) == {1, 5, 7}) or
                (self.hare_poz == 6 and set(self.hounds_poz) == {3, 5, 9}))

    def jucator_opus(self):  # Functie care returneaza jucatorul opus
        if self.jucator == Joc.HARE:
            return Joc.HOUNDS
        return Joc.HARE

    def hare_moves(self):  # Functie care returneaza toate starile de joc posibile in urma unei mutari a iepurelui
        moves = []

        for neighbour in Joc.NEIGHBOURS_HARE[self.hare_poz]:
            if neighbour in self.hounds_poz:
                continue

            new_hare_position = neighbour
            moves.append(StareJoc(self.jucator_opus(), new_hare_position, self.hounds_poz, self.adancime - 1))

        return moves

    def hounds_moves(self):  # Functie care returneaza toate starile de joc posibile in urma unei mutari a unui caine
        moves = []

        for hound in range(3):
            hound_poz = self.hounds_poz[hound]

            for neighbour in Joc.NEIGHBOURS_HOUNDS[hound_poz]:
                if neighbour == self.hare_poz or neighbour in self.hounds_poz:
                    continue

                new_hounds_positions = self.hounds_poz.copy()
                for i in range(0, 3):
                    if new_hounds_positions[i] == hound_poz:
                        new_hounds_positions[i] = neighbour
                moves.append(StareJoc(self.jucator_opus(), self.hare_poz, new_hounds_positions, self.adancime - 1))

        return moves

    def mutari_stare(self):  # Functie ce returneaza starile de joc posibile in urma unei mutari in starea curenta
        if self.jucator == Joc.HARE:
            return self.hare_moves()
        return self.hounds_moves()

    def scor_euristic(self):  # Functia euristica ce calculeaza scorul unei stari de joc
        if self.is_hare_escaped():  # Daca iepurele poate scapa, scorul este maximizat
            return INF - Joc.ADANCIME_MAX - 1 + self.adancime  # Se tine cont si de adancimea starii in arbore
        if self.is_hare_cornered():  # Daca iepurele este incoltit, scorul este minimizat
            return -INF + Joc.ADANCIME_MAX + 1 - self.adancime  # Se tine cont si de adancimea starii in arbore
        # Daca nu poate nici scapa, nici sa fie incoltit, se tine cont de distanta ramasa fata de
        return Joc.DISTANCE_FROM_HSTART[self.hare_poz]  # punctul destinatie (de scapare) - Distanta Manhattan

    def show_board(self):     # Functie ce returneaza tabla formatata a starii curente de joc
        pozitii = ['*'] * 11
        pozitii[self.hare_poz] = 'i'
        for i in range(0, 3):
            pozitii[self.hounds_poz[i]] = 'c'
        return board(pozitii)


def min_max(stare):
    # Daca am ajuns la o frunza a arborelui, adica:
    # - daca am expandat arborele pana la adancimea maxima permisa
    # - sau daca am ajuns intr-o configuratie finala de joc
    if stare.adancime == 0 or stare.is_hare_cornered() or stare.is_hare_escaped():
        # calculam scorul frunzei apeland "estimeaza_scor"
        stare.scor = stare.scor_euristic()
        return stare

    # Altfel, calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari_stare()

    # Aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutari_scor = [min_max(mutare) for mutare in stare.mutari_posibile]

    if stare.jucator == Joc.HARE:
        # Daca jucatorul e HARE, aleg starea-fiu cu scorul maxim
        stare.stare_aleasa = max(mutari_scor, key=lambda x: x.scor)
    else:
        # Daca jucatorul e HOUNDS aleg starea-fiu cu scorul minim
        stare.stare_aleasa = min(mutari_scor, key=lambda x: x.scor)

    # Actualizez scorul „tatalui” = scorul „fiului” ales
    stare.scor = stare.stare_aleasa.scor
    return stare


def alpha_beta(stare, alpha, beta):
    # Daca am ajuns la o frunza a arborelui, adica:
    # - daca am expandat arborele pana la adancimea maxima permisa
    # - sau daca am ajuns intr-o configuratie finala de joc
    if stare.adancime == 0 or stare.is_hare_cornered() or stare.is_hare_escaped():
        # Calculam scorul frunzei apeland "estimeaza_scor"
        stare.scor = stare.scor_euristic()
        return stare

    # Conditia de retezare:
    if alpha >= beta:
        return stare  # Interval invalid, nu mai procesam

    # Calculez toate mutarile posibile din starea curenta (toti „fiii”)
    stare.mutari_posibile = stare.mutari_stare()

    if stare.jucator == Joc.HARE:
        scor_curent = -INF  # Scorul „tatalui” de tip MAX

        # Pentru fiecare „fiu” de tip MIN:
        for mutare in stare.mutari_posibile:
            # Calculeaza scorul fiului curent
            stare_noua = alpha_beta(mutare, alpha, beta)

            # Incerc sa imbunatatesc (cresc) scorul si alfa „tatalui” de tip MAX, folosind scorul fiului curent
            if scor_curent <= stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if alpha < stare_noua.scor:
                alpha = stare_noua.scor
                if alpha >= beta:  # Verific conditia de retezare
                    break  # Nu se mai extind ceilalti fii de tip MIN

    elif stare.jucator == Joc.HOUNDS:
        scor_curent = INF  # Scorul „tatalui” de tip MIN

        # Pentru fiecare „fiu” de tip MAX:
        for mutare in stare.mutari_posibile:
            stare_noua = alpha_beta(mutare, alpha, beta)

            # Incerc sa imbunatatesc (scad) scorul si beta „tatalui” de tip MIN, folosind scorul fiului curent
            if scor_curent >= stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if beta > stare_noua.scor:
                beta = stare_noua.scor
                if alpha >= beta:  # Verific conditia de retezare
                    break  # Nu se mai extind ceilalti fii de tip MAX

    # Actualizez scorul „tatalui” = scorul „fiului” ales
    stare.scor = stare.stare_aleasa.scor

    return stare


def final_joc(stare):   # Functie care verifica daca jocul s-a sfarsit si afiseaza mesajul corespunzator in caz pozitiv
    if stare.is_hare_cornered():
        print("Cainii au castigat!")
        return True
    if stare.is_hare_escaped():
        print("Iepurele a castigat!")
        return True
    return False


def main():
    print("\nProgramul poate fi oprit in timpul jocului prin introducerea \" -1 \"\n")
    ture = 0
    tip_algoritm = None
    raspuns_valid = False
    while not raspuns_valid:    # Alegem tipul algoritmului
        tip_algoritm = input("Algorimul folosit? (raspundeti cu 1 sau 2)\n 1.Minimax\n 2.Alpha-Beta\n ")
        if tip_algoritm in ['1', '2']:
            raspuns_valid = True
        else:
            print("Nu ati ales o varianta corecta.")

    # Initializare ADANCIME_MAX
    raspuns_valid = False
    while not raspuns_valid:
        n = input("Nivel de dificultate (2-3=incepator, 4-5=mediu, 6-7=avansat):\n")  # Adancimea maxima a arborelui
        if n.isdigit() and 1 < int(n) < 8:
            Joc.ADANCIME_MAX = int(n)
            raspuns_valid = True
        else:
            print("Trebuie sa introduceti un numar natural nenul intre 2 si 7.")

    # Initializare jucatori
    player = None
    raspuns_valid = False
    while not raspuns_valid:
        player = input("Doriti sa jucati cu iepurele(i) sau cu cainii(c)? ").lower()
        if player in ['i', 'c']:
            raspuns_valid = True
        else:
            print("Raspunsul trebuie sa fie i sau c.")

    # Creare stare initiala
    stare_curenta = Joc.stare_initiala()

    while True:
        if stare_curenta.jucator == player:
            # Mutare jucator

            # Preiau timpul in secunde de dinainte de mutare
            t_inainte = int(round(time.time()))

            raspuns_valid = False
            while not raspuns_valid:

                print(board(list(range(11))))   # Afisam modelul tablei de joc cu pozitiile posibile

                print(stare_curenta.show_board())   # Afisam tabla de joc actuala

                if player == 'i':
                    pozitie_noua_i = int(input("Pozitie noua a iepurelui = "))
                    if (pozitie_noua_i in Joc.NEIGHBOURS_HARE[stare_curenta.hare_poz]   # Verificam pozitiile valide
                            and pozitie_noua_i not in stare_curenta.hounds_poz):
                        stare_curenta.hare_poz = pozitie_noua_i          # Schimbam pozitia
                        raspuns_valid = True
                    elif pozitie_noua_i == -1:           # Verificam daca se cere terminarea jocului
                        print("Ai facut " + str(ture) + " mutari.")
                        return
                    else:
                        print("\nNu ati introdus o pozitie valida.")
                else:
                    hound = int(input("Mutati cainele de pe pozitia = "))
                    if hound in stare_curenta.hounds_poz:
                        pozitie_noua_c = int(input("Pozitie noua a cainelui = "))
                        if (pozitie_noua_c in Joc.NEIGHBOURS_HOUNDS[hound] and pozitie_noua_c not in  # Verif poz valide
                                stare_curenta.hounds_poz and pozitie_noua_c != stare_curenta.hare_poz):
                            for i in range(0, 3):
                                if stare_curenta.hounds_poz[i] == hound:
                                    stare_curenta.hounds_poz[i] = pozitie_noua_c    # Schimbam pozitia
                            raspuns_valid = True
                        elif pozitie_noua_c == -1:      # Verificam daca se cere terminarea jocului
                            print("Ai facut " + str(ture) + " mutari.")
                            return
                        else:
                            print("\nNu ati introdus o pozitie valida.")
                    elif hound == -1:                   # Verificam daca se cere terminarea jocului
                        print("Ai facut " + str(ture) + " mutari.")
                        return
                    else:
                        print("\nNu exista un caine pe acea pozitie.")

            # Afisarea starii jocului in urma mutarii utilizatorului
            print("\nTabla dupa mutarea jucatorului:")
            print(stare_curenta.show_board())

            # Preiau timpul in secunde de dupa mutare
            t_dupa = int(round(time.time()))
            print("Jucatorul a gandit timp de " + str(t_dupa - t_inainte) + " secunde.")
            ture = ture + 1

            # Testam daca jocul a ajuns intr-o stare finala
            # si afisez un mesaj corespunzator in caz pozitiv
            if final_joc(stare_curenta):
                break

            # S-a realizat o mutare. Schimb jucatorul cu cel opus
            stare_curenta.jucator = stare_curenta.jucator_opus()

        else:
            # Mutare calculator

            # Preiau timpul in milisecunde de dinainte de mutare
            t_inainte = int(round(time.perf_counter() * 1000))
            if tip_algoritm == '1':
                stare_actualizata = min_max(stare_curenta)
            else:  # tip_algoritm == '2'
                stare_actualizata = alpha_beta(stare_curenta, -INF, INF)

            stare_curenta.hare_poz = stare_actualizata.stare_aleasa.hare_poz   # Actualizam starea curenta de joc
            stare_curenta.hounds_poz = stare_actualizata.stare_aleasa.hounds_poz.copy()

            print("Tabla dupa mutarea calculatorului:")     # Afisam tabla de joc de dupa mutarea calculatorului
            print(stare_curenta.show_board())

            # Preiau timpul in milisecunde de dupa mutare
            t_dupa = int(round(time.perf_counter() * 1000))
            print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")

            if final_joc(stare_curenta):    # Testam daca jocul s-a finalizat
                break

            # S-a realizat o mutare. Schimb jucatorul cu cel opus
            stare_curenta.jucator = stare_curenta.jucator_opus()
    print("Ai facut " + str(ture) + " mutari.")


if __name__ == "__main__":

    # Preiau timpul in secunde de la inceputul programului
    t_start = int(round(time.time()))

    main()

    # Preiau timpul in secunde de dupa mutare
    t_end = int(round(time.time()))
    print("\nProgramul a rulat timp de " + str(t_end - t_start) + " secunde.")
