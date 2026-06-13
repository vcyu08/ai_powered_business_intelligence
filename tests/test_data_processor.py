import pytest

from data_processor import DataProcessor

CSV_CONTENT = (
    "Date,Product,Region,Sales,Customer_Age,Customer_Gender,Customer_Satisfaction\n"
    "2024-01-15,Widget A,North,100.0,30,Male,4.0\n"
    "2024-01-20,Widget B,South,200.0,25,Female,3.5\n"
    "2024-02-10,Widget A,East,150.0,40,Male,4.5\n"
    "2024-02-15,Widget C,West,300.0,35,Female,5.0\n"
    "2024-03-05,Widget D,North,250.0,50,Male,3.0\n"
    "2024-03-20,Widget B,East,180.0,28,Female,4.0\n"
)

EXPECTED_TOTAL = 100.0 + 200.0 + 150.0 + 300.0 + 250.0 + 180.0
VALID_PRODUCTS = {"Widget A", "Widget B", "Widget C", "Widget D"}


@pytest.fixture
def csv_file(tmp_path):
    path = tmp_path / "test_sales.csv"
    path.write_text(CSV_CONTENT)
    return str(path)


@pytest.fixture
def loaded_dp(csv_file):
    dp = DataProcessor(csv_file)
    dp.load_data()
    return dp


@pytest.fixture
def computed_dp(loaded_dp):
    loaded_dp.compute_statistics()
    return loaded_dp


def test_load_data_required_columns(loaded_dp):
    required = {
        "Date", "Product", "Region", "Sales",
        "Customer_Age", "Customer_Gender", "Customer_Satisfaction",
    }
    assert required.issubset(set(loaded_dp.df.columns))


def test_load_data_row_count(loaded_dp):
    assert len(loaded_dp.df) == 6


def test_compute_statistics_total_sales(computed_dp):
    assert abs(computed_dp.stats["total_sales"] - EXPECTED_TOTAL) < 1e-6


def test_compute_statistics_total_records(computed_dp):
    assert computed_dp.stats["total_records"] == 6


def test_compute_statistics_top_product(computed_dp):
    assert computed_dp.stats["top_product"] in VALID_PRODUCTS


def test_compute_statistics_avg_sales_bounds(computed_dp):
    stats = computed_dp.stats
    df = computed_dp.df
    assert df["Sales"].min() <= stats["avg_sales"] <= df["Sales"].max()


def test_create_documents_count(computed_dp):
    docs = computed_dp.create_documents()
    assert len(docs) == 11


def test_create_documents_overview_present(computed_dp):
    docs = computed_dp.create_documents()
    overview = [d for d in docs if d.metadata["category"] == "overview"]
    assert len(overview) == 1


def test_create_documents_all_categories(computed_dp):
    docs = computed_dp.create_documents()
    categories = {d.metadata["category"] for d in docs}
    assert categories == {"overview", "product", "region", "time_series", "customer"}
