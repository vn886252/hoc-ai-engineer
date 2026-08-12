import numpy as np

m = np.array([15, 22, 8, 34, 19, 41, 7])
print(m.mean())
print(m.max())
print(m.min())
print(m.std())
print(m[m > m.mean()])
 #2/

a = np.array([1,2,3,4])
b = np.array([5,6,7,8])
print (a + b)
print (a * b)
print (np.dot(a,b))

#3/
m = np.array([[1,2,3],[4,5,6],[7,8,9]])
print(m.T)

#4/
n = np.random.randint(1,100,20)
print(n)
print(len(n[n%2==0]))