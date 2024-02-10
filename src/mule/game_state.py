import mule

class GameState:
	def __init__(self):
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
