import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from services.announcement_service import AnnouncementService


class App:
    pass


def main():
    app = App()
    app.logger = None
    with open(Path.cwd() / 'launcher' / 'config.json', 'r', encoding='utf-8') as f:
        app.config = json.load(f)
    svc = AnnouncementService(app)
    res = svc.fetch()
    out = json.dumps(res, ensure_ascii=False) if res else 'None'
    print(out)
    try:
        (Path.cwd() / 'launcher' / 'announcement_test_output.txt').write_text(out, encoding='utf-8')
    except Exception:
        pass


if __name__ == '__main__':
    main()
