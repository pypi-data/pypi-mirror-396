# `opts-wrds` Package

Implementation Note: When mapping [IvyDB](https://wrds-www.wharton.upenn.edu/pages/about/data-vendors/optionmetrics/), cast strikes immediately to `Decimal`:

```
from decimal import Decimal
# ... inside mapper ...
strike = Decimal(str(row['strike_price'])) / Decimal("1000")
```

