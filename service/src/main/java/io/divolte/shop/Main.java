package io.divolte.shop;

import io.divolte.shop.catalog.BasketResource;
import io.divolte.shop.catalog.CatalogCategoryResource;
import io.divolte.shop.catalog.DataAccess;
import io.divolte.shop.catalog.CatalogItemResource;
import io.divolte.shop.catalog.CheckoutResource;
import io.dropwizard.Application;
import io.dropwizard.setup.Bootstrap;
import io.dropwizard.setup.Environment;

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.util.EnumSet;

import javax.servlet.DispatcherType;
import javax.servlet.FilterRegistration.Dynamic;

import org.eclipse.jetty.servlets.CrossOriginFilter;
import org.elasticsearch.ElasticsearchException;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.settings.Settings;
import org.elasticsearch.common.transport.InetSocketTransportAddress;

import com.google.common.io.Resources;
import org.elasticsearch.transport.client.PreBuiltTransportClient;

public class Main extends Application<ServiceConfiguration> {

    @Override
    public void initialize(final Bootstrap<ServiceConfiguration> bootstrap) {
    }

    @Override
    public void run(final ServiceConfiguration configuration, final Environment environment) throws Exception {
        enableCrossOriginResourceSharing(environment);

        final TransportClient client = setupElasticSearchClient(configuration);
        createIndexesIfNotExists(client);

        environment.jersey().register(new CatalogItemResource(client));
        environment.jersey().register(new CatalogCategoryResource(client));
        environment.jersey().register(new BasketResource(client));
        environment.jersey().register(new CheckoutResource());

        environment.healthChecks().register("ElasticSearch", new ElasticSearchHealthCheck(client));
    }

    private void createIndexesIfNotExists(TransportClient client) throws ElasticsearchException, IOException {
        if (!client.admin().indices().prepareExists(DataAccess.CATALOG_INDEX).get().isExists()) {
            client.admin().indices()
                    .prepareCreate(DataAccess.CATALOG_INDEX)
                    .setSettings(Resources.toString(Resources.getResource("settings.json"), StandardCharsets.UTF_8))
                    .addMapping(DataAccess.ITEM_DOCUMENT_TYPE,
                            Resources.toString(Resources.getResource("mapping.json"), StandardCharsets.UTF_8))
                    .get();
        }
    }

    private void enableCrossOriginResourceSharing(final Environment environment) {
        Dynamic filter = environment.servlets().addFilter("CORS", CrossOriginFilter.class);
        filter.setInitParameter("allowedOrigins", "*"); // allowed origins comma
                                                        // separated
        filter.setInitParameter("allowedHeaders", "Content-Type,Authorization,X-Requested-With,Content-Length,Accept,Origin");
        filter.setInitParameter("allowedMethods", "GET,PUT,POST,DELETE,OPTIONS,HEAD");
        filter.setInitParameter("preflightMaxAge", "5184000"); // 2 months
        filter.setInitParameter("allowCredentials", "true");
        filter.addMappingForUrlPatterns(EnumSet.allOf(DispatcherType.class), true, "/*");
    }

    private TransportClient setupElasticSearchClient(final ServiceConfiguration configuration) throws UnknownHostException {

        final Settings esSettings = Settings.builder().put("cluster.name", configuration.esClusterName).build();
        final TransportClient client = new PreBuiltTransportClient(esSettings);
        configuration.esHosts.forEach((host) -> {
                    try {
                        client.addTransportAddress(new InetSocketTransportAddress(InetAddress.getByName(host), configuration.esPort));
                    } catch (UnknownHostException e) {
                        // Do nothing
                    }
                }
        );
        return client;
    }

    public static void main(String[] args) throws Exception {
        new Main().run(args);
    }
}
