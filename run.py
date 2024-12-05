import testData
import convert
import random

pastTrain = ['MineralTree', 'Nextera Energy', 'Oktagon Games', 'Macworld', 'Liberty Mutual', 'NeonMob', 'University of Nottingham', 'Amarillo Globe-News', 'UMMC', 'LabCorp', 'Veeva Systems', 'Red Tricycle', 'A View From My Seat', 'Sonic Electronix', 'W3 Consulting', 'WickedLocal', 'MovieTickets.com', 'Granicus', 'Rabt', 'Navvia', 'TrueAbility', 'Librato', '250ok', 'GigSky', 'Blue Jeans Network']

def getTrainingSample(n):
    # return [random.choice(testData.companyToWebsiteTrainingDictionary.keys()) for i in range(n)]
    out = []
    for i in range(n):
        r = random.choice(testData.companyToWebsiteTrainingDictionary.keys())
        while r in out or r in pastTrain:
            r = random.choice(testData.companyToWebsiteTrainingDictionary.keys())
        out.append(r)
    pastTrain += out
    return out

def checkAndPrintTrain(outputDictionary, notFoundList, query2URLS):
    correct = 0
    for k in outputDictionary:
        print (k)
        print (outputDictionary)[k]
        print (testData.companyToWebsiteTrainingDictionary[k])
        if outputDictionary[k][0] == testData.companyToWebsiteTrainingDictionary[k]:
            print("correct")
            correct += 1
        else:
            print("incorrect")
    print ("total correct: " + str(correct) + " out of " + str(len(outputDictionary.keys())))
    print
    for e in notFoundList:
        print (e)
        print (query2URLS[e])
        print (testData.companyToWebsiteTrainingDictionary[e])
        print

def printTrainingCorrectness(outputDictionary):
    correct = 0
    for k in outputDictionary:
        if outputDictionary[k][0] == testData.companyToWebsiteTrainingDictionary[k]:
            correct += 1
    print ("total correct: " + str(correct) + " out of " + str(len(outputDictionary.keys())))

def thresholdForTrainingSample(value, outputDictionary):
    correctMin = 1
    incorrectMax = 0
    for k in outputDictionary:
        if outputDictionary[k][2] == value:
            if outputDictionary[k][0] == testData.companyToWebsiteTrainingDictionary[k]:
                correctMin = min(outputDictionary[k][1], correctMin)
            else:
                incorrectMax = max(outputDictionary[k][1], incorrectMax)
    return (correctMin, incorrectMax)

def getThresholdForValue(value):
    correctMinList = []
    incorrectMaxList = []
    for i in range(10):
        companyNamesSample = getTrainingSample(25)
        query2URLSMap = convert.getQuery2URLS(companyNamesSample)
        outputDictionary, notFoundList = convert.getBestURLForName(query2URLSMap)
        correctMin, incorrectMax = thresholdForTrainingSample(value, outputDictionary)
        correctMinList.append(correctMin)
        incorrectMaxList.append(incorrectMax)
    return correctMinList, incorrectMaxList

companyNamesSample = getTrainingSample(25)
query2URLSMap = convert.getQuery2URLS(companyNamesSample)
outputDictionary, notFoundList = convert.getBestURLForName(query2URLSMap)
print (thresholdForTrainingSample("domain in companyName or vice versa", outputDictionary))
printTrainingCorrectness(outputDictionary)

##################### My Webscrape ##########################################
# d, notFound, query2URLS = convert.matchURLToName(testData.getNCompanies(15))
# for k in d:
#     print(k)
#     print(d[k])

# print(notFound)


# query2URLS = {}
# query2URLS['Southern Company'] = ['http://www.southerncompany.com/', 'http://www.southerncompany.com/about-us/careers/home.cshtml', 'http://www.southerncompany.com/what-doing/energy-innovation/nuclear-energy/job-opportunity.cshtml', 'https://en.wikipedia.org/wiki/Southern_Company']
# d, notFound = convert.getBestURLForName(query2URLS)

##################### CORRECT ANSWER SIMPLE ##########################################
# query2URLS = {}
# query2URLS["Microsoft"] = ['https://www.microsoft.com/', 'https://www.microsoft.com/en-us/download', 'https://support.microsoft.com/', 'https://en.wikipedia.org/wiki/Microsoft']
# query2URLS["National Pen Company"] = ['http://www.pens.com/national-pen-company', 'http://www.pens.com/', 'http://www.pens.com/customer-service-national-pen', 'http://www.pens.com/about-national-pen']
# query2URLS["Designzillas, LLC"] = ['http://www.designzillas.com/', 'http://www.designzillas.com/hiring', 'http://www.designzillas.com/about-us', 'http://www.designzillas.com/contact-us']
# query2URLS["California College of Arts"] = ['https://www.cca.edu/', 'https://www.cca.edu/academics', 'https://www.cca.edu/admissions', 'https://en.wikipedia.org/wiki/California_College_of_the_Arts']
# query2URLS["Flynn"] = ['http://www.flynncenter.org/', 'https://flynn.io/', 'https://en.wikipedia.org/wiki/Errol_Flynn', 'https://github.com/flynn/flynn']
# d, notFound = convert.getBestURLForName(query2URLS)

# for k in d:
#     print(k)
#     print(d[k])
#     print

# print notFound

# Microsoft -> microsoft.com
# National Pen Company -> nationalpen.com
# Designzillas, LLC -> designzillas.com
# California college of Arts -> cca.edu
# Flynn -> flynn.io
