package io.divolte.shop.catalog;

import io.divolte.shop.catalog.CatalogItemResource.Item;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

import javax.ws.rs.DefaultValue;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.container.AsyncResponse;
import javax.ws.rs.container.Suspended;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.Response.Status;

import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.index.query.QueryBuilders;
import org.elasticsearch.search.SearchHit;
import org.elasticsearch.search.sort.SortBuilders;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.collect.ImmutableList;

@Path("/api/catalog/category")
public class CatalogCategoryResource {
    private final TransportClient client;

    public CatalogCategoryResource(TransportClient client) {
        this.client = client;
    }

    @Path("{name}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public void getCategory(
            @PathParam("name") final String name,
            @DefaultValue("ID") @QueryParam("order") final String order,
            @DefaultValue("0") @QueryParam("page") final int page,
            @DefaultValue("20") @QueryParam("size") final int imagesPerPage,
            @Suspended final AsyncResponse response) {

        client.prepareSearch(DataAccess.CATALOG_INDEX).setQuery(QueryBuilders.constantScoreQuery(QueryBuilders.termQuery("categories", name)));
        DataAccess.execute(
                client.prepareSearch(DataAccess.CATALOG_INDEX)
                        .setQuery(QueryBuilders.constantScoreQuery(QueryBuilders.termQuery("categories", name)))
                        .addSort(SortBuilders.fieldSort("_uid")) // Since we only
                                                                // support ID at
                                                                // this point
                        .setSize(imagesPerPage)
                        .setFrom(page * imagesPerPage),
                (r, e) -> {
                    if (e.isPresent()) {
                        response.resume(e.get());
                    } else {
                        if (r.get().getHits().hits().length == 0) {
                            response.resume(Response.status(Status.NOT_FOUND).entity("Not found.").build());
                        } else {
                            final List<Item> items = StreamSupport
                                    .stream(r.get().getHits().spliterator(), false)
                                    .map(SearchHit::getSourceAsString)
                                    .map(DataAccess::sourceToItem)
                                    .collect(Collectors.toList());
                            response.resume(new Category(name, page, r.get().getHits().getHits().length, r.get().getHits().totalHits(), items));
                        }
                    }
                });
    }

    public static enum ORDER {
        ID;
    }

    public static final class Category {
        @JsonProperty("name")
        public final String name;
        @JsonProperty("page")
        public final int page;
        @JsonProperty("size")
        public final int size;
        @JsonProperty("total")
        public final long total;
        @JsonProperty("items")
        public final List<Item> items;

        @JsonCreator
        public Category(
                @JsonProperty("name") final String name,
                @JsonProperty("page") final int page,
                @JsonProperty("size") final int size,
                @JsonProperty("total") final long total,
                @JsonProperty("items") final List<Item> items) {
            this.name = name;
            this.page = page;
            this.size = size;
            this.total = total;
            this.items = ImmutableList.copyOf(items);
        }
    }
}
