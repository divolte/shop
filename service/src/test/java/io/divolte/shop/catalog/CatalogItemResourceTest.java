package io.divolte.shop.catalog;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.divolte.shop.catalog.CatalogItemResource.Item;
import io.divolte.shop.catalog.CatalogItemResource.Item.Owner;
import io.divolte.shop.catalog.CatalogItemResource.Item.Variant;
import io.dropwizard.jackson.Jackson;
import org.junit.Test;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import static io.dropwizard.testing.FixtureHelpers.fixture;
import static org.assertj.core.api.Assertions.assertThat;

public class CatalogItemResourceTest {
    private static final ObjectMapper MAPPER = Jackson.newObjectMapper();

    @Test
    public void serializesToJSON() throws Exception {
        String id = "13559935634";
        List<String> categories = Arrays.asList("flowers");
        String title = "Flowers";
        String description = "Flowers";
        List<String> tags = Arrays.asList("flowers");
        Integer favs = 50;
        Integer price = 2;

        String user_name = "Nouhailler";
        String user_id = "7737054@N07";
        String real_name = "Patrick Nouhailler";
        Owner owner = new Owner(user_name, user_id, real_name);

        Variant square = new Variant(75, 75, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/sq/", "https://farm4.staticflickr.com/3715/13559935634_d519417ab2_s.jpg");
        Variant large_square = new Variant(150, 150, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/q/", "https://farm4.staticflickr.com/3715/13559935634_d519417ab2_q.jpg");
        Variant thumbnail = new Variant(100, 67, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/t/", "https://farm4.staticflickr.com/3715/13559935634_d519417ab2_t.jpg");
        Variant small = new Variant(240, 160, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/s/", "https://farm4.staticflickr.com/3715/13559935634_d519417ab2_m.jpg");
        Variant small_320 = new Variant(320, 213, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/n/", "https://farm4.staticflickr.com/3715/13559935634_d519417ab2_n.jpg");
        Variant medium = new Variant(500, 333, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/m/", "https://farm4.staticflickr.com/3715/13559935634_d519417ab2.jpg");
        Variant medium_640 = new Variant(640, 427, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/z/", "https://farm4.staticflickr.com/3715/13559935634_d519417ab2_z.jpg");
        Variant medium_800 = new Variant(800, 534, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/c/", "https://farm4.staticflickr.com/3715/13559935634_d519417ab2_c.jpg");
        Variant large = new Variant(1024, 683, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/l/", "https://farm4.staticflickr.com/3715/13559935634_d519417ab2_b.jpg");
        Variant large_1600 = new Variant(1600, 1067, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/h/", "https://farm4.staticflickr.com/3715/13559935634_2e2095c11f_h.jpg");
        Variant large_2048 = new Variant(2048, 1365, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/k/", "https://farm4.staticflickr.com/3715/13559935634_eae6be4acc_k.jpg");
        Variant original = new Variant(4272, 2848, "https://www.flickr.com/photos/patrick_nouhailler/13559935634/sizes/o/", "https://farm4.staticflickr.com/3715/13559935634_bcf246b95d_o.jpg");
        Map<String, Variant> variants = new LinkedHashMap<String, Variant>() {{
            put("Square", square);
            put("Large Square", large_square);
            put("Thumbnail", thumbnail);
            put("Small", small);
            put("Small 320", small_320);
            put("Medium", medium);
            put("Medium 640", medium_640);
            put("Medium 800", medium_800);
            put("Large", large);
            put("Large 1600", large_1600);
            put("Large 2048", large_2048);
            put("Original", original);
        }};

        final Item item = new Item(id, categories, title, description, tags, favs, price, owner, variants);

        final String expected = MAPPER.writeValueAsString(
                MAPPER.readValue(fixture("item.json"), Item.class));

        assertThat(MAPPER.writeValueAsString(item)).isEqualTo(expected);
    }
}
