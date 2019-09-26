package io.divolte.shop.catalog;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.Response.Status;


@Path("/api/status")
public class APIStatusResource {

    public APIStatusResource() {

    }

    /**
    Purpose is to determine whether the api is still alive and running
    */
    @Path("/ping")
    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public Response getStatus() {
        Response.ResponseBuilder builder = Response.status(Status.ACCEPTED);

        return builder.entity("pong").build();

    }

}
