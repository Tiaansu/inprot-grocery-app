from tabulate import tabulate
import sqlite3
import time
import sys
import os
import random
import datetime

con = sqlite3.connect("grocery-app.db")
cur = con.cursor()

shoppingCartItems = []
chosenCategory = -1

def clrscr():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def sleepThread(i: int):
    time.sleep(i)

def beep():
    sys.stdout.write("\a")
    sys.stdout.flush()

def getDateNow():
    now = datetime.datetime.now()
    weekday = now.strftime("%A")
    month = now.strftime("%B")
    day = now.strftime("%d")
    year = now.strftime("%Y")
    hour = now.strftime("%I")
    minute = now.strftime("%M")
    second = now.strftime("%S")
    meridian = now.strftime("%p")
    return f"{weekday}, {month} {day}, {year} - {hour}:{minute}:{second} {meridian}"

def getCategory(categoryId: int):
    category = "unknown"

    match categoryId:
        case 0: category = "Fruits"
        case 1: category = "Vegetables"
        case 2: category = "Meats"
        case 3: category = "Seafoods"
        case 4: category = "Dairy and eggs"
        case 5: category = "Pantry items"
        case 6: category = "Drinks"
        case 7: category = "Others"
        case 8: category = "Rice cakes"
        case 9: category = "Sweets"

    return category

def GroceryTable(groceryItems):
    headers = ["ID", "Name", "Category", "Stocks", "Price"]
    print(tabulate(groceryItems, headers, tablefmt="rounded_grid"))

def PrintEnterIDMessage():
    try:
        id = int(input("Enter the ID of the product: (Type -1 to choose on other categories) "))

        return id
    except ValueError:
        beep()
        PrintEnterIDMessage()
    except TypeError:
        beep()
        PrintEnterIDMessage()
    except KeyboardInterrupt:
        clrscr()
        print("Good bye! :)")
        exit(1)


def PrintEnterQuantityMessage():
    try:
        quantity = int(input("Enter quantity: "))

        return quantity
    except ValueError:
        beep()
        PrintEnterQuantityMessage()
    except TypeError:
        beep()
        PrintEnterQuantityMessage()
    except KeyboardInterrupt:
        clrscr()
        print("Good bye! :)")
        exit(1)

def PrintEnterWantToContinue(message):
    try:
        option = input(message)

        match option.lower():
            case "y": return 1
            case "n": return 0
            case _: 
                beep()
                PrintEnterWantToContinue(message)
    except ValueError:
        beep()
        PrintEnterWantToContinue(message)
    except TypeError:
        beep()
        PrintEnterWantToContinue(message)
    except KeyboardInterrupt:
        clrscr()
        print("Good bye! :)")
        exit(1)

def PrintWantToBuyItem(totalAmount, productName):
    try:
        option = input(f"Want to buy {productName}? Its total amount is ${totalAmount}. [Y/N]: ")

        match option.lower():
            case "y": return 1
            case "n": return 0
            case _: 
                beep()
                PrintEnterWantToContinue(totalAmount, productName)
    except ValueError:
        beep()
        PrintWantToBuyItem(totalAmount, productName)
    except TypeError:
        beep()
        PrintWantToBuyItem(totalAmount, productName)
    except KeyboardInterrupt:
        clrscr()
        print("Good bye! :)")
        exit(1)

def PrintShoppingCartItems(shoppingCartItems):
    shoppingCartItemsTable = []
    totalAmount = 0
    headers = ["ID", "Name", "Quantity", "Price", "Total Price"]

    for element in shoppingCartItems:
        totalAmount += element[3] * element[2]
        shoppingCartItemsTable.append([element[0], element[1], element[2], element[3], element[3] * element[2]])

    print(tabulate(shoppingCartItemsTable, headers, tablefmt="rounded_grid"))

def PrintEnterArrayIndexOfShoppingCartItems():
    try:
        index = int(input("Enter the ID you want to remove on your shopping cart: "))

        shoppingCartItems.pop(index)

        print("Done deleting the item on your cart.")

        wantToReduceItem = PrintEnterWantToContinue("Want to reduce item(s) in your cart? [Y/N]: ")

        if wantToReduceItem:
            clrscr()
            print(" --- item to be removed by you ---")
            PrintShoppingCartItemsToBeRemoved()
        else:
            PrintCheckout()
    except ValueError:
        beep()
        clrscr()
        PrintShoppingCartItemsToBeRemoved()
    except TypeError:
        beep()
        clrscr()
        PrintEnterArrayIndexOfShoppingCartItems()
    except IndexError:
        beep()
        clrscr()
        print(f"Sorry but the ID {index} is not in your shopping cart.")
        PrintShoppingCartItemsToBeRemoved()
    except KeyboardInterrupt:
        clrscr()
        print("Good bye! :)")
        exit(1)

def PrintShoppingCartItemsToBeRemoved():
    shoppingCartItemsTable = []
    headers = ["ID", "Name", "Quantity", "Price", "Total Price"]

    for index, element in enumerate(shoppingCartItems):
        shoppingCartItemsTable.append([index, element[1], element[2], element[3], element[3] * element[2]])

    print(tabulate(shoppingCartItemsTable, headers, tablefmt="rounded_grid"))

    PrintEnterArrayIndexOfShoppingCartItems()

def PrintGroceryTicket(change: int):
    print(f"Thank you for purchasing on our store! Your change is ${change}")
    print("You can see the item(s) you bought below.")

    PrintShoppingCartItems(shoppingCartItems)

    for element in shoppingCartItems:
        cur.execute(f"UPDATE grocery_items SET stocks = stocks - {element[2]} WHERE id = ?", [(element[0])])
        con.commit()

    shoppingCartItems.clear()

    print(f"You completed your purchase on our store on {getDateNow()}.")

    print("Preparing the start menu...")
    sleepThread(2.5)
    EnterGroceryStore()

def PrintEnterUserMoney():
    totalAmount = 0;

    for element in shoppingCartItems:
        totalAmount += element[3] * element[2]

    money = int(input(f"Enter the amount of your money: (Please make sure it's higher than ${totalAmount}) "))

    if money < totalAmount:
        print(f"You still need ${totalAmount - money} to proceed.")

        wantToReduceItem = PrintEnterWantToContinue("Want to reduce item(s) in your cart? [Y/N]: ")

        if wantToReduceItem:
            clrscr()
            print(" --- Item to be removed by you --- ")
            PrintShoppingCartItemsToBeRemoved()
        else:
            PrintEnterUserMoney()
    else:
        clrscr()
        PrintGroceryTicket(money - totalAmount)

def PrintCheckout():
    clrscr()

    print(" --- Shopping cart item(s) --- ")
    PrintShoppingCartItems(shoppingCartItems)

    shoppingCartItemsTable = []
    totalAmount = 0

    for element in shoppingCartItems:
        totalAmount += element[3] * element[2]
        shoppingCartItemsTable.append([element[0], element[1], element[2], element[3], element[3] * element[2]])

    wantToCheckout = PrintEnterWantToContinue(f"Want to checkout {len(shoppingCartItemsTable)} item(s) with overall price of ${totalAmount} in your cart? [Y/N]: ")

    if wantToCheckout:
        PrintEnterUserMoney()
    else:
        BrowseGroceryItemOnCategory(chosenCategory)

def BrowseGroceryItemOnCategory(categoryId: int):
    clrscr()

    result = cur.execute("SELECT * FROM grocery_items WHERE category = ?", [(categoryId)])
    result = result.fetchall()

    groceryItems = []
    
    for element in result:
        id, name, category, stocks, price = element
        groceryItems.append([id, name, getCategory(category), stocks if stocks > 0 else "out of stock", price])

    print(" --- Buy --- ")
    GroceryTable(groceryItems)

    id = PrintEnterIDMessage()

    if id <= -1:
        BrowseAndBuyGroceryItems()
        return
    
    quantity = PrintEnterQuantityMessage()

    totalAmount = 0
    price = 0
    productName = "unknown"

    result = cur.execute("SELECT name, stocks, price FROM grocery_items WHERE id = ?", [(id)])
    result = result.fetchall()

    for element in result:
        name, stocks, priceFromDB = element
        if stocks - quantity < 0:
            if stocks <= 0:
                print("No stocks, choose another product.")
                sleepThread(0.5)
                BrowseGroceryItemOnCategory(categoryId)
            else:
                print(f"Stocks of {name} which is {stocks} is not enough to the quantity {quantity}.")
            
                wantToContinue = PrintEnterWantToContinue(f"Want to continue? This will set the quantity of your chosen product to {stocks}. [Y/N]: ")

                if not wantToContinue:
                    BrowseGroceryItemOnCategory(categoryId)
                    return
                
                quantity = stocks
        
        price = priceFromDB
        totalAmount = price * quantity
        productName = name

    wantToBuyItem = PrintWantToBuyItem(totalAmount, productName)

    if wantToBuyItem:
        shoppingCartItems.append([id, productName, quantity, price])
    else:
        BrowseGroceryItemOnCategory(categoryId)
        return
    
    wantToCheckout = PrintEnterWantToContinue("Want to checkout? [Y/N]: ")

    if not wantToCheckout:
        print(f"Added {productName} in your shopping cart.")
        print("Loading...")
        sleepThread(0.5)
        BrowseGroceryItemOnCategory(categoryId)
    else:
        PrintCheckout()

def BrowseAndBuyGroceryItems():
    clrscr()

    try:
        print("Options: ")
        print("[0] - Fruits")
        print("[1] - Vegetables")
        print("[2] - Meats")
        print("[3] - Meats")
        print("[4] - Dairy and eggs")
        print("[5] - Pantry items")
        print("[6] - Drinks")
        print("[7] - Others")
        print("[8] - Rice cakes")
        print("[9] - Sweets")
        global chosenCategory
        chosenCategory = int(input("Choose: "))

        if chosenCategory > 9 or chosenCategory < 0:
            beep()
            BrowseAndBuyGroceryItems()
            return

        BrowseGroceryItemOnCategory(chosenCategory)
    except ValueError:
        beep()
        BrowseAndBuyGroceryItems()
    except TypeError:
        beep()
        BrowseAndBuyGroceryItems()
    except KeyboardInterrupt:
        clrscr()
        print("Good bye! :)")
        exit(1)

def LoadGroceryItems():
    clrscr()

    print("Loading grocery items...")

    groceryItems = [
        [
            ["Mangoes",                 35],
            ["Bananas",                 30],
            ["Pineapples",              30],
            ["Papayas",                 25],
            ["Oranges",                 25],
            ["Apples",                  20],
            ["Grapes",                  35],
            ["Watermelons",             50],
            ["Cantaloupe",              40]
        ],
        [
            ["Broccoli",                15],
            ["Carrots",                 20],
            ["Cauliflower",             15],
            ["Celery",                   5],
            ["Onions",                  10],
            ["Potatoes",                15],
            ["Tomatoes",                15]
        ],
        [
            ["Chicken",                120],
            ["Pork",                   150],
            ["Beef",                   200],
            ["Hotdogs",                 30],
            ["Bacon",                   60],
            ["Sausage",                 40]
        ],
        [
            ["Fish",                   120],
            ["Shrimp",                 150],
            ["Squid",                  150],
            ["Crab",                   135],
            ["Tuna",                   200],
            ["Sardines",               135]
        ],
        [
            ["Milk",                    25],
            ["Cheese",                  40],
            ["Eggs (per tray)",         30],
            ["Yogurt",                  25],
            ["Butter",                  25],
            ["Ice cream",               20]
        ],
        [
            ["Rice (sack)",           1250],
            ["Bread",                   50],
            ["Flour",                   50],
            ["Sugar",                   25],
            ["Salt",                    25],
            ["Pepper",                  10],
            ["Garlic",                   5],
            ["Onions",                   5],
            ["Cooking oil",             10],
            ["Soy sauce",               10],
            ["Vinegar",                 10],
            ["Bagoong isda",            35],
            ["Bagoong alamang",         35],
            ["Patis",                   15],
            ["Sardines (canned)",       20],
            ["Tuna (canned)",           20],
            ["Corned beef",             20],
            ["Fruits (canned)",         20],
            ["Vegetables (canned)",     20],
            ["Instant noodles",         15],
            ["Pasta",                   20],
            ["Cereal",                  20],
            ["Chips",                   15],
            ["Cookies",                 10],
            ["Candy (pack)",            25]
        ],
        [
            ["Water",                   15],
            ["Juice",                   15],
            ["Soda",                    15],
            ["Coffee",                  15],
            ["Tea",                     15]
        ],
        [
            ["Shampoo",                 10],
            ["Soap",                    10],
            ["Toothpaste",              10],
            ["Deodorant",               10],
            ["Pet food",               100],
            ["Baby supplies",           50]
        ],
        [
            ["Puto",                    15],
            ["Bibingka",                25],
            ["Kutsinta",                 5],
            ["Kalamay",                 15]
        ],
        [
            ["Halo-halo",               15],
            ["Leche flan",              25],
            ["Turon",                   15],
            ["Taho",                    10]
        ]
    ]

    con.execute("DROP TABLE IF EXISTS grocery_items")
    con.execute("""
        CREATE TABLE grocery_items (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category INTEGER NOT NULL,
            stocks INTEGER NOT NULL,
            price INTEGER NOT NULL
        );
    """)

    for index, element in enumerate(groceryItems):
        for idx, el in enumerate(element):
            cur.execute("INSERT INTO grocery_items (name, price, category, stocks) VALUES (?, ?, ?, ?)", (el[0], el[1], index, random.randint(0, 200)))
            con.commit()

    print("Done loading grocery items.")
    sleepThread(0.25)
    EnterGroceryStore()

def EnterGroceryStore():
    clrscr()

    try:
        print("Welcome to Grocery App version 0.0.1-dev!\n")

        print("Options: ")
        print("[1] - Load grocery items (startup)")
        print("[2] - Browse & buy grocery items")
        print("[3] - Exit the store")
        option = int(input("Choose: "))

        match option:
            case 1:
                LoadGroceryItems()

            case 2:
                BrowseAndBuyGroceryItems()

            case 3:
                clrscr()
                print("Good bye! :)")
                exit(1)

            case _:
                beep()
                EnterGroceryStore()
    except ValueError:
        beep()
        EnterGroceryStore()
    except TypeError:
        beep()
        EnterGroceryStore()
    except KeyboardInterrupt:
        clrscr()
        print("Good bye! :)")
        exit(1)

if __name__ == "__main__":
    EnterGroceryStore()