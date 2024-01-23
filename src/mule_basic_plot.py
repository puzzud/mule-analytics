# mule_basic_plot.py
# imports a M.U.L.E. game file and plots out total wealth (money + land + goods) month by month
#

import json
import sys
import matplotlib.pyplot as plt
import numpy as np

# array for storing total values by month
scores = [[0 for i in range(13)] for j in range(4)]

player_species = ['Mechtron', 'Gollumer', 'Packer', 'Bonzoid', 'Spheroid', 'Flapper', 'Leggite', 'Humanoid']

# player_colors is list that really contains only 4 colors, but due to C64 indexing requires 9 values

player_colors = ['', '', '', '', 'magenta', 'green', 'blue', '', 'red']

# empty lists for colors and names (indexed to player). Probably a more elegant way to do this...
player_color = ['', '', '', '']
player_name = ['', '', '', '']

# list of possible monthly events

month_events = ['Pest attack', 'Pirate ship', 'Acid rain storm', 'Planetquake', 'Sunspot activity',
				  'Meteorite strike', 'Radiation - M.U.L.E. goes crazy', 'Fire in the store']

month_event = ['Landing on the planet Irata']
event_label_colors = ['gray']

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

	# Player data
	player_data: dict[str] = mule_game_data["player"]
	players_data: list[dict[str]] = player_data["players"]
	for player_index in range(len(players_data)):
		current_player_data: dict[str] = players_data[player_index]
		input_type: int = current_player_data["inputType"]

		color_id: int = current_player_data["colorId"]
		species_id: int = current_player_data["speciesId"]

		player_color[player_index] = player_colors[color_id]

		if input_type == 255:
			player_name[player_index] = "Computer"
		else:
			player_name[player_index] = input("Who was playing the " + player_color[player_index] + " " + player_species[species_id]+ "? ")

		good_amounts: list[int] = current_player_data["goodAmounts"]
		for good_type in range(len(good_amounts)):
			good_amount = good_amounts[good_type]
	
	# Game round status summaries
	
	history_data: dict[str] = mule_game_data["history"]
	rounds_data: list[dict[str]] = history_data["rounds"]
	for round_number in range(len(rounds_data)):
		round_data: dict[str] = rounds_data[round_number]
		
		status_screen_data: list[dict[str]] = None
		screen_events_data: list[dict[str]] = None

		status_month_data: list[dict[str]] = None
		month_events_data: list[dict[str]] = None

		screens_data: list[dict[str]] = round_data["screens"]
		for screen_data in screens_data:
			screen_events_data = screen_data.get("0")
			is_status_screen_data: bool = (screen_events_data != None)
			if is_status_screen_data:
				status_screen_data = screen_data
				break

		for screen_data in screens_data:
			month_events_data = screen_data.get("2")
			is_status_month_data: bool = (month_events_data != None)
			if is_status_month_data:
				status_month_data = screen_data
				break


		if status_screen_data != None:
			for screen_event_data in screen_events_data:
				screen_event_id: int = screen_event_data["id"]

				screen_event_parameters: list[int] = screen_event_data["parameters"]

				for player_index in range(4):

					score_event_parameter_player_offset_index = player_index * 3
					score_money = screen_event_parameters[score_event_parameter_player_offset_index + 0]
					score_land = screen_event_parameters[score_event_parameter_player_offset_index + 1]
					score_goods = screen_event_parameters[score_event_parameter_player_offset_index + 2]

					player_total = score_goods + score_land + score_money

					scores[player_index][round_number] = player_total

					player_rank: int = screen_event_parameters[13 + player_index]

		if status_month_data != None:
			for month_event_data in month_events_data:
				month_event_id: int = month_event_data["id"]

				month_event_parameters: list[int] = month_event_data["parameters"]

				if month_event_id == 290:
					month_event.append(month_events[month_event_parameters[0]])

		# the three player-specific events below assume that the player with the plot at the end of the game
		# is the same one who had the plot at the time of the event.

					# for pest attack, decide which player got nailed, set color for "pest attack" axis label
					if month_event_parameters[0] == 0:
						for player_index in range(len(players_data)):
							current_player_data: dict[str] = players_data[player_index]
							owned_plots: list[dict[str]] = current_player_data["ownedPlotTypes"]

							if str(month_event_parameters[1]) in owned_plots:
								event_label_colors.append(player_color[player_index])

					# for "M.U.L.E. goes crazy," decide which poor player lost their M.U.L.E., set label color
					elif month_event_parameters[0] == 6:
						for player_index in range(len(players_data)):
							current_player_data: dict[str] = players_data[player_index]
							owned_plots: list[dict[str]] = current_player_data["ownedPlotTypes"]

							if str(month_event_parameters[1]) in owned_plots:
								event_label_colors.append(player_color[player_index])

					# for meteorite strike, decide which lucky/unlucky player ends up with this plot, set label color
					elif month_event_parameters[0] == 5:
						for player_index in range(len(players_data)):
							current_player_data: dict[str] = players_data[player_index]
							owned_plots: list[dict[str]] = current_player_data["ownedPlotTypes"]

							if str(month_event_parameters[1]) in owned_plots:
								event_label_colors.append(player_color[player_index])

					else:
						event_label_colors.append('black')


# Example usage:
# python mule_basic_plot.py path/to/1234.mulegame

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

	month_event.append('The ship has returned!')
	event_label_colors.append('gray')

	# Create plot using matplotlib package
	fig, ax = plt.subplots(figsize=(10, 6))
	plt.subplots_adjust(bottom=0.4)
	for player_plot in range(4):
		ax.plot(scores[player_plot], player_color[player_plot], marker='o', label=player_name[player_plot])
	ax.legend(player_name)
	ax.set_ylabel("Total Wealth")
	ax.tick_params(axis='x', labelrotation = 80)
	ax.set_xticks(np.arange(0, 13, 1), month_event)
	for i in range(13):
		ax.get_xticklabels()[i].set_color(event_label_colors[i])
	plt.show()
