# File: airflow_provider_intersystems_iris/sensors/iris_sensor.py

from typing import Any, Optional
from airflow.sensors.base import BaseSensorOperator
from airflow_provider_iris.hooks.iris_hook import IrisHook
from sqlalchemy import text


class IrisSensor(BaseSensorOperator):
    """
    Generic InterSystems IRIS SQL Sensor.

    Waits until a SQL query:
      • Returns at least one row                     → expected_result=None (default)
      • First column value == expected_result        → exact match
      • First column value within tolerance          → numeric tolerance

    Perfect for:
      • Waiting for bulk loads (e.g. AirflowDemo.BulkSales)
      • Waiting for flags in control tables
      • Waiting for row count thresholds
      • Waiting for class method results via SQL projection
    """

    template_fields = ("sql", "expected_result", "tolerance")
    ui_color = "#0066CC"  # Official InterSystems IRIS blue

    def __init__(
        self,
        *,
        sql: str,
        iris_conn_id: str = "iris_default",
        expected_result: Optional[Any] = None,
        tolerance: Optional[float] = None,
        poke_interval: float = 300.0,
        timeout: float = 6 * 3600,
        mode: str = "reschedule",
        **kwargs,
    ):
        super().__init__(
            poke_interval=poke_interval,
            timeout=timeout,
            mode=mode,
            **kwargs,
        )
        self.sql = sql
        self.iris_conn_id = iris_conn_id
        self.expected_result = expected_result
        self.tolerance = tolerance

    def poke(self, context: Any) -> bool:
        hook = IrisHook(iris_conn_id=self.iris_conn_id)
        engine = hook.get_engine()

        self.log.info(f"Executing sensor query: {self.sql.strip()}")

        try:
            with engine.connect() as conn:
                result = conn.execute(text(self.sql))
                row = result.fetchone()

                if not row or row[0] is None:
                    self.log.info("Query returned no result or NULL. Retrying...")
                    return False

                value = row[0]

                # Case 1: Just wait for any non-null row
                if self.expected_result is None:
                    self.log.info(f"Success! Query returned value: {value}")
                    return True

                # Case 2: Numeric tolerance
                if self.tolerance is not None:
                    try:
                        diff = abs(float(value) - float(self.expected_result))
                        success = diff <= float(self.tolerance)
                        self.log.info(f"Value {value} ≈ {self.expected_result} (±{self.tolerance}) → {success}")
                        return success
                    except (ValueError, TypeError):
                        self.log.warning("Tolerance requested but value not numeric. Falling back to exact match.")

                # Case 3: Exact match
                success = value == self.expected_result
                self.log.info(f"Value '{value}' == '{self.expected_result}' → {success}")
                return success

        except Exception as e:
            self.log.error(f"Error during poke: {e}")
            return False
        finally:
            engine.dispose()