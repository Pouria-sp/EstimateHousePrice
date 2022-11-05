from time import sleep
import requests
from bs4 import BeautifulSoup
import mysql.connector
import re
from sklearn import tree

mydb = mysql.connector.connect(
  host="localhost",
  username="root",
  password="admin",
  database='maktabkhoone1'
)
cursor = mydb.cursor()

def exist(price:int,province:str,city:str,meterage:int,rooms:int,year:int):
  cursor.execute(f"SELECT COUNT(*) from `project` WHERE `price` = '{str(price)}' AND `province` = '{province}' AND `city` = '{city}' AND `meterage` = {meterage} AND `rooms` = {rooms} AND `year` = {year};")
  if cursor.fetchone()[0] > 0:
    return(True)
  else:
    return(False)

def insert(price:int,province:str,city:str,meterage:int,rooms:int,year:int):
  cursor.execute(f"INSERT INTO project VALUES({price},'{province}','{city}',{meterage},{rooms},{year});")
  mydb.commit()

print('Wellcome To estimate House Price')
if input('Do You Want To Update DataBase ? (Y or N)').lower() == 'y':
  page = 1
  items = 0
  newadd = 0
  while True:
    soup = BeautifulSoup(requests.get(f'https://shabesh.com/search/%D8%AE%D8%B1%DB%8C%D8%AF-%D9%81%D8%B1%D9%88%D8%B4/%D9%88%DB%8C%D9%84%D8%A7/%DA%AF%DB%8C%D9%84%D8%A7%D9%86?location_ids=3&page={page}').text,'html.parser')

    result = soup.find_all('div',attrs={'class':'list_infoBox__iv8WI'})
    for i in result:
      price = i.find('span',attrs={'class':'list_infoPrice___aJXK'}).get_text()
      if price == 'تماس بگیرید':
        continue
      price = int(re.sub(r'[^\d]*','',price))
      province = i.find('span',attrs={'class':'list_infoItem__8EH57 ellipsis d-block'}).get_text()
      province = re.findall(r'\s+(\w*)$',province)[0]
      city = i.find('span',attrs={'class':'list_infoItem__8EH57 ellipsis d-block'}).get_text()
      city = re.sub(r'\s+(\w*)$','',city)
      if len(i.find_all('span',attrs={'class':'px-1 font-12'})) != 3:
        continue
      meterage = i.find_all('span',attrs={'class':'px-1 font-12'})[0].get_text()
      meterage = int(re.findall('\d+',meterage)[0])
      rooms = i.find_all('span',attrs={'class':'px-1 font-12'})[1].get_text()
      rooms = int(re.findall('\d+',rooms)[0])
      years = int(i.find_all('span',attrs={'class':'px-1 font-12'})[2].get_text())
      if exist(price,province,city,meterage,rooms,years):
        items += 1
        continue
      
      else:
        insert(price,province,city,meterage,rooms,years)
        items += 1
        newadd += 1

    if items > 600:
      del page
      del items
      print(newadd,'New Items Added !')
      del newadd
      break

    page += 1

sleep(2)

cursor.execute('SELECT * FROM project')

provincedict = {}
citydict = {}
provincelist = []
citylist = []
for i in cursor:
  if provincelist.count(i[1]) == 0:
    provincelist.append(i[1])
  if citylist.count(i[2]) == 0:
    citylist.append(i[2])

for i in provincelist:
  provincedict[i] = provincelist.index(i)
for i in citylist:
  citydict[i] = citylist.index(i)

cursor.execute('SELECT * FROM project')
x = []
y = []
for i in cursor:
  tmp = [provincedict[i[1]],citydict[i[2]],i[3],i[4],i[5]]
  x.append(tmp)
  y.append(int(i[0]))

clf = tree.DecisionTreeClassifier()
clf.fit(x,y)

print(' - '.join(provincelist))
province = input('Enter House Province : ')
cursor.execute(f'SELECT city FROM project WHERE province = \'{province}\'')
province = provincedict[province]

citylist.clear()
for i in cursor:
  if citylist.count(i[0]) == 0:
    citylist.append(i[0])
print(' - '.join(citylist))
city = input('Enter House City : ')
city = citydict[city]


meterage = int(input('Enter House Meterage : '))
rooms =  int(input('Enter House BedRooms : '))
years = int(input('Enter The year the house was built : '))

print(str(clf.predict([[province,city,meterage,rooms,years]])[0]) + ' toman')