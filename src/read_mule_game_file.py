import sys
import json


def read_mule_game_file(file_path: str) -> dict:
	try:
		with open(file_path, 'r') as file:
			data = json.load(file)
		return data
	except FileNotFoundError:
		print(f"Error: File '{file_path}' not found.")
	except json.JSONDecodeError:
		print(f"Error: Invalid JSON format in file '{file_path}'.")
	
	return None


def process_mule_game_data(mule_game_data: dict):
	print("Client Version: %s" % (mule_game_data["version"]["client"]))

	print("Game Name: %s" % (mule_game_data["name"]))

	# Settings data
	settings_data: dict[str] = mule_game_data["settings"]
	print("Play Level: %d" % (settings_data["playLevel"]))
	print("Human Player Count: %d" % (settings_data["numberOfHumanPlayers"]))

	# Player data
	player_data: dict[str] = mule_game_data["player"]
	players_data: list[dict[str]] = player_data["players"]
	for player_index in range(len(players_data)):
		current_player_data: dict[str] = players_data[player_index]
		input_type: int = current_player_data["inputType"]
		computer_player_suffix = " (Computer)" if input_type == 255 else ""

		color_id: int = current_player_data["colorId"]
		species_id: int = current_player_data["speciesId"]

		money_amount: int = current_player_data["moneyAmount"]

		print("Player %d%s:" % (player_index, computer_player_suffix))
		#print(" - Type: %d" % (input_type))
		print(" - Color: %d" % (color_id))
		print(" - Species: %d" % (species_id))
		print(" - Money: %d" % (money_amount))

		print(" - Goods:")
		good_amounts: list[int] = current_player_data["goodAmounts"]
		for good_type in range(len(good_amounts)):
			good_amount = good_amounts[good_type]
			print("   - %d: %d" % (good_type, good_amount))
	
	# Game round status summaries
	print("Rounds:")		
	
	history_data: dict[str] = mule_game_data["history"]
	rounds_data: list[dict[str]] = history_data["rounds"]
	for round_number in range(len(rounds_data)):
		round_data: dict[str] = rounds_data[round_number]
		
		status_screen_data: list[dict[str]] = None
		screen_events_data: list[dict[str]] = None

		screens_data: list[dict[str]] = round_data["screens"]
		for screen_data in screens_data:
			screen_events_data = screen_data.get("0")
			is_status_screen_data: bool = (screen_events_data != None)
			if is_status_screen_data:
				status_screen_data = screen_data
				break

		if status_screen_data != None:
			for screen_event_data in screen_events_data:
				screen_event_id: int = screen_event_data["id"]
				print(" - Status #%d:" % (round_number))

				screen_event_parameters: list[int] = screen_event_data["parameters"]

				colony_score = 0

				for player_index in range(4):
					print("   - Player #%d:" % (player_index))

					score_event_parameter_player_offset_index = player_index * 3
					score_money = screen_event_parameters[score_event_parameter_player_offset_index + 0]
					score_land = screen_event_parameters[score_event_parameter_player_offset_index + 1]
					score_goods = screen_event_parameters[score_event_parameter_player_offset_index + 2]

					print("     - Score")
					print("       - Money: %d" % (score_money))
					print("       - Land:  %d" % (score_land))
					print("       - Goods: %d" % (score_goods))

					colony_score += score_money + score_land + score_goods

					player_rank: int = screen_event_parameters[13 + player_index]
					print("     - Rank: %d" % (player_rank))
				
				print("   - Colony Score: %d" % (colony_score))
				colony_score_rating: int = screen_event_parameters[12]
				print("   - Colony Score Rating: %d" % (colony_score_rating))


# Example usage:
# python read_mule_game_file.py path/to/1234.mulegame

if __name__ == "__main__":
	# Check if a command-line argument is provided
	if len(sys.argv) != 2:
		print("Usage: python read_mule_game_file.py <mule_game_file_path>")
		sys.exit(1)

	input_file_path = sys.argv[1]
	
	mule_game_data = read_mule_game_file(input_file_path)
	if mule_game_data == None:
		sys.exit(1)
	
	print("MULE game loaded successfully")

	process_mule_game_data(mule_game_data)
