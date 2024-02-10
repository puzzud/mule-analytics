import sys

import mule


def process_mule_game_history(mule_game_history: mule.GameHistory) -> None:
	print("Client Version: %s" % (mule_game_history.client_version))

	print("Game Name: %s" % (mule_game_history.game_name))

	# Settings data
	print("Play Level: %d" % (mule_game_history.get_setting_play_level()))
	print("Human Player Count: %d" % (mule_game_history.get_setting_number_of_human_players()))

	# Player info
	for player_index in range(mule.MAX_NUMBER_OF_PLAYERS):
		input_type = mule_game_history.get_player_input_type(player_index)
		computer_player_suffix = " (Computer)" if input_type == mule.PLAYER_INPUT_TYPE_COMPUTER else ""
		print("Player %d%s:" % (player_index, computer_player_suffix))
		print(" - Color: %d" % (mule_game_history.get_player_color_id(player_index)))
		print(" - Species: %d" % (mule_game_history.get_player_species_id(player_index)))
	
	# Game round status summaries
	print("Rounds:")

	for round_number in range(mule_game_history.get_number_of_rounds()):
		mule_game_history.set_round_number(round_number)
		mule_game_history.process_round_screen_events()

		print("Round %d:" % (round_number))

		for player_index in range(mule.MAX_NUMBER_OF_PLAYERS):
			print("   - Player #%d:" % (player_index))

			print("     - Score")
			print("       - Money: %d" % (mule_game_history.game_state.get_planeteer_score_money(player_index)))
			print("       - Land:  %d" % (mule_game_history.game_state.get_planeteer_score_land(player_index)))
			print("       - Goods: %d" % (mule_game_history.game_state.get_planeteer_score_goods(player_index)))

			print("     - Rank: %d" % (mule_game_history.game_state.get_planeteer_rank(player_index)))

		print("   - Colony Score: %d" % (mule_game_history.game_state.get_colony_score()))
		print("   - Colony Score Rating: %d" % (mule_game_history.game_state.get_colony_score_rating()))

	# Final player data
	for player_index in range(mule.MAX_NUMBER_OF_PLAYERS):
		print("   - Player #%d:" % (player_index))

		print("     - Money: %d" % (mule_game_history.game_state.get_planeteer_money_amount(player_index)))
		
		print("     - Goods:")
		for good_type in range(mule.NUMBER_OF_GOOD_TYPES):
			good_amount = mule_game_history.game_state.get_planeteer_good_amount(player_index, good_type)
			print("       - %d: %d" % (good_type, good_amount))


# Example usage:
# python read_mule_game_file.py path/to/1234.mulegame

if __name__ == "__main__":
	# Check if a command-line argument is provided
	if len(sys.argv) != 2:
		print("Usage: python read_mule_game_file.py <mule_game_file_path>")
		sys.exit(1)

	input_file_path = sys.argv[1]
	
	mule_game_history = mule.GameHistory(input_file_path)
	if not mule_game_history.is_populated():
		sys.exit(1)
	
	print("MULE game history loaded successfully")

	process_mule_game_history(mule_game_history)
