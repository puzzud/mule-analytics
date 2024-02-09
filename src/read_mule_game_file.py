import sys
import mule


def process_mule_history(mule_history: mule.game_history) -> None:
	print("Client Version: %s" % (mule_history.client_version))

	print("Game Name: %s" % (mule_history.game_name))

	# Settings data
	print("Play Level: %d" % (mule_history.get_setting_play_level()))
	print("Human Player Count: %d" % (mule_history.get_setting_number_of_human_players()))

	# Player data
	# TODO: Use constant.
	for player_index in range(4):
		input_type = mule_history.get_player_input_type(player_index)
		computer_player_suffix = " (Computer)" if input_type == 255 else ""
		print("Player %d%s:" % (player_index, computer_player_suffix))
		print(" - Color: %d" % (mule_history.get_player_color_id(player_index)))
		print(" - Species: %d" % (mule_history.get_player_species_id(player_index)))
	
	# Game round status summaries
	print("Rounds:")

	for round_number in range(mule_history.get_number_of_rounds()):
		mule_history.set_round_number(round_number)
		mule_history.process_round_screen_events()

		print("Round %d:" % (round_number))
	
		# TODO: Use constant.
		for player_index in range(4):
			print("   - Player #%d:" % (player_index))

			score_money = mule_history.planeteers_score_money[player_index]
			score_land = mule_history.planeteers_score_land[player_index]
			score_goods = mule_history.planeteers_score_goods[player_index]

			print("     - Score")
			print("       - Money: %d" % (score_money))
			print("       - Land:  %d" % (score_land))
			print("       - Goods: %d" % (score_goods))

			player_rank = mule_history.planeteers_rank[player_index]
			print("     - Rank: %d" % (player_rank))

		print("   - Colony Score: %d" % (mule_history.colony_score))
		print("   - Colony Score Rating: %d" % (mule_history.colony_score_rating))

	# Player data
	# TODO: Use constants.
	for player_index in range(4):
		print("   - Player #%d:" % (player_index))

		money_amount = mule_history.get_planeteer_money_amount(player_index)
		print("     - Money: %d" % (money_amount))

		print("     - Goods:")
		for good_type in range(4):
			good_amount = mule_history.get_planeteer_good_amount(player_index, good_type)
			print("       - %d: %d" % (good_type, good_amount))


# Example usage:
# python read_mule_game_file.py path/to/1234.mulegame

if __name__ == "__main__":
	# Check if a command-line argument is provided
	if len(sys.argv) != 2:
		print("Usage: python read_mule_game_file.py <mule_game_file_path>")
		sys.exit(1)

	input_file_path = sys.argv[1]
	
	mule_history = mule.game_history(input_file_path)
	if not mule_history.is_populated():
		sys.exit(1)
	
	print("MULE game history loaded successfully")

	process_mule_history(mule_history)
