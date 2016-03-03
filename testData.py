import csv
import random

def getDictionary():
    with open("dataset1.csv") as f:
        for line in f:
            arr = line.replace("\r", "").split(",")[:-1]
        compToWeb = {}
        for i in range(len(arr)):
            if i % 2 == 0:
                compToWeb[arr[i]] = arr[i+1].strip()
        return compToWeb

def getNCompanies(n=20):
    n = 20 if n < 1 or n > 947 else int(n)
    with open("companies.txt") as f:
        s = random.sample(range(1, 947), n)
        i = 1
        arr = []
        for line in f:
            if i in s:
                data = line.strip('\n').replace("\x00", "")[:-1]
                if data[0] == "\"":
                    data = data[1:len(data)-1]
                arr.append(data)
            i += 1
    return arr

