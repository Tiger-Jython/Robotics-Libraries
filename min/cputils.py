def cat(filename):
	with open(filename)as B:
		A=B.readline()
		while A:print(A[:-1]);A=B.readline()
from math import asin,atan2,sqrt,degrees
def getPitch(a):A=atan2(a[1],a[2]);return int(degrees(A))
def getRoll(a):A=sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2]);B=asin(a[0]/A);return int(degrees(B))