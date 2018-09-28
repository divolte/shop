package sparkjob

package object Parameters {
  case class Input(eventType: String, timestamp: Long)
  case class WindowOutput(eventType: String, window: String, count: Long)

}
