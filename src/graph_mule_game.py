# graph_mule_game.py
# imports a M.U.L.E. game file and makes two graphs:
# 1) total wealth (money + land + goods) month by month plus monthly events color-coded by player
# 2) per-player summary graphs (total, money, land and goods) and individual player turn events

import copy
import sys
import matplotlib.pyplot as plt
import matplotlib.text as mtext
import numpy as np

import mule

species = ['Mechtron', 'Gollumer', 'Packer', 'Bonzoid', 'Spheroid', 'Flapper', 'Leggite', 'Humanoid']

scores = [[0 for i in range(13)] for j in range(4)]

money = [[0 for i in range(13)] for j in range(4)]
goods = [[0 for i in range(13)] for j in range(4)]
land = [[0 for i in range(13)] for j in range(4)]

player_name = []
player_species = []
player_color = []

# player_colors is list that really contains only 4 colors, but due to C64 indexing requires 9 values
player_colors = ['', '', '', '', 'magenta', 'green', 'blue', '', 'red']

month_events = ['Pest attack', 'Pirate ship', 'Acid rain storm', 'Planetquake', 'Sunspot activity',
				'Meteorite strike', 'Radiation - M.U.L.E. goes crazy', 'Fire in the store']

turn_events_list = ['YOU JUST RECEIVED A PACKAGE FROM YOUR HOME-WORLD RELATIVES CONTAINING 3 FOOD AND 2 ENERGY UNITS.',
					'A WANDERING SPACE TRAVELER REPAID YOUR HOSPITALITY BY LEAVING TWO BARS OF SMITHORE.',
					'MISCHIEVOUS GLAC-ELVES BROKE INTO YOUR STORAGE SHED AND STOLE HALF YOUR FOOD.',
					'YOUR MULE WAS JUDGED "BEST BUILT" AT THE COLONY FAIR. YOU WON \\${0}.',
					'ONE OF YOUR MULES LOST A BOLT. REPAIRS COST YOU \\${0}.',
					'YOUR MULE WON THE COLONY TAP-DANCING CONTEST. YOU COLLECTED ${0}.',
					'YOUR MINING MULES HAVE DETERIORATED FROM HEAVY USE AND COST \\${0} EACH TO REPAIR. THE TOTAL COST IS \\${1}.',
					'THE SOLAR COLLECTORS ON YOUR ENERGY MULES ARE DIRTY. CLEANING COST YOU \\${0} EACH FOR A TOTAL OF \\${1}.',
					'THE COLONY COUNCIL FOR AGRICULTURE AWARDED YOU \\${0} FOR EACH FOOD PLOT YOU HAVE DEVELOPED. THE TOTAL GRANT IS \\${1}.',
					'THE COLONY AWARDED YOU \\${0} FOR STOPPING THE WART WORM INFESTATION.',
					'THE MUSEUM BOUGHT YOUR ANTIQUE PERSONAL COMPUTER FOR \\${0}.',
					'YOU WON THE COLONY SWAMP EEL EATING CONTEST AND COLLECTED \\${0}. (YUCK!).',
					'A CHARITY FROM YOUR HOME-WORLD TOOK PITY ON YOU AND SENT \\${0}.',
					'YOUR OFFWORLD INVESTMENTS IN ARTIFICIAL DUMBNESS PAID \\${0} IN DIVIDENDS.',
					'A DISTANT RELATIVE DIED AND LEFT YOU A VAST FORTUNE. BUT AFTER TAXES YOU ONLY GOT \\${0}.',
					'YOU FOUND A DEAD MOOSE RAT AND SOLD THE HIDE FOR \\${0}.',
					'YOUR SPACE GYPSY INLAWS MADE A MESS OF THE TOWN. IT COST YOU \\${0} TO CLEAN IT UP,',
					'FLYING CAT-BUGS ATE THE ROOF OFF YOUR HOUSE. REPAIRS COST \\${0}.',
					'YOU LOST \\${0} BETTING ON THE TWO-LEGGED KAZINGA RACES.',
					'YOUR CHILD WAS BITTEN BY A BAT LIZARD AND THE HOSPITAL BILL COST YOU \\${0}.',
					'YOU LOST A PLOT OF LAND BECAUSE THE CLAIM WAS NOT RECORDED.',
					'YOU RECEIVED AN EXTRA PLOT OF LAND TO ENCOURAGE COLONY DEVELOPMENT.']

commodity_names = ['Food', 'Energy', 'Smithore', 'Crystite']
month_event = []
event_label_colors = []
turn_events = []

class WrapText(mtext.Text):
	"""
	WrapText(x, y, s, width, widthcoords, **kwargs)
	x, y       : position (default transData)
	text       : string
	width      : box width
	widthcoords: coordinate system (default screen pixels)
	**kwargs   : sent to matplotlib.text.Text
	Return     : matplotlib.text.Text artist
	"""

	def __init__(self,
				 x=0, y=0, text='',
				 width=0,
				 widthcoords=None,
				 **kwargs):
		mtext.Text.__init__(self,
							x=x, y=y, text=text,
							wrap=True,
							clip_on=False,
							**kwargs)
		if not widthcoords:
			self.width = width
		else:
			a = widthcoords.transform_point([(0, 0), (width, 0)])
			self.width = a[1][0] - a[0][0]

	def _get_wrap_line_width(self):
		return self.width


def process_round_event(round_event, game_state):
	if round_event['id'] == mule.GameHistoryEventId.GAME_HISTORY_EVENT_ID_ROUND_EVENT.value:
		event = month_events[round_event['parameters'][0]]

		if round_event['parameters'][0] in [mule.RoundEventId.ROUND_EVENT_ID_PEST_ATTACK.value,
											mule.RoundEventId.ROUND_EVENT_ID_METEORITE_STRIKE.value,
											mule.RoundEventId.ROUND_EVENT_ID_RADIATION.value]:

			# determine who the plot belonged to, and return color-coded event
			plot = round_event['parameters'][1]
			owner = game_state.get_plot_owner(plot)
			return event, owner

		else:  # just return the event with its default color
			return event, 'black'

def process_turn_event(turn_event):
	if turn_event['id'] == mule.GameHistoryEventId.GAME_HISTORY_EVENT_ID_TURN_EVENT.value:

		# Here need to decide number of parameters so we can figure out which format to use
		if len(turn_event['parameters']) == 2:
			event = turn_events_list[turn_event['parameters'][0]]

		elif len(turn_event['parameters']) == 3:
			money1 = str(turn_event['parameters'][1])
			event = turn_events_list[turn_event['parameters'][0]].format(money1)

		elif len(turn_event['parameters']) == 4:
			money1 = str(turn_event['parameters'][1])
			money2 = str(turn_event['parameters'][2])
			event = turn_events_list[turn_event['parameters'][0]].format(money1, money2)

		return event

def process_mule_game_history(mule_game_history: mule.GameHistory) -> None:
	print("Client Version: %s" % mule_game_history.client_version)

	print("Game Name: %s" % mule_game_history.game_name)

	#	player_name[]
	#	player_species[]
	#	player_color[]

	# Player info
	for player_index in range(mule.MAX_NUMBER_OF_PLAYERS):

		player_color.append(player_colors[mule_game_history.get_player_color_id(player_index)])
		player_species.append(species[mule_game_history.get_player_species_id(player_index)])

		input_type = mule_game_history.get_player_input_type(player_index)
		if input_type == mule.PLAYER_INPUT_TYPE_COMPUTER:
			player_name.append("Computer")
			player_species[player_index] = "Mechtron"
		else:
			player_name.append(
				input("Who was playing the " + player_color[player_index] + " " + player_species[player_index] + "? "))

	# Game round status summaries
	mule_game_history.set_round_number(mule_game_history.get_number_of_rounds() - 1)
	mule_game_history.process_round_screen_events()

	# Make sure we use the end game state to decide which player experienced which event
	last_round_game_state = copy.deepcopy(mule_game_history.game_state)

	for round_number in range(mule_game_history.get_number_of_rounds()):

		mule_game_history.set_round_number(round_number)
		mule_game_history.process_round_screen_events()

		round_event_data = mule_game_history.get_round_event_data()
		if round_event_data is not None:

			# Get text description of each event, and color of player it happened to (for the 3 player-specific events)
			round_event, event_color = process_round_event(round_event_data, last_round_game_state)
			month_event.append(round_event)

			if event_color == 'black':
				event_label_colors.append(event_color)
			else:
				event_label_colors.append(player_color[event_color])

		for player_index in range(mule.MAX_NUMBER_OF_PLAYERS):

			turn_event_data = mule_game_history.get_turn_event_data(player_index)

			if turn_event_data is not None:
				turn_events.append(player_index)
				turn_events.append(round_number)
				turn_events.append(str(round_number) + ' - ' + process_turn_event(turn_event_data))

			score_money = mule_game_history.game_state.get_planeteer_score_money(player_index)
			score_land = mule_game_history.game_state.get_planeteer_score_land(player_index)
			score_goods = mule_game_history.game_state.get_planeteer_score_goods(player_index)

			money[player_index][round_number] = score_money
			land[player_index][round_number] = score_land
			goods[player_index][round_number] = score_goods

			scores[player_index][round_number] = score_money + score_land + score_goods

def plot_mule_game_data():
	# Create plot using matplotlib package

	months = np.arange(mule_game_history.get_number_of_rounds())
	month_event.append('The ship has returned!')
	event_label_colors.append('gray')

	# Set up graph display dimensions
	fig, ax = plt.subplots(figsize=(10, 8))
	plt.subplots_adjust(bottom=0.3)

	# Graph total player scores with different colors, markers and linestyles
	markerstyles = ['o', 's', '^', 'D']
	for player_graph in range(4):
		ax.plot(scores[player_graph], player_color[player_graph], marker=markerstyles[player_graph],
				label=player_name[player_graph])

	ax.legend(player_name)
	ax.set_ylabel("Total Wealth")

	# Set up tick formats and labels
	ax.set_xticks(months)
	minor_ticks = months[:-1] + 0.5  # Positions between major ticks
	ax.set_xticks(minor_ticks, minor=True)
	ax.set_xticklabels(month_event, minor=True, rotation=60)
	ax.tick_params(axis='x', which='major', length=5)  # Major ticks length
	ax.tick_params(axis='x', which='minor', length=15)  # Minor ticks are longer

	# Adjust label alignment and color
	minor_labels = ax.xaxis.get_minorticklabels()
	for i, label in enumerate(minor_labels):
		label.set_color(event_label_colors[i])
		label.set_horizontalalignment('right')  # Shift labels left to align with the ticks

	# Draw light gray vertical lines at minor tick positions to indicate month events
	for mtick in minor_ticks:
		ax.axvline(x=mtick, color='gainsboro', linewidth=2, alpha=0.35)

	# Clean up graph by making top and right boundaries invisible
	ax.spines.right.set_visible(False)
	ax.spines.top.set_visible(False)

	ax.set_title(mule_game_history.game_name)
	plt.savefig(mule_game_history.game_name + '_summary.png', dpi=200)


def plot_mule_round_data():
	# Plot individual round data for each player
	months = np.arange(mule_game_history.get_number_of_rounds())

	# create a 2x2 grid of plots, one for each player
	fig, ax = plt.subplots(2, 2, sharey=True, figsize=(10, 11))
	plt.rcParams['text.usetex'] = False
	plt.subplots_adjust(left=0.125, right=0.9, bottom=0.2, top=0.95, hspace=0.8)

	for player_graph in range(4):
		# Iterate for each of the 4 individual player graphs
		xindex = int(player_graph / 2)
		yindex = player_graph - xindex
		if yindex == 2:
			yindex = 0

		# Set up different linestyles and alphas for total, money, land, and goods
		ax[xindex, yindex].plot(scores[player_graph], player_color[player_graph], alpha=0.4, marker='|', label='total')
		ax[xindex, yindex].plot(money[player_graph], player_color[player_graph], alpha=0.6, label='money')
		ax[xindex, yindex].plot(land[player_graph], player_color[player_graph], alpha=0.3, label='land')
		ax[xindex, yindex].plot(goods[player_graph], player_color[player_graph], alpha=0.8, label='goods', ls='--')

		# Legend
		ax[xindex, yindex].legend(loc='upper left')
		ax[xindex, yindex].set_title(
			player_name[player_graph] + " (" + player_color[player_graph] + " " + player_species[player_graph] + ")",
			color=player_color[player_graph])

		# Set major ticks for each month and make labels empty
		ax[xindex, yindex].set_xticks(months)
		ax[xindex, yindex].set_xticklabels([''] * len(months))  # Empty labels for major ticks

		# Set up minor ticks to be invisible and label them
		minor_ticks = months[:-1] + 0.5  # Positions between the major ticks
		ax[xindex, yindex].set_xticks(minor_ticks, minor=True)
		ax[xindex, yindex].set_xticklabels([f"{int(m + 1)}" for m in months[:-1]], minor=True)  # Month numbers as labels

		# Customize the appearance of ticks
		ax[xindex, yindex].tick_params(axis='x', which='major', length=10)  # Major ticks
		ax[xindex, yindex].tick_params(axis='x', which='minor', length=0)  # Minor ticks are invisible

		# Ensure the minor tick labels are visible and adjust settings
		for label in ax[xindex, yindex].xaxis.get_minorticklabels():
			label.set_visible(True)  # Make sure labels are visible

		txt1 = []

		for i in range(0, len(turn_events), 3):
			if turn_events[i] == player_graph:

				# Create a gray bar indicating the development phase between "status" screens
				# (which is when these events occur)
				ax[xindex, yindex].axvspan(xmin=turn_events[i+1]-1, xmax=turn_events[i+1], color='gray', ls=':', alpha=0.2)

				# Take all individual per-player events and turn them into a string with newlines between events
				txt1.append(turn_events[i+2])

		if txt1:
			txt = '\n'.join(txt1)

			# Create a temporary WrapText object to calculate the height of the text
			temp_text = WrapText(0, 0, txt, width=1, widthcoords=ax[xindex, yindex].transAxes,
								 transform=ax[xindex, yindex].transAxes, fontsize=8.0)
			ax[xindex, yindex].add_artist(temp_text)  # Temporarily add to axis
			ax[xindex, yindex].figure.canvas.draw()  # Force a draw to update the text size
			text_bbox = temp_text.get_window_extent(renderer=ax[xindex, yindex].figure.canvas.get_renderer())
			temp_text.remove()  # Remove the temporary text object

			# Calculate the height of the text box in axis coordinates
			height_in_axis_coords = text_bbox.height / ax[xindex, yindex].figure.bbox.height

			y_text = -0.08 - height_in_axis_coords * 3.7  # Empirical values discovered by trial and error

			# Use the custom wrapping function defined above to wrap the text block string to the width of the plot for each player
			ax[xindex, yindex].add_artist(WrapText(0, y_text, txt, width=1, widthcoords=ax[xindex, yindex].transAxes,
													   transform=ax[xindex, yindex].transAxes,
													   color=player_color[player_graph], fontsize=8.0))

	# Figure needs to be saved out at 200 dpi to preserve proper wrapping as defined above.
	plt.savefig(mule_game_history.game_name + '_rounds.png', dpi=200)

def plot_mule_commodity_data():
	# Plot monthly commodity prices
	months = np.arange(mule_game_history.get_number_of_rounds())

	# create a 2x2 grid of plots, one for each commodity
	fig, ax = plt.subplots(2, 2, sharey=True, figsize=(10, 8))
	plt.rcParams['text.usetex'] = False
	fig.suptitle(mule_game_history.game_name)
	#plt.subplots_adjust(left=0.125, right=0.9, bottom=0.2, top=0.95, hspace=0.8)

	for commodity in range(mule.NUMBER_OF_GOOD_TYPES):
		# Iterate for each of the individual commodities
		xindex = int(commodity / 2)
		yindex = commodity - xindex
		if yindex == 2:
			yindex = 0

		price = []

		for round_number in range(mule_game_history.get_number_of_rounds()):
			mule_game_history.set_round_number(round_number)
			mule_game_history.process_round_screen_events()

			price.append(mule_game_history.game_state.get_store_good_price_buy(commodity))

		ax[xindex, yindex].bar(months, price)
		ax[xindex, yindex].yaxis.set_tick_params(labelleft=True)

		# Legend
		ax[xindex, yindex].set_title(commodity_names[commodity])

		ax[xindex, yindex].set_xticks(months)
		ax[xindex, yindex].grid(axis='y', color='gray', linestyle='--', linewidth=0.5)

	# Figure needs to be saved out at 200 dpi to preserve proper wrapping as defined above.
	plt.savefig(mule_game_history.game_name + '_prices.png', dpi=200)

# Example usage:
# python read_mule_game_file.py path/to/1234.mulegame

if __name__ == "__main__":
	# Check if a command-line argument is provided
	if len(sys.argv) != 2:
		print("Usage: python graph_mule_game_file.py <mule_game_file_path>")
		sys.exit(1)

	input_file_path = sys.argv[1]

	mule_game_history = mule.GameHistory(input_file_path)
	if not mule_game_history.is_populated():
		sys.exit(1)

	print("MULE game history loaded successfully")

	process_mule_game_history(mule_game_history)
	plot_mule_game_data()
	plot_mule_round_data()
	plot_mule_commodity_data()
