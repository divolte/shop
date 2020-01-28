$(document).ready(function() {
    var titles = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('suggestion'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: 'http://localhost:8080/api/complete?prefix=%QUERY',
            wildcard: '%QUERY',
            transform: function(searchesResponse) {
                return searchesResponse.searches;
            }
        }
    });

    $('#search-box .typeahead').typeahead({
        hint: true,
        highlight: true,
        minLength: 3
    },
    {
        name: 'titles',
        display: 'suggestion',
        source: titles
    });
})
