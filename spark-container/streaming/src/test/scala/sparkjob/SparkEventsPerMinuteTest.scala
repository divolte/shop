package sparkjob

import com.holdenkarau.spark.testing.{
  SharedSparkContext,
  StructuredStreamingBase
}
import org.apache.spark.sql.Dataset
import org.scalatest.FunSuite
import sparkjob.Parameters._

class SparkEventsPerMinuteTest
    extends FunSuite
    with StructuredStreamingBase
    with SharedSparkContext {

  override implicit def reuseContextIfPossible: Boolean = true

  test("Testing window function ") {

    import spark.implicits._
    val input = Seq(Seq(Input("preview", 1538143025000L)),
                    Seq(Input("preview", 1538143027000L)),
                    Seq(Input("pageView", 1538143025000L)))

    val expected = Seq(
      WindowOutput("preview", "[2018-09-28 15:57:00, 2018-09-28 15:58:00]", 2),
      WindowOutput("pageView", "[2018-09-28 15:57:00, 2018-09-28 15:58:00]", 1)
    )

    def compute(input: Dataset[Input]): Dataset[WindowOutput] = {
      SparkEventsPerMinute.runQuery(input.toDF()).as[WindowOutput]
    }

    testSimpleStreamEndState(spark, input, expected, "update", compute)

  }

}
