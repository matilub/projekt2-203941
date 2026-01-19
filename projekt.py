import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QPolygonF


class Rura:
    def __init__(self, punkty, grubosc=12, kolor=Qt.gray):

        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255)  # Jasny niebieski
        self.czy_plynie = False

    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie

    def draw(self, painter):
        if len(self.punkty) < 2:
            return

        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        # 1. Rysowanie obudowy rury
        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_rura)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        # 2. Rysowanie cieczy w srodku (jesli plynie)
        if self.czy_plynie:
            pen_ciecz = QPen(self.kolor_cieczy, self.grubosc - 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)


class Zbiornik:
    def __init__(self, x, y, width=100, height=140, nazwa=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0

    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano

    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto

    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc

    def czy_pusty(self): return self.aktualna_ilosc <= 0.1

    def czy_pelny(self): return self.aktualna_ilosc >= self.pojemnosc - 0.1

    # Punkty zaczepienia dla rur
    def punkt_gora_srodek(self): return (self.x + self.width / 2, self.y)

    def punkt_dol_srodek(self): return (self.x + self.width / 2, self.y + self.height)

    def draw(self, painter):
        # 1. Rysowanie cieczy
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height - h_cieczy
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 200))
            painter.drawRect(int(self.x + 3), int(y_start), int(self.width - 6), int(h_cieczy - 2))

        # 2. Rysowanie obrysu
        pen = QPen(Qt.white, 4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        # 3. Podpis
        painter.setPen(Qt.white)
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)


class Pompa:
    def __init__(self, x, y):
        self.x = x #położenie pompy
        self.y = y
        self.wlaczona = False  # Stan początkowy

    def draw(self, painter): #rysowanie pompy

        kolor = Qt.green if self.wlaczona else Qt.red #ustawianie koloru gdy włączona/wyłączona

        painter.setPen(QPen(Qt.white, 2))#kontur
        painter.setBrush(kolor)
        painter.drawEllipse(int(self.x - 15), int(self.y - 15), 30, 30)#okrąg średnica 30px
        painter.setPen(Qt.white)
        painter.drawText(int(self.x - 20), int(self.y + 35), "POMPA")#opis

class Zawor:
    def __init__(self, x, y):
        self.x = x#położenie zaworu
        self.y = y
        self.kierunek = "PRAWO"#ustawienie kierunku jako domyślne

    def draw(self, painter): #rysowanie zaworu

        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QColor(50, 50, 50)) #rysowanie ciemnego kwadratu z białym obrysem
        painter.drawRect(int(self.x - 15), int(self.y - 15), 30, 30)


        painter.setPen(Qt.NoPen)#usuwanie obrysu strzałki

        if self.kierunek == "PRAWO":#jeśli zawór jest w prawo to strzałka jesy ustawiana w prawo i ma kolor zielony

            painter.setBrush(QColor(0, 255, 0))
            points = [
                QPointF(self.x - 5, self.y - 8),#3 punkty tworzące trójkąt w prawo
                QPointF(self.x - 5, self.y + 8),
                QPointF(self.x + 8, self.y)
            ]
        else: #w innym wypadku jest w lewo i jest pomarańczowa

            painter.setBrush(QColor(255, 165, 0))
            points = [
                QPointF(self.x + 5, self.y - 8),#3 punkty tworzące trójkąt w lewo
                QPointF(self.x + 5, self.y + 8),
                QPointF(self.x - 8, self.y)
            ]

        painter.drawPolygon(QPolygonF(points))#rysuje strzałke z aktualnym położeniem


        painter.setPen(Qt.white)
        painter.drawText(int(self.x - 15), int(self.y - 20), "ZAWÓR")#opis

class SymulacjaKaskady(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symulacja")
        self.setFixedSize(1100, 800)
        self.setStyleSheet("background-color: #222;")

        self.z1 = Zbiornik(50, 50, nazwa="Zbiornik 1")
        self.z1.aktualna_ilosc = 100.0;#napełnienie z1 do pełna i aktualizacja poziomu
        self.z1.aktualizuj_poziom()

        self.z2 = Zbiornik(300, 250, nazwa="Zbiornik 2")
        self.z3 = Zbiornik(450, 550, nazwa="Zbiornik 3")
        self.z4 = Zbiornik(150, 550, nazwa="Zbiornik 4")
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4] #lista zbiorników

        self.pompa=Pompa(500,740)#ustawianie pompy i zaworu
        self.zawor = Zawor(350, 500)


        #ustawianie rur punktowo

        p_start = self.z1.punkt_dol_srodek() #tworzenie punktu startu i końca rury
        p_koniec = self.z2.punkt_gora_srodek()
        mid_y = (p_start[1] + p_koniec[1]) / 2 #tworzenie dodatkowej zmiennej do łamania rury

        self.rura1 = Rura([  #ustawianie punktów w odpowiedniej kolejności rura Z1---> Z2
            p_start, (p_start[0], mid_y), (p_koniec[0], mid_y), p_koniec
        ])

        #Rura Z2---> ZAWÓR
        p_start2 = self.z2.punkt_dol_srodek()
        p_koniec2 = (self.zawor.x,self.zawor.y)
        mid_y2 = (p_start2[1] + p_koniec2[1]) / 2

        self.rura2 = Rura([
            p_start2,
            (p_start2[0], mid_y2),
            (p_koniec2[0], mid_y2),
            p_koniec2
        ])

        #Rura ZAWÓR-->Z3
        p_start3 = (self.zawor.x , self.zawor.y)
        p_koniec3 = self.z3.punkt_gora_srodek()
        mid_y3 = (p_start3[1] + p_koniec3[1]) / 2


        self.rura3 = Rura([
            p_start3,
            (p_koniec3[0], p_start3[1]),
            (p_koniec3[0], mid_y3),
            p_koniec3
        ])

        # Rura ZAWÓR-->Z4
        p_start4 = (self.zawor.x, self.zawor.y)
        p_koniec4 = self.z4.punkt_gora_srodek()
        mid_y4 = (p_start4[1] + p_koniec4[1]) / 2

        self.rura4 = Rura([
            p_start4,
            (p_koniec4[0], p_start4[1]),
            (p_koniec4[0], mid_y4),
            p_koniec4
        ])

        # Rura Z4-->Z1
        p_start5 = self.z4.punkt_dol_srodek()
        p_koniec5 = self.z1.punkt_gora_srodek()

        x_pompa = self.pompa.x
        y_pompa = self.pompa.y

        self.rura_powrot = Rura([
            p_start5,  # start Z4
            (p_start5[0], p_start5[1] + 50),
            (x_pompa, p_start5[1] + 50),
            (x_pompa + 100, p_start5[1] + 50),
            (x_pompa + 100, p_koniec5[1]-20),
            (p_koniec5[0], p_koniec5[1] - 20),
            p_koniec5
        ])

        self.rury = [self.rura1, self.rura2, self.rura3, self.rura4, self.rura_powrot] #lista wszystkich rur

        self.timer = QTimer() #timer
        self.timer.timeout.connect(self.logika_przeplywu) #wywołanie funkcji logika przepływu

        lbl_raport = QLabel("LOGI:", self)#okno raportów
        lbl_raport.setGeometry(700, 50, 200, 20)
        lbl_raport.setStyleSheet("color: white; font-weight: bold;")

        self.okno_raportow = QTextEdit(self)
        self.okno_raportow.setGeometry(700, 80, 350, 450)
        self.okno_raportow.setReadOnly(True) #pole tekstowe tylko do odczytu
        self.okno_raportow.setStyleSheet("background-color: #111; color: #00FF00; font-family: Consolas; border: 1px solid #555;")


        #ustawianie przycisków

        self.btn = QPushButton("Start/Stop", self)
        self.btn.setGeometry(700, 550, 170, 40)
        self.btn.setStyleSheet("background-color: #555; color: white;")
        self.btn.clicked.connect(self.przelacz_symulacje)#start stop uruchamiający symulacje

        self.btn_pompa = QPushButton("WŁĄCZ POMPĘ", self)
        self.btn_pompa.setGeometry(880, 550, 170, 40)
        self.btn_pompa.setStyleSheet("background-color: #AA0000; color: white; font-weight: bold;")
        self.btn_pompa.clicked.connect(self.przelacz_pompe)


        self.btn_dolej_z1 = QPushButton("DOLEJ Z1", self)
        self.btn_dolej_z1.setGeometry(700, 600, 170, 40)
        self.btn_dolej_z1.setStyleSheet(
            "background-color: #0066CC; color: white; font-weight: bold;"
        )
        self.btn_dolej_z1.clicked.connect(self.dolej_z1)


        self.btn_usun_z3 = QPushButton("USUŃ Z3", self)
        self.btn_usun_z3.setGeometry(880, 600, 170, 40)
        self.btn_usun_z3.setStyleSheet(
            "background-color: #CC6600; color: white; font-weight: bold;"
        )
        self.btn_usun_z3.clicked.connect(self.usun_z3)

        self.running = False
        self.flow_speed = 0.8#prędkość przepływu
        self.stan_zaworu_ostatni = "PRAWO"
        self.log("System uruchomiony i gotowy do pracy.")

    def log(self, wiadomosc):

        self.okno_raportow.append(f"{wiadomosc}")#dodawanie wiadomości do logów
        cursor = self.okno_raportow.textCursor()
        cursor.movePosition(cursor.End)#ustawianie kursora na końcu
        self.okno_raportow.setTextCursor(cursor)#wyświetla najnowszy wpis


    def przelacz_symulacje(self):#przełączanie symulacji
        if self.running:
            self.timer.stop()
            self.log("ZATRZYMANO symulację.")
        else:
            self.timer.start(20)
            self.log("URUCHOMIONO symulację.")
        self.running = not self.running#zmiana stanu symulacji na przeciwny

    def dolej_z1(self):
        ilosc = 20.0#dolewa 20l
        dodano = self.z1.dodaj_ciecz(ilosc)

        if dodano > 0:#dolewanie cieczy jeśli prawie pełny to doleje ile może
            self.log(f"OPERATOR: Dolano {dodano:.1f} do Zbiornika 1.")
        else:
            self.log("OPERATOR: Zbiornik 1 jest już PEŁNY.")

        self.update() #update stanu

    def usun_z3(self):
        ilosc = 100.0
        usunieto = self.z3.usun_ciecz(ilosc)

        if usunieto > 0:
            self.log(f"OPERATOR: Usunięto {usunieto:.1f} z Zbiornika 3.")
        else:
            self.log("OPERATOR: Zbiornik 3 jest PUSTY.")

        self.update()

    def przelacz_pompe(self):
        self.pompa.wlaczona = not self.pompa.wlaczona#zmiana stanu pompy
        if self.pompa.wlaczona:
            self.btn_pompa.setText("POMPA PRACUJE")
            self.btn_pompa.setStyleSheet("background-color: #00AA00; color: white;")
            self.log("STEROWANIE: Pompa została WŁĄCZONA.")
        else:
            self.btn_pompa.setText("WŁĄCZ POMPĘ")
            self.btn_pompa.setStyleSheet("background-color: #AA0000; color: white;")
            self.log("STEROWANIE: Pompa została WYŁĄCZONA.")

    def logika_przeplywu(self):

        plynie_1 = False

        if self.z1.czy_pusty() == False:
            if self.z2.czy_pelny() == False:
                ilosc = self.z1.usun_ciecz(self.flow_speed)
                self.z2.dodaj_ciecz(ilosc)
                plynie_1 = True#jeśli z1 nie jest pysty a z2 nie jest pełne ustawia przepływ między nimi

        self.rura1.ustaw_przeplyw(plynie_1)#w rurze widać wode


        if self.z3.aktualna_ilosc >= 99.0:#ustawianie automatyczne zaworu
            self.zawor.kierunek = "LEWO"
            cel_z3 = False
        else:
            self.zawor.kierunek = "PRAWO"
            cel_z3 = True


        if self.zawor.kierunek != self.stan_zaworu_ostatni:#sprawdzenie czy zawór zmienił położenie
            if self.zawor.kierunek == 'LEWO':
                self.log("AUTO: Przełączono zawór na: Z4 (Powrót)")
            else:
                self.log("AUTO: Przełączono zawór na: Z3 (Cel)")
            self.stan_zaworu_ostatni = self.zawor.kierunek


        plynie_2 = False
        plynie_3 = False
        plynie_4 = False

        if self.z2.aktualna_ilosc > 0:
            plynie_2 = True
            if cel_z3:

                self.z2.usun_ciecz(self.flow_speed)
                self.z3.dodaj_ciecz(self.flow_speed)#jeśli usuwanie i dodawanie cieczy synchornicznie
                plynie_3 = True
            else:

                if not self.z4.czy_pelny():
                    self.z2.usun_ciecz(self.flow_speed)
                    self.z4.dodaj_ciecz(self.flow_speed)
                    plynie_4 = True

        self.rura2.ustaw_przeplyw(plynie_2)#zapalanie rury kiedy płynie ciecz
        self.rura3.ustaw_przeplyw(plynie_3)
        self.rura4.ustaw_przeplyw(plynie_4)


        plynie_powrot = False
        if self.pompa.wlaczona:#czekanie aż operator włączy pompe
            if not self.z4.czy_pusty() and not self.z1.czy_pelny():#sprawdzamy czy z4 i z1 nie są puste

                ilosc = self.z4.usun_ciecz(self.flow_speed)
                self.z1.dodaj_ciecz(ilosc)#usuwamy i dodajemy tyle samo cieczy z z4 do z1
                plynie_powrot = True
            elif self.z4.czy_pusty():#jeśli pompa pracuje bez cieczy to ją wyłącza automatycznie

                self.przelacz_pompe()
                self.log("ALARM: Pompa zatrzymana - brak cieczy w Z4!")

        self.rura_powrot.ustaw_przeplyw(plynie_powrot)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        for r in self.rury: r.draw(p)#rysuje wszystkie rury
        for z in self.zbiorniki: z.draw(p)#rysuje wszystkie zbiorniki
        self.pompa.draw(p)#rysuje zawór i pompe
        self.zawor.draw(p)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = SymulacjaKaskady()
    okno.show()
    sys.exit(app.exec_())