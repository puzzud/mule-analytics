import mule

class GameState:
	def __init__(self):
		self.plot_owner = [mule.PLOT_UNOWNED for _ in range(mule.PLANET_NUMBER_OF_PLOTS)]
		self.plot_type = [mule.PlotType.PLOT_TYPE_UNUSED for _ in range(mule.PLANET_NUMBER_OF_PLOTS)]

		self.good_values = [0 for _ in range(mule.NUMBER_OF_GOOD_TYPES)]

		self.store_good_prices_buy = [0 for _ in range(mule.NUMBER_OF_GOOD_TYPES)]
		self.store_mule_price = 0

		self.planeteers_money_amount = [0 for _ in range(mule.MAX_NUMBER_OF_PLAYERS)]

		self.planeteers_money_amount = [0 for _ in range(mule.MAX_NUMBER_OF_PLAYERS)]
		self.planeteers_good_amount = [[0 for _ in range(mule.MAX_NUMBER_OF_PLAYERS)] for _ in range(mule.NUMBER_OF_GOOD_TYPES)]
		
		self.planeteers_score_money = [0 for _ in range(mule.MAX_NUMBER_OF_PLAYERS)]
		self.planeteers_score_land = [0 for _ in range(mule.MAX_NUMBER_OF_PLAYERS)]
		self.planeteers_score_goods = [0 for _ in range(mule.MAX_NUMBER_OF_PLAYERS)]
		self.planeteers_rank = [0 for _ in range(mule.MAX_NUMBER_OF_PLAYERS)]

		self.colony_score: int = 0
		self.colony_score_rating: int = 0


	def reset(self) -> None:
		self.__init__()


	def get_plot_owner(self, plot_index: int) -> int:
		return self.plot_owner[plot_index]


	def set_plot_owner(self, plot_index: int, player_index: int) -> None:
		self.plot_owner[plot_index] = player_index
	
	
	def get_plot_type(self, plot_index: int) -> mule.PlotType:
		return self.plot_type[plot_index]


	def set_plot_type(self, plot_index: int, plot_type: mule.PlotType) -> None:
		self.plot_type[plot_index] = plot_type


	def get_good_value(self, good_type: int) -> int:
		return self.good_values[good_type]


	def set_good_value(self, good_type: int, value: int) -> None:
		self.good_values[good_type] = value


	def get_store_good_price_buy(self, good_type: int) -> int:
		return self.store_good_prices_buy[good_type]


	def set_store_good_price_buy(self, good_type: int, price: int) -> None:
		self.store_good_prices_buy[good_type] = price


	def get_store_mule_price(self) -> int:
		return self.store_mule_price


	def set_store_mule_price(self, price: int) -> None:
		self.store_mule_price = price


	def get_planeteer_money_amount(self, player_index: int) -> int:
		return self.planeteers_money_amount[player_index]


	def set_planeteer_money_amount(self, player_index: int, amount: int) -> None:
		self.planeteers_money_amount[player_index] = amount


	def get_planeteer_good_amount(self, player_index: int, good_type: int) -> int:
		return self.planeteers_good_amount[good_type][player_index]
	

	def set_planeteer_good_amount(self, player_index: int, good_type: int, amount: int) -> None:
		self.planeteers_good_amount[good_type][player_index] = amount


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


	def get_planeteer_rank(self, player_index: int) -> list[int]:
		return self.planeteers_rank[player_index]


	def set_planeteers_rank(self, _planeteers_rank: list[int]) -> None:
		self.planeteers_rank = _planeteers_rank


	def get_colony_score(self) -> int:
		return self.colony_score


	def set_colony_score(self, _colony_score: int) -> None:
		self.colony_score = _colony_score
	

	def get_colony_score_rating(self) -> int:
		return self.colony_score_rating


	def set_colony_score_rating(self, _colony_score_rating: int) -> None:
		self.colony_score_rating = _colony_score_rating


	def print_plot_owner_map(self) -> None:
		plot_index: int = 0

		for plot_y in range(mule.PLANET_PLOT_HEIGHT):
			row_string = ""

			for plot_x in range(mule.PLANET_PLOT_WIDTH):
				player_index = self.get_plot_owner(plot_index)
				plot_owner_character = "." if player_index == mule.PLOT_UNOWNED else str(player_index)

				row_string += plot_owner_character

				plot_index += 1
			
			print(row_string)


	def print_plot_type_map(self) -> None:
		plot_index: int = 0

		for plot_y in range(mule.PLANET_PLOT_HEIGHT):
			row_string = ""

			for plot_x in range(mule.PLANET_PLOT_WIDTH):
				player_type = self.get_plot_type(plot_index)
				plot_type_character = str(player_type.value)

				row_string += plot_type_character

				plot_index += 1
			
			print(row_string)
