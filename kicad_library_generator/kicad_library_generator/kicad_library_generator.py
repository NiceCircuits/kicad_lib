'''
Created on 11-05-2014

@author: Piotr Nowicki
'''
import exceptions
from enaml.enums import Orientation

class kicad_library_generator(object):
    libFile=None
    
    def __init__(self,filePath):
        self.libFile = open(filePath, "w")
        
    def library_generator(self, classes):         
        self.libraryHeader()
        for c in classes:
            instance = c(self.libFile)
            instance.library()
        self.libraryFooter()
        self.libFile.close()
    
    def libraryHeader(self):
        self.libFile.write("EESchema-LIBRARY Version 2.3\n#encoding utf-8\n")
        
    def libraryFooter(self):
        self.libFile.write("#\n#End Library\n")
    
class symbol():
    libFile=None
    
    def __init__(self, libFile):
        self.libFile = libFile
    
    def startDraw(self):
        self.libFile.write("DRAW\n")
        
    def endDraw(self):
        self.libFile.write("ENDDRAW\n")
        
    def symbolHeader(self, name, reference, refPos=[0,0], namePos=[0,0], footprint="", footprintPos=[0,0]):
        header = r"""#
# %s
#
DEF %s %s 0 1 Y N 1 F N\n
F0 "%s" %d %d 60 H V C CNN
F1 "%s" %d %d 60 H V C CNN
F2 "%s" %d %d 40 H V C CNN
F3 "" 0 0 40 H V C CNN
""" % (name, name, reference, reference, refPos[1], refPos[0], name, namePos[1], namePos[0], \
       footprint, footprintPos[1], footprintPos[0])
        self.libFile.write(header)
    
    def symbolFooter(self):
        self.libFile.write("ENDDEF\n")
    
    def drawRect(self, x1, y1, x2, y2, width=0, fill=0):
        # fill = 0 - none, 1 - foreground, 2 - background
        if fill == 1:
            fill = "f"
        elif fill == 2:
            fill = "F"
        else:
            fill = "N"
        self.libFile.write("S %d %d %d %d 0 1 %d %s\n" % (x1, y1, x2, y2, width, fill))
        
    def drawPin(self, name, number, x, y, orientation, length=100, electricalType="P"):
        # orientation = R/L/U/D
        # electricalType = (P)assive, (I)nput, (O)utput, (B)idir, (T)ristate, po(W)er input, po(w)er output, open (C)ollector, open (E)mitter, (N)ot connected 
        if type(name) is int:
            name = str(name)
        if type(number) is int:
            number = str(number)
        self.libFile.write("X %s %s %d %d %d %s 50 50 1 1 %s\n" % (name, number, x, y, length, orientation, electricalType))

class conSymbol(symbol):
    def symbol(self, rows, cols):
        if cols == 1:
            name = "CON%d" % (rows)
        elif cols == 2:
            name = "CON%dx%d" % (rows, cols)
        else:
            raise Exception("Number of columns (%d) to high!" % cols)
        # header
        h = rows * 50
        self.symbolHeader(name, "CON", refPos=[h+70,0], namePos=[-h-50,0])
        # body
        self.startDraw()
        self.drawRect(-100, -h, 100, h, 0, 1)
        # pins
        for c in range(cols):
            if c==0:
                x = -200
                orientation = "R"
            else:
                x = 200
                orientation = "L"
            for r in range(rows):
                self.drawPin(r*cols+c+1, r*cols+c+1, x, 50*(rows-1)-100*r, orientation, 100, "P")
        self.endDraw()
        self.symbolFooter()

    
    def library(self, rows=range(1,41), cols=[1,2]):
        for c in cols:
            for r in rows:
                self.symbol(r, c)

        
if __name__ == "__main__":
    gen = kicad_library_generator("test.lib")
    gen.library_generator([conSymbol])
