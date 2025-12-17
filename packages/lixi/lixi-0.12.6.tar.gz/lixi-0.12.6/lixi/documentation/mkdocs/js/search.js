require([
    base_url + '/mkdocs/js/mustache.min.js',
    base_url + '/mkdocs/js/lunr.min.js',
], function (Mustache, lunr) {
   "use strict";

    function getSearchTerm()
    {
        var sPageURL = window.location.search.substring(1);
        var sURLVariables = sPageURL.split('&');
        for (var i = 0; i < sURLVariables.length; i++)
        {
            var sParameterName = sURLVariables[i].split('=');
            if (sParameterName[0] == 'q')
            {
                return decodeURIComponent(sParameterName[1].replace(/\+/g, '%20'));
            }
        }
    }
    
    var getUrlParameter = function getUrlParameter(sParam) {
        var sPageURL = window.location.search.substring(1),
            sURLVariables = sPageURL.split('&'),
            sParameterName,
            i;

        for (i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');

            if (sParameterName[0] === sParam) {
                return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
            }
        }
    };
    
    var TYPE = getUrlParameter('type');
    var TRANSACTION = getUrlParameter('transaction');
    var VERSION = getUrlParameter('version');
    
    if (TYPE == 'Master')    
      document.getElementById("lixi-transaction-version").textContent = "LIXI " + TYPE + " " + VERSION;  
    if (TYPE == 'Transaction')    
      document.getElementById("lixi-transaction-version").textContent = "LIXI " + TRANSACTION + " " + VERSION;  

    var index = lunr(function () {
        this.field('title', {boost: 10});
        this.field('text');
        this.ref('location');
    });
		
		var results_template = `<article>
  <h3><a href="{{location}}">{{title}}</a></h3>
  <p>{{summary}}</p>
</article>`

    if (TYPE == 'Transaction') {
		
		var XSLT = `<xsl:stylesheet xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:lx="lixi.org.au/schema/appinfo_elements" xmlns:li="lixi.org.au/schema/appinfo_instructions" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2018-11-16">
	<xsl:output method="xml" indent="yes" omit-xml-declaration="yes" />
	<xsl:template match="@*|text()"/>
	<xsl:template name="element" match="//*[local-name()='element' and contains(./xs:annotation/xs:appinfo/li:transactions, '` + TRANSACTION + `')]|//*[local-name()='attribute' and contains(./xs:annotation/xs:appinfo/li:transactions, '` + TRANSACTION + `')]|//*[local-name()='simpleType' and contains(./xs:annotation/xs:appinfo/li:transactions, '` + TRANSACTION + `')]">
		{
			"location": "/index.html?type=` + TYPE + `&amp;transaction=` + TRANSACTION + `&amp;version=` + VERSION + `#<xsl:value-of select="./*/*/*[local-name()='path']"/>",
			"text": "<xsl:value-of select="translate(./*/*[local-name()='documentation'],'&quot;','')"/> <xsl:value-of select="translate(./*/*/*[local-name()='CustomDocumentation'],'&#10;','')"/> (label: <xsl:value-of select="./*/*/*[local-name()='label']"/> , path: <xsl:value-of select="./*/*/*[local-name()='path']"/>)",
            "title": "<xsl:value-of select="./@name"/><xsl:value-of select="./@value"/> (<xsl:value-of select="local-name()"/>)"
		},<xsl:apply-templates/></xsl:template>
	<xsl:template match="/">{
	"docs": [<xsl:apply-templates/>
		{
			"location": "",
			"text": "",
			"title": ""
		}
  ]
}</xsl:template> 
</xsl:stylesheet>`

    }
    else {
      
  var XSLT = `<xsl:stylesheet xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:lx="lixi.org.au/schema/appinfo_elements" xmlns:li="lixi.org.au/schema/appinfo_instructions" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2018-11-16">
	<xsl:output method="xml" indent="yes" omit-xml-declaration="yes" />
	<xsl:template match="@*|text()"/>
	<xsl:template name="element" match="//*[local-name()='element']|//*[local-name()='attribute']|//*[local-name()='simpleType']">
		{
			"location": "/index.html?type=` + TYPE + `&amp;version=` + VERSION + `#<xsl:value-of select="./*/*/*[local-name()='path']"/>",
			"text": "<xsl:value-of select="./*/*/*[local-name()='path']"/> LINEBREAK <xsl:value-of select="translate(./*/*[local-name()='documentation'],'&quot;','')"/> <xsl:value-of select="translate(./*/*/*[local-name()='CustomDocumentation'],'&#10;','')"/> (label: <xsl:value-of select="./*/*/*[local-name()='label']"/>)",
			"title": "<xsl:value-of select="./@name"/><xsl:value-of select="./@value"/> (<xsl:value-of select="local-name()"/>)"
		},<xsl:apply-templates/></xsl:template>
	<xsl:template match="/">{
	"docs": [<xsl:apply-templates/>
		{
			"location": "",
			"text": "",
			"title": ""
		}
  ]
}</xsl:template> 
</xsl:stylesheet>`

    }

    //alert(XSLT);

		var parser = new DOMParser();
		var XSLTdom = parser.parseFromString(XSLT,"text/xml");
		var XMLdom = parser.parseFromString(schemaString,"text/xml");
		var xsltProcessor = new XSLTProcessor();
		xsltProcessor.importStylesheet(XSLTdom);
		var searchIndexString  = document.createElement("SEARCHINDEX");
		var resultDocument = xsltProcessor.transformToFragment(XMLdom, document);
		var data = JSON.parse(resultDocument.textContent);
    
    console.log(data);
		
		var documents = {};

		for (var i=0; i < data.docs.length; i++){
				var doc = data.docs[i];
				doc.location = base_url + doc.location;
				index.add(doc);
				documents[doc.location] = doc;
		}

		var search = function(){

			var query = document.getElementById('mkdocs-search-query').value;
			var search_results = document.getElementById("mkdocs-search-results");
			while (search_results.firstChild) {
					search_results.removeChild(search_results.firstChild);
			}

			if(query === ''){
					return;
			}

			var results = index.search(query);

			if (results.length > 0){
					for (var i=0; i < results.length; i++){
							var result = results[i];
							doc = documents[result.ref];
							doc.base_url = base_url;
							doc.summary = doc.text.substring(0, 200);
							var html = Mustache.to_html(results_template, doc);
							search_results.insertAdjacentHTML('beforeend', html.replace("LINEBREAK", "<br/>"));
					}
			} else {
					search_results.insertAdjacentHTML('beforeend', "<p>No results found</p>");
			}

			if(jQuery){
					/*
					 * We currently only automatically hide bootstrap models. This
					 * requires jQuery to work.
					 */
					jQuery('#mkdocs_search_modal a').click(function(){
							jQuery('#mkdocs_search_modal').modal('hide');
					});
			}
		};

		var search_input = document.getElementById('mkdocs-search-query');

		$(search_input).keypress(
			function(event){
				if (event.which == '13') {
					event.preventDefault();
				}
		});

		var term = getSearchTerm();
		if (term){
				search_input.value = term;
				search();
		}

		search_input.addEventListener("keyup", search);

		
});

