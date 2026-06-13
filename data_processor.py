import logging

import pandas as pd
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "Date", "Product", "Region", "Sales",
    "Customer_Age", "Customer_Gender", "Customer_Satisfaction",
}


class DataProcessor:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df: pd.DataFrame | None = None
        self.stats: dict | None = None

    def load_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.csv_path)
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
        self.df = df
        logger.warning("Loaded %d records from %s", len(df), self.csv_path)
        return df

    def compute_statistics(self) -> dict:
        if self.df is None:
            raise RuntimeError("Call load_data() before compute_statistics()")
        df = self.df

        product_breakdown = (
            df.groupby("Product")["Sales"]
            .agg(["sum", "mean", "count"])
            .reset_index()
        )

        regional_breakdown = (
            df.groupby("Region")["Sales"]
            .agg(["sum", "mean", "count"])
            .reset_index()
        )

        monthly_series = df.resample("ME", on="Date")["Sales"].sum()
        monthly_sales = {str(k)[:7]: float(v) for k, v in monthly_series.items()}

        age_groups = pd.cut(
            df["Customer_Age"],
            bins=[0, 25, 35, 45, 55, 100],
            labels=["18-25", "26-35", "36-45", "46-55", "55+"],
        )
        age_group_breakdown = (
            df.assign(AgeGroup=age_groups)
            .groupby("AgeGroup", observed=True)
            .agg(
                count=("Sales", "count"),
                avg_satisfaction=("Customer_Satisfaction", "mean"),
            )
            .reset_index()
        )

        satisfaction_pivot = df.pivot_table(
            values="Customer_Satisfaction",
            index="Product",
            columns="Region",
            aggfunc="mean",
        )

        self.stats = {
            "total_sales": float(df["Sales"].sum()),
            "total_records": int(len(df)),
            "avg_sales": float(df["Sales"].mean()),
            "top_product": str(df.groupby("Product")["Sales"].sum().idxmax()),
            "top_region": str(df.groupby("Region")["Sales"].sum().idxmax()),
            "product_breakdown": product_breakdown,
            "regional_breakdown": regional_breakdown,
            "monthly_sales": monthly_sales,
            "age_group_breakdown": age_group_breakdown,
            "satisfaction_pivot": satisfaction_pivot,
        }
        return self.stats

    def create_documents(self) -> list[Document]:
        if self.df is None or self.stats is None:
            raise RuntimeError(
                "Call load_data() and compute_statistics() before create_documents()"
            )
        df = self.df
        stats = self.stats
        total = stats["total_sales"]
        docs: list[Document] = []

        # Overview document
        best_month = max(stats["monthly_sales"], key=stats["monthly_sales"].get)
        docs.append(Document(
            page_content=(
                f"Business Overview: Total sales: ${total:,.2f}. "
                f"Total transactions: {stats['total_records']:,}. "
                f"Average sale: ${stats['avg_sales']:,.2f}. "
                f"Top performing product: {stats['top_product']}. "
                f"Top performing region: {stats['top_region']}. "
                f"Best sales month: {best_month} "
                f"(${stats['monthly_sales'][best_month]:,.2f})."
            ),
            metadata={"category": "overview", "source": "sales_data.csv"},
        ))

        # Product documents
        for _, row in stats["product_breakdown"].iterrows():
            pct = (row["sum"] / total * 100) if total > 0 else 0.0
            docs.append(Document(
                page_content=(
                    f"Product: {row['Product']}. "
                    f"Total sales: ${row['sum']:,.2f} ({pct:.1f}% of total). "
                    f"Average sale: ${row['mean']:,.2f}. "
                    f"Transaction count: {int(row['count']):,}."
                ),
                metadata={"category": "product", "source": "sales_data.csv"},
            ))

        # Region documents
        for _, row in stats["regional_breakdown"].iterrows():
            pct = (row["sum"] / total * 100) if total > 0 else 0.0
            docs.append(Document(
                page_content=(
                    f"Region: {row['Region']}. "
                    f"Total sales: ${row['sum']:,.2f} ({pct:.1f}% of total). "
                    f"Average sale: ${row['mean']:,.2f}. "
                    f"Transaction count: {int(row['count']):,}."
                ),
                metadata={"category": "region", "source": "sales_data.csv"},
            ))

        # Time series document
        monthly_items = sorted(stats["monthly_sales"].items())
        monthly_str = "; ".join(f"{m}: ${v:,.2f}" for m, v in monthly_items)
        docs.append(Document(
            page_content=f"Monthly sales trend (chronological): {monthly_str}.",
            metadata={"category": "time_series", "source": "sales_data.csv"},
        ))

        # Customer document
        gender_counts = df["Customer_Gender"].value_counts().to_dict()
        gender_str = ", ".join(f"{g}: {c}" for g, c in gender_counts.items())
        avg_sat = float(df["Customer_Satisfaction"].mean())
        age_str = "; ".join(
            f"{row['AgeGroup']}: {int(row['count'])} customers "
            f"(avg satisfaction {row['avg_satisfaction']:.2f})"
            for _, row in stats["age_group_breakdown"].iterrows()
        )
        docs.append(Document(
            page_content=(
                f"Customer demographics: Gender breakdown: {gender_str}. "
                f"Overall average satisfaction: {avg_sat:.2f}/5. "
                f"Age group breakdown: {age_str}."
            ),
            metadata={"category": "customer", "source": "sales_data.csv"},
        ))

        return docs
