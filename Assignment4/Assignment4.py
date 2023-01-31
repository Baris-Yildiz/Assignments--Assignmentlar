import sys


def open_grid_file(file, player_name):
    """
    Reads the "board/grid" file of a player and stores the board/grid into the "hidden_grids" dictionary.
    Prototype of hidden_grids : keys = names of players, values = dictionaries that represent the player's board. The keys for this
    dictionary are coordinates (e.g. A1, H3) and values are "" if there is no part of a ship at that coordinate or the letter that represents the
    ship if there is a part of a ship there. Raises an AssertionError if any character other than C,B,S,D,P are encountered.
    """
    with open(file) as f:
        lines = f.readlines()
        line_count = len(lines)
        assert line_count == 10     # our boards have to be 10 x 10, if not, the program should kaBOOM.
        for line_index in range(line_count):
            line_contents = lines[line_index].rstrip("\n").split(";")   # contains every character in every row in the player's board.
            assert len(line_contents) == 10
            for square_index in range(len(line_contents)):
                assert line_contents[square_index] in ["B", "C", "S", "D", "P", ""]
                hidden_grids[player_name][f"{chr(65 + square_index)}{line_index + 1}"] = line_contents[square_index]    # initialize the "hidden_grids" dictionary


def get_hit_coordinates(file):
    """
    Reads the file that contains the move coordinates of a player and returns those coordinates as a list.
    """
    with open(file) as f:
        contents = f.read().rstrip(";")    # removes a trailing semicolon (;) if there is such a semicolon because it causes an empty string at the end to be interpreted as a move coordinate.
        coordinates = contents.split(";")
    return coordinates


def find_boat_coordinates(player_name, ship):
    """
    Attempts to get a list of coordinates for each part of the ship in the board of the player.
    For example, returns the coordinates of the ship "Carrier" for "Player1". This is done in this
    separate function instead of the read board function because of the different placements of Battleship and Patrol
    Boat. Also because there may be wrong placements of ships in the board file. If this function catches any
    exceptions, the game is stopped. (kaBOOM)
    """
    (boat_size, boat_count) = boats[ship]
    symbol = ship[0]    # symbol is the character that is representing the boat. e.g. C for Carrier.
    symbols_in_board = list(hidden_grids[player_name].values()).count(symbol)
    boats_found = 0
    individual_boats = []
    if ship in ["Battleship", "Patrol Boat"]:   # finds the coordinates of Battleships and Patrol Boats.
        with open(player_info[player_name]["Optional_File"]) as f:
            for line in f:
                if line[0] == symbol:
                    (origin, direction) = line.split(";")[0][3:], line.split(";")[1]
                    (row, column) = origin.split(",")
                    boat_coordinates = [f"{chr(ord(column) + (i * directions[direction][1]))}{int(row) + (i * directions[direction][0])}" for i in range(boat_size)]
                    for coordinate in boat_coordinates:
                        assert hidden_grids[player_name][coordinate] == symbol
                    boats_found += 1
                    individual_boats.append(boat_coordinates)
    else:   # finds the coordinates of other ships by calling vertical and horizontal lookup functions.
        boats_found = vertical_lookup(individual_boats, boat_size, symbol) + horizontal_lookup(individual_boats, boat_size, symbol)
    assert boats_found == boat_count and symbols_in_board == boats_found * boat_size    # checks if the given board is valid.
    return individual_boats


def vertical_lookup(individual_boats, boat_size, symbol):
    """
    A function used for searching for the boats Submarine, Destroyer and Carrier vertically.
    If a boat is found vertically, adds that boat's coordinates to the list individual_boats and lastly,
    returns the number of vertical placed boats it has found.
    """
    boats_found = 0
    for column_index in range(65, 75):
        column = chr(column_index)
        found_length = 0
        for row in range(1, 11):
            if hidden_grids[player][column+str(row)] == symbol:
                if found_length == boat_size - 1:
                    boat_coordinates = [f"{column}{row - index + 1}" for index in range(boat_size, 0, -1)]
                    individual_boats.append(boat_coordinates)
                    boats_found += 1
                    found_length = 0
                    continue
                found_length += 1
            elif found_length > 0:
                found_length = 0
    return boats_found


def horizontal_lookup(individual_boats, boat_size, symbol):
    """
    A function identical to vertical_lookup(), except it finds horizontal placed ships rather than vertical
    ones. Parameters are also identical to vertical_lookup().
    """
    boats_found = 0
    for row in range(1, 11):
        found_length = 0
        for column_index in range(65, 75):
            column = chr(column_index)
            if hidden_grids[player][column+str(row)] == symbol:
                if found_length == boat_size - 1:
                    boat_coordinates = [f"{chr(column_index - index + 1)}{row}" for index in range(boat_size, 0, -1)]
                    individual_boats.append(boat_coordinates)
                    boats_found += 1
                    found_length = 0
                    continue
                found_length += 1
            elif found_length > 0:
                found_length = 0
    return boats_found


def display_move(player_name, opponent_name, round_number, move):
    """
    This function returns : The player's name who is about to make a move, the coordinates of that move,
    the round number, players' boards just before this current move and the states of players' ships.
    """
    out = f"{player_name}'s Move\n\nRound : {round_number}\t\t\t\t\tGrid Size: 10x10\n\n" + display_player_grids() + f"Enter Your Move: {move}\n"
    potential_error_message = check_if_move_is_valid(player_name, move)
    while potential_error_message != "":    # if the current move is invalid, enters this loop which asks for another move until a valid move is given.
        del player_info[player_name]["Moves"][turn]
        move = player_info[player_name]["Moves"][turn]
        out += f"\n{potential_error_message}Enter Your Move: {move}\n"
        potential_error_message = check_if_move_is_valid(player_name, move)
    player_info[player_name]["Performed_Moves"].append(move)
    shoot_grid(opponent_name, move)
    player_info["Player1"]["Boat_State"], player_info["Player2"]["Boat_State"] = [boat_states[0], *boat_states[2:4], boat_states[6], boat_states[8], *boat_states[10:14]], [boat_states[1], *boat_states[4:6], boat_states[7], boat_states[9], *boat_states[14:]]
    return out


def display_player_grids(state="ongoing"):
    """
    Returns a string showing players' boards side by side. Unless the parameter "state" is given as final,
    the boards shown do not give away the positions of the ships, they only show the moves made/shots fired by the opponent.
    If "state" is given as final, shots and positions of boats are showcased.
    """
    if state == "final":    # changes the "hidden" board to show any unsunken ships.
        for player_name in players:
            ship_list = player_info[player_name]["Boats"]
            for ship_type in ship_list:
                for ship in ship_list[ship_type]:
                    for coordinate in ship:
                        symbol = hidden_grids[player_name][coordinate]
                        column, row = ord(coordinate[0])-65, int(coordinate[1:]) - 1
                        player_info[player_name]["Grid"][row][column] = symbol
        out = "Final Information\n\nPlayer1's Board\t\t\t\tPlayer2's Board\n  A B C D E F G H I J\t\t  A B C D E F G H I J\n"
    else:       # keeps the hidden board as is.
        out = f"Player1's Hidden Board\t\tPlayer2's Hidden Board\n  A B C D E F G H I J\t\t  A B C D E F G H I J\n"
    for (common_row, rows) in enumerate(zip(player_info["Player1"]["Grid"], player_info["Player2"]["Grid"])):   # prepares a string that shows rows, columns and squares in the board. In short, creates the board table.
        (player1_row, player2_row) = " ".join(rows[0]), " ".join(rows[1])
        common_row += 1
        space = "" if common_row == 10 else " "
        out += f"{common_row}{space}{player1_row}\t\t{common_row}{space}{player2_row}\n"
    out += """
Carrier		{}				Carrier		{}
Battleship	{} {}				Battleship	{} {}
Destroyer	{}				Destroyer	{}
Submarine	{}				Submarine	{}
Patrol Boat	{} {} {} {}			Patrol Boat	{} {} {} {}\n
""".format(*boat_states)    # this is the part that shows which ships have been sunk. Right side for player2, left for player1.
    return out


def check_if_move_is_valid(player_name, move):
    """
    This function is used to check if the move entered is valid. If it is not, an error message is returned.
    Otherwise, an empty string is returned. The returnee of this function is used in the function display_move().
    """
    try:
        count_of_commas = move.count(",")   # this portion looks at errors related with argument numbers/absence or multiplicity of provided rows and columns.
        assert count_of_commas != 0, f"IndexError: Coordinate '{move}' is missing a comma! Please try again."
        assert count_of_commas == 1, f"ValueError: Coordinate '{move}' has too many commas! There should only be 1 comma that separates the row and the column from each other. Please try again."
        (first_coordinate, second_coordinate) = move.split(",")
        assert move not in player_info[player_name]["Performed_Moves"], f"AssertionError: Invalid Operation."
        assert move != ",", f"IndexError: Coordinate '{move}' is missing a required row and column value! Please try again."
        assert first_coordinate != "", f"IndexError: Coordinate '{move}' is missing a required row value! Please try again."
        assert second_coordinate != "", f"IndexError: Coordinate '{move}' is missing a required column value! Please try again."
        message = ""
        # this portion looks at the correctness of provided rows and columns
        try:    # checking the row
            assert 49 <= ord(first_coordinate) <= 57    # checking if the row is among [1, 2, 3, 4, 5, 6, 7, 8, 9]
        except AssertionError:  # if not, error.
            message = f"ValueError: First operand of coordinate '{move}' is not an integer! Please try again."
        except TypeError:   # the code goes here if provided row is not a character. (if it consists of more than 1 character)
            if first_coordinate != "10":    # except for row = 10, all other possibilites should result in an error message
                try:
                    int_test = int(first_coordinate)    # testing if the input is an integer that has more than 1 digit.
                except ValueError:  # if not, it is a string that results in a value error.
                    message = f"ValueError: First operand of coordinate '{move}' is not an integer! Please try again."
                else:   # if it is, this is an "out of range" error.
                    message = "AssertionError: Invalid Operation."
        try:    # checking the column
            assert 65 <= ord(second_coordinate) <= 90   # checking if the column is an uppercase letter
        except (AssertionError, TypeError):     # if not, value error.
            message = f"ValueError: First and second operand of coordinate '{move}' is invalid! Please try again." if message else f"ValueError: Second operand of coordinate '{move}' is not an uppercase letter! Please try again."
        else:   # if it is, verify that it is not out of bounds.
            try:
                assert ord(second_coordinate) <= 74     # checking if the column is out of bounds
            except AssertionError:  # goes here if so
                message = "AssertionError: Invalid Operation."
        assert not message, f"{message}"    # if the message is not empty (if there is an error), raises an error with that message
    except AssertionError as error_message:
        return f"{str(error_message)}\n\n"
    return ""


def shoot_grid(player_name, move):
    """
    This function "shoots" a cell/square in a player's board (puts a "X" if there was a part of a ship there and "O" if not).
    """
    (row, column) = int(move.split(",")[0]), move.split(",")[1]
    target = hidden_grids[player_name][f"{column}{row}"]    # the content ("" or first letters of each ship type) of the targeted square.
    if target == "":    # miss
        player_info[player_name]["Grid"][row-1][ord(column) - 65] = "O"     # place "O"
    else:   # hit
        player_info[player_name]["Grid"][row-1][ord(column) - 65] = "X"     # place "X"
        shoot_boat(player_name, f"{column}{row}", target)


def shoot_boat(player_name, coordinates, ship):
    """
    Deletes the coordinate of the part of the boat that was sunken from a list that stores coordinates of all boats of a player.
    If there is no coordinate left for a boat after this operation, that means all parts of a certain boat were sunken.
    Therefore, an "X" is put on the part that shows the states of players' boats.
    """
    boat_list = player_info[player_name]["Boats"]
    for boat_coordinates in boat_list[ship]:
        if coordinates in boat_coordinates:
            del boat_coordinates[boat_coordinates.index(coordinates)]   # deletes the coordinate
            if len(boat_coordinates) == 0:  # if the ship was completely sunken after this shot
                boat_states[player_info[player_name]["Boat_Indexes"][ship]] = "X"
                player_info[player_name]["Boat_Indexes"][ship] += 1
            break


def endgame():
    """
    Checks if the game is over.
    """
    player1_lost, player2_lost = player_info["Player1"]["Boat_State"].count("-") == 0, player_info["Player2"]["Boat_State"].count("-") == 0
    if player1_lost and player2_lost:
        return "It is a Draw!\n\n"
    elif player1_lost or player2_lost:
        return "Player2 Wins!\n\n" if player1_lost else "Player1 Wins!\n\n"
    else:
        return ""


def write_file(content):
    """
    Writes and prints out the game.
    """
    with open("Battleship.out", "w", encoding="utf-8") as f:
        f.write(content)
    print(content)


try:
    player1_grid_file, player2_grid_file, player1_moves_file, player2_moves_file = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    player1_grid, player2_grid = [["-" for i in range(10)] for j in range(10)], [["-" for k in range(10)] for m in range(10)]           # initializes hidden/empty boards for players. These are the boards that the shots are recorded on and these boards initially show only "-" characters for each square.
    player1_boats, player2_boats = {}, {}                                                                                               # these store the coordinates of boats of players. e.g. player1_boats = {'C': [['G1', 'G2', 'G3', 'G4', 'G5']], 'B': [['B6', 'C6', 'D6', 'E6'], ['E2', 'E3', 'E4', 'E5']], ... }
    player1_boat_index, player2_boat_index = {"C": 0, "B": 2, "D": 6, "S": 8, "P": 10}, {"C": 1, "B": 4, "D": 7, "S": 9, "P": 14}       # this dictionary stores the indexes to place "X" on the "boat_states" variable whenever a certain player's ship gets sunk.
    boat_states = ["-" for g in range(18)]                                                                                              # initially consits of 18 "-" characters. Used to format the string that shows boat states for each turn.
    hidden_grids = {"Player1": {}, "Player2": {}}                                                                                       # the "hidden_grids" dictionary that was mentioned previously. It maps players to another dictionary that maps coordinates to contents of the coordinate in the board.
    boats = {"Carrier": [5, 1], "Battleship": [4, 2], "Destroyer": [3, 1], "Submarine": [3, 1], "Patrol Boat": [2, 4]}                  # stores boat types and their specifications as a list. the first element of this list is the size and the second element is the count.

    directions = {"right": (0, 1), "down": (1, 0)}                                                                                      # stores directions that are used in finding Battleships and Patrol Boats by the help of Optional text files.
    player_info = {"Player1": {"Grid": player1_grid, "Boats": player1_boats, "Boat_Indexes": player1_boat_index, "Grid_File": player1_grid_file, "Moves": [], "Moves_File": player1_moves_file, "Optional_File": "OptionalPlayer1.txt", "Performed_Moves": []}, "Player2": {"Grid": player2_grid, "Boats": player2_boats, "Boat_Indexes": player2_boat_index, "Grid_File": player2_grid_file, "Moves": [], "Moves_File": player2_moves_file, "Optional_File": "OptionalPlayer2.txt", "Performed_Moves": []}}  # stores every list or variable associated with a player
    players = ["Player1", "Player2"]
    bad_files = []                                                      # stores any potentially unreachable file.
    for player in players:
        try:
            open_grid_file(player_info[player]["Grid_File"], player)    # reads the board file of players.
        except IOError:                                                 # IOError handling
            bad_files.append(player_info[player]["Grid_File"])          # if any file is unreachable, appends it to the bad_files list.

        try:
            player_info[player]["Moves"] = get_hit_coordinates(player_info[player]["Moves_File"])   # gets the moves for players
        except IOError:
            bad_files.append(player_info[player]["Moves_File"])         # if any file is unreachable, appends it to the bad_files list.

    if bad_files:   # if one or more files provided are unreachable, prints a proper error message.
        if len(bad_files) == 1:
            raise IOError(f"IOError: input file {bad_files[0]} is not reachable.")
        else:
            bad_file_names = ", ".join(bad_files)
            raise IOError(f"IOError: input files {bad_file_names} are not reachable.")

    for player in players:
        for boat in boats:                  # gets the ship coordinates for each player, also checks whether the boat placements are valid.
            boat_symbol = boat[0]
            player_info[player]["Boats"][f"{boat_symbol}"] = find_boat_coordinates(player, boat)

    turn = 0
    output = "Battle of Ships Game\n\n"             # "output" stores the whole game.
    while True:                                     # while the game is going
        try:                                        # calculates results for each round
            for player_index in range(1, 3):
                player = f"Player{player_index}"
                opponent = f"Player{(player_index % 2) + 1}"
                output += display_move(player, opponent, turn + 1, player_info[player]["Moves"][turn]) + "\n"
            end_message = endgame()             # checks if the game is over after each round.
            if end_message != "":               # if the game is over, goes here and breaks the loop
                output += end_message
                break
            turn += 1
        except IndexError:     # this except block is mainly used for ending the game if players run out of moves, but no player has lost yet. (if there is such a case).
            break              # changed from except to except IndexError.
    output += display_player_grids("final")
    write_file(output)
except IOError as error:
    write_file(str(error))
except:                 # in case of any missed errors.
    write_file("kaBOOM: run for your life!")
