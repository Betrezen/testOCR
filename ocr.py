# -*- coding: utf-8 -*-
import json
import sys
print sys.getdefaultencoding()

def main(argv):
    print argv
    #делаем преобразования
    print getPassportDataInJson('Вася', 'Петров', 38, 'М')

def getPassportDataInJson(name, surname, age, sex ): #и так далее сколько надо
	data = Object()
	data.name = name
	data.surname = surname
	data.age = age
	data.sex = sex
	return data.to_JSON()
	
class Object:
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

main(sys.argv[0])
			