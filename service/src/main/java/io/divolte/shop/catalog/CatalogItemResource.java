package io.divolte.shop.catalog;

import static io.divolte.shop.catalog.CatalogEsConstants.execute;
import static org.elasticsearch.common.xcontent.XContentFactory.jsonBuilder;
import io.dropwizard.jackson.JsonSnakeCase;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import javax.validation.Valid;
import javax.validation.constraints.Pattern;
import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.PUT;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.container.AsyncResponse;
import javax.ws.rs.container.Suspended;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.Response.Status;

import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.xcontent.XContentBuilder;
import org.hibernate.validator.constraints.NotEmpty;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;

@Produces(MediaType.APPLICATION_JSON)
@Path("/api/catalog/item")
public class CatalogItemResource {
	private static final String ID_REGEXP = "^[0-9]{6,15}$";
	
	private final TransportClient client;
	
	public CatalogItemResource(final TransportClient client) {
		this.client = client;
	}

	@Path("{id}")
	@GET
	public void getItem(@Pattern(regexp=ID_REGEXP) @PathParam("id") final String id, @Suspended final AsyncResponse response) {
		execute(client.prepareGet(CatalogEsConstants.CATALOG_INDEX, CatalogEsConstants.ITEM_DOCUMENT_TYPE, id),
				(r,e) -> {
					if (e.isPresent()) {
						response.resume(e.get());
					} else {
						if (r.get().isSourceEmpty()) {
							response.resume(Response.status(Status.NOT_FOUND).entity("Not found.").build());
						} else {
							// We perform our own JSON parsing, because the ES JSON
							// objects are pretty much useless API-wise.
							final Item item = CatalogEsConstants.sourceToItem(r.get().getSourceAsString());
							response.resume(item);
						}
					}
				});
	}

	@Consumes(MediaType.APPLICATION_JSON)
	@PUT
	public void putItem(@Valid final Item item, @Suspended final AsyncResponse response) throws IOException {
		final XContentBuilder builder = itemToContentBuilder(item);
		execute(
				client.prepareIndex(CatalogEsConstants.CATALOG_INDEX, CatalogEsConstants.ITEM_DOCUMENT_TYPE).setSource(builder),
				(r,e) -> {
					if (e.isPresent()) {
						response.resume(e.get());
					} else {
						response.resume(item);
					}
				});
	}
	
	private XContentBuilder itemToContentBuilder(final Item item) throws IOException {
		final XContentBuilder builder = jsonBuilder();
		builder.startObject()
			   .field("id", item.id)
			   .field("title", item.title)
			   .field("description", item.description)
			   .field("tags", item.tags)
			   .field("categories", item.categories)
			   .field("favs", item.favs)
			   .startObject("owner")
			   .field("user_id", item.owner.userId)
			   .field("user_name", item.owner.userName)
			   .field("real_name", item.owner.realName)
			   .endObject()
			   .startArray("variants");
		
		item.variants.entrySet().stream().forEach((v) -> {
			try {
				builder.startObject()
					   .field("name", v.getKey())
					   .field("flickr_url", v.getValue().flickrUrl)
					   .field("img_source", v.getValue().imgSource)
					   .field("width", v.getValue().width)
					   .field("height", v.getValue().height)
					   .endObject();
			} catch(IOException ioe) {
				throw new RuntimeException(ioe);
			}
		});
		builder.endArray();
		return builder;
	}
	
	@JsonSnakeCase
	public static final class Item {
		public final @NotEmpty @Pattern(regexp=ID_REGEXP) String id;
		public final @NotEmpty List<String> categories;
		public final String title;
		public final String description;
		public final List<String> tags;
		public final int favs;
		public final Owner owner;
		public final Map<String,Variant> variants;
		
		@JsonCreator
		public Item(
				@JsonProperty("id") final String id,
		        @JsonProperty("categories") final List<String> categories,
	            @JsonProperty("title") final String title,
	            @JsonProperty("description") final String description,
	            @JsonProperty("tags") final List<String> tags,
	            @JsonProperty("favs") final int favs,
	            @JsonProperty("owner") final Owner owner,
	            @JsonProperty("variants") final Map<String, Variant> variants) {
			this.id = id;
			this.categories = ImmutableList.copyOf(categories);
			this.title = title;
			this.description = description;
			this.tags = ImmutableList.copyOf(tags);
			this.favs = favs;
			this.owner = owner;
			this.variants = ImmutableMap.copyOf(variants);
		}

		@Override
		public String toString() {
			return "Item [id=" + id + ", title=" + title + ", description="
					+ description + ", tags=" + tags + ", favs=" + favs
					+ ", owner=" + owner + ", variants=" + variants + "]";
		}

		@JsonSnakeCase
		public static final class Owner {
			@NotEmpty public final String userName;
			@NotEmpty public final String userId;
			public final String realName;
			
			public Owner(
					@JsonProperty("user_name") final String userName,
			        @JsonProperty("user_id") final String userId,
			        @JsonProperty("real_name") final String realName) {
				this.userName = userName;
				this.userId = userId;
				this.realName = realName;
			}

			@Override
			public String toString() {
				return "Owner [userName=" + userName + ", userId=" + userId
						+ ", realName=" + realName + "]";
			}
		}
		
		@JsonSnakeCase
		public static final class Variant {
			@NotEmpty public final int width;
			@NotEmpty public final int height;
			@NotEmpty public final String flickrUrl;
			@NotEmpty public final String imgSource;
			
			public Variant(
					@JsonProperty("width") final int width,
			        @JsonProperty("height") final int height,
			        @JsonProperty("flickr_url") final String flickrUrl,
			        @JsonProperty("img_source") final String imgSource) {
				this.width = width;
				this.height = height;
				this.flickrUrl = flickrUrl;
				this.imgSource = imgSource;
			}

			@Override
			public String toString() {
				return "Variant [width=" + width + ", height=" + height
						+ ", flickrUrl=" + flickrUrl + ", imgSource="
						+ imgSource + "]";
			}
		}
	}
}
