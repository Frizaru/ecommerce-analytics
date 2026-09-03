import pandas as pd

import ecommerce_product_analytics


def test_project_package_and_pandas_are_importable() -> None:
    assert ecommerce_product_analytics.__version__ == "0.1.0"
    assert int(pd.__version__.split(".")[0]) >= 2
