import sys
file_name = sys.argv[1]
category_names = dict()
category_seats = dict()
tickets = {"student": "S", "full": "F", "season": "T"}


def create_category():  # creates a category
    category = line_contents[1]  # this is the name of the category
    if category not in category_names:
        (rows, columns) = [int(dimension) for dimension in line_contents[2].split("x")]   # gets the number of rows and columns of the category and stores them in variables
        category_names[category] = (rows, columns)   # stores the category with its size into a dictionary.
        category_seats[category] = {chr(row)+str(column): "X" for row in range(64+rows, 64, -1) for column in range(0, columns)}    # initializes all seats in the category and represents them as dictionary values.
        message = f"The category '{category}' having {rows*columns} seats has been created\n"
    else:
        message = f"Warning: Cannot create the category for the second time. The staduim has already {category}\n"
    return message


def sell_ticket():  # attempts to sell tickets to customers
    (customer, ticket, category, seats) = (line_contents[1], line_contents[2], line_contents[3], line_contents[4:])
    messages = ""
    for seat in seats:
        seat_row = seat[0]
        seat_columns = [int(column) for column in seat[1:].split("-")]
        max_seat_column = seat_columns[0] if "-" not in seat else seat_columns[1]
        if row_exception(category, seat_row) or column_exception(category, max_seat_column):    # if rows or columns exceed the boundary
            messages += boundary_error_message(category, seat_row, max_seat_column, seat)
        elif "-" in seat:       # if it is a seat range
            seat_start = seat_columns[0]
            for column in range(seat_start, max_seat_column+1):      # check each seat in range for availability
                if not seat_is_empty(category, seat_row+str(column)):
                    messages += f"Warning: The seats {seat} cannot be sold to {customer} due some of them have already been sold\n"
                    break
                if column == max_seat_column:        # if every seat is available
                    for seat_col in range(seat_start, max_seat_column+1):
                        buy_seat(category, seat_row+str(seat_col), tickets[ticket])
                    messages += f"Success: {customer} has bought {seat} at {category}\n"
        else:       # if it is a single seat
            if seat_is_empty(category, seat):
                messages += f"Success: {customer} has bought {seat} at {category}\n"
                buy_seat(category, seat, tickets[ticket])
            else:
                messages += f"Warning: The seat {seat} cannot be sold to {customer} since it was already sold!\n"
    return messages


def row_exception(category, row):
    return row > chr(64 + category_names[category][0])  # true if given row is outside the boundaries


def column_exception(category, column):
    return column > (category_names[category][1]-1)  # true if given column is outside the boundaries


def boundary_error_message(category, row, column, seat):    # gives the appropriate error message when rows or columns exceed the boundary
    if row_exception(category, row) and column_exception(category, column):
        return f"Error: The category '{category}' has less row and column than the specified index {seat}!\n"
    elif row_exception(category, row) or column_exception(category, column):
        dimension = "row" if row_exception(category, row) else "column"
        return f"Error: The category '{category}' has less {dimension} than the specified index {seat}!\n"


def seat_is_empty(category, seat):      # returns True or False depending on whether the seat is taken or not
    return category_seats[category][seat] == "X"


def buy_seat(category, seat, ticket):       # buys the seat by changing the proper seat's dictionary value to ticket type
    category_seats[category][seat] = ticket


def cancel_ticket():    # attempts to cancel a ticket
    category, seats = line_contents[1], line_contents[2:]
    messages = ""
    for seat in seats:
        seat_row = seat[0]
        seat_column = int(seat[1:])
        if row_exception(category, seat_row) or column_exception(category, seat_column):    # checks if rows or columns exceed the boundaries of the category
            messages += boundary_error_message(category, seat_row, seat_column, seat)
        else:
            if not seat_is_empty(category, seat):
                category_seats[category][seat] = "X"  # cancels the ticket on the seat
                messages += f"Success: The seat {seat} at '{category}' has been canceled and now ready to sell again\n"
            else:
                messages += f"Error: The seat {seat} at '{category}' has already been free! Nothing to cancel\n"
    return messages


def show_category():    # displays all seats of a category.
    category = line_contents[1]
    table = f"Printing category layout of {category}"
    (columns, count) = (category_names[category][1], 0)
    for seat in category_seats[category]:                   # creates the table that displays every seat in the category
        if count % columns == 0:
            table += f"\n{seat[0]} "
        table += f"{category_seats[category][seat]}  "
        count += 1
    table += "\n  {}\n".format(("".join([str(i)+" "*(2 if i < 9 else 1) for i in range(0, int(category_names[category][1]))])))  # add the column numbers on the bottom of the table
    return table


def balance():  # calculates and returns the total revenue of a category.
    category = line_contents[1]
    ticket_amounts = {"S": 0, "F": 0, "T": 0}   # shows how many of each ticket has been bought for the category
    for seat in category_seats[category]:     # go through tickets of every seat
        ticket = category_seats[category][seat]
        if ticket in ticket_amounts:        # counting algorithm with dictionary
            ticket_amounts[ticket] += 1
        else:
            ticket_amounts[ticket] = 1
    (student_pay, full_pay, season_pay) = (ticket_amounts["S"], ticket_amounts["F"], ticket_amounts["T"])
    message = f"category report of '{category}'\n" + "--------------------------------\n" + f"Sum of students = {student_pay}, Sum of full pay = {full_pay}, Sum of season ticket = {season_pay}, and Revenues = {student_pay*10 + full_pay*20 + season_pay*250} Dollars\n"
    return message


functions = {"CREATECATEGORY": create_category, "SELLTICKET": sell_ticket, "CANCELTICKET": cancel_ticket, "SHOWCATEGORY": show_category, "BALANCE": balance}    # associates command strings with functions
output = ""

with open(file_name) as input_file:  # scans the input file
    for line in input_file:
        line_contents = line.split()    # line_contents stores the command and every argument. line_contents[0] stores the command in each line.
        output += functions[line_contents[0]]()     # calls a function based on the command

with open("output.txt", "w") as output_file:    # opens an output file to write the output
    output_file.write(output)
    print(output)
