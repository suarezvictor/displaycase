
def mod(a,b):
    return ( a % b)

class Spline:
    def __init__(self, m, points):
        self.m = m
        self.points = points

    def StandardKnot(self):
        knot = []
        L = len(self.points) - 2
        if L <= self.m -2 :
            print 'make more self.points than m'
            return []
        for i in range(self.m - 1):
            knot.append(0)
        for i in range(L - self.m + 3):
            knot.append(i)
        for i in range(self.m):
            knot.append(L - self.m + 3)
        return knot

    def Nopen(self, k,m,t,knot):
        if m <= 1:
            if t < knot[k] or t > knot[k + 1]:
                Sum = 0.0
            else:
                Sum = 1.0
        else:
            d = knot[k+m-1]-knot[k]
            if d != 0:
                Sum = (t-knot[k])*self.Nopen(k,m-1,t,knot)/d
            else:
                Sum = 0.0
            d = knot[k+m] - knot[k+1]
            if d != 0:
                Sum = Sum + (knot[k+m] - t)*self.Nopen(k + 1,m-1,t,knot)/d
        return Sum

    def P(self, t,knot,Ncycle):
        L = len(self.points)
        SumX = 0.0
        SumY = 0.0
        SumZ = 0.0
        for k in range(L):
            n = Ncycle(k,self.m,t,knot)
            SumX = SumX + n * self.points[k][0]
            SumY = SumY + n * self.points[k][1]
            SumZ = SumZ + n * self.points[k][2]
        return (SumX,SumY,SumZ)

    def plot(self, step=0.1):
        res = []
        knot = self.StandardKnot()
        if len(knot) == 0:
           return
        #print knot
        #print self.points
        x = self.points[0][0]
        y = self.points[0][1]
        z = self.points[0][2]
        t = 0.0
        L = len(self.points)
        while t <= L - self.m  + 1:
            p = self.P(t, knot, self.Nopen)
            res.append(p)
            if t == (L - self.m+1):
                break
            t = t + step
            if t > (L - self.m+1):
                t = (L - self.m+1)
                p = self.P(t, knot, self.Nopen)
                res.append(p)
                break
        return res

    def Spaceout(self):
        newpoints = []
        L = len(self.points)
        newpoints.append(self.points[0])
        knot = self.StandardKnot()
        if len(knot) == 0:
            return
        for t in range( 1, L - self.m  + 2):
            p = self.P(t - 0.5,knot,self.Nopen)
            x = self.points[t][0] - p[0]
            y = self.points[t][1] - p[1]
            z = self.points[t][2] - p[2]
            newpoints.append((self.points[t][0] + x,
                             self.points[t][1] + y,
                             self.points[t][2] + z))
        newpoints.append(self.points[-1])
        self.points = newpoints

if __name__ == '__main__':
    points1 = [(0,0,0), (100,0,20), (200,0,0), (300,0, 60)]
    #points2 = [(0,100,0), (100,100,10), (200,100,0), (300, 120, 100)]
    #points3 = [(0,200,50), (100,200,0), (200,200,50), (300, 220, 80)]

    s = Spline(3, points1)

    print s.plot()

