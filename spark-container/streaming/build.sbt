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
  "org.scalatest" %% "scalatest" % "3.0.1" % "test",
  "org.apache.spark" %% "spark-sql-kafka-0-10" % sparkVersion excludeAll (ExclusionRule(
    organization = "net.jpountz.lz4",
    name = "lz4")),
  "com.databricks" %% "spark-avro" % "4.0.0",
  "com.github.scopt" %% "scopt" % "3.7.0",
  "com.holdenkarau" %% "spark-testing-base" % "2.3.1_0.10.0" % "test" excludeAll (
    ExclusionRule(organization = "org.scalacheck"),
    ExclusionRule(organization = "org.scalactic"),
    ExclusionRule(organization = "org.scalatest")
  )
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
