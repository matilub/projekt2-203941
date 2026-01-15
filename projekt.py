import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QPolygonF


class Rura:
    def __init__(self, punkty, grubosc=12, kolor=Qt.gray):
        # Konwersja listy krotek na obiekty QPointF
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
        self.poziom = 0.0  # Wartosc 0.0-1.0

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
        self.x = x
        self.y = y
        self.wlaczona = False  # Stan początkowy

    def draw(self, painter):
        # Zielony jak włączona, Czerwony jak wyłączona
        kolor = Qt.green if self.wlaczona else Qt.red

        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(kolor)
        painter.drawEllipse(int(self.x - 15), int(self.y - 15), 30, 30)  # Kółko R=15

        painter.setPen(Qt.white)
        painter.drawText(int(self.x - 20), int(self.y + 35), "POMPA")

class Zawor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kierunek = "PRAWO"

    def draw(self, painter):
        # 1. Rysujemy KWADRAT (Obudowa)
        # Rozmiar 30x30, wyśrodkowany w punkcie x, y
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QColor(50, 50, 50)) # Ciemne tło zaworu
        painter.drawRect(int(self.x - 15), int(self.y - 15), 30, 30)

        # 2. Rysujemy TRÓJKĄT (Strzałka) w środku
        # Wyłączamy obrys dla trójkąta, żeby był czysty kolor
        painter.setPen(Qt.NoPen)

        if self.kierunek == "PRAWO":
            # Zielony trójkąt w prawo (do Z3)
            painter.setBrush(QColor(0, 255, 0))
            points = [
                QPointF(self.x - 5, self.y - 8),  # Lewa góra
                QPointF(self.x - 5, self.y + 8),  # Lewy dół
                QPointF(self.x + 8, self.y)       # Dziób w prawo
            ]
        else:
            # Pomarańczowy trójkąt w lewo (do Z4)
            painter.setBrush(QColor(255, 165, 0))
            points = [
                QPointF(self.x + 5, self.y - 8),  # Prawa góra
                QPointF(self.x + 5, self.y + 8),  # Prawy dół
                QPointF(self.x - 8, self.y)       # Dziób w lewo
            ]

        painter.drawPolygon(QPolygonF(points))

        # 3. Podpis nad zaworem
        painter.setPen(Qt.white)
        painter.drawText(int(self.x - 15), int(self.y - 20), "ZAWÓR")

class SymulacjaKaskady(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kaskada: Dol -> Gora")
        self.setFixedSize(1100, 800)
        self.setStyleSheet("background-color: #222;")

        self.z1 = Zbiornik(50, 50, nazwa="Zbiornik 1")
        self.z1.aktualna_ilosc = 100.0;
        self.z1.aktualizuj_poziom()

        self.z2 = Zbiornik(300, 250, nazwa="Zbiornik 2")
        self.z3 = Zbiornik(450, 550, nazwa="Zbiornik 3")
        self.z4 = Zbiornik(150, 550, nazwa="Zbiornik 4")
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4]

        self.pompa=Pompa(500,700)
        self.zawor = Zawor(350, 500)

        p_start = self.z1.punkt_dol_srodek()
        p_koniec = self.z2.punkt_gora_srodek()
        mid_y = (p_start[1] + p_koniec[1]) / 2

        self.rura1 = Rura([
            p_start, (p_start[0], mid_y), (p_koniec[0], mid_y), p_koniec
        ])

        p_start2 = self.z2.punkt_dol_srodek()
        p_koniec2 = (self.zawor.x,self.zawor.y)
        mid_y2 = (p_start2[1] + p_koniec2[1]) / 2

        self.rura2 = Rura([
            p_start2,
            (p_start2[0], mid_y2),
            (p_koniec2[0], mid_y2),
            p_koniec2
        ])

        p_start3 = (self.zawor.x , self.zawor.y)
        p_koniec3 = self.z3.punkt_gora_srodek()
        mid_y3 = (p_start3[1] + p_koniec3[1]) / 2

        self.rura3 = Rura([
            p_start3,  # WYJŚCIE Z PRAWEGO BOKU ZAWORU
            (p_koniec3[0], p_start3[1]),  # POZIOMO W PRAWO
            (p_koniec3[0], mid_y3),  # SKRĘT W DÓŁ
            p_koniec3
        ])

        p_start4 = (self.zawor.x, self.zawor.y)
        p_koniec4 = self.z4.punkt_gora_srodek()
        mid_y4 = (p_start4[1] + p_koniec4[1]) / 2

        self.rura4 = Rura([
            p_start4,  # WYJŚCIE Z PRAWEGO BOKU ZAWORU
            (p_koniec4[0], p_start4[1]),  # POZIOMO W PRAWO
            (p_koniec4[0], mid_y4),  # SKRĘT W DÓŁ
            p_koniec4
        ])

        # RURA Z4 -> Z1: dół Z4 -> prawo -> góra -> 90° do Z1
        p_start4 = self.z4.punkt_dol_srodek()  # Dół Z4 (150+50, 550+140) = (200, 690)
        p_koniec1 = self.z1.punkt_gora_srodek()  # Góra Z1 (50+50, 50) = (100, 50)


        x_pompa = self.pompa.x
        y_pompa = self.pompa.y

        self.rura_powrot = Rura([
            p_start4,  # start Z4
            (p_start4[0], p_start4[1] + 50),  # w dół 50 px
            (x_pompa, p_start4[1] + 50),  # poziomo w prawo do pompy
            (x_pompa, y_pompa),  # w górę do poziomu pompy
            (p_koniec1[0], y_pompa),  # poziomo w lewo nad Z1
            p_koniec1  # pionowo w dół do Z1
        ])

        self.rury = [self.rura1, self.rura2, self.rura3, self.rura4, self.rura_powrot]

        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_przeplywu)

        self.btn = QPushButton("start/stop", self)
        self.btn.setGeometry(50, 550, 100, 30)
        self.btn.setStyleSheet("background-color: #444; color: white;")
        self.btn.clicked.connect(self.przelacz_symulacje)


        # # z1
        # self.btn_z1_dodaj = QPushButton("(+) Napełnij z1", self)
        # self.btn_z1_dodaj.setGeometry(150, 520, 100, 30)
        # self.btn_z1_dodaj.setStyleSheet("background-color: #444; color: white;")
        # self.btn_z1_dodaj.clicked.connect(self.napelnij_z1)
        #
        # self.btn_z1_usun = QPushButton("(-) Opróżnij z1", self)
        # self.btn_z1_usun.setGeometry(150, 555, 100, 30)
        # self.btn_z1_usun.setStyleSheet("background-color: #444; color: white;")
        # self.btn_z1_usun.clicked.connect(self.oproznij_z1)
        #
        # # z2
        # self.btn_z2_dodaj = QPushButton("(+) Napełnij z2", self)
        # self.btn_z2_dodaj.setGeometry(250, 520, 100, 30)
        # self.btn_z2_dodaj.setStyleSheet("background-color: #444; color: white;")
        # self.btn_z2_dodaj.clicked.connect(self.napelnij_z2)
        #
        # self.btn_z2_usun = QPushButton("(-) Opróżnij z2", self)
        # self.btn_z2_usun.setGeometry(250, 555, 100, 30)
        # self.btn_z2_usun.setStyleSheet("background-color: #444; color: white;")
        # self.btn_z2_usun.clicked.connect(self.oproznij_z2)
        #
        # # z3
        # self.btn_z3_dodaj = QPushButton("(+) Napełnij z3", self)
        # self.btn_z3_dodaj.setGeometry(350, 520, 100, 30)
        # self.btn_z3_dodaj.setStyleSheet("background-color: #444; color: white;")
        # self.btn_z3_dodaj.clicked.connect(self.napelnij_z3)
        #
        # self.btn_z3_usun = QPushButton("(-) Opróżnij z3", self)
        # self.btn_z3_usun.setGeometry(350, 555, 100, 30)
        # self.btn_z3_usun.setStyleSheet("background-color: #444; color: white;")
        # self.btn_z3_usun.clicked.connect(self.oproznij_z3)

        self.running = False
        self.flow_speed = 0.8

        # sloty do wypelbiania

    def napelnij_z1(self):
        self.z1.aktualna_ilosc = 100.0
        self.z1.aktualizuj_poziom()
        self.update()

    def oproznij_z1(self):
        self.z1.aktualna_ilosc = 0.0
        self.z1.aktualizuj_poziom()
        self.update()

    def napelnij_z2(self):
        self.z2.aktualna_ilosc = 100.0
        self.z2.aktualizuj_poziom()
        self.update()

    def oproznij_z2(self):
        self.z2.aktualna_ilosc = 0.0
        self.z2.aktualizuj_poziom()
        self.update()

    def napelnij_z3(self):
        self.z3.aktualna_ilosc = 100.0
        self.z3.aktualizuj_poziom()
        self.update()

    def oproznij_z3(self):
        self.z3.aktualna_ilosc = 0.0
        self.z3.aktualizuj_poziom()
        self.update()


    def przelacz_symulacje(self):
        if self.running:
            self.timer.stop()
        else:
            self.timer.start(20)
        self.running = not self.running

    def logika_przeplywu(self):
        plynie_1 = False
        if not self.z1.czy_pusty() and not self.z2.czy_pelny():
            ilosc = self.z1.usun_ciecz(self.flow_speed)
            self.z2.dodaj_ciecz(ilosc)
            plynie_1 = True
        self.rura1.ustaw_przeplyw(plynie_1)

        plynie_2 = False
        if self.z2.aktualna_ilosc > 5.0 and not self.z3.czy_pelny():
            ilosc = self.z2.usun_ciecz(self.flow_speed)
            self.z3.dodaj_ciecz(ilosc)
            plynie_2 = True
            self.rura2.ustaw_przeplyw(plynie_2)

            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        for r in self.rury: r.draw(p)
        for z in self.zbiorniki: z.draw(p)
        self.pompa.draw(p)
        self.zawor.draw(p)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = SymulacjaKaskady()
    okno.show()
    sys.exit(app.exec_())