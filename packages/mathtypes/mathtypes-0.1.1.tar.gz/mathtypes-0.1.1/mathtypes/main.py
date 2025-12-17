class Fraction():
    def __init__(self,numerator,denominator):
        self.numerator = numerator
        self.denominator = denominator
    def __str__(self):
        w = len(str(max(self.numerator,self.denominator)))
        return f"""{str(self.numerator).center(w)}
{"─"*w}
{str(self.denominator).center(w)}"""
    def LCM(self,a,b):
        low = min(a,b)
        high = max(a,b)
        l = high
        if(high % low == 0):
            return high
        while l % low != 0:
            l+=high
        return l
    def HCF(self,a,b):
        return a*b//self.LCM(a,b)
    def toLowestTerm(self):
        h = self.HCF(self.denominator,self.numerator)
        self.numerator //= h
        self.denominator //= h
    def reciprocal(self):
        reci = Fraction(self.denominator,self.numerator)
        return reci
    def __add__(self,a):
        if isinstance(a, self.__class__) != True:
            raise TypeError(" you cannot add another types in a fraction")
        lcm = self.LCM(self.denominator,a.denominator)
        s = lcm // self.denominator
        b = lcm // a.denominator
        s = Fraction(self.numerator*s,self.denominator*s)
        b = Fraction(a.numerator*b,a.denominator*b)
        f = Fraction(s.numerator+b.numerator,s.denominator)
        return f
    def __sub__(self,a):
        if isinstance(a, self.__class__) != True:
            raise TypeError(" you cannot subtract another types in a fraction")
        lcm = self.LCM(self.denominator,a.denominator)
        s = lcm // self.denominator
        b = lcm // a.denominator
        s = Fraction(self.numerator*s,self.denominator*s)
        b = Fraction(a.numerator*b,a.denominator*b)
        f = Fraction(s.numerator-b.numerator,s.denominator)
        return f
    def __mul__(self,a):
        if isinstance(a, self.__class__) != True:
            raise TypeError(" you cannot multiply another types with a fraction")
        
        f = Fraction(self.numerator*a.numerator,self.denominator*a.denominator)
        return f
    def __truediv__(self,a):
        if isinstance(a, self.__class__) != True:
            raise TypeError(" you cannot divide another types with a fraction")
        
        
        f = Fraction(self.numerator*a.denominator,self.denominator*a.numerator)
        return f

