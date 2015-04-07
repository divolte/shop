mapping {
  map duplicate() onto 'detectedDuplicate'
  map corrupt() onto 'detectedCorruption'
  map firstInSession() onto 'firstInSession'
  map timestamp() onto 'timestamp'
  map clientTimestamp() onto 'clientTimestamp'
  map remoteHost() onto 'remoteHost'
  map referer() onto 'referer'
  map location() onto 'location'
  map viewportPixelWidth() onto 'viewportPixelWidth'
  map viewportPixelHeight() onto 'viewportPixelHeight'
  map screenPixelWidth() onto 'screenPixelWidth'
  map screenPixelHeight() onto 'screenPixelHeight'
  map partyId() onto 'partyId'
  map sessionId() onto 'sessionId'
  map pageViewId() onto 'pageViewId'
  map eventId() onto 'eventId'
  map eventType() onto 'eventType'
  map userAgentString() onto 'userAgentString'

  def ua = userAgent()
  map ua.name() onto 'userAgentName'
  map ua.family() onto 'userAgentFamily'
  map ua.vendor() onto 'userAgentVendor'
  map ua.type() onto 'userAgentType'
  map ua.version() onto 'userAgentVersion'
  map ua.deviceCategory() onto 'userAgentDeviceCategory'
  map ua.osFamily() onto 'userAgentOsFamily'
  map ua.osVersion() onto 'userAgentOsVersion'
  map ua.osVendor() onto 'userAgentOsVendor'

  def locationUri = parse location() to uri
  section {
    when locationUri.path().equalTo('/') apply {
      map 'home' onto 'pageType'
      exit()
    }

    def pathMatcher = match '^/([a-z]+)/([^/]+)?[/]?([^/]+)?.*' against locationUri.path()
    when pathMatcher.matches() apply {
      map pathMatcher.group(1) onto 'pageType'

      when pathMatcher.group(1).equalTo('category') apply {
        map pathMatcher.group(2) onto 'category'
        when pathMatcher.group(3).isAbsent() apply {
          map 0 onto 'page'
        }
        map { parse pathMatcher.group(3) to int32 } onto 'page'
      }

      when pathMatcher.group(1).equalTo('product') apply {
        map pathMatcher.group(2) onto 'productId'
      }

      when pathMatcher.group(1).equalTo('download') apply {
        map pathMatcher.group(2) onto 'downloadId'
      }

      exit()
    }
  }

  when eventType().equalTo('pageView') apply {
    def fragmentUri = parse locationUri.rawFragment() to uri
    map fragmentUri.query().value('source') onto 'source'
  }

  when eventType().equalTo('impression') apply {
    map eventParameters().value('productId') onto 'productId'
    map eventParameters().value('source') onto 'source'    
  }

  section {
    when eventType().equalTo('removeFromBasket') apply {
      map eventParameters().value('item_id') onto 'productId'
      exit()
    }

    when eventType().equalTo('addToBasket') apply {
      map eventParameters().value('item_id') onto 'productId'
      exit()
    }

    when eventType().equalTo('preview') apply {
      map eventParameters().value('item_id') onto 'productId'
      exit()
    }
  }
}
