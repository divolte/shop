package sparkjob

import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types.TimestampType

object SparkEventsPerMinute extends SparkJob {

  def runQuery(df: DataFrame): DataFrame = {

    df.select(col("eventType"),
              (col("timestamp") / 1000).cast(TimestampType).alias("ts"))
      .withWatermark("ts", "2 minutes")
      .groupBy(window(col("ts"), "1 minute"), col("eventType"))
      .count()
  }

}
