package sparkjob

import com.holdenkarau.spark.testing.{
  SharedSparkContext,
  StructuredStreamingBase
}
import org.apache.spark.sql.Dataset
import org.scalatest.FunSuite
import sparkjob.Parameters.Input

class SparkEventsAllTest
    extends FunSuite
    with StructuredStreamingBase
    with SharedSparkContext {

  override implicit def reuseContextIfPossible: Boolean = true

  test("Testing all events: input and output df should be the same ") {

    import spark.implicits._
    val input = Seq(Seq(Input("preview", 1500000)),
                    Seq(Input("pageView", 1500000)),
                    Seq(Input("preview", 1500000)))

    val expected = Seq(Input("preview", 1500000),
                       Input("pageView", 1500000),
                       Input("preview", 1500000))

    def compute(input: Dataset[Input]): Dataset[Input] = {
      SparkEventsAll.runQuery(input.toDF()).as[Input]
    }

    testSimpleStreamEndState(spark, input, expected, "update", compute)

  }

}
