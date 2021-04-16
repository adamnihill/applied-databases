# Database menu
# Adam Nihill
# Applied Databases
# Computer Science and Data Analytics 
# GMIT
# 2020
import sys 
import pymongo
import pymysql
import re

myClient = None
conn = None

def connectMySQL():
    global conn
    conn = pymysql.connect("localhost", "root", "root", "world", cursorclass=pymysql.cursors.DictCursor)
    
def connectMongo():
    global myClient
    myClient = pymongo.MongoClient()
    myClient.admin.command("ismaster")


def main():
    if(not conn):
        try:
            connectMySQL();
        except Exception as e:
            print("Error", e)
    if(not myClient):
        try:
            connectMongo();
        except Exception as e:
            print("Error", e)
    menu()

def menu():
    print("--------")
    print("World DB")
    print("--------")
    print()
    print("====")
    print("MENU")
    print("====")
    
    choice = input("""
1 - View People
2 - View Countries by Independence Year
3 - Add New Person
4 - View Countries by Name
5 - View Countries by Population
6 - Find Students by Address
7 - Add New Course
x - Exit Application

Choice: """)

    if choice == "1":
        viewPeople()
    elif choice == "2":
        viewIndependence()
    elif choice == "3":
        addPerson()
    elif choice == "4":
        viewCountry()
    elif choice == "5":
        viewPopulation()
    elif choice == "6":
        findAddress()
    elif choice == "7":
        addCourse()
    elif choice == "X" or choice == "x":
        sys.exit
    else:
        print("You must only select either 1, 2, 3, 4, 5, 6 or 7.")
        print("Please try again")
        menu()

# view people
def viewPeople():
    print("-----------")
    print("View People")
    print("-----------")
    query = "Select * FROM person;"
    
    with conn:
        cursor = conn.cursor()
        cursor.execute(query)
    
    while True:
        people = cursor.fetchmany(size = 2)
        for p in people:
            print(p["personID"], "|", p["personname"], "|", p["age"])
        
        keypress = input("-- Quit <q> --")
        if keypress == "Q" or keypress == "q":
            break
    menu()

# view by year of indepence 
def viewIndependence():
    print("------------------------------")
    print("Countries by Independence Year")
    print("------------------------------")
    year = int(input("Enter Year: "))
    query = "Select name, continent, indepyear from country where indepyear = %s"
    
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, (year, ))
    
    while True:    
        year = cursor.fetchall()
        print()
        for y in year:
            print(y["name"], "|", y["continent"], "|", y["indepyear"])
        break
    menu()

# add new person
def addPerson():
    print("--------------")
    print("Add New Person")
    print("--------------")

    ins = "INSERT INTO person (personname, age) VALUES (%s, %s)"
    
    with conn:
        while True:
            try:
                name = input("Name: ")
                if not name:
                    raise ValueError("enter name")
                age = int(input("Age: "))
                cursor = conn.cursor()
                cursor.execute(ins, (name, age))
                conn.commit()
                print()
                print(name, "added")
                break
                menu()
            except ValueError as e:
                print("Error", e)
            except pymysql.err.InternalError as e:
                print("Internal Error", e)
            except pymysql.err.IntegrityError:
                print("*** ERROR ***", name, "already exists")
            except Exception as e:
                print("error", e)
        menu()

# country by string        
def viewCountry():
    print("-----------------")
    print("Countries by Name")
    print("-----------------")
    name = input("Enter Country Name: ")
    query = "SELECT * FROM country WHERE name LIKE %s"
    
    with conn:
        while True:
            cursor = conn.cursor()
            cursor.execute(query, ("%" + name + "%"))
            cname = cursor.fetchall()
            conn.commit()
            print()
            for c in cname:
                print(c["Name"], "|", c["Continent"], "|", c["Population"], "|", c["HeadOfState"])
                
            print()
            keypress = input("-- Quit <q> --")
            if keypress == "Q" or keypress == "q":
                break
        menu()

        

def viewPopulation():
    print("----------------")
    print("Countries by Pop")
    print("----------------")
    lessthan = "SELECT * FROM country  WHERE population < (%s)"
    greaterthan = "SELECT * FROM country  WHERE population > (%s)"
    equals = "SELECT * FROM country  WHERE population = (%s)"
    while True:
        compare = input("Enter < > or = : ")
        if not compare in ["<", ">", "="]:
            continue
        elif compare == "<":
            query = lessthan
            break
        elif compare == ">":
            query = greaterthan
            break
        elif compare == "=":
            query = equals
            break
        
    pop = int(input("Enter Population: "))
    cursor = conn.cursor()
    cursor.execute(query, (pop))
    popul = cursor.fetchall()
    print()
    for p in popul:
        print(p["Name"], "|", p["Continent"], "|", p["Population"] )
    while True:
        
        print()
        keypress = input("-- Quit <q> --")
        if keypress == "Q" or keypress == "q":
            break
    menu()

    

# find student by address    
def findAddress():
    db = myClient["proj20DB"]
    docs = db["docs"]
    print("-----------------------")
    print("Find Student by Address")
    print("-----------------------")
    address = input("Enter Address: ")
    query = {"details.address": re.compile('^' + address + '$', re.IGNORECASE)}
    while True:
        people = docs.find(query)
        for p in people:
            print(p["_id"], "|", p["details"]["name"], "|", p["details"]["address"])
        print()     
        keypress = input("-- Quit <q> --")
        if keypress == "Q" or keypress == "q":
            break
    menu()

# add new course    
def addCourse():
    db = myClient["proj20DB"]
    docs = db["docs"]
    print("--------------")
    print("Add New Course")
    print("--------------")
    _id = input("_id: ")
    name = input("Name: ")
    level = int(input("Level: "))
    addNew = {"_id" : _id, "name":name, "level": level}
    while True:
        try:
            new = docs.insert_one(addNew)
            print(name, "added.")
            keypress = input("-- Quit <q> --")
            if keypress == "Q" or keypress == "q":
                break
            menu()
        
        except pymongo.errors.DuplicateKeyError as e:
            print("*** ERROR ***: ""_ID ", _id, " already exists")
            print()
            keypress = input("--Quit <q>--")
            if keypress == "Q" or keypress == "q":
                break
    menu()





if __name__ == "__main__":
    main()