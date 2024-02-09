from typing import Callable
import json


class game_history:
	def __init__(self, input = None):
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

		self._game_state = {}
		self.planeteers_money_amount: list[int] = [0, 0, 0, 0]
		self.planeteers_good_amount: list[list[int]] = [
			[0, 0, 0, 0],
			[0, 0, 0, 0],
			[0, 0, 0, 0],
			[0, 0, 0, 0]
		]
		self.planeteers_score_money: list[int] = [0, 0, 0, 0]
		self.planeteers_score_land: list[int] = [0, 0, 0, 0]
		self.planeteers_score_goods: list[int] = [0, 0, 0, 0]
		self.planeteers_rank: list[int] = [0, 0, 0, 0]

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

		self.game_name = json_data["name"]

		self._settings_data = json_data["settings"]
		self._player_data: dict[str] = json_data["player"]
		self._history_data = json_data["history"]
		self._planet_data = json_data["planet"]
		self._store_data = json_data["store"]

		self._populated = True

		self.clear_game_state()
		self.set_round_number(0)


	def is_populated(self) -> bool:
		return self._populated


	def get_round_number(self) -> int:
		return self._round_number


	def set_round_number(self, round_number: int) -> None:
		round_number_offset = round_number - self._round_number
		
		if round_number == 0:
			self.clear_game_state()

		if round_number_offset == 0:
			return
		
		if round_number_offset < 0:
			# NOTE: If going backwards from current round number, reset to round 0 and work upwards.
			# TODO: Work backwards by rolling back events in reverse, unless going back to 0.
			# NOTE: Can only work backwards if history events that affect game state are all implemented.
			self.clear_game_state()
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

		# TODO: This logic will not be needed when history processing is fully implemented
		# and represents the final game state after all screen events have been processed.
		if round_number >= self.get_number_of_rounds() - 1:
			self.populate_final_game_state()


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


	def get_round_screen_events_data_by_id(self, screen_id: int, round_number: int = -1) -> list[dict[str]]:
		if round_number < 0:
			round_number = self._round_number

		for screen_data in self.get_round_screens_data(round_number):
			screen_events_data = screen_data.get(str(screen_id))
			if screen_events_data != None:
				return screen_events_data
		
		return None


	def get_round_status_screen_events_data(self, round_number: int = -1) -> list[dict[str]]:
		if round_number < 0:
			round_number = self._round_number

		# TODO: Get from constant.
		return self.get_round_screen_events_data_by_id(0, round_number)


	def process_round_screen_events(self) -> None:
		round_screens_data = self.get_round_screens_data(self._round_number)
		
		while self._screen_index < len(round_screens_data):
			round_screen_data = round_screens_data[self._screen_index]

			screen_id_string: str = next(iter(round_screen_data.keys()))
			screen_events_data: list[dict[str]] = round_screen_data[screen_id_string]

			self._screen_event_index = 0
			while self._screen_event_index < len(screen_events_data):
				screen_event_data = screen_events_data[self._screen_event_index]

				screen_event_id: int = screen_event_data["id"]
				screen_event_parameters: list[int] = screen_event_data["parameters"]

				self.process_screen_event(screen_event_id, screen_event_parameters)

				self._screen_event_index += 1
			
			self._screen_index += 1


	def process_screen_event(self, screen_event_id: int, screen_event_parameters: list[int]) -> None:
		method = self.process_screen_event_methods.get(screen_event_id)
		if method == None:
			return
	
		method(self, screen_event_parameters)


	def process_screen_event_status_score(self, screen_event_parameters: list[int]) -> None:
		colony_score: int = 0

		# TODO: Add constants.
		for player_index in range(4):
			score_event_parameter_player_offset_index = player_index * 3
			score_money = screen_event_parameters[score_event_parameter_player_offset_index + 0]
			score_land = screen_event_parameters[score_event_parameter_player_offset_index + 1]
			score_goods = screen_event_parameters[score_event_parameter_player_offset_index + 2]

			colony_score += score_money + score_land + score_goods

			self.set_planeteer_scores(player_index, score_money, score_land, score_goods)

			self.planeteers_rank[player_index] = screen_event_parameters[13 + player_index]

		self.colony_score = colony_score
		self.colony_score_rating: int = screen_event_parameters[12]


	process_screen_event_methods: dict[int, Callable] = {
		# TODO: Need to create a constant.
		150: process_screen_event_status_score,
	}


	# TODO: Use constants.
	def get_setting_play_level(self) -> int:
		return self._settings_data["playLevel"]


	def get_setting_number_of_human_players(self) -> int:
		return self._settings_data["numberOfHumanPlayers"]


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


	# Game State
	def populate_final_game_state(self) -> None:
		# TODO:
		print("Error: Final game state population not implemented")


	def clear_game_state(self) -> None:
		self._round_number = 0
		self._screen_index = 0
		self._screen_event_index = 0

		# TODO:
		print("Error: clear_game_state not fully implemented")


	def get_planeteer_money_amount(self, player_index: int) -> int:
		#return current_player_data["moneyAmount"]
		return self.planeteers_money_amount[player_index]


	def set_planeteer_money_amount(self, player_index: int, amount: int) -> None:
		self.planeteers_money_amount[player_index] = amount


	def get_planeteer_good_amount(self, player_index: int, good_type: int) -> int:
		#return current_player_data["goodAmounts"]
		return self.planeteers_good_amount[good_type][player_index]
	

	def set_planeteer_good_amount(self, player_index: int, good_type: int, amount: int) -> None:
		self.planeteers_money_amount[good_type][player_index] = amount


	def get_planeteer_score_money(self, player_index: int) -> int:
		return self.planeteers_score_money[player_index]


	def get_planeteer_score_land(self, player_index: int) -> int:
		return self.planeteers_score_land[player_index]
	

	def get_planeteer_score_goods(self, player_index: int) -> int:
		return self.planeteers_score_goods[player_index]


	def set_planeteer_scores(self, player_index: int, score_money: int, score_land: int, score_goods: int) -> None:
		self.planeteers_score_money[player_index] = score_money
		self.planeteers_score_land[player_index] = score_land
		self.planeteers_score_goods[player_index] = score_goods
