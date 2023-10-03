import json
from datetime import datetime, timedelta, timezone
import requests

USER_NAME = ''
USER_ID = ''

# Функция вычисления стоимости услуги
def ServiceCost(guestsNumber: int,
                minutesNumber: int,
                studentsNumber=0,
                costPerMinute=4,
                stop_check=750,
                discountStudent=0.15 ) -> int:
    cost_students = costPerMinute * minutesNumber * studentsNumber * discountStudent
    print(f'cost_students={cost_students}')
    cost_guest = (costPerMinute * minutesNumber * (guestsNumber-studentsNumber)) + cost_students
    print(f'cost_guest={cost_guest}')
    cost_stop = guestsNumber  * stop_check
    print(f'cost_stop={cost_stop}')
    min_cost = cost_stop if cost_stop < cost_guest else cost_guest
    return min_cost


function_descriptions = [
    {
        "name": "get_service_cost",
        "description": "Calculate the cost of a service for a given number of guests per number of minutes",
        "parameters": {
            "type": "object",
            "properties": {
                "guests_number": {
                    "type": "integer",
                    "description": "Number of guests including students, e.g. 7",
                },
                "students_number": {
                    "type": "integer",
                    "description": "Number of students or schoolchildren or children over 5 years old, e.g. 2",
                },
                "minutes_number": {
                    "type": "integer",
                    "description": "The number of minutes, e.g. 120",
                },
            },
            "required": ["guests_number", "minutes_number"],
        },
    },
    {
        "name": "get_dish",
        "description": "Get information about the dish, restaurant name, name of the dish, price of the dish and description of the dish",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_name": {
                    "type": "string",
                    "description": "The Restaurant name, e.g. Allo BEIRUT",
                },
                "dish_name": {
                    "type": "string",
                    "description": "The dish, name, e.g. Juice Cocktail",
                },
                "dish_description": {
                    "type": "string",
                    "description": "The description of the dish, e.g. Guava, banana, strawberry, mango & milk",
                },
                "dish_price": {
                    "type": "integer",
                    "description": "The dish price, e.g. 120",
                },
                "placed_order": {
                    "type": "string",
                    "description": "The client placed an order, e.g. YES or NO",
                },

            },
            "required": ["restaurant_name", "dish_name", "dish_price", "placed_order"],
        },
    },
 ]

def get_dish(restaurant_name, dish_name, dish_price, dish_description='', placed_order='NO'):
    """Get information about the dish, restaurant name, name of the dish, price of the dish and description of the dish"""
    print(f'placed_order={placed_order}')
    # Output
    get_dish_info = {
        "user_name": USER_NAME,
        "user_id": USER_ID,
        "restaurant_name": restaurant_name,
        "dish_name": dish_name,
        "dish_price": dish_price,
        "dish_description": dish_description
    }
    dish = json.dumps(get_dish_info)
    if placed_order == 'YES':
        # Get the current date and time
        current_datetime = datetime.now(tz=timezone(timedelta(hours=3)))
        # Format the date and time as a string
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        orderfilename = "Logs/" + formatted_datetime + "_order.txt"
        with open(orderfilename, 'w', encoding='utf-8') as file:
            file.write(dish)

    return dish

def get_service_cost(guests_number, minutes_number, students_number=0):
    """Calculate the cost of a service for a given number of guests per number of minutes"""
    service_cost = ServiceCost(guests_number, minutes_number, students_number)
    # Output
    service_cost_info = {
        "guests_number": guests_number,
        "students_number": students_number,
        "minutes_number": minutes_number,
        "service_cost": service_cost
    }
    # print(f'service_cost_info={service_cost_info}')

    return json.dumps(service_cost_info)

if __name__ == '__main__':
    # params = {'guests_number': 20, 'minutes_number': 240, 'students_number': 20}
    # function_name = 'get_service_cost'
    # chosen_function = eval(function_name)
    # functionResult = chosen_function(**params)
    # print(functionResult)

    params = {'restaurant_name': 'Allo BEIRUT', 'dish_name': 'Machbous Lamb', 'dish_price': 59, 'dish_description': ''}
    function_name = 'get_dish'
    chosen_function = eval(function_name)
    functionResult = chosen_function(**params)
    print(functionResult)



