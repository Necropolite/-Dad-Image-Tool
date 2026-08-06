from __future__ import annotations

import app
import providers


def collect_item(item, destination):
    return providers.collect_item(item, destination, app)


app.collect_item = collect_item


if __name__ == "__main__":
    app.main()
