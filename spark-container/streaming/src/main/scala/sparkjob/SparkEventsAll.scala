package sparkjob

import org.apache.spark.sql.DataFrame

object SparkEventsAll extends SparkJob {

  def runQuery(df: DataFrame): DataFrame = {
    df
  }

}
