'''
Created on 11-06-2014

@author: Piotr Nowicki
'''
import os

class footprint_generator(object):
    libPath=None
    
    def __init__(self,_libPath):
        self.libPath = _libPath
        if not os.path.exists(_libPath):
            os.makedirs(_libPath)
                    
    def library_generator(self, classes):         
        for c in classes:
            instance = c(self.libPath)
            instance.library()
        
class footprint():
    libPath=""
    libFile=None
    
    def __init__(self, _libPath):
        self.libPath = _libPath
    
    def footprintHeader(self, name, reference, refPos=[0,0], namePos=[0,0]):
        header = r"""(module %s (layer F.Cu)
  (fp_text reference %s (at %f %f) (layer F.SilkS)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_text value %s (at %f %f) (layer F.SilkS)
    (effects (font (size 1 1) (thickness 0.15)))
  )
""" % (name, reference, refPos[0], refPos[1], name, namePos[0], namePos[1])
        self.libFile = open(self.libPath + "\\" + name + ".kicad_mod", "w")
        self.libFile.write(header)
    
    def footprintFooter(self):
        self.libFile.write(")\n")

    def drawLine(self, start, end, layer = "F.SilkS", width=0.15):
        self.libFile.write("(fp_line (start %f %f) (end %f %f) (layer %s) (width %f))\n" %
            (start[0], start[1], end[0], end[1], layer, width))
    
    def drawRect(self, start, end, layer = "F.SilkS", width=0.15):
        self.drawLine(start, [start[0], end[1]], layer, width)
        self.drawLine([start[0], end[1]], end, layer, width)
        self.drawLine(end, [end[0], start[1]], layer, width)
        self.drawLine([end[0], start[1]], start, layer, width)
    
    def drawPolygon(self, points, layer = "F.SilkS", width=0.15):
        for i in range(len(points)-1):
            self.drawLine(points[i], points[i+1], layer, width)
        self.drawLine(points[0], points[-1], layer, width)
        
    def drawPad(self, name, position, size, orientation = 0, shape = "rect", padType = "smd", drill = 0, layers ="F.Cu F.Paste F.Mask"):
        # type = "smd"/"thru_hole"
        # shape = "round"/"circle"
        if type(name) is int:
            name = str(name)
        if orientation == 0:
            orientationString = ""
        else:
            orientationString = " %f" % orientation
        if padType == "smd":
            drillString = ""
        else:
            drillString = " (drill %f)" % drill
        self.libFile.write("  (pad %s %s %s (at %f %f%s) (size %f %f)%s (layers %s))\n" % 
            (name, padType, shape, position[0], position[1], orientationString, size[0], size[1], drillString, layers))

class pinFootprint(footprint):
    kinds = [{"name":"standard", "postfix":"","pinSize":[2,2]},
        {"name":"narrowPads", "postfix":"_a","pinSize":[1.5,2]}]
    def footprint(self, rows, cols, kind=None):
        if not kind:
            kind = self.kinds[0]
        if cols == 1:
            name = "PIN%d%s" % (rows, kind["postfix"])
        elif cols == 2:
            name = "PIN%dx%d%s" % (rows, cols, kind["postfix"])
        else:
            raise Exception("Number of columns (%d) to high!" % cols)
        # header
        h = cols * 1.27
        self.footprintHeader(name, "CON", refPos=[0,h+0.75], namePos=[0,-h-0.75])
        # body
        h = cols * 1.27
        l = rows * 1.27
        self.drawRect([-l, -h], [l, h])
        self.drawPolygon([[-l+0.635, cols*1.27+1.27], [-l+1.905, cols*1.27+1.27], [-l+1.27, cols*1.27]])
        # pins
        self.drawPins(rows, cols, kind)
        self.footprintFooter()
    
    def drawPins(self, rows, cols, kind):
        for c in range(cols): # 1 or 2
            for r in range(rows):
                if (c==0 and r==0):
                    shape = "rect"
                else:
                    shape = "oval"
                self.drawPad(r*cols+c+1, [((-rows/2.0 + 0.5 +r) * 2.54), (-c+0.5*(cols-1))*2.54], kind["pinSize"], 
                    shape = shape, drill = 1.0, padType = "thru_hole", layers ="*.Cu *.Mask F.SilkS")

    def library(self, rows=range(1,41), cols=[1,2]):
        for c in cols:
            for r in rows:
                for kind in self.kinds:
                    self.footprint(r, c, kind)

class idcFootprint(pinFootprint):
    def footprint(self, rows, cols, kind=None):
        if not kind:
            kind = self.kinds[0]
        name = "IDC%d%s" % (rows*2, kind["postfix"])
        # header
        self.footprintHeader(name, "CON", refPos=[0,6], namePos=[0,-5])
        # body
        h = 4.2
        l = rows * 1.27 + 3.8
        self.drawRect([-l, -h], [l, h])
        self.drawRect([-1.5, h], [1.5, h+1])
        self.drawPolygon([[-l+0.635, h+1.27], [-l+1.905, h+1.27], [-l+1.27, h]])
        # pins
        self.drawPins(rows, cols, kind)
        self.footprintFooter()

    def library(self, rows=range(3,35)):
        for r in rows:
            for kind in self.kinds:
                self.footprint(r, 2, kind)

class pinSmdFootprint(footprint):
    kinds = [{"name":"standard", "postfix":"", "pinSize":[[1,2.75],[1,3.25]]}]
    def footprint(self, rows, cols, kind=None):
        if not kind:
            kind = self.kinds[0]
        if cols == 1:
            name = "PIN%dSMD%s" % (rows, kind["postfix"])
        elif cols == 2:
            name = "PIN%dx%dSMD%s" % (rows, cols, kind["postfix"])
        else:
            raise Exception("Number of columns (%d) to high!" % cols)
        # header
        h = (6+(cols-1)*2.5)/2 
        l = rows * 1.27
        self.footprintHeader(name, "CON", refPos=[0,h+0.75], namePos=[0,-h-0.75])
        # body
        self.drawRect([-l, -h], [l, h])
        self.drawPolygon([[-l, (cols-1)*1.27], [-l-1.27, (cols-0.5)*1.27], [-l-1.27, (cols-1.5)*1.27]])
        # pins
        self.drawPins(rows, cols, kind)
        self.footprintFooter()
    
    def drawPins(self, rows, cols, kind):
        for c in range(cols): # 1 or 2
            for r in range(rows):
                shape = "rect"
                self.drawPad(r*cols+c+1, [((-rows/2.0 + 0.5 +r) * 2.54), (1.375 if cols==1 else 2.375)*(1 if (r*cols+c+1)%2 else -1)], kind["pinSize"][cols-1], 
                    shape = shape, drill = 1.0, padType = "smd", layers ="F.Cu F.Paste F.Mask")

    def library(self, rows=range(1,41), cols=[1,2]):
        for c in cols:
            for r in rows:
                for kind in self.kinds:
                    self.footprint(r, c, kind)

        
if __name__ == "__main__":
    if 1:
        gen = footprint_generator("test.pretty")
        gen.library_generator([pinSmdFootprint])
    if 1:
        pass
