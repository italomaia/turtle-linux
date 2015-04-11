import random

class PInterpolator:
    def __init__(self, pinicio, pfin):
        self.inicio = complex(pinicio[0],pinicio[1])
        self.fin = complex(pfin[0],pfin[1])
        
class MadamBezier(PInterpolator):
    def __init__(self, pinicio, pfin, prev=None, aux2=None):
        """ We use 2 auxiliary points for bezier interpolation (them are bezier
        interpolation standard points).
        We can generate them or them can be especified by the caller.
        
        In the especification the order is:
            MadamBezier( initial_point, end_point [, prev [, aux_2]])
        where the points, if are in a line should be in this order:
            initial_point ....   aux_2  end_point
            
        In the case you set prev to an instance of this class, it 
        will take the aux_2 point from them and mirror it to use
        as aux_1 point for the initial_point of the newly instance.
        
        """
        PInterpolator.__init__(self,pinicio, pfin)
        d = self.fin-self.inicio
        ycoef = abs(int(d.imag))
        if prev<>None:
            if isinstance(prev,MadamBezier):
                #it's an instance, take the value and mirror it!
                self.m1 = 2*self.inicio - prev.getPrev()
            else:
                #just use it as a normal point
                self.m1 = prev
        else:
            self.m1 = self.inicio + d/4 + complex(0, 
                                    random.randint(-ycoef, ycoef))   
        if aux2<>None:
            self.m2 = aux2
        else:
            self.m2 = self.fin-d/4 + complex(0, random.randint(-ycoef, ycoef))   #random here please 
        
    def getAt(self, t):
        c = ((1-t)**3)*self.inicio + \
                3*t*((1-t)**2)*self.m1+\
                3*(t**2)*(1-t)*self.m2+\
                (t**3)*self.fin 
        return c.real, c.imag
        
    def getPrev(self):
        return self.m2
        
if __name__=="__main__":
    inter = MadamBezier( (0,0), (4,4) )
    for r in range(10):
        print inter.getAt( 1.0/(r+1) )
