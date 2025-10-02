"""DuckDB 데이터베이스 스키마 및 관리

주식 시계열 데이터와 메타데이터를 저장하기 위한 DuckDB 스키마
"""

import logging
from pathlib import Path

import duckdb
import pandas as pd
from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """DuckDB 데이터베이스 관리 클래스"""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.DUCKDB_PATH
        self.connection: duckdb.DuckDBPyConnection | None = None

        # 데이터베이스 디렉토리 생성
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()

    def connect(self) -> None:
        """데이터베이스 연결"""
        if self.connection is None:
            self.connection = duckdb.connect(self.db_path)
            self._create_tables()
            logger.info(f"데이터베이스 연결됨: {self.db_path}")

    def close(self) -> None:
        """데이터베이스 연결 종료"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("데이터베이스 연결 종료됨")

    def _create_tables(self) -> None:
        """테이블 생성"""
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        # 주식 마스터 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS stocks (
                symbol VARCHAR PRIMARY KEY,
                name VARCHAR,
                sector VARCHAR,
                industry VARCHAR,
                market_cap BIGINT,
                country VARCHAR,
                currency VARCHAR,
                exchange VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # 일일 주가 데이터 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_prices (
                symbol VARCHAR,
                date DATE,
                open DECIMAL(12, 4),
                high DECIMAL(12, 4),
                low DECIMAL(12, 4),
                close DECIMAL(12, 4),
                adjusted_close DECIMAL(12, 4),
                volume BIGINT,
                dividend_amount DECIMAL(8, 4) DEFAULT 0,
                split_coefficient DECIMAL(8, 4) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, date)
            )
        """
        )

        # 인트라데이 데이터 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS intraday_prices (
                symbol VARCHAR,
                datetime TIMESTAMP,
                interval_type VARCHAR,  -- '1min', '5min', '15min', '30min', '60min'
                open DECIMAL(12, 4),
                high DECIMAL(12, 4),
                low DECIMAL(12, 4),
                close DECIMAL(12, 4),
                volume BIGINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, datetime, interval_type)
            )
        """
        )

        # 백테스트 결과 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS backtest_results (
                id VARCHAR PRIMARY KEY,
                strategy_name VARCHAR,
                symbols VARCHAR[],  -- 배열로 여러 심볼 지원
                start_date DATE,
                end_date DATE,
                initial_cash DECIMAL(15, 2),
                final_value DECIMAL(15, 2),
                total_return DECIMAL(8, 4),
                annual_return DECIMAL(8, 4),
                volatility DECIMAL(8, 4),
                sharpe_ratio DECIMAL(8, 4),
                max_drawdown DECIMAL(8, 4),
                parameters JSON,  -- 전략 파라미터
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # 거래 기록 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id VARCHAR PRIMARY KEY,
                backtest_id VARCHAR,
                symbol VARCHAR,
                datetime TIMESTAMP,
                action VARCHAR,  -- 'BUY', 'SELL'
                quantity INTEGER,
                price DECIMAL(12, 4),
                commission DECIMAL(8, 4) DEFAULT 0,
                value DECIMAL(15, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (backtest_id) REFERENCES backtest_results(id)
            )
        """
        )

        # 인덱스 생성
        self._create_indexes()
        logger.info("데이터베이스 테이블 생성 완료")

    def _create_indexes(self) -> None:
        """인덱스 생성"""
        if not self.connection:
            return

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_daily_prices_symbol ON daily_prices(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_daily_prices_date ON daily_prices(date)",
            "CREATE INDEX IF NOT EXISTS idx_intraday_prices_symbol ON intraday_prices(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_intraday_prices_datetime ON intraday_prices(datetime)",
            "CREATE INDEX IF NOT EXISTS idx_trades_backtest_id ON trades(backtest_id)",
            "CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_trades_datetime ON trades(datetime)",
        ]

        for index_sql in indexes:
            self.connection.execute(index_sql)

    def insert_stock_info(self, symbol: str, info: dict) -> None:
        """주식 정보 삽입/업데이트"""
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        self.connection.execute(
            """
            INSERT OR REPLACE INTO stocks
            (symbol, name, sector, industry, market_cap, country, currency, exchange, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
            [
                symbol,
                info.get("Name", ""),
                info.get("Sector", ""),
                info.get("Industry", ""),
                (
                    int(info.get("MarketCapitalization", 0))
                    if info.get("MarketCapitalization")
                    else None
                ),
                info.get("Country", ""),
                info.get("Currency", ""),
                info.get("Exchange", ""),
            ],
        )
        logger.info(f"주식 정보 저장됨: {symbol}")

    def insert_daily_prices(self, df: pd.DataFrame) -> int:
        """일일 주가 데이터 삽입"""
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        if df.empty:
            return 0

        # 필요한 컬럼만 선택하고 정렬
        required_columns = [
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "adjusted_close",
            "volume",
            "dividend_amount",
            "split_coefficient",
        ]

        # 인덱스를 date 컬럼으로 변환
        df_copy = df.copy()
        df_copy["date"] = df_copy.index.to_series().dt.date

        # 필요한 컬럼만 선택
        df_insert = df_copy[["date"] + required_columns].copy()

        # ON CONFLICT DO UPDATE 대신 INSERT OR REPLACE 사용
        rows_inserted = 0
        for _, row in df_insert.iterrows():
            self.connection.execute(
                """
                INSERT OR REPLACE INTO daily_prices
                (symbol, date, open, high, low, close, adjusted_close, volume,
                 dividend_amount, split_coefficient)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    row["symbol"],
                    row["date"],
                    row["open"],
                    row["high"],
                    row["low"],
                    row["close"],
                    row["adjusted_close"],
                    row["volume"],
                    row["dividend_amount"],
                    row["split_coefficient"],
                ],
            )
            rows_inserted += 1

        logger.info(f"일일 주가 데이터 {rows_inserted}건 저장됨")
        return rows_inserted

    def insert_intraday_prices(self, df: pd.DataFrame, interval_type: str) -> int:
        """인트라데이 주가 데이터 삽입"""
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        if df.empty:
            return 0

        # 필요한 컬럼만 선택
        required_columns = ["symbol", "open", "high", "low", "close", "volume"]

        # 인덱스를 datetime 컬럼으로 변환
        df_copy = df.copy()
        df_copy["datetime"] = df_copy.index
        df_copy["interval_type"] = interval_type

        # 필요한 컬럼만 선택
        df_insert = df_copy[["datetime", "interval_type"] + required_columns].copy()

        rows_inserted = 0
        for _, row in df_insert.iterrows():
            self.connection.execute(
                """
                INSERT OR REPLACE INTO intraday_prices
                (symbol, datetime, interval_type, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    row["symbol"],
                    row["datetime"],
                    row["interval_type"],
                    row["open"],
                    row["high"],
                    row["low"],
                    row["close"],
                    row["volume"],
                ],
            )
            rows_inserted += 1

        logger.info(f"인트라데이 주가 데이터 {rows_inserted}건 저장됨")
        return rows_inserted

    def get_daily_prices(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        """일일 주가 데이터 조회"""
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        query = """
            SELECT date, symbol, open, high, low, close, adjusted_close,
                   volume, dividend_amount, split_coefficient
            FROM daily_prices
            WHERE symbol = ?
        """
        params = [symbol]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date"

        df = self.connection.execute(query, params).df()

        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)

        return df

    def get_available_symbols(self) -> list[str]:
        """사용 가능한 심볼 목록 조회"""
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        result = self.connection.execute(
            """
            SELECT DISTINCT symbol FROM daily_prices ORDER BY symbol
        """
        ).fetchall()

        return [row[0] for row in result]

    def get_data_range(self, symbol: str) -> tuple[str | None, str | None]:
        """특정 심볼의 데이터 기간 조회"""
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        result = self.connection.execute(
            """
            SELECT MIN(date) as start_date, MAX(date) as end_date
            FROM daily_prices
            WHERE symbol = ?
        """,
            [symbol],
        ).fetchone()

        if result:
            return result[0], result[1]
        return None, None

    def save_backtest_result(self, result_data: dict) -> str:
        """백테스트 결과 저장"""
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        import json
        import uuid

        result_id = str(uuid.uuid4())

        self.connection.execute(
            """
            INSERT INTO backtest_results
            (id, strategy_name, symbols, start_date, end_date, initial_cash,
             final_value, total_return, annual_return, volatility, sharpe_ratio,
             max_drawdown, parameters)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                result_id,
                result_data["strategy_name"],
                result_data["symbols"],
                result_data["start_date"],
                result_data["end_date"],
                result_data["initial_cash"],
                result_data["final_value"],
                result_data["total_return"],
                result_data["annual_return"],
                result_data["volatility"],
                result_data["sharpe_ratio"],
                result_data["max_drawdown"],
                json.dumps(result_data.get("parameters", {})),
            ],
        )

        logger.info(f"백테스트 결과 저장됨: {result_id}")
        return result_id


def get_database() -> DatabaseManager:
    """데이터베이스 매니저 인스턴스 생성"""
    return DatabaseManager()


if __name__ == "__main__":
    # 사용 예시
    with DatabaseManager() as db:
        # 테이블 생성 확인
        symbols = db.get_available_symbols()
        print(f"사용 가능한 심볼: {symbols}")

        # 데이터 기간 확인
        for symbol in symbols[:3]:  # 처음 3개만
            start, end = db.get_data_range(symbol)
            print(f"{symbol}: {start} ~ {end}")
