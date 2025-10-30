# Chứa các hàm normalize_text, search_algorithm
import unicodedata

def normalize_text(text):
	if not text:
		return ""
	text = text.lower()
	text = unicodedata.normalize('NFD', text)\
					  .encode('ascii', 'ignore')\
					  .decode('utf-8')
	return text

def search_algorithm(query, restaurants_db, menus_db):
	normalized_query = normalize_text(query)
	if not normalized_query:
		return []

	scores = {}  # restaurant_id: score
	# 1. Tìm trong Tên nhà hàng (ưu tiên cao nhất)
	for restaurant in restaurants_db:
		rid = str(restaurant['id'])
		normalized_name = normalize_text(restaurant.get('name'))
		if normalized_query in normalized_name:
			scores[rid] = scores.get(rid, 0) + 10  # match name: +10

	# 2. Tìm trong Tags nhà hàng (ưu tiên vừa)
	for restaurant in restaurants_db:
		rid = str(restaurant['id'])
		normalized_tags = [normalize_text(tag) for tag in restaurant.get('tags', [])]
		if any(normalized_query in tag for tag in normalized_tags):
			scores[rid] = scores.get(rid, 0) + 5  # match tag: +5

	# 3. Tìm trong Tên món ăn (ưu tiên thấp hơn)
	for restaurant_id, details in menus_db.items():
		for item in details.get('menu', []):
			normalized_dish = normalize_text(item.get('dish_name'))
			if normalized_query in normalized_dish:
				scores[restaurant_id] = scores.get(restaurant_id, 0) + 2  # match dish: +2
				break

	# 4. Cộng thêm điểm theo rating (nếu có)
	restaurants_dict = {str(r['id']): r for r in restaurants_db}
	for rid in scores:
		res = restaurants_dict.get(rid)
		if res:
			rating = res.get('rating')
			if isinstance(rating, (int, float)):
				scores[rid] += rating * 2  # mỗi 1 điểm rating = +2 điểm

	# 5. Biên soạn kết quả, sắp xếp theo điểm giảm dần
	sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
	final_results = []
	for res_id, score in sorted_results:
		if res_id in restaurants_dict:
			res = dict(restaurants_dict[res_id])
			res['score'] = score
			final_results.append(res)
	return final_results
