# 센서 시야와 보정 확인

[공식 센서 사양](https://x2-aimdk.agibot.com/en/latest/about_agibot_X2/sensor_fov.html#id2)에서 관련 센서의 사양·조건을 직접 확인한다. 이 파일에는 제조사 FOV 수치표를 복제하지 않았다. [좌표계와 기체 보정](https://x2-aimdk.agibot.com/en/latest/about_agibot_X2/coordinate_system.html)도 필요한 부분만 읽는다.

컬러와 깊이 FOV를 구분하고, 사양값과 실제 크롭·회전·왜곡 보정 후 유효 시야를 구분한다. 특정 기체의 센서 배치를 전체 기종에 일반화하지 않는다. 정밀 투영·거리·좌표 변환은 실제 CameraInfo, 해상도, 단위, 왜곡 모델과 해당 기체의 보정값으로 계산한다.

공식 문서를 열 수 없으면 명목 FOV를 추측하지 않는다. 일반적인 투영 원리는 가정을 밝히고 설명할 수 있으나 X2의 검증된 수치로 제시하지 않는다. 영상 형식인 encoding과 거리 단위·스케일을 별도로 확인한다.
