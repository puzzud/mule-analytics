from enum import Enum
from typing import Callable
import json

import mule
from .game_state import GameState


class GameHistoryScreenId(Enum):
	GAME_HISTORY_SCREEN_ID_INTRO:       int = 0
	GAME_HISTORY_SCREEN_ID_STATUS:      int = 1
	GAME_HISTORY_SCREEN_ID_DEVELOPMENT: int = 2
	GAME_HISTORY_SCREEN_ID_AUCTION:     int = 3


class GameHistoryEventId(Enum):
	GAME_HISTORY_EVENT_ID_NONE:                        int = -1
#	GAME_HISTORY_EVENT_ID_INIT_TOWN_GOODS_AMOUNT:      int = 30
#	GAME_HISTORY_EVENT_ID_INIT_PLANETEER_GOODS_AMOUNT: int = 40
#	GAME_HISTORY_EVENT_ID_INIT_PLANETEER_MONEY_AMOUNT: int = 41
	GAME_HISTORY_EVENT_ID_ROUND_GOODS_VALUATION:       int = 50
#	GAME_HISTORY_EVENT_ID_ROUND_MULE_PRODUCTION:       int = 75
	GAME_HISTORY_EVENT_ID_ROUND_MULE_VALUATION:        int = 76
	GAME_HISTORY_EVENT_ID_ROUND_SCORE:                 int = 150
#	GAME_HISTORY_EVENT_ID_LAND_GRANT:                  int = 200
#	GAME_HISTORY_EVENT_ID_LAND_AUCTION:                int = 201
#	GAME_HISTORY_EVENT_ID_TURN_START:                  int = 210
#	GAME_HISTORY_EVENT_ID_TURN_END:                    int = 211
	GAME_HISTORY_EVENT_ID_TURN_EVENT:                  int = 215
#	GAME_HISTORY_EVENT_ID_TURN_TOWN_MULE_TRADE:        int = 220
#	GAME_HISTORY_EVENT_ID_TURN_TOWN_MULE_OUTFIT:       int = 221
#	GAME_HISTORY_EVENT_ID_TURN_PLOT_MULE_TRANSFER:     int = 230
	GAME_HISTORY_EVENT_ID_TURN_PLOT_ASSAY_RESULT:      int = 240
#	GAME_HISTORY_EVENT_ID_TURN_PLOT_FOR_SALE_MARK:     int = 250
#	GAME_HISTORY_EVENT_ID_TURN_WAMPUS_MOVE:            int = 260
#	GAME_HISTORY_EVENT_ID_TURN_WAMPUS_CAUGHT:          int = 270
#	GAME_HISTORY_EVENT_ID_ROUND_PRODUCTION:            int = 280
	GAME_HISTORY_EVENT_ID_ROUND_EVENT:                 int = 290
	GAME_HISTORY_EVENT_ID_AUCTION_STORE_PRICES:        int = 300
#	GAME_HISTORY_EVENT_ID_AUCTION_STATUS_PREVIOUS:     int = 310
#	GAME_HISTORY_EVENT_ID_AUCTION_STATUS_USAGE:        int = 311
#	GAME_HISTORY_EVENT_ID_AUCTION_STATUS_SPOILAGE:     int = 312
#	GAME_HISTORY_EVENT_ID_AUCTION_STATUS_PRODUCTION:   int = 313
#	GAME_HISTORY_EVENT_ID_AUCTION_STATUS_SURPLUS:      int = 314
#	GAME_HISTORY_EVENT_ID_AUCTION_DECLARE:             int = 320
#	GAME_HISTORY_EVENT_ID_AUCTION_SKIP:                int = 330
#	GAME_HISTORY_EVENT_ID_AUCTION_TRADE_GOOD:          int = 340


class GameHistory:
	def __init__(self, input = None):
		self.screen_id_value_api_translation_table: dict[GameHistoryScreenId, int] = {}

		self.client_version = ""
		self.game_name = ""

		self._settings_data: dict[str] = {}
		self._player_data: dict[str] = {}
		self._history_data: dict[str] = {}
		self._planet_data: dict[str] = {}
		self._store_data: dict[str] = {}

		self._populated = False

		self._round_number: int = 0
		self._screen_index: int = 0
		self._screen_event_index: int = 0

		self.game_state = GameState()

		if input != None:
			if isinstance(input, str):
				self.read_mule_game_file(input)


	def read_mule_game_file(self, file_path: str) -> int:
		try:
			json_data: dict = None

			with open(file_path, 'r') as file:
				json_data = json.load(file)
			
			self.process_json_data(json_data)

			return 0
		except FileNotFoundError:
			print(f"Error: File '{file_path}' not found.")
		except json.JSONDecodeError:
			print(f"Error: Invalid JSON format in file '{file_path}'.")

		return -1


	def process_json_data(self, json_data: dict):
		# TODO: Process any API versioning after reading client version.
		self.client_version = json_data["version"]["client"]
		self.process_api_versioning()

		self.game_name = json_data["name"]

		self._settings_data = json_data["settings"]
		self._player_data = json_data["player"]
		self._history_data = json_data["history"]
		self._planet_data = json_data["planet"]
		self._store_data = json_data["store"]

		self._populated = True

		self.reset_game_state()
		self.set_round_number(0)


	def process_api_versioning(self):
		self.screen_id_value_api_translation_table[GameHistoryScreenId.GAME_HISTORY_SCREEN_ID_INTRO] = GameHistoryScreenId.GAME_HISTORY_SCREEN_ID_INTRO.value
		self.screen_id_value_api_translation_table[GameHistoryScreenId.GAME_HISTORY_SCREEN_ID_STATUS] = GameHistoryScreenId.GAME_HISTORY_SCREEN_ID_STATUS.value
		self.screen_id_value_api_translation_table[GameHistoryScreenId.GAME_HISTORY_SCREEN_ID_DEVELOPMENT] = GameHistoryScreenId.GAME_HISTORY_SCREEN_ID_DEVELOPMENT.value
		self.screen_id_value_api_translation_table[GameHistoryScreenId.GAME_HISTORY_SCREEN_ID_AUCTION] = GameHistoryScreenId.GAME_HISTORY_SCREEN_ID_AUCTION.value

		if compare_versions(self.client_version, "1.11.0") < 0:
			# For earlier versions the screen ID for the Status screen was not consistent with
			# how screens are ID'd in MULE Online (technically a bug).
			self.screen_id_value_api_translation_table[GameHistoryScreenId.GAME_HISTORY_SCREEN_ID_STATUS] = 0


	def is_populated(self) -> bool:
		return self._populated


	def get_round_number(self) -> int:
		return self._round_number


	def set_round_number(self, round_number: int) -> None:
		round_number_offset = round_number - self._round_number
		
		if round_number == 0:
			self.reset_game_state()

		if round_number_offset == 0:
			return
		
		if round_number_offset < 0:
			# NOTE: If going backwards from current round number, reset to round 0 and work upwards.
			# TODO: Work backwards by rolling back events in reverse, unless going back to 0.
			# NOTE: Can only work backwards if history events that affect game state are all implemented.
			self.reset_game_state()
			self.set_round_number(round_number)
			return

		# Cycle through all rounds and their events to the beginning of this round number.
		# +1 to ensure current round gets fully processed (screen & screen event indices exhausted).
		for _index in range(round_number_offset + 1):
			self.process_round_screen_events()

			self._round_number += 1
			self._screen_index = 0
		
		self._round_number = round_number
		self._screen_index = 0
		self._screen_event_index = 0


	def get_rounds_data(self) -> list[dict[str]]:
		return self._history_data["rounds"]


	def get_number_of_rounds(self) -> int:
		return len(self.get_rounds_data())


	def get_round_data(self, round_number: int = -1) -> dict[str]:
		if round_number < 0:
			round_number = self._round_number

		rounds_data = self.get_rounds_data()
		round_data: dict[str] = rounds_data[round_number]

		return round_data


	def get_round_screens_data(self, round_number: int = -1) -> list[dict[str]]:
		if round_number < 0:
			round_number = self._round_number

		round_data = self.get_round_data(round_number)

		return round_data["screens"]


	def get_round_screen_events_data_by_id(self, screen_id: GameHistoryScreenId, round_number: int = -1) -> list[dict[str]]:
		if round_number < 0:
			round_number = self._round_number

		# NOTE: This is the only API that takes a screen ID as a parameter,
		# so it should be filtered based on API version differences. In the future,
		# it's a good idea to always do this when receiving a game history screen ID when
		# resolving its integer "value", but probably not necessary.
		screen_id_value: int = self.screen_id_value_api_translation_table[screen_id]

		for screen_data in self.get_round_screens_data(round_number):
			screen_events_data = screen_data.get(str(screen_id_value))
			if screen_events_data != None:
				return screen_events_data
		
		return []


	def get_round_status_screen_events_data(self, round_number: int = -1) -> list[dict[str]]:
		if round_number < 0:
			round_number = self._round_number

		return self.get_round_screen_events_data_by_id(GameHistoryScreenId.GAME_HISTORY_SCREEN_ID_STATUS, round_number)


	def get_round_development_screen_events_data(self, round_number: int = -1) -> list[dict[str]]:
		if round_number < 0:
			round_number = self._round_number

		return self.get_round_screen_events_data_by_id(GameHistoryScreenId.GAME_HISTORY_SCREEN_ID_DEVELOPMENT, round_number)


	def process_round_screen_events(self) -> None:
		round_screens_data = self.get_round_screens_data(self._round_number)
		
		while self._screen_index < len(round_screens_data):
			round_screen_data = round_screens_data[self._screen_index]

			screen_id_string: str = next(iter(round_screen_data.keys()))
			screen_events_data: list[dict[str]] = round_screen_data[screen_id_string]

			self._screen_event_index = 0
			while self._screen_event_index < len(screen_events_data):
				screen_event_data = screen_events_data[self._screen_event_index]

				screen_event_id: GameHistoryEventId = screen_event_data["id"]
				screen_event_parameters: list[int] = screen_event_data["parameters"]

				self.process_screen_event(screen_event_id, screen_event_parameters)

				self._screen_event_index += 1
			
			self._screen_index += 1
		
		# TODO: This logic will not be needed when history processing is fully implemented
		# and represents the final game state after all screen events have been processed.
		if self._round_number >= self.get_number_of_rounds() - 1:
			self.populate_final_game_state()


	def process_screen_event(self, screen_event_id: GameHistoryEventId, screen_event_parameters: list[int]) -> None:
		method = self.process_screen_event_methods.get(screen_event_id)
		if method == None:
			#print("GameHistory::process_screen_event: event ID not supported: %d" % (screen_event_id))
			return
	
		method(self, screen_event_parameters)


	def process_screen_event_goods_valuation(self, screen_event_parameters: list[int]) -> None:
		for good_type in range(len(screen_event_parameters)):
			self.game_state.set_good_value(good_type, screen_event_parameters[good_type])


	def process_screen_event_mule_valuation(self, screen_event_parameters: list[int]) -> None:
		self.game_state.set_store_mule_price(screen_event_parameters[0])


	def process_screen_event_status_score(self, screen_event_parameters: list[int]) -> None:
		colony_score: int = 0
		planeteers_rank = [0 for _ in range(mule.MAX_NUMBER_OF_PLAYERS)]

		# TODO: Add constants for parameter offsets.
		for player_index in range(mule.MAX_NUMBER_OF_PLAYERS):
			score_event_parameter_player_offset_index = player_index * 3

			score_money = screen_event_parameters[score_event_parameter_player_offset_index + 0]
			score_land = screen_event_parameters[score_event_parameter_player_offset_index + 1]
			score_goods = screen_event_parameters[score_event_parameter_player_offset_index + 2]

			colony_score += score_money + score_land + score_goods

			self.game_state.set_planeteer_scores(player_index, score_money, score_land, score_goods)

			planeteers_rank[player_index] = screen_event_parameters[13 + player_index]

		self.game_state.set_planeteers_rank(planeteers_rank)

		self.game_state.set_colony_score(colony_score)
		self.game_state.set_colony_score_rating(screen_event_parameters[12])


	def process_screen_event_auction_store_prices(self, screen_event_parameters: list[int]) -> None:
		good_type: int = screen_event_parameters[0]
		self.game_state.set_store_good_price_buy(good_type, screen_event_parameters[1])


	process_screen_event_methods: dict[int, Callable] = {
		GameHistoryEventId.GAME_HISTORY_EVENT_ID_ROUND_GOODS_VALUATION.value: process_screen_event_goods_valuation,
		GameHistoryEventId.GAME_HISTORY_EVENT_ID_ROUND_MULE_VALUATION.value: process_screen_event_mule_valuation,
		GameHistoryEventId.GAME_HISTORY_EVENT_ID_ROUND_SCORE.value: process_screen_event_status_score,
		GameHistoryEventId.GAME_HISTORY_EVENT_ID_AUCTION_STORE_PRICES.value: process_screen_event_auction_store_prices,
	}


	def get_round_event_data(self, round_number: int = -1) -> dict[str]:
		if round_number < 0:
			round_number = self._round_number

		for development_screen_event in self.get_round_development_screen_events_data(round_number):
			if development_screen_event["id"] == GameHistoryEventId.GAME_HISTORY_EVENT_ID_ROUND_EVENT.value:
				return development_screen_event

		return None


	def get_turn_event_data(self, player_index: int, round_number: int = -1) -> dict[str]:
		if round_number < 0:
			round_number = self._round_number

		for development_screen_event in self.get_round_development_screen_events_data(round_number):
			if development_screen_event["id"] == GameHistoryEventId.GAME_HISTORY_EVENT_ID_TURN_EVENT.value:
				parameters: list[int] = development_screen_event["parameters"]
				event_player_index = parameters[len(parameters) - 1]
				if event_player_index == player_index:
					return development_screen_event

		return None


	def get_setting_play_level(self) -> int:
		return self._settings_data["playLevel"]


	def get_setting_number_of_human_players(self) -> int:
		if compare_versions(self.client_version, "1.11.0") >= 0:
			return self._v_1_11_get_setting_number_of_human_players()
		else:
			return self._v_x_get_setting_number_of_human_players()


	def _v_x_get_setting_number_of_human_players(self) -> int:
		# NOTE: numberOfHumanPlayers has been removed in v1.11.0.
		return self._settings_data["numberOfHumanPlayers"]


	def _v_1_11_get_setting_number_of_human_players(self) -> int:
		number_of_human_players = 0
		
		for player_index in range(mule.MAX_NUMBER_OF_PLAYERS):
			if self.get_player_input_type(player_index) != mule.PLAYER_INPUT_TYPE_COMPUTER:
				number_of_human_players += 1
		
		return number_of_human_players


	def _get_player_data(self, player_index: int) -> dict[str]:
		return self._player_data["players"][player_index]


	def get_player_input_type(self, player_index: int) -> int:
		player_data = self._get_player_data(player_index)
		return player_data["inputType"]


	def get_player_color_id(self, player_index: int) -> int:
		player_data = self._get_player_data(player_index)
		return player_data["colorId"]
	

	def get_player_species_id(self, player_index: int) -> int:
		player_data = self._get_player_data(player_index)
		return player_data["speciesId"]


	def reset_game_state(self) -> None:
		self._round_number = 0
		self._screen_index = 0
		self._screen_event_index = 0

		self.game_state.reset()
	

	# TODO: This method only needed while all game state affecting history events are not
	# implemented fully.
	def populate_final_game_state(self) -> None:
		for player_index in range(mule.MAX_NUMBER_OF_PLAYERS):
			player_data = self._get_player_data(player_index)
			self.game_state.set_planeteer_money_amount(player_index, player_data["moneyAmount"])

			player_data_good_amounts: list[int] = player_data["goodAmounts"]
			for good_type in range(mule.NUMBER_OF_GOOD_TYPES):
				self.game_state.set_planeteer_good_amount(player_index, good_type, player_data_good_amounts[good_type])
			
			planeteer_owned_plot_types: dict[str, int] = player_data["ownedPlotTypes"]

			for plot_index_string in planeteer_owned_plot_types.keys():
				plot_index = int(plot_index_string)
				
				self.game_state.set_plot_owner(plot_index, player_index)

				plot_type = (mule.PlotType)(planeteer_owned_plot_types[plot_index_string])
				self.game_state.set_plot_type(plot_index, plot_type)


def compare_versions(version1: str, version2: str) -> int:
	# Split the version strings by '.' and convert each part to an integer.
	v1_parts = list(map(int, version1.split('.')))
	v2_parts = list(map(int, version2.split('.')))

	# Find the longest length between the two versions.
	max_length = max(len(v1_parts), len(v2_parts))

	# Pad the shorter version with zeros (for comparison purposes).
	v1_parts.extend([0] * (max_length - len(v1_parts)))
	v2_parts.extend([0] * (max_length - len(v2_parts)))

	# Compare corresponding parts.
	for part1, part2 in zip(v1_parts, v2_parts):
		if part1 < part2:
			return -1
		elif part1 > part2:
			return 1

	# If all parts are equal.
	return 0
