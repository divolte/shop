name := "spark-scala-application"
version := "0.0.1-SNAPSHOT"
organization := "divolte"

scalaVersion := "2.11.11"
val sparkVersion = "2.3.1"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % sparkVersion % Provided,
  "org.apache.spark" %% "spark-sql" % sparkVersion % Provided,
  "org.apache.spark" %% "spark-hive" % sparkVersion % Provided,
  "org.apache.spark" %% "spark-streaming" % sparkVersion % Provided,
  "org.scalatest" %% "scalatest" % "2.2.1" % "test",
  "org.apache.spark" %% "spark-sql-kafka-0-10" % sparkVersion,
  "com.databricks" %% "spark-avro" % "4.0.0",
  "com.github.scopt" %% "scopt" % "3.7.0"
)

// test run settings
//parallelExecution in Test := false
assembly / test := {}

// Measure time for each test
Test / testOptions += Tests.Argument("-oD")

scalafmtOnCompile in ThisBuild := true

assemblyMergeStrategy in assembly := {
  case PathList("META-INF", "MANIFEST.MF", xs @ _*) => MergeStrategy.discard
  case PathList("META-INF", xs @ _*)                => MergeStrategy.concat
  case x                                            => MergeStrategy.first

}
