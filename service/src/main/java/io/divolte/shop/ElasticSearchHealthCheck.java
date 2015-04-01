package io.divolte.shop;

import static org.elasticsearch.common.unit.TimeValue.timeValueMillis;
import io.divolte.shop.catalog.DataAccess;

import java.util.concurrent.TimeUnit;

import org.elasticsearch.ElasticsearchException;
import org.elasticsearch.action.admin.indices.stats.IndicesStatsResponse;
import org.elasticsearch.client.Client;
import org.elasticsearch.common.unit.TimeValue;

import com.codahale.metrics.health.HealthCheck;

public class ElasticSearchHealthCheck extends HealthCheck {
    private static final TimeValue MAX_ES_RESPONSE_TIME = timeValueMillis(300);
    private final Client esClient;

    public ElasticSearchHealthCheck(final Client esClient) {
        this.esClient = esClient;
    }

    @Override
    protected Result check() throws Exception {
        try {
            IndicesStatsResponse response = esClient
                    .admin()
                    .indices()
                    .prepareStats(DataAccess.CATALOG_INDEX)
                    .execute()
                    .get(MAX_ES_RESPONSE_TIME.millis(), TimeUnit.MILLISECONDS);
            if (response.getTotal().docs.getCount() == 0) {
                return Result.unhealthy("Zero items found in catalog");
            }
        } catch (ElasticsearchException ee) {
            // Also occurs in case of timeout
            return Result.unhealthy(ee.getMessage());
        }

        return Result.healthy();
    }
}
