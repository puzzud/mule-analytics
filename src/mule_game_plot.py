# mule_game_plot.py
# imports a M.U.L.E. game file and makes two graphs:
# 1) total wealth (money + land + goods) month by month plus monthly events color-coded by player
# 2) per-player summary graphs (total, money, land and goods) and individual player turn events

import json
import sys
import matplotlib.pyplot as plt
import numpy as np

# array for storing total values by month
scores = [[0 for i in range(13)] for j in range(4)]

money = [[0 for i in range(13)] for j in range(4)]
goods = [[0 for i in range(13)] for j in range(4)]
land = [[0 for i in range(13)] for j in range(4)]

species = ['Mechtron', 'Gollumer', 'Packer', 'Bonzoid', 'Spheroid', 'Flapper', 'Leggite', 'Humanoid']

# player_colors is list that really contains only 4 colors, but due to C64 indexing requires 9 values
player_colors = ['', '', '', '', 'magenta', 'green', 'blue', '', 'red']

# empty lists for colors and names (indexed to player). Probably a more elegant way to do this...
player_color = ['', '', '', '']
player_name = ['', '', '', '']
player_species = ['', '', '', '']

# list of possible monthly events
month_events = ['Pest attack', 'Pirate ship', 'Acid rain storm', 'Planetquake', 'Sunspot activity',
				  'Meteorite strike', 'Radiation - M.U.L.E. goes crazy', 'Fire in the store']

turn_events = []
txt = []

turn_events_list = ['YOU JUST RECEIVED A PACKAGE FROM YOUR HOME-WORLD RELATIVES CONTAINING 3 FOOD AND 2 ENERGY UNITS.',
			   'A WANDERING SPACE TRAVELER REPAID YOUR HOSPITALITY BY LEAVING TWO BARS OF SMITHORE.',
			   'MISCHIEVOUS GLAC-ELVES BROKE INTO YOUR STORAGE SHED AND STOLE HALF YOUR FOOD.',
			   'YOUR MULE WAS JUDGED "BEST BUILT" AT THE COLONY FAIR. YOU WON ${0}.',
			   'ONE OF YOUR MULES LOST A BOLT. REPAIRS COST YOU ${0}.',
			   'YOUR MULE WON THE COLONY TAP-DANCING CONTEST. YOU COLLECTED ${0}.',
			   'YOUR MINING MULES HAVE DETERIORATED FROM HEAVY USE AND COST ${0} EACH TO REPAIR. THE TOTAL COST IS ${1}.',
			   'THE SOLAR COLLECTORS ON YOUR ENERGY MULES ARE DIRTY. CLEANING COST YOU ${0} EACH FOR A TOTAL OF ${1}.',
			   'THE COLONY COUNCIL FOR AGRICULTURE AWARDED YOU ${0} FOR EACH FOOD PLOT YOU HAVE DEVELOPED. THE TOTAL GRANT IS ${1}.',
			   'THE COLONY AWARDED YOU #1 FOR STOPPING THE WART WORM INFESTATION.',
			   'THE MUSEUM BOUGHT YOUR ANTIQUE PERSONAL COMPUTER FOR ${0}.',
			   'YOU WON THE COLONY SWAMP EEL EATING CONTEST AND COLLECTED ${0}. (YUCK!).',
			   'A CHARITY FROM YOUR HOME-WORLD TOOK PITY ON YOU AND SENT ${0}.',
			   'YOUR OFFWORLD INVESTMENTS IN ARTIFICIAL DUMBNESS PAID ${0} IN DIVIDENDS.',
			   'A DISTANT RELATIVE DIED AND LEFT YOU A VAST FORTUNE. BUT AFTER TAXES YOU ONLY GOT ${0}.',
			   'YOU FOUND A DEAD MOOSE RAT AND SOLD THE HIDE FOR ${0}.',
			   'YOUR SPACE GYPSY INLAWS MADE A MESS OF THE TOWN. IT COST YOU ${0} TO CLEAN IT UP,',
			   'FLYING CAT-BUGS ATE THE ROOF OFF YOUR HOUSE. REPAIRS COST ${0}.',
			   'YOU LOST #1 BETTING ON THE TWO-LEGGED KAZINGA RACES.',
			   'YOUR CHILD WAS BITTEN BY A BAT LIZARD AND THE HOSPITAL BILL COST YOU ${0}.',
			   'YOU LOST A PLOT OF LAND BECAUSE THE CLAIM WAS NOT RECORDED.',
			   'YOU RECEIVED AN EXTRA PLOT OF LAND TO ENCOURAGE COLONY DEVELOPMENT.']

# initial values on month 0
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
			player_species[player_index] = "Mechtron"
		else:
			player_name[player_index] = input("Who was playing the " + player_color[player_index] + " " + species[species_id]+ "? ")
			player_species[player_index] = species[species_id]

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

					money[player_index][round_number] = score_money
					land[player_index][round_number] = score_land
					goods[player_index][round_number] = score_goods

					scores[player_index][round_number] = player_total

					player_rank: int = screen_event_parameters[13 + player_index]

		if status_month_data != None:
			for month_event_data in month_events_data:
				month_event_id: int = month_event_data["id"]

				month_event_parameters: list[int] = month_event_data["parameters"]

				if month_event_id == 215:
					# here need to decide number of parameters so we can figure out which format to use
					if len(month_event_parameters) == 2:
						name_param = player_name[month_event_parameters[1]]
						event_name_param = turn_events_list[month_event_parameters[0]]
						turn_event = name_param + ': In month ' + str(round_number) + ', ' + event_name_param
						turn_events.append(month_event_parameters[1])
						turn_events.append(round_number)
						turn_events.append(turn_event)

					elif len(month_event_parameters) == 3:
						name_param = player_name[month_event_parameters[2]]
						event_name_param = turn_events_list[month_event_parameters[0]]
						money1 = str(month_event_parameters[1])
						turn_event = name_param + ': In month ' + str(round_number) + ', ' + event_name_param.format(money1)
						turn_events.append(month_event_parameters[2])
						turn_events.append(round_number)
						turn_events.append(turn_event)

					elif len(month_event_parameters) == 4:
						name_param = player_name[month_event_parameters[3]]
						event_name_param = turn_events_list[month_event_parameters[0]]
						money1 = str(month_event_parameters[1])
						money2 = str(month_event_parameters[2])
						turn_event = name_param + ': In month ' + str(round_number) + ', ' + event_name_param.format(money1, money2)
						turn_events.append(month_event_parameters[3])
						turn_events.append(round_number)
						turn_events.append(turn_event)

				elif month_event_id == 290:
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
						break



def plot_mule_game_data():
	# Create plot using matplotlib package

	month_event.append('The ship has returned!')
	event_label_colors.append('gray')

	fig, ax = plt.subplots(figsize=(10, 8))
	plt.subplots_adjust(bottom=0.3)
	for player_graph in range(4):
		ax.plot(scores[player_graph], player_color[player_graph], marker='.', label=player_name[player_graph])

	ax.legend(player_name)
	ax.set_ylabel("Total Wealth")
	ax.tick_params(axis='x', labelrotation = 80)
	ax.set_xticks(np.arange(0, 13, 1), month_event)
	for i in range(13):
		ax.get_xticklabels()[i].set_color(event_label_colors[i])

	ax.set_title(mule_game_data["name"])
	plt.show()

def plot_mule_round_data():
	# Plot individual round data for each player

	fig, ax = plt.subplots(2,2, sharey=True, figsize=(10, 10))
	for player_graph in range(4):
		xindex = int(player_graph/2)
		yindex = player_graph-xindex
		if yindex == 2:
			yindex = 0
		ax[xindex, yindex].plot(scores[player_graph], player_color[player_graph], alpha=0.6, marker='|', label='total')
		ax[xindex, yindex].plot(money[player_graph], player_color[player_graph], alpha=1.0, label='money')
		ax[xindex, yindex].plot(land[player_graph], player_color[player_graph], alpha=0.4, label='land')
		ax[xindex, yindex].plot(goods[player_graph], player_color[player_graph], alpha=0.3, label='goods', ls='--')
		ax[xindex, yindex].set_xticks(np.arange(0, 13, 1))
		ax[xindex, yindex].legend(loc='upper left')
		ax[xindex, yindex].set_title(player_name[player_graph]+" ("+player_color[player_graph]+" "+player_species[player_graph]+")", color=player_color[player_graph])

		for i in range(0, len(turn_events), 3):
			txt1 = []
			if turn_events[i] == player_graph:
				ax[xindex, yindex].axvline(x=turn_events[i+1], color='gray', ls=':', alpha=0.5)
				txt1.append(turn_events[i+2])
				txt = '\n'.join(txt1)
				print(txt)

	plt.show()

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
	plot_mule_game_data()
	plot_mule_round_data()


