package sparkjob

import org.apache.avro.Schema
import org.apache.avro.io.DatumReader
import org.apache.avro.io.Decoder
import org.apache.avro.specific.SpecificDatumReader
import org.apache.avro.generic.GenericRecord
import org.apache.avro.io.DecoderFactory
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import com.databricks.spark.avro.SchemaConverters
import org.apache.spark.sql.types._
import scala.collection.JavaConverters._
import scopt.OptionParser

case class Config(broker: String = "lcoalhost:9092",
                  topic: String = "divolte",
                  group: String = "divolte_spark_streaming")

object SparkJobKafka {

  def convertSchemaToStructType(schema: Schema): StructType = {
    val schemaFields = schema
      .getFields()
      .asScala
      .map(field =>
        StructField(field.name(),
                    SchemaConverters.toSqlType(field.schema()).dataType))
    StructType(schemaFields)
  }

  def getAvroSchema: Schema = {
    val schemaFile = getClass().getResourceAsStream("/ShopEventRecord.avsc") //new java.io.File(schemaName)
    Schema.parse(schemaFile)
  }

  val reader: DatumReader[GenericRecord] =
    new SpecificDatumReader[GenericRecord](getAvroSchema)

  def parseMessage(message: Array[Byte]): String = {
    val decoder: Decoder = DecoderFactory.get().binaryDecoder(message, null)
    val messageData: GenericRecord = reader.read(null, decoder)
    return messageData.toString
  }

  def parseMessageUDF = udf(parseMessage _)

  val parser = new OptionParser[Config]("Spark-ETL") {
    head("Spark-ETL", "Process Divolte events")
    opt[String]('b', "broker").action((x, c) => c.copy(broker = x))
    opt[String]('t', "topic").action((x, c) => c.copy(topic = x))
    opt[String]('g', "group").action((x, c) => c.copy(group = x))

  }

  def run(kafkaParams: Map[String, String]): Unit = {

    val spark = SparkSession.builder().appName("Spark-ETL").getOrCreate()
    println("spark session passed")
    val jsonSchema = convertSchemaToStructType(getAvroSchema)
    println("json schema passed")

    val kafkaStream =
      spark.readStream.format("kafka").options(kafkaParams).load()

    val parsedStream = kafkaStream
      .select(parseMessageUDF(col("value")).alias("record"))
      .select(from_json(col("record"), jsonSchema).alias("json"))
      .select(col("json.*"))
    val query = parsedStream.writeStream.format("console").start()
    query.awaitTermination()

    spark.stop()
  }

  def main(args: Array[String]): Unit = {

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
}
