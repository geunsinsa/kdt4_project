import math

class Tracker:
    def __init__(self):
        # 객체의 중심 위치와 클래스를 저장하는 딕셔너리
        self.object_info = {}
        # 객체의 ID 수를 추적하는 변수
        # 새로운 객체가 감지될 때마다 카운트가 1씩 증가
        self.id_count = 0

    def update(self, objects_rect, classes):
        # 객체의 바운딩 박스, ID, 클래스를 저장하는 리스트
        objects_bbs_ids_classes = []

        # 새로운 객체의 중심 좌표를 가져옴
        for rect, obj_class in zip(objects_rect, classes):
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # 해당 객체가 이미 감지된 객체인지 확인
            same_object_detected = False
            for id, info in self.object_info.items():
                # 두 중심점 사이의 거리를 계산
                dist = math.hypot(cx - info['center'][0], cy - info['center'][1])

                # 거리가 일정 값 미만이면 같은 객체로 판정
                if dist < 35:
                    self.object_info[id] = {'center': (cx, cy), 'class': obj_class}
                    objects_bbs_ids_classes.append([x, y, w, h, id, obj_class])
                    same_object_detected = True
                    break

            # 새로운 객체가 감지되면 해당 객체에 ID와 클래스를 할당
            if same_object_detected is False:
                self.object_info[self.id_count] = {'center': (cx, cy), 'class': obj_class}
                objects_bbs_ids_classes.append([x, y, w, h, self.id_count, obj_class])
                self.id_count += 1

        # 사용되지 않는 ID를 제거하여 객체 정보 딕셔너리를 정리
        new_object_info = {}
        for obj_bb_id_class in objects_bbs_ids_classes:
            _, _, _, _, object_id, _ = obj_bb_id_class
            info = self.object_info[object_id]
            new_object_info[object_id] = info

        # 사용되지 않는 ID가 제거된 딕셔너리로 업데이트
        self.object_info = new_object_info.copy()
        return objects_bbs_ids_classes