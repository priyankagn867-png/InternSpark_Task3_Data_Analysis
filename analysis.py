from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "data" / "sales.csv"
OUTPUT_DIR = BASE / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_and_clean():
    df = pd.read_csv(DATA_FILE)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    numeric_cols = ["Quantity", "UnitPrice", "Discount"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["OrderID", "Date", "Region", "Category", "Quantity", "UnitPrice"])
    df["Discount"] = df["Discount"].fillna(0).clip(lower=0, upper=1)
    df = df[df["Quantity"] > 0]
    df["GrossSales"] = df["Quantity"] * df["UnitPrice"]
    df["NetSales"] = df["GrossSales"] * (1 - df["Discount"])
    return df

def generate_report(df):
    region_summary = (
        df.groupby("Region", as_index=False)["NetSales"]
        .sum()
        .sort_values("NetSales", ascending=False)
    )

    category_summary = (
        df.groupby("Category", as_index=False)["NetSales"]
        .sum()
        .sort_values("NetSales", ascending=False)
    )

    product_summary = (
        df.groupby("Product", as_index=False)["NetSales"]
        .sum()
        .sort_values("NetSales", ascending=False)
    )

    monthly = (
        df.assign(Month=df["Date"].dt.to_period("M").astype(str))
        .groupby("Month", as_index=False)["NetSales"]
        .sum()
    )

    region_summary.to_csv(OUTPUT_DIR / "region_summary.csv", index=False)
    category_summary.to_csv(OUTPUT_DIR / "category_summary.csv", index=False)
    product_summary.to_csv(OUTPUT_DIR / "product_summary.csv", index=False)
    monthly.to_csv(OUTPUT_DIR / "monthly_summary.csv", index=False)

    plt.figure(figsize=(8, 5))
    plt.bar(region_summary["Region"], region_summary["NetSales"])
    plt.title("Net Sales by Region")
    plt.xlabel("Region")
    plt.ylabel("Net Sales")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "sales_by_region.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.bar(category_summary["Category"], category_summary["NetSales"])
    plt.title("Net Sales by Category")
    plt.xlabel("Category")
    plt.ylabel("Net Sales")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "sales_by_category.png", dpi=160)
    plt.close()

    print("=== Data Analysis Summary ===")
    print(f"Rows after cleaning: {len(df)}")
    print(f"Total net sales: ₹{df['NetSales'].sum():,.2f}")
    print(f"Average order net sales: ₹{df['NetSales'].mean():,.2f}")
    print("\nSales by region:")
    print(region_summary.to_string(index=False))
    print("\nSales by category:")
    print(category_summary.to_string(index=False))
    print("\nTop products:")
    print(product_summary.head(5).to_string(index=False))

    insights = [
        f"Total net sales across cleaned records: ₹{df['NetSales'].sum():,.2f}.",
        f"Highest-sales region: {region_summary.iloc[0]['Region']} (₹{region_summary.iloc[0]['NetSales']:,.2f}).",
        f"Highest-sales category: {category_summary.iloc[0]['Category']} (₹{category_summary.iloc[0]['NetSales']:,.2f}).",
        f"Top product by net sales: {product_summary.iloc[0]['Product']} (₹{product_summary.iloc[0]['NetSales']:,.2f}).",
        f"Average order net sales: ₹{df['NetSales'].mean():,.2f}.",
    ]
    (OUTPUT_DIR / "insights.txt").write_text("\n".join(insights), encoding="utf-8")

def main():
    df = load_and_clean()
    generate_report(df)
    print(f"\nOutputs saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
