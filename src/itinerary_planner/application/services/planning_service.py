from typing import List, Dict, Any, Tuple, Optional
from datetime import time, date, timedelta

from ...domain.models.itinerary import Itinerary, Day, Visit, Accommodation
from ...domain.models.story import Story
from ...infrastructure.persistence.orm_models import Place

class GreedyPlanner:
    """
    一個簡單的貪婪規劃器，用於生成行程草案。
    """

    def plan(
        self,
        story: Story,
        candidates: List[Place],
        travel_matrix: List[List[float]]
    ) -> Itinerary:
        """
        執行貪婪演算法來生成行程。

        演算法思路:
        1. 根據評分對候選點進行排序。
        2. 遍歷天數。
        3. 在每一天中，從當前位置出發，選擇一個尚未訪問且「可行」的下一個地點。
        4. 「可行」的定義是：
           a. 加入該點後，不會超過當天的時間窗。
           b. 該點在預計到達時間是營業的。
        5. 重複直到當天時間滿了，或沒有可行的點了。
        """
        
        # 建立候選點 ID 到索引的映射，以便查詢交通矩陣
        # 注意：這個映射必須與 travel_matrix 的索引順序完全一致
        # 由於 travel_matrix 是基於 candidates 的順序建立的，所以映射應該正確
        place_id_to_idx = {str(p.id): i for i, p in enumerate(candidates)}
        
        # 調試：打印 place_id_to_idx 映射
        print(f"🔍 **調試 place_id_to_idx 映射**")
        for place_id, idx in place_id_to_idx.items():
            place_name = candidates[idx].name if idx < len(candidates) else 'Unknown'
            print(f"  {idx}: {place_name} (ID: {place_id})")
        print()
        
        # 調試：打印交通時間矩陣
        print(f"🔍 **調試交通時間矩陣**")
        for i, row in enumerate(travel_matrix):
            place_name = candidates[i].name if i < len(candidates) else 'Unknown'
            print(f"  Row {i} ({place_name}): {row}")
        print()
        
        # 1. 獲取所有候選點的營業時間
        candidate_ids = [str(p.id) for p in candidates]
        # TODO: 這裡假設 repo 是可用的，在真實的架構中應透過依賴注入傳入
        from ...infrastructure.persistence.database import SessionLocal
        from ...infrastructure.repositories.postgres_place_repo import PostgresPlaceRepository
        db = SessionLocal()
        repo = PostgresPlaceRepository(db)
        hours_map = repo.get_hours_for_places(candidate_ids)
        db.close()

        itinerary_days: List[Day] = []
        visited_place_ids = set()

        # 假設從第一個候選點作為起點
        start_point_idx = 0
        
        for day_num in range(story.days):
            # 2. 從 story 中獲取日期和時間窗
            current_date_str = (story.date_range[0] if story.date_range else date.today().isoformat())
            current_day = date.fromisoformat(current_date_str) + timedelta(days=day_num)
            
            daily_visits: List[Visit] = []
            
            # 使用 Story 中的時間窗，確保正確處理用戶的時間需求
            day_start_time = self._parse_time_to_minutes(story.daily_window.start) if story.daily_window else 9 * 60
            day_end_time = self._parse_time_to_minutes(story.daily_window.end) if story.daily_window else 18 * 60
            
            print(f"📅 第{day_num + 1}天時間窗: {story.daily_window.start if story.daily_window else '09:00'} - {story.daily_window.end if story.daily_window else '18:00'}")
            current_time = day_start_time
            
            last_place_idx = start_point_idx

            # 允許稍微超過結束時間，以更好利用時間窗（增加到90分鐘緩衝）
            while current_time < day_end_time + 90:
                next_visit = self._find_next_best_visit(
                    candidates,
                    travel_matrix,
                    place_id_to_idx,
                    visited_place_ids,
                    last_place_idx,
                    current_time,
                    day_end_time,
                    hours_map,
                    current_day.weekday()
                )

                if not next_visit:
                    break

                place, travel_minutes = next_visit
                
                eta_minutes = current_time + travel_minutes
                etd_minutes = eta_minutes + place.stay_minutes

                visit = Visit(
                    place_id=str(place.id),
                    name=place.name,
                    eta=self._minutes_to_time_str(eta_minutes),
                    etd=self._minutes_to_time_str(etd_minutes),
                    travel_minutes=travel_minutes
                )
                daily_visits.append(visit)

                visited_place_ids.add(str(place.id))
                current_time = etd_minutes
                last_place_idx = place_id_to_idx[str(place.id)]

            # 為每天添加住宿推薦
            accommodation = self._get_accommodation_for_day(day_num, story)
            
            day_plan = Day(date=current_day.isoformat(), visits=daily_visits, accommodation=accommodation)
            self._refine_with_2_opt(day_plan, candidates, travel_matrix, place_id_to_idx)
            itinerary_days.append(day_plan)

        return Itinerary(days=itinerary_days)

    def _is_open(self, place_id: str, arrival_minute: int, weekday: int, hours_map: Dict[str, List[Any]]) -> bool:
        """3. 檢查地點在指定時間是否營業"""
        place_hours = hours_map.get(place_id, [])
        if not place_hours:
            return True # 沒有營業時間資訊，假設全天開放

        # Python's weekday(): Monday is 0 and Sunday is 6
        # Our weekday: Sunday is 0 and Monday is 1...
        db_weekday = (weekday + 1) % 7

        for hour_range in place_hours:
            if hour_range.weekday == db_weekday:
                if hour_range.open_min <= arrival_minute <= hour_range.close_min:
                    return True
        return False

    def _refine_with_2_opt(
        self,
        day_plan: Day,
        candidates: List[Place],
        travel_matrix: List[List[float]],
        place_id_to_idx: Dict[str, int]
    ):
        """使用 2-opt 演算法對一天的行程進行局部優化以減少總旅行時間。"""
        if len(day_plan.visits) < 4:
            return

        improved = True
        while improved:
            improved = False
            for i in range(1, len(day_plan.visits) - 2):
                for j in range(i + 1, len(day_plan.visits)):
                    p1_idx = place_id_to_idx[day_plan.visits[i-1].place_id]
                    p2_idx = place_id_to_idx[day_plan.visits[i].place_id]
                    p3_idx = place_id_to_idx[day_plan.visits[j-1].place_id]
                    p4_idx = place_id_to_idx[day_plan.visits[j].place_id]

                    original_dist = travel_matrix[p1_idx][p2_idx] + travel_matrix[p3_idx][p4_idx]
                    new_dist = travel_matrix[p1_idx][p3_idx] + travel_matrix[p2_idx][p4_idx]

                    if new_dist < original_dist:
                        # 檢查地理位置的合理性：避免過度的跳躍
                        # 如果新路線的總距離比原路線短很多，可能是因為地理跳躍
                        distance_improvement = original_dist - new_dist
                        if distance_improvement > 1800:  # 如果改善超過30分鐘，可能是地理跳躍
                            print(f"⚠️ 跳過可能的地理跳躍優化: 改善 {distance_improvement/60:.1f} 分鐘")
                            continue
                        
                        # 交換路線
                        day_plan.visits[i:j] = day_plan.visits[j-1:i-1:-1]
                        # 重新計算時間
                        self._recalculate_times(day_plan, candidates, travel_matrix, place_id_to_idx)
                        improved = True
        
        print(f"Refined day {day_plan.date} with 2-opt.")

    def _recalculate_times(self, day_plan: Day, candidates: List[Place], travel_matrix: List[List[float]], place_id_to_idx: Dict[str, int]):
        """重新計算行程的時間安排"""
        if not day_plan.visits:
            return
        
        # 創建候選點 ID 到 Place 物件的映射
        place_id_to_place = {str(p.id): p for p in candidates}
        
        # 從第一個景點開始重新計算時間
        current_time = self._parse_time_to_minutes(day_plan.visits[0].eta)
        
        for i, visit in enumerate(day_plan.visits):
            place = place_id_to_place.get(visit.place_id)
            if not place:
                continue
            
            # 計算到達時間
            eta_minutes = current_time
            visit.eta = self._minutes_to_time_str(eta_minutes)
            
            # 計算離開時間
            etd_minutes = eta_minutes + place.stay_minutes
            visit.etd = self._minutes_to_time_str(etd_minutes)
            
            # 計算到下一個景點的交通時間
            if i < len(day_plan.visits) - 1:
                current_idx = place_id_to_idx[visit.place_id]
                next_idx = place_id_to_idx[day_plan.visits[i + 1].place_id]
                travel_seconds = travel_matrix[current_idx][next_idx]
                travel_minutes = round(travel_seconds / 60)
                visit.travel_minutes = travel_minutes
                current_time = etd_minutes + travel_minutes
            else:
                visit.travel_minutes = 0

    def handle_feedback(self, itinerary: Itinerary, dsl: Dict[str, Any]) -> Itinerary:
        """
        根據解析後的 DSL 指令，修改現有行程。
        """
        print(f"Handling feedback DSL: {dsl}")
        op = dsl.get("op")

        if op == "DROP":
            target = dsl.get("target", {})
            day_to_modify = target.get("day")

            if day_to_modify and day_to_modify <= len(itinerary.days):
                itinerary.days[day_to_modify - 1].visits = []
                print(f"Dropped all visits for day {day_to_modify}")
        
        return itinerary

    def _find_next_best_visit(
        self,
        candidates: List[Place],
        travel_matrix: List[List[float]],
        place_id_to_idx: Dict[str, int],
        visited_place_ids: set,
        from_place_idx: int,
        current_time: int,
        day_end_time: int,
        hours_map: Dict[str, List[Any]],
        weekday: int
    ) -> Optional[Tuple[Place, int]]:
        """
        從當前位置找到下一個最佳的、可行的訪問點。
        優先選擇能更好利用時間窗的景點。
        """
        best_visit = None
        best_score = -1
        
        for i, place in enumerate(candidates):
            if str(place.id) in visited_place_ids:
                continue

            travel_seconds = travel_matrix[from_place_idx][i]
            travel_minutes = round(travel_seconds / 60)
            
            # 調試：打印交通時間計算
            if place.name in ['水都活海鮮', '烏石港活海鮮餐廳']:
                print(f"🔍 **交通時間計算調試**")
                print(f"  景點: {place.name}")
                print(f"  from_place_idx: {from_place_idx}")
                print(f"  i: {i}")
                print(f"  travel_seconds: {travel_seconds}")
                print(f"  travel_minutes: {travel_minutes}")
                print()

            eta = current_time + travel_minutes
            etd = eta + place.stay_minutes

            # 4. 加入營業時間和時間窗檢查
            # 允許景點稍微超過結束時間（最多90分鐘），以更好利用時間窗
            max_allowed_end = day_end_time + 90
            
            if etd <= max_allowed_end and self._is_open(str(place.id), eta, weekday, hours_map):
                # 檢查地理位置的合理性：避免過度的跳躍
                # 如果交通時間超過60分鐘，可能是地理跳躍，降低優先級
                if travel_minutes > 60:
                    print(f"⚠️ 跳過可能的地理跳躍: {place.name} (交通時間: {travel_minutes}分鐘)")
                    continue
                
                # 計算時間利用分數：優先選擇能更充分利用時間窗的景點
                # 分數越高表示時間利用越好
                time_remaining = day_end_time - current_time
                time_utilization_score = (etd - day_end_time) / 60.0  # 超過結束時間的分鐘數
                
                # 如果景點能在正常時間內完成，給予額外分數
                if etd <= day_end_time:
                    time_utilization_score += 10  # 額外獎勵
                
                # 如果景點能充分利用剩餘時間，給予額外分數
                if place.stay_minutes >= time_remaining * 0.8:  # 至少利用80%的剩餘時間
                    time_utilization_score += 5
                
                # 優先選擇能更好利用時間窗的景點
                if time_utilization_score > best_score:
                    best_score = time_utilization_score
                    best_visit = (place, travel_minutes)
        
        return best_visit

    def _parse_time_to_minutes(self, time_str: str) -> int:
        """將時間字串 (HH:MM) 轉換為從午夜開始的分鐘數"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return hour * 60 + minute
        except:
            return 9 * 60  # 預設 9:00

    def _minutes_to_time_str(self, minutes: int) -> str:
        """將分鐘數轉換為 'HH:MM' 格式"""
        h, m = divmod(minutes, 60)
        return f"{int(h):02d}:{int(m):02d}"
    
    def _get_accommodation_for_day(self, day_num: int, story: Story) -> Optional[Accommodation]:
        """為指定天數獲取住宿推薦"""
        # 檢查用戶是否明確表示不要住宿
        no_accommodation_keywords = ["不住宿", "不住宿", "當天來回", "一日遊", "no accommodation"]
        user_input_lower = story.preference.themes if hasattr(story, 'user_input') else []
        if any(keyword in str(user_input_lower).lower() for keyword in no_accommodation_keywords):
            return None
            
        # 每天都需要住宿推薦（除了最後一天，因為最後一天不需要過夜）
        if day_num >= story.days - 1:
            return None
            
        # 檢查用戶是否要求環保住宿
        prefer_eco = any("環保" in theme.lower() or "eco" in theme.lower() for theme in story.preference.themes)
        
        # 從資料庫獲取住宿推薦
        from ...infrastructure.persistence.database import SessionLocal
        from ...infrastructure.repositories.postgres_place_repo import PostgresPlaceRepository
        from ...infrastructure.persistence.orm_models import Accommodation as OrmAccommodation
        from sqlalchemy import func
        
        db = SessionLocal()
        try:
            if prefer_eco:
                # 優先推薦環保標章住宿
                eco_accommodations = db.query(OrmAccommodation).filter(
                    func.array_to_string(OrmAccommodation.amenities, ',').contains('環保標章')
                ).order_by(OrmAccommodation.rating.desc()).limit(5).all()
                
                if eco_accommodations:
                    # 根據天數選擇不同的環保住宿，避免重複
                    acc = eco_accommodations[day_num % len(eco_accommodations)]
                    print(f"🌱 第{day_num+1}天推薦環保住宿: {acc.name} (評分: {acc.rating})")
                    return Accommodation(
                        place_id=str(acc.id),
                        name=acc.name,
                        check_in="15:00",
                        check_out="11:00", 
                        nights=1,  # 每天都是1晚
                        type=acc.type
                    )
            
            # 如果沒有環保住宿或用戶沒有特別要求，推薦一般住宿
            accommodations = db.query(OrmAccommodation).order_by(
                OrmAccommodation.rating.desc()
            ).limit(10).all()
            
            if accommodations:
                # 根據天數選擇不同的住宿，避免重複
                acc = accommodations[day_num % len(accommodations)]
                print(f"🏨 第{day_num+1}天推薦住宿: {acc.name} (評分: {acc.rating})")
                return Accommodation(
                    place_id=str(acc.id),
                    name=acc.name,
                    check_in="15:00",
                    check_out="11:00",
                    nights=1,  # 每天都是1晚
                    type=acc.type
                )
                
        except Exception as e:
            print(f"❌ 獲取住宿推薦失敗: {e}")
        finally:
            db.close()
            
        return None

# 建立一個單例供應用程式使用
greedy_planner = GreedyPlanner()
