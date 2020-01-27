package io.divolte.shop;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.action.search.SearchResponse;
import org.elasticsearch.client.RestHighLevelClient;
import org.elasticsearch.common.unit.Fuzziness;
import org.elasticsearch.search.builder.SearchSourceBuilder;
import org.elasticsearch.search.suggest.SuggestBuilder;
import org.elasticsearch.search.suggest.completion.CompletionSuggestionBuilder;

import javax.annotation.ParametersAreNonnullByDefault;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.container.AsyncResponse;
import javax.ws.rs.container.Suspended;
import javax.ws.rs.core.MediaType;
import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

import static io.divolte.shop.catalog.DataAccess.CATALOG_INDEX;
import static io.divolte.shop.catalog.DataAccess.COMPLETE_TITLE_FIELD;
import static org.elasticsearch.client.RequestOptions.DEFAULT;

@Path("/api/complete")
@Produces(MediaType.APPLICATION_JSON)
public class CompletionResource {
    private final RestHighLevelClient esClient;

    public CompletionResource(RestHighLevelClient esClient) {
        this.esClient = esClient;
    }

    @GET
    public void complete(@QueryParam("prefix") final String prefix, @Suspended final AsyncResponse response) {
        try {

            SearchResponse searchResponse = this.getCompletionSuggestions(prefix);
            response.resume(new CompletionResponse(searchResponse));

        } catch (IOException ex) {
            response.resume(ex);
        }
    }

    public SearchResponse getCompletionSuggestions(final String prefix) throws IOException {
        SearchRequest searchRequest = new SearchRequest(CATALOG_INDEX);
        CompletionSuggestionBuilder suggestBuilder = new CompletionSuggestionBuilder(COMPLETE_TITLE_FIELD);

        suggestBuilder.size(10)
                .prefix(prefix, Fuzziness.AUTO)
                .skipDuplicates(true)
                .analyzer("catalog");

        SearchSourceBuilder sourceBuilder = new SearchSourceBuilder();
        sourceBuilder.suggest(new SuggestBuilder().addSuggestion("suggestion", suggestBuilder));
        searchRequest.source(sourceBuilder);

        return esClient.search(searchRequest, DEFAULT);
    }

    public static final class CompletionResponse {
        @JsonProperty(required = true)
        public final List<CompletionOption> searches;

        public CompletionResponse(SearchResponse searchResponse) {
            /*
             * We request only one suggestion, so it's safe to take all
             * responses and flatMap out the options of the entries into a list.
             */
            this.searches = StreamSupport
                    .stream(searchResponse.getSuggest().spliterator(), false)
                    .flatMap((suggestions) -> suggestions.getEntries().stream())
                    .flatMap((entries) -> entries.getOptions().stream())
                    .map((option) -> new CompletionOption(option.getText().string()))
                    .collect(Collectors.toList());
        }

        @ParametersAreNonnullByDefault
        @JsonInclude(Include.NON_NULL)
        public static final class CompletionOption {
            @JsonProperty(value = "suggestion", required = true)
            public final String suggestion;

            public CompletionOption(final String suggestion) {
                this.suggestion = suggestion;
            }
        }
    }
}
