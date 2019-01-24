package sparkjob

import org.apache.spark.sql.DataFrame

object SparkEventsAll extends SparkJob {

  /**
    * Identity function to output all records in dataframe, useful for debugging
    *
    * @param df
    * @return
    */
  def runQuery(df: DataFrame): DataFrame = {
    df
  }

}
