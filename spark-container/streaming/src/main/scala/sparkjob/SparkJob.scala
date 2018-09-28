package sparkjob

import org.apache.avro.Schema
import org.apache.spark.sql.{DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import com.databricks.spark.avro.SchemaConverters
import org.apache.spark.sql.streaming.DataStreamWriter
import org.apache.spark.sql.types._

import scala.collection.JavaConverters._
import scopt.OptionParser

case class Config(broker: String = "lcoalhost:9092",
                  topic: String = "divolte",
                  group: String = "divolte_spark_streaming")

@SerialVersionUID(1L)
trait SparkJob extends Serializable {

  val decoder = AvroDecoder(getAvroSchema)
  def convertSchemaToStructType(schema: Schema): StructType = {
    val schemaFields = schema.getFields.asScala
      .map(
        field =>
          StructField(field.name(),
                      SchemaConverters.toSqlType(field.schema()).dataType))
    StructType(schemaFields)
  }

  def getAvroSchema: Schema = {
    val schemaFile = getClass.getResourceAsStream("/ShopEventRecord.avsc")
    new Schema.Parser().parse(schemaFile)
  }

  def parseMessage(message: Array[Byte]): String = {
    decoder.decode(message).toString
  }

  def parseMessageUDF = udf[String, Array[Byte]](parseMessage)

  def run(kafkaParams: Map[String, String]): Unit = {

    val spark = SparkSession.builder().appName("Spark-ETL").getOrCreate()

    val jsonSchema = convertSchemaToStructType(decoder.schema)

    val kafkaStream =
      spark.readStream.format("kafka").options(kafkaParams).load()

    val parsedStream = kafkaStream
      .select(parseMessageUDF(col("value")).alias("record"))
      .select(from_json(col("record"), jsonSchema).alias("json"))
      .select(col("json.*"))

    val query = runQuery(parsedStream)
    val stream = writeStreamToOutput(query, "console").start()

    stream.awaitTermination()
    spark.stop()
  }

  def main(args: Array[String]): Unit = {

    val parser = new OptionParser[Config]("Spark-ETL") {
      head("Spark-ETL", "Process Divolte events")
      opt[String]('b', "broker").action((x, c) => c.copy(broker = x))
      opt[String]('t', "topic").action((x, c) => c.copy(topic = x))
      opt[String]('g', "group").action((x, c) => c.copy(group = x))

    }

    parser.parse(args, Config()) match {
      case Some(config) =>
        val kafkaParams = Map[String, String](
          "kafka.bootstrap.servers" -> config.broker,
          "group.id" -> config.group,
          "auto.offset.reset" -> "latest",
          "subscribe" -> config.topic
        )
        run(kafkaParams)
      case None =>
        println("Wrong arguments provided")

    }
  }

  def runQuery(df: DataFrame): DataFrame

  def writeStreamToOutput(df: DataFrame,
                          outputFormat: String): DataStreamWriter[Row] = {
    df.writeStream.outputMode("update").format(outputFormat)
  }
}
