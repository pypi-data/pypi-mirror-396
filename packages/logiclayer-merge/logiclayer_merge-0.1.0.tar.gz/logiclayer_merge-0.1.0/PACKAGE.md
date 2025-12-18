<p>
<a href="https://pypi.org/project/logiclayer-merge/"><img src="https://flat.badgen.net/pypi/v/logiclayer-merge" /></a>
<a href="https://github.com/Datawheel/logiclayer-merge/"><img src="https://flat.badgen.net/static/github/repo/green?icon=github" /></a>
<a href="https://github.com/Datawheel/logiclayer-merge/issues"><img src="https://flat.badgen.net/static/github/issues/blue?icon=github" /></a>
</p>

## Getting started

This module must be used with [LogicLayer](https://pypi.org/project/logiclayer). An instance of `OlapServer` from the `tesseract_olap` package is optional to retrieve the data.

```python
# app.py

__title__ = "logiclayer-merge"
__description__ = "Logiclayer-Merge instance"

import os
import logging

from logiclayer import LogicLayer
from src.logiclayer_merge import MergeModule
from tesseract_olap import OlapServer

logging.basicConfig(level=logging.DEBUG)

olap_backend = os.environ["TESSERACT_BACKEND"]
olap_schema = os.environ["TESSERACT_SCHEMA"]
allowed_domains = os.environ.get("ALLOWED_DOMAINS", "")

olap = OlapServer(backend=olap_backend, schema=olap_schema)
mod = MergeModule(olap=olap, allowed_domains=allowed_domains)
mod.startup_tasks()
layer = LogicLayer()
layer.add_module('/merge', mod)
```

---
&copy; 2022 [Datawheel, LLC.](https://www.datawheel.us/)  
This project is licensed under [MIT](./LICENSE).