import com.databricks.spark.avro._

val df = spark.read.format("com.databricks.spark.avro").load("data/generate/mount-data/finished")

df.show()

df.count()
                                           
df.select("sessionId").distinct.count()
