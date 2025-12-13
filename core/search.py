import unicodedata
import math

# --- HÀM TÍNH KHOẢNG CÁCH (Haversine) ---
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Tính khoảng cách (km) giữa 2 tọa độ."""
    if not all(isinstance(i, (int, float)) for i in [lat1, lon1, lat2, lon2]):
        return None
    R = 6371  # Bán kính Trái Đất (km)
    phi1, phi2 = map(math.radians, [lat1, lat2])
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- HÀM CHUẨN HÓA VĂN BẢN ---
def normalize_text(text):
    if not text: return ""
    text = str(text).lower()
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    return text

# --- MAPPING CATEGORY KEYWORDS (Thêm để tìm kiếm theo loại món) ---
CATEGORY_KEYWORDS = {
    1: ["man", "dry", "kho", "chien", "xao", "rang", "nuong", "mon man"],  # Món mặn
    2: ["nuoc", "soup", "pho", "bun", "mien", "canh", "lau", "mon nuoc"],  # Món nước
    3: ["chay", "vegetarian", "rau", "trai cay", "mon chay"],              # Món chay
    4: ["man", "salty", "muoi", "dung", "mon dung", "bo"],                 # Món mặn/dùng
    5: ["seafood", "hai san", "ca", "tom", "cua", "oc", "ngao"]            # Hải sản
}

def match_category_from_query(norm_query):
    """Kiểm tra xem query có khớp với category nào không"""
    for cat_id, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in norm_query for kw in keywords):
            return cat_id
    return None

# --- THUẬT TOÁN TÌM KIẾM CHÍNH (CẢI TIẾN) ---
def search_algorithm(query, restaurants_db, menus_by_res_id, restaurants_dict, 
                     province=None, user_lat=None, user_lon=None):
    
    norm_query = normalize_text(query) if query else ""
    norm_province = normalize_text(province) if province else ""
    
    # ⭐ KIỂM TRA XEM QUERY CÓ CHỨA TÊN CATEGORY KHÔNG
    matched_category = match_category_from_query(norm_query) if norm_query else None
    
    # 1. XÁC ĐỊNH BÁN KÍNH TÌM KIẾM
    # - Không query, không province (Tìm quanh đây): 2km
    # - Các trường hợp còn lại: 5km
    if not norm_query and not norm_province:
        radius_km = 2.0
    else:
        radius_km = 5.0

    final_results = []

    # Duyệt qua tất cả nhà hàng
    for r in restaurants_db:
        rid = str(r['id'])
        
        # 2. TÍNH KHOẢNG CÁCH & LỌC THEO BÁN KÍNH
        dist = None
        if user_lat is not None and user_lon is not None:
            dist = calculate_haversine_distance(user_lat, user_lon, r.get('lat'), r.get('lon'))
            
            # LỌC CỨNG: Nếu xa hơn bán kính quy định -> Bỏ qua ngay
            if dist is not None and dist > radius_km:
                continue 

        # 3. LOGIC TÌM KIẾM (MATCHING)
        is_match = False
        match_score = 0

        # TRƯỜNG HỢP A: CÓ TỪ KHÓA (QUERY)
        if norm_query:
            # Nếu có Province, phải khớp Province trước
            if norm_province:
                addr = normalize_text(r.get('address', ''))
                tags = [normalize_text(t) for t in r.get('tags', [])]
                # ⭐ CẢI TIẾN: Kiểm tra cả trong address VÀ tags
                province_match = (norm_province in addr) or any(norm_province in t for t in tags)
                if not province_match:
                    continue # Bỏ qua nếu không đúng tỉnh

            # ⭐ MỚI: Tìm theo CATEGORY_ID nếu query khớp với category keyword
            if matched_category and r.get('category_id') == matched_category:
                match_score += 15  # Điểm cao nhất cho exact category match
                is_match = True
            
            # Tìm trong Tên quán (+10 điểm)
            if norm_query in normalize_text(r.get('name', '')):
                match_score += 10
                is_match = True
            
            # Tìm trong Tags (+8 điểm - tăng từ 5)
            tags_list = r.get('tags', [])
            for tag in tags_list:
                if norm_query in normalize_text(tag):
                    match_score += 8
                    is_match = True
                    break
                
            # Tìm trong Menu (+5 điểm - tăng từ 2)
            menu_items = menus_by_res_id.get(rid, [])
            for item in menu_items:
                if norm_query in normalize_text(item.get('dish_name', '')):
                    match_score += 5
                    is_match = True
                    break
            
            # Nếu không khớp gì cả, bỏ qua
            if not is_match: 
                continue

        # TRƯỜNG HỢP B: KHÔNG QUERY, NHƯNG CÓ PROVINCE
        elif norm_province:
            addr = normalize_text(r.get('address', ''))
            tags = [normalize_text(t) for t in r.get('tags', [])]
            if norm_province in addr or any(norm_province in t for t in tags):
                is_match = True
                match_score = 1 # Điểm cơ bản
            else:
                continue

        # TRƯỜNG HỢP C: KHÔNG QUERY, KHÔNG PROVINCE (GẦN TÔI)
        else:
            # Đã được lọc bởi logic bán kính 2km ở trên rồi
            is_match = True
            match_score = 10 # Ưu tiên vì đang tìm gần

        # 4. TÍNH TỔNG ĐIỂM
        # Cộng điểm Rating (* 2)
        rating_score = (r.get('rating') or 0) * 2
        
        # Cộng điểm Khoảng cách (Càng gần càng cao, tối đa 10 điểm)
        proximity_score = 0
        if dist is not None:
            proximity_score = max(0, 10 * (1 - dist/radius_km))

        final_score = match_score + rating_score + proximity_score
        
        # 5. ĐÓNG GÓI KẾT QUẢ
        res_copy = dict(r)
        res_copy['score'] = round(final_score, 2)
        if dist is not None:
            res_copy['distance_km'] = round(dist, 2)
        # ⭐ THÊM matched_category để debug
        if matched_category:
            res_copy['matched_category'] = matched_category
            
        final_results.append(res_copy)

    # 6. SẮP XẾP: Điểm cao nhất lên đầu
    final_results.sort(key=lambda x: x['score'], reverse=True)
    
    return final_results
