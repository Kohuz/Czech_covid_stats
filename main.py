import json
import datetime
from functools import reduce
import sys

from pip._vendor import requests
import matplotlib.pyplot as plt


class Region:
    infected_men = 0
    infected_women = 0

    def __init__(self, name, code, muzi, zeny):
        self.name = name
        self.code = code
        self.muzi = muzi
        self.zeny = zeny
        self.pop = muzi + zeny
        self.infected = []

    def pridat_infikovane(self, sex, person):
        self.infected.append(person)
        if sex == "M":
            self.infected_men += 1
            # self.infected_men_total_age += age
        else:
            self.infected_women += 1
            # self.infected_woman_total_age += age

    def infected_by_days(self, days):
        counter = 0
        for person in self.infected:
            if person.date == str(datetime.date.today() - datetime.timedelta(days=days)):
                counter += 1
        return counter


class Person:

    def __init__(self, date, age, sex, imported):
        self.date = date
        self.age = age
        self.sex = sex
        self.imported = imported


def create_last_days_infected(regions, days):
    lastdays = {}
    for day in range(days):
        lastdays[str(datetime.date.today() - datetime.timedelta(days=day + 1))] = []

    for region in regions.values():
        for infect in region.infected:
            curDate = infect.date
            if curDate in lastdays.keys():
                lastdays[curDate].append(infect)
    return lastdays


def create_regions():
    regions = {}
    file = open("arccr_kraje_polygony.json", encoding="utf8")
    data = json.load(file)
    for region in data['features']:
        curCode = region['attributes']['KOD_CZNUTS3']
        regions[curCode] = Region(region['attributes']['NAZ_CZNUTS3'],
                                  region['attributes']['KOD_CZNUTS3'],
                                  region['attributes']['MUZI'],
                                  region['attributes']['ZENY'],
                                  )
    return regions


def fetch_infected_data(regions):
    ill_api = requests.get("https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19/osoby.json")
    json_ill_data = ill_api.json()

    for person in json_ill_data['data']:
        infected = Person(person['DatumHlaseni'],
                          person['Vek'],
                          person['Pohlavi'],
                          person['Import'])
        regions[person['OkresKodBydliste']].pridat_infikovane(person['Pohlavi'],
                                                              infected)


def main():
    regions = create_regions()
    fetch_infected_data(regions)

    # print(f"Počet nakažených za den {datetime.date.today() - datetime.timedelta(days=2)}")
    # for region in regions.values():
    #     print(f"{region.name}: {region.infected_by_days(2)}")



    plt.subplot(2, 1, 1)

    last14days = create_last_days_infected(regions, 14)
    values = []
    for day in last14days.values():
        values.append(len(day))
    last7days = values[:7]

    total_infected = 0
    total65 = 0
    for region in regions.values():
        total_infected = total_infected + len(region.infected)





    if len(sys.argv) == 1:
        print(f"Potvrzené případy za posledních 7 dní na 100 000 obyvatel:"
              f"\n{reduce((lambda a, b: a + b), last7days) / 100}")
        print(f"Potvrzené případy za posledních 14 dní na 100 000 obyvatel:"
              f"\n{reduce((lambda a, b: a + b), values) / 100}")
        print(f"Potvrzené případy celkově:"
              f"\n{total_infected:,}")
        exit(0)

    plt.scatter([i for i in range(7)], values, s=100)


    plt.subplot(2, 1, 2)
    plt.bar([i for i in range(7)], values)


    plt.figtext(-1,-1,"hello")
    plt.show()




if __name__ == "__main__":
    main()
