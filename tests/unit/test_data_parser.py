import pytest
import sys
from pathlib import Path

# 修正 sys.path 以便能導入 scripts 目錄下的模組
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root / "scripts"))

from import_data import parse_open_time

@pytest.mark.parametrize("time_str, expected", [
    # 正常情況
    ("週一至週日 11:00-21:00", [
        {"weekday": i, "open_min": 660, "close_min": 1260} for i in range(1, 7)
    ] + [{"weekday": 0, "open_min": 660, "close_min": 1260}]),
    # 多個時段
    ("週二、週四、週五、週六、週日 11:30-14:00、17:00-21:00", [
        {"weekday": 2, "open_min": 690, "close_min": 840},
        {"weekday": 2, "open_min": 1020, "close_min": 1260},
        {"weekday": 4, "open_min": 690, "close_min": 840},
        {"weekday": 4, "open_min": 1020, "close_min": 1260},
        {"weekday": 5, "open_min": 690, "close_min": 840},
        {"weekday": 5, "open_min": 1020, "close_min": 1260},
        {"weekday": 6, "open_min": 690, "close_min": 840},
        {"weekday": 6, "open_min": 1020, "close_min": 1260},
        {"weekday": 0, "open_min": 690, "close_min": 840},
        {"weekday": 0, "open_min": 1020, "close_min": 1260},
    ]),
    # 只有時間，假設每天
    ("10:00-18:00", [
        {"weekday": i, "open_min": 600, "close_min": 1080} for i in range(7)
    ]),
    # 包含公休
    ("週一至週五 09:00-17:00; 週六日公休", [
        {"weekday": i, "open_min": 540, "close_min": 1020} for i in range(1, 6)
    ]),
    # 空字串或無效
    ("", []),
    ("休息", []),
    ("無", []),
])
def test_parse_open_time(time_str, expected):
    # 使用 set 比較，忽略順序
    result = parse_open_time(time_str)
    assert set(tuple(sorted(d.items())) for d in result) == set(tuple(sorted(d.items())) for d in expected)
