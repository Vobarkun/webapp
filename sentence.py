import numpy as np
import random
from enum import Enum, IntEnum

class probabilities:
    ADJEKTIV = 0.3
    ZAHL = 0.4
    ADVERB = 0.2
    RELATIVSATZ = 0.5
    NAME_ALS_SUBJEKT = 0.6
    PERSONALPRONOMEN_IN_DRITTER_PERSON = 0 #0.1
    GENITIV_AN_SUBSTANTIV = 0.1
    PRÄPOSITION_AN_SUBSTANTIV = 0.1
    NAME_ALS_AKKUSATIVOBJEKT = 0.3 # 0.1
    PRÄPOSITIONALOBJEKT = 0.2
    KONJUNKTION = 0.4

def weightedChoice(arr, weights):
    return np.random.choice(arr, 1, p=weights)[0]

class casus(IntEnum):
    NOMINATIV = 0
    GENITIV = 1
    DATIV = 2
    AKKUSATIV = 3
class numerus(IntEnum):
    SINGULAR = 0
    PLURAL = 1
class genus(IntEnum):
    MASKULIN = 0
    FEMININ = 1
    NEUTRUM = 2
class tempus(IntEnum):
    PLUSQUAMPERFEKT = 0
    PRÄTERITUM = 1
    PERFEKT = 2
    PRÄSENS = 3
    FUTUR2 = 4
    FUTUR1 = 5
class person(IntEnum):
    ERSTE = 0
    ZWEITE = 1
    DRITTE = 2
class determination(IntEnum):
    DEFINIT = 0
    INDEFINIT = 1
class satz(IntEnum):
    HAUPTSATZ = 0
    NEBENSATZ = 1

casusList = list(casus)
numerusList = list(numerus)
genusList = list(genus)
tempusList = list(tempus)
personList = list(person)
determinationList = list(determination)
satzList = list(satz)

class Node:
    def __init__(self):
        self.leftChilds = []
        self.rightChilds = []

    def populate(self):
        pass

class Artikel(Node):
    values = {
        determination.DEFINIT: {
            genus.MASKULIN: [["der", "des", "dem", "den"], ["die", "der", "den", "die"]],
            genus.FEMININ:  [["die", "der", "der", "die"], ["die", "der", "den", "die"]],
            genus.NEUTRUM:  [["das", "des", "dem", "das"], ["die", "der", "den", "die"]]
        },
        determination.INDEFINIT: {
            genus.MASKULIN: [["ein",  "eines", "einem", "einen"], ["", "", "", ""]],
            genus.FEMININ:  [["eine", "einer", "einer", "eine"],  ["", "", "", ""]],
            genus.NEUTRUM:  [["ein",  "eines", "einem", "ein"],   ["", "", "", ""]],
        }
    }

    def __init__(self, determination, casus, numerus, genus, parent = None):
        super().__init__()
        self.genus = genus
        self.determination = determination
        self.numerus = numerus
        self.casus = casus
        self.parent = parent

    def evaluate(self):
        return Artikel.values[self.determination][self.genus][self.numerus][self.casus]

class Wort(Node):
    def __init__(self, value, parent = None):
        super().__init__()
        self.value = value
        self.parent = parent

    def evaluate(self):
        return self.value

class Name(Node):
    # values = ["Sven", "Robert", "Harald", "Wolfgang", "Anneliese", "Darth Vader", "Gandalf", "Harry Potter", "Frodo", "Karl", "Tim", "Frank", "Nathalie", "Bob", "Donald", "Tom", "Herbert", "Kevin"]
    values = ["Robert", "Tim", "Charlotte", "Jonas", "Steffen", "Renate"]

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

    def evaluate(self):
        return random.choice(Name.values)

class Adverb(Node):
    values = ["langsam", "schnell", "einmal", "zweimal"]

    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

    def evaluate(self):
        return random.choice(Adverb.values)

class Zahlwort(Node):
    values = ["zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf", "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn", "zwanzig"]

    def __init__(self, casus = None, parent = None):
        super().__init__()
        self.casus = casus
        self.parent = parent

    def evaluate(self):
        return random.choice(Zahlwort.values)

class Personalpronomen(Node):
    values = [[["ich"], ["du"], ["er", "sie", "es"]],
              [["wir"], ["ihr"], ["sie"]]]

    def __init__(self, person, numerus, parent = None):
        super().__init__()
        self.person = person
        self.numerus = numerus
        self.parent = parent

    def evaluate(self):
        return random.choice(Personalpronomen.values[self.numerus][self.person])

class Adjektiv(Node):
    endung = {
        determination.DEFINIT: {
            genus.MASKULIN: [["e", "en", "en", "en"], ["en", "en", "en", "en"]],
            genus.FEMININ: [["e", "en", "en", "e"], ["en", "en", "en", "en"]],
            genus.NEUTRUM: [["e", "en", "en", "e"], ["en", "en", "en", "en"]]
        },
        determination.INDEFINIT: {
            genus.MASKULIN: [["er", "en", "en", "en"], ["e", "er", "en", "e"]],
            genus.FEMININ: [["e", "en", "en", "e"], ["e", "er", "en", "e"]],
            genus.NEUTRUM: [["es", "en", "en", "es"], ["e", "er", "en", "e"]]
        }
    }
    values = ["albern", "alt", "arg", "arm", "bange", "bieder", "bitter", "blank", "blass", "blau", "bleich", "blind", "blöd", "blöde", "blond", "bloß", "böse", "braun", "brav", "breit", "brüsk", "bunt", "derbe", "deutsch", "dicht", "dick", "doof", "dreist", "dumm", "dumpf", "dunkl", "dünn", "dürr", "düster", "eben", "echt", "edl", "eigen", "eitl", "elend", "eng", "ernst", "fad", "fahl", "falsch", "faul", "feige", "fein", "feist", "fern", "fesch", "fest", "fett", "feucht", "fies", "finster", "firn", "flach", "flau", "flink", "flott", "forsch", "frech", "frei", "fremd", "froh", "fromm", "früh", "gar", "geil", "gelb", "gemein", "genau", "gerade", "gering", "gesund", "glatt", "gleich", "grau", "greis", "greise", "grell", "grimm", "grob", "groß", "grün", "gut", "hager", "harsch", "hart", "hehr", "heikl", "heil", "heiser", "heiß", "heiter", "hell", "helle", "herb", "hohl", "hold", "hübsch", "irre", "jung", "kahl", "kalt", "kaputt", "karg", "keck", "kess", "keusch", "klamm", "klar", "klein", "klug", "knapp", "krank", "krass", "kraus", "krude", "krumm", "kühl", "kühn", "kurz", "lahm", "lang", "lasch", "lau", "laut", "lauter", "lecker", "leer", "leicht", "leise", "lieb", "locker", "lose", "mager", "matt", "mau", "mies", "mild", "morsch", "müde", "munter", "mürb", "mürbe", "nackt", "nah", "nahe", "nass", "nett", "neu", "nieder", "öde", "offen", "orange", "plan", "platt", "plump", "prall", "prüde", "rank", "rar", "rasch", "rau", "recht", "rege", "reich", "reif", "rein", "roh", "rot", "rüde", "rund", "sachte", "sanft", "satt", "sauber", "sauer", "schal", "scharf", "scheu", "schick", "schief", "schier", "schlaff", "schlank", "schlapp", "schlau", "schlecht", "schlicht", "schlimm", "schmal", "schmuck", "schnell", "schnöde", "schön", "schräg", "schrill", "schroff", "schütter", "schwach", "schwarz", "schwer", "schwul", "schwül", "seicht", "selten", "sicher", "spät", "spitz", "spröde", "stark", "starr", "steif", "steil", "still", "stolz", "straff", "stramm", "streng", "stumm", "stumpf", "stur", "süß", "tapfer", "taub", "teuer", "tief", "toll", "tot", "träge", "traut", "treu", "trocken", "trüb", "unscharf", "vage", "voll", "wach", "wacker", "wahr", "warm", "weh", "weich", "weise", "weiß", "weit", "welk", "wert", "wild", "wirr", "wund", "wüst", "zäh", "zahm", "zart"]

    def __init__(self, determination, casus, numerus, genus, parent = None):
        super().__init__()
        self.determination = determination
        self.genus = genus
        self.numerus = numerus
        self.casus = casus
        self.parent = parent

    def populate(self):
        for child in self.rightChilds:
            child.populate()
        for child in self.leftChilds:
            child.populate()

    def evaluate(self):
        result = ""
        for child in self.leftChilds:
            result += child.evaluate() + " "

        stamm = random.choice(Adjektiv.values)
        endung = Adjektiv.endung[self.determination][self.genus][self.numerus][self.casus]
        if stamm[-1] == "e":
            endung = endung[1:]
        result += stamm + endung

        for child in self.rightChilds:
            result += " " + child.evaluate()

        return result

class Relativpronomen(Node):
    values = {
        genus.MASKULIN: [["der", "dessen", "dem", "den"], ["die", "deren", "denen", "die"]],
        genus.FEMININ:  [["die", "deren", "der", "die"], ["die", "deren", "denen", "die"]],
        genus.NEUTRUM:  [["das", "dessen", "dem", "das"], ["die", "deren", "denen", "die"]]
    }

    def __init__(self, numerus, genus, casus = None, depth = 0, parent = None):
        super().__init__()
        self.numerus = numerus
        self.genus = genus
        self.depth = depth
        self.parent = parent
        self.casus = casus

    def populate(self):
        self.rightChilds.append(Prädikat(person = person.DRITTE, numerus = self.numerus, parent = self, depth = self.depth))
        if self.casus is None:
            self.casus = random.choice(Prädikat.values[self.rightChilds[0].index][1] + [casus.NOMINATIV])
        for child in self.rightChilds:
            child.populate()
        for child in self.leftChilds:
            child.populate()

    def evaluate(self):
        result = ""
        for child in self.leftChilds:
            result += child.evaluate() + " "

        result += ", " + Relativpronomen.values[self.genus][self.numerus][self.casus]

        for child in self.rightChilds:
            result += " " + child.evaluate()

        result += ","

        return result


class Konjunktion(Node):
    values = {
        satz.HAUPTSATZ: ["und", ", aber", ", denn"],
        satz.NEBENSATZ: [", weil", ", nachdem", ", während", ", bevor", ", obwohl", ", da", ", damit"]
    }
    tempusShift = {
        satz.HAUPTSATZ: [None, None, None],
        satz.NEBENSATZ: [0, -1, 0, 0, None, 0, 1]
    }

    def __init__(self, satztyp = None, tempus = None, depth = 0, parent = None):
        if satztyp is None:
            satztyp = weightedChoice(satzList, [0.3, 0.7])
        if tempus is None:
            tempus = random.choice(tempusList)
        super().__init__()
        self.satztyp = satztyp
        self.depth = depth
        self.tempus = tempus
        self.index = random.randrange(len(Konjunktion.values[satztyp]))
        self.parent = parent

    def populate(self):
        shift = Konjunktion.tempusShift[self.satztyp][self.index]
        if shift is None:
            self.rightChilds.append(Prädikat(depth = self.depth, parent = self))
        elif shift == 0:
            self.rightChilds.append(Prädikat(tempus = self.tempus, depth = self.depth, parent = self))
        elif shift == 1:
            if self.tempus in [tempus.PLUSQUAMPERFEKT, tempus.PERFEKT, tempus.FUTUR2]:
                self.rightChilds.append(Prädikat(tempus = self.tempus + 1, depth = self.depth, parent = self))
            else:
                self.rightChilds.append(Prädikat(tempus = self.tempus, depth = self.depth, parent = self))
        elif shift == -1:
            if self.tempus in [tempus.PRÄTERITUM, tempus.PRÄSENS, tempus.FUTUR1]:
                self.rightChilds.append(Prädikat(tempus = self.tempus - 1, depth = self.depth, parent = self))
            else:
                self.rightChilds.append(Prädikat(tempus = self.tempus, depth = self.depth, parent = self))

        for child in self.rightChilds:
            child.populate()
        for child in self.leftChilds:
            child.populate()

    def evaluate(self):
        result = ""
        for child in self.leftChilds:
            result += child.evaluate() + " "

        result += Konjunktion.values[self.satztyp][self.index]

        for child in self.rightChilds:
            result += " " + child.evaluate()

        return result

class Präposition(Node):
    values = {
        casus.GENITIV: ["innerhalb", "diesseits", "außerhalb"],
        casus.DATIV: ["aus", "bei", "mit", "nach", "nahe", "an", "auf", "hinter", "in", "neben", "über", "unter", "vor"],
        casus.AKKUSATIV: ["ohne"]
    }

    def __init__(self, casus = None, depth = 0, parent = None):
        if casus is None:
            casus = weightedChoice(casusList[1:], [0, 15/16, 1/16])
        super().__init__()
        self.casus = casus
        self.depth = depth
        self.parent = parent

    def populate(self):
        self.rightChilds.append(Substantiv(self.casus, depth = self.depth, parent = self))

        for child in self.rightChilds:
            child.populate()
        for child in self.leftChilds:
            child.populate()

    def evaluate(self):
        result = ""
        for child in self.leftChilds:
            result += child.evaluate() + " "

        result += random.choice(Präposition.values[self.casus])

        for child in self.rightChilds:
            result += " " + child.evaluate()

        return result

class Substantiv(Node):
    values = {
        genus.MASKULIN: [
            [["Fisch", "Fischs", "Fisch", "Fisch"], ["Fische", "Fische", "Fischen", "Fische"]],
            [["Apfel", "Apfels", "Apfel", "Apfel"], ["Äpfel", "Äpfel", "Äpfeln", "Äpfel"]],
            [["Imperator", "Imperators", "Imperator", "Imperator"], ["Imperatoren", "Imperatoren", "Imperatoren", "Imperatoren"]],
            [["Mensch", "Menschen", "Menschen", "Menschen"], ["Menschen", "Menschen", "Menschen", "Menschen"]],
            [["Koch", "Kochs", "Koch", "Koch"], ["Köche", "Köche", "Köchen", "Köche"]],
            [["Teufel", "Teufels", "Teufel", "Teufel"], ["Teufel", "Teufel", "Teufeln", "Teufel"]],
            [["Autor", "Autors", "Autor", "Autor"], ["Autoren", "Autoren", "Autoren", "Autoren"]],
            [["Hobbit", "Hobbits", "Hobbit", "Hobbit"], ["Hobbits", "Hobbits", "Hobbits", "Hobbits"]],
            [["Ausländer", "Ausländers", "Ausländer", "Ausländer"], ["Ausländer", "Ausländer", "Ausländern", "Ausländer"]],
            [["Nachbar", "Nachbars", "Nachbarn", "Nachbarn"], ["Nachbarn", "Nachbarn", "Nachbarn", "Nachbarn"]],
            [["Student", "Studenten", "Studenten", "Studenten"], ["Studenten", "Studenten", "Studenten", "Studenten"]],
            [["Vater", "Vaters", "Vater", "Vater"], ["Väter", "Väter", "Vätern", "Väter"]],
            [["Satanist", "Satanisten", "Satanisten", "Satanisten"], ["Satanisten", "Satanisten", "Satanisten", "Satanisten"]],
            [["Doktor", "Doktors", "Doktor", "Doktor"], ["Doktoren", "Doktoren", "Dokteren", "Doktoren"]],
            [["Roboter", "Roboters", "Roboter", "Roboter"], ["Roboter", "Roboter", "Robotern", "Roboter"]],
            [["Professor", "Professors", "Professor", "Professor"], ["Professoren", "Professoren", "Professoren", "Professoren"]],
            [["Zwerg", "Zwergs", "Zwerg", "Zwerg"], ["Zwerge", "Zwerge", "Zwergen", "Zwerge"]],
            [["Orc", "Orcs", "Orc", "Orc"], ["Orcs", "Orcs", "Orcs", "Orcs"]],
            [["Zauberer", "Zauberers", "Zauberer", "Zauberer"], ["Zauberer", "Zauberer", "Zauberern", "Zauberer"]],
            [["Spielplatz", "Spielplatzes", "Spielplatz", "Spielplatz"], ["Spielplätze", "Spielplätze", "Spielplätzen", "Spielplätze"]]
        ],
        genus.FEMININ: [
            [["Schule", "Schule", "Schule", "Schule"], ["Schulen", "Schulen", "Schulen", "Schulen"]],
            [["Giraffe", "Giraffe", "Giraffe", "Giraffe"], ["Giraffen", "Giraffen", "Giraffen", "Giraffen"]],
            [["Schildkröte", "Schildkröte", "Schildkröte", "Schildkröte"], ["Schildkröten", "Schildkröten", "Schildkröten", "Schildkröten"]],
            [["Maus", "Maus", "Maus", "Maus"], ["Mäuse", "Mäuse", "Mäusen", "Mäuse"]],
            [["Kuh", "Kuh", "Kuh", "Kuh"], ["Kühe", "Kühe", "Kühen", "Kühe"]],
            [["Bundeskanzlerin", "Bundeskanzlerin", "Bundeskanzlerin", "Bundeskanzlerin"], ["Bundeskanzlerinnen", "Bundeskanzlerinnen", "Bundeskanzlerinnen", "Bundeskanzlerinnen"]],
            [["Banane", "Banane", "Banane", "Banane"], ["Bananen", "Bananen", "Bananen", "Bananen"]],
            [["Bohne", "Bohne", "Bohne", "Bohne"], ["Bohnen", "Bohnen", "Bohnen", "Bohnen"]],
            [["Feuerwehr", "Feuerwehr", "Feuerwehr", "Feuerwehr"], ["Feuerwehren", "Feuerwehren", "Feuerwehren", "Feuerwehren"]],
            [["Studentin", "Studentin", "Studentin", "Studentin"], ["Studentinnen", "Studentinnen", "Studentinnen", "Studentinnen"]],
            [["Großmutter", "Großmutter", "Großmutter", "Großmutter"], ["Großmütter", "Großmütter", "Großmüttern", "Großmütter"]],
            [["Krankenkasse", "Krankenkasse", "Krankenkasse", "Krankenkasse"], ["Krankenkassen", "Krankenkassen", "Krankenkassen", "Krankenkassen"]],
            [["Hexe", "Hexe", "Hexe", "Hexe"], ["Hexen", "Hexen", "Hexen", "Hexen"]]
        ],
        genus.NEUTRUM: [
            [["Känguru", "Kängurus", "Känguru", "Känguru"], ["Kängurus", "Kängurus", "Kängurus", "Kängurus"]],
            [["Auto", "Autos", "Auto", "Auto"], ["Autos", "Autos", "Autos", "Autos"]],
            [["Amt", "Amts", "Amt", "Amt"], ["Ämter", "Ämter", "Ämtern", "Ämter"]],
            [["Kamel", "Kamels", "Kamel", "Kamel"], ["Kamele", "Kamele", "Kamelen", "Kamele"]],
            [["Brot", "Brotes", "Brot", "Brot"], ["Brote", "Brote", "Broten", "Brote"]],
            [["Kind", "Kindes", "Kind", "Kind"], ["Kinder", "Kinder", "Kindern", "Kinder"]],
            [["Seeungeheuer", "Seeungeheuers", "Seeungeheuer", "Seeungeheuer"], ["Seeungeheuer", "Seeungeheuer", "Seeungeheuern", "Seeungeheuer"]],
            [["Baby", "Babys", "Baby", "Baby"], ["Babys", "Babys", "Babys", "Babys"]]
        ]
    }

    def __init__(self, casus = None, numerus = None, genus = None, depth = 0, parent = None):
        if casus is None:
            casus = random.choice(casusList)
        if numerus is None:
            numerus = random.choice(numerusList)
        if genus is None:
            genus = weightedChoice(genusList, [0.4, 0.4, 0.2])
        super().__init__()
        self.genus = genus
        self.numerus = numerus
        self.casus = casus
        self.depth = depth
        self.parent = parent

    def populate(self):
        det = random.choice(determinationList)
        if self.numerus == numerus.PLURAL and self.casus == casus.GENITIV:
            det = determination.DEFINIT
        self.leftChilds.append(Artikel(det, self.casus, self.numerus, self.genus, parent = self))
        if random.random() < probabilities.ZAHL and self.numerus == numerus.PLURAL:
            self.leftChilds.append(Zahlwort(self.casus, parent = self))
        if random.random() < probabilities.ADJEKTIV:
            self.leftChilds.append(Adjektiv(det, self.casus, self.numerus, self.genus, parent = self))

        if self.depth < 1:
            if random.random() < probabilities.RELATIVSATZ:
                self.rightChilds.append(Relativpronomen(numerus = self.numerus, genus = self.genus, depth = self.depth + 1, parent = self))
            elif random.random() < probabilities.PRÄPOSITION_AN_SUBSTANTIV:
                self.rightChilds.append(Präposition(depth = self.depth + 1, parent = self))
            elif random.random() < probabilities.GENITIV_AN_SUBSTANTIV:
                self.rightChilds.append(Substantiv(casus.GENITIV, depth = self.depth + 1, parent = self))

        for child in self.rightChilds:
            child.populate()
        for child in self.leftChilds:
            child.populate()

    def evaluate(self):
        result = ""
        for child in self.leftChilds:
            result += child.evaluate() + " " if child.evaluate() != "" else ""

        result += random.choice(Substantiv.values[self.genus])[self.numerus][self.casus]

        for child in self.rightChilds:
            result += " " + child.evaluate()

        return result

class Prädikat(Node):
    endung = {
        tempus.PRÄSENS:    [["e", "st", "t"], ["en", "t", "en"]],
        tempus.PRÄTERITUM: [["", "st", ""], ["n", "t", "n"]]
    }

    values = [
        # [[[Präsens, 2./3. Singular Indikativ], Präteritum, Partizip], [Ojekte], Präfix, Perfekt mit haben]
        [[["lach", "lach"], "lachte", "gelacht"], [], "", True],
        [[["schreib", "schreib"], "schrieb", "geschrieben"], [casus.DATIV], "", True],
        [[["brüll", "brüll"], "brüllte", "gebrüllt"], [], "", True],
        [[["brems", "brems"], "bremste", "gebremst"], [casus.AKKUSATIV], "", True],
        [[["dicht", "dicht"], "dichtete", "gedichtet"], [casus.AKKUSATIV], "", True],
        [[["färb", "färb"], "färbte", "gefärbt"], [casus.AKKUSATIV], "", True],
        [[["mal", "mal"], "malte", "gemalt"], [casus.AKKUSATIV], "", True],
        [[["töt", "töt"], "tötete", "getötet"], [casus.AKKUSATIV], "", True],
        [[["spuk", "spuk"], "spukte", "gespukt"], [], "", True],
        [[["dank", "dank"], "dankte", "gedankt"], [casus.DATIV], "", True],
        [[["manipulier", "manipulier"], "manipulierte", "manipuliert"], [casus.AKKUSATIV], "", True],
        [[["bad", "bad"], "badete", "gebadet"], [], "", True],
        [[["bau", "bau"], "baute", "gebaut"], [casus.AKKUSATIV], "", True],
        [[["beweg", "beweg"], "bewegte", "bewegt"], [casus.AKKUSATIV], "", True],
        [[["beantrag", "beantrag"], "beantragte", "beantragt"], [casus.AKKUSATIV], "", True],
        [[["lüg", "lüg"], "log", "gelogen"], [], "", True],
        [[["stehl", "stiehl"], "stahl", "gestohlen"], [casus.AKKUSATIV], "", True],
        [[["bet", "bet"], "betete", "angebetet"], [casus.AKKUSATIV], "an", True],
        [[["brech", "brich"], "brach", "abgebrochen"], [casus.DATIV, casus.AKKUSATIV], "ab", True],
        [[["wisch", "wisch"], "wusch", "abgewaschen"], [casus.AKKUSATIV], "ab", True],
        [[["geh", "geh"], "ging", "abgegangen"], [], "ab", False],
        [[["sing", "sing"], "sang", "vorgesungen"], [casus.DATIV], "vor", True],
        [[["brech", "brich"], "brach", "eingebrochen"], [], "ein", False],
        [[["schlag", "schläg"], "schlug", "totgeschlagen"], [casus.AKKUSATIV], "tot", True],
        [[["vergess", "vergiss"], "vergaß", "vergessen"], [casus.AKKUSATIV], "", True],
        [[["helf", "hilf"], "half", "geholfen"], [casus.DATIV], "", True],
        [[["fahr", "fähr"], "fuhr", "gefahren"], [casus.AKKUSATIV], "", False]
    ]

    def __init__(self, person = None, numerus = None, tempus = None, depth = 0, parent = None, satztyp = None):
        if person is None:
            person = random.choice(personList)
        if numerus is None:
            numerus = random.choice(numerusList)
        if tempus is None:
            tempus = random.choice(tempusList)
        super().__init__()
        self.person = person
        self.numerus = numerus
        self.tempus = tempus
        self.index = random.randrange(len(Prädikat.values))
        self.depth = depth
        self.parent = parent
        self.satztyp = satztyp
        if self.satztyp == None:
            self.satztyp = satz.HAUPTSATZ
            if type(self.parent) == Konjunktion:
                if self.parent.satztyp == satz.NEBENSATZ:
                    self.satztyp = satz.NEBENSATZ
            if type(self.parent) == Relativpronomen:
                self.satztyp = satz.NEBENSATZ

    def populate(self):
        value = Prädikat.values[self.index]

        #Subjekt
        parentCasus = None
        if type(self.parent) == Relativpronomen:
            parentCasus = self.parent.casus
        if parentCasus != casus.NOMINATIV:
            if self.person == person.ERSTE or self.person == person.ZWEITE:
                self.leftChilds.append(Personalpronomen(self.person, self.numerus, parent = self))
            if self.person == person.DRITTE:
                if random.random() < probabilities.PERSONALPRONOMEN_IN_DRITTER_PERSON and parentCasus is None:
                    self.leftChilds.append(Personalpronomen(self.person, self.numerus, parent = self))
                elif random.random() < probabilities.NAME_ALS_SUBJEKT and self.numerus == numerus.SINGULAR:
                    self.leftChilds.append(Name(parent = self))
                else:
                    self.leftChilds.append(Substantiv(casus.NOMINATIV, numerus = self.numerus, parent = self, depth = self.depth))

        #Objekte
        if parentCasus is not None:
            if random.random() < probabilities.ADVERB:
                self.rightChilds.append(Adverb(parent = self))
        if casus.DATIV in value[1] and parentCasus != casus.DATIV:
                self.rightChilds.append(Substantiv(casus.DATIV, parent = self, depth = self.depth))
        if parentCasus is None:
            if random.random() < probabilities.ADVERB:
                self.rightChilds.append(Adverb(parent = self))
        if casus.GENITIV in value[1] and parentCasus != casus.GENITIV:
                self.rightChilds.append(Substantiv(casus.GENITIV, parent = self, depth = self.depth))
        if casus.AKKUSATIV in value[1] and parentCasus != casus.AKKUSATIV:
            if random.random() < probabilities.NAME_ALS_AKKUSATIVOBJEKT:
                self.rightChilds.append(Name(parent = self))
            else:
                self.rightChilds.append(Substantiv(casus.AKKUSATIV, parent = self, depth = self.depth))

        if random.random() < probabilities.PRÄPOSITIONALOBJEKT:
            self.rightChilds.append(Präposition(depth = 1, parent = self))

        if self.tempus == tempus.PERFEKT or self.tempus == tempus.PLUSQUAMPERFEKT:
            self.rightChilds.append(Wort(value[0][2], parent = self))
        elif self.tempus == tempus.FUTUR1:
            self.rightChilds.append(Wort(value[2] + value[0][0][0] + "en", parent = self))
        elif self.tempus == tempus.FUTUR2:
            self.rightChilds.append(Wort(value[0][2], parent = self))
            self.rightChilds.append(Wort("haben" if value[3] else "sein", parent = self))
        elif value[2] != "" and self.satztyp == satz.HAUPTSATZ:
            self.rightChilds.append(Wort(value[2], parent = self))

        if self.satztyp == satz.NEBENSATZ:
                self.leftChilds.extend(self.rightChilds)
                self.rightChilds = []

        if random.random() < probabilities.KONJUNKTION and self.depth < 1 and self.satztyp == satz.HAUPTSATZ:
            self.rightChilds.append(Konjunktion(depth = self.depth + 1, tempus = self.tempus, parent = self))

        for child in self.rightChilds:
            child.populate()
        for child in self.leftChilds:
            child.populate()

    def evaluate(self):
        result = ""
        for child in self.leftChilds:
            result += child.evaluate() + " "

        value = Prädikat.values[self.index]

        if self.tempus == tempus.PERFEKT:
            if value[3]:
                result += [["habe", "hast", "hat"], ["haben", "habt", "haben"]][self.numerus][self.person]
            else:
                result += [["bin", "bist", "ist"], ["sind", "seid", "sind"]][self.numerus][self.person]
        elif self.tempus == tempus.PLUSQUAMPERFEKT:
            if value[3]:
                result += [["hatte", "hattest", "hatte"], ["hatten", "hattet", "hatten"]][self.numerus][self.person]
            else:
                result +=  [["war", "warst", "war"], ["waren", "wart", "waren"]][self.numerus][self.person]
        elif self.tempus == tempus.FUTUR1 or self.tempus == tempus.FUTUR2:
            result += [["werde", "wirst", "wird"], ["werden", "werdet", "werden"]][self.numerus][self.person]
        else:
            stamm = value[0][1]
            if self.tempus == tempus.PRÄSENS:
                stamm = value[0][0][0]
                if (self.person == person.ZWEITE or self.person == person.DRITTE) and self.numerus == numerus.SINGULAR:
                    stamm = value[0][0][1]
            endung = Prädikat.endung[self.tempus][self.numerus][self.person]
            if self.tempus == tempus.PRÄSENS:
                if stamm[-1] == "d" or stamm[-1] == "t":
                    if endung[0] == "s":
                        stamm += "e"
                if stamm[-1] == "d" or stamm[-1] == "t":
                    if endung[0] == "t" or endung[0] == "n":
                        stamm += "e"
            if self.tempus == tempus.PRÄTERITUM and stamm[-1] != "e" and self.numerus == numerus.PLURAL and self.person != person.ZWEITE:
                stamm += "e"
            if (stamm[-1] == "s" or stamm[-1] == "ß") and self.person == person.ZWEITE:
                endung  = endung[1:]
            if self.satztyp == satz.NEBENSATZ:
                stamm = value[2] + stamm
            result += stamm + endung

        for child in self.rightChilds:
            result += " " + child.evaluate()

        return result

def sentence():
    prädikat = Prädikat(person =  weightedChoice(personList, [0.05, 0.05, 0.9]), numerus = weightedChoice(numerusList, [0.7, 0.3]), tempus = weightedChoice(tempusList, [0.05, 0.3, 0.2, 0.3, 0.05, 0.1]))
    #prädikat = Prädikat(person = person.DRITTE, numerus = numerus.SINGULAR)
    prädikat.populate()

    sentence = prädikat.evaluate()
    sentence += "."
    sentence = sentence[0].capitalize() + sentence[1:]
    sentence = sentence.replace(" ,", ",").replace("  ", " ").replace(",,", ",").replace(",.", ".")

    return sentence
