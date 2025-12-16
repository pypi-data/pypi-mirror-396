import argparse
import os
from typing import List, Optional, Union

from GetStockNews import OutputFormat
from run_get_stock_news import run_get_stock_news


def main() -> None:
    parser = argparse.ArgumentParser(description="https://github.com/abin-trading/GetStockNews CLI")
    parser.add_argument("-f", "--folder", default=os.getcwd(), help="新聞儲存根目錄")
    parser.add_argument("--from", dest="from_date", help="起始日期")
    parser.add_argument("--to", dest="to_date", help="結束日期")
    parser.add_argument("-l", "--limit", type=int, help="每檔股票爬取筆數")
    parser.add_argument(
        "-s",
        "--target",
        "--code",
        dest="targets",
        action="append",
        help="股票代碼（4位數）或關鍵字，可重複指定多筆",
    )
    parser.add_argument(
        "--latest",
        dest="update_latest",
        action="store_true",
        help="從現有資料延伸到最新日期",
    )
    parser.add_argument(
        "--output-format",
        choices=[fmt.value for fmt in OutputFormat],
        default=OutputFormat.PARQUET.value,
        help="輸出格式：csv or parquet",
    )
    args = parser.parse_args()

    run_get_stock_news(
        folder=args.folder,
        from_date=args.from_date,
        to_date=args.to_date,
        limit=args.limit,
        targets=args.targets,
        update_latest=args.update_latest,
        output_format=args.output_format,
    )


if __name__ == "__main__":
    main()
