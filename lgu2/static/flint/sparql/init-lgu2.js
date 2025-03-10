$(document)
		.ready(
				function() {
					// LCRD sample queries

// List titles and numbers of UKPGAs from 2020
var sampleQuery1=
"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n"+
"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \n"+
"PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> \n"+
"PREFIX leg: <http://www.legislation.gov.uk/def/legislation/> \n"+
"\n"+
"select * {\n"+
"   ?item a leg:UnitedKingdomPublicGeneralAct ;\n"+
"      leg:year 2020 ;\n"+
"      leg:title ?title ;\n"+
"      leg:number ?number .\n"+
"}\n"+
"order by ?number\n"+
"limit 100\n";

// Show contents of graph for a particular item
var sampleQuery2=
"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n"+
"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \n"+
"PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> \n"+
"PREFIX leg: <http://www.legislation.gov.uk/def/legislation/> \n"+
"\n"+
"select ?s ?p ?o\n"+
"where {\n"+
"   graph ?g {\n"+
"      <http://www.legislation.gov.uk/id/asc/2020/1> a leg:Item .\n"+
"      ?s ?p ?o\n"+
"   }\n"+
"}\n"+
"order by desc(?s) ?p ?o\n"+
"limit 100\n";

// Show datasets
var sampleQuery3=
"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n"+
"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \n"+
"PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> \n"+
"PREFIX leg: <http://www.legislation.gov.uk/def/legislation/> \n"+
"PREFIX dct: <http://purl.org/dc/terms/> \n"+
"PREFIX void: <http://rdfs.org/ns/void#> \n"+
"PREFIX sd: <http://www.w3.org/ns/sparql-service-description#> \n"+
"PREFIX drafts: <http://www.legislation.gov.uk/def/drafts/DraftLegislation> \n"+
"\n"+
"select ?ds ?graph (count(?ng) as ?numberOfGraphs) ?numberOfTriples ?title ?created ?modified \n"+
"where { \n"+
"   graph ?graph { \n"+
"      ?ds a leg:DataUnitDataset ; \n"+
"         void:triples ?numberOfTriples ;\n"+
"         dct:title ?title ;\n"+
"         dct:created ?created ;\n"+
"         dct:modified ?modified ;\n"+
"         sd:namedGraph ?ng .\n"+
"   }\n"+
"} \n"+
"group by ?ds ?graph ?numberOfTriples ?title ?created ?modified  \n";

// Find the 20 most recently updated legislation items in core dataset
var sampleQuery4=
"prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n"+
"prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> \n"+
"prefix xsd: <http://www.w3.org/2001/XMLSchema#> \n"+
"prefix void: <http://rdfs.org/ns/void#> \n"+
"prefix dct: <http://purl.org/dc/terms/> \n"+
"prefix sd: <http://www.w3.org/ns/sparql-service-description#> \n"+
"prefix prov: <http://www.w3.org/ns/prov#> \n"+
"prefix leg: <http://www.legislation.gov.uk/def/legislation/> \n"+
"prefix legprov: <http://www.legislation.gov.uk/def/provenance/> \n"+
"\n"+
"select ?time ?graph ?item ?actClass ?activity \n"+
"where { \n"+
"   ?activity a ?actClass ; \n"+
"      prov:endedAtTime ?time . \n"+
"   filter(?actClass!=prov:Activity) \n"+
"   ?graph prov:wasInfluencedBy ?activity . \n"+
"   { \n"+
"      ?dataUnitDataSet sd:namedGraph ?graph . \n"+
"      graph ?graph { ?item a leg:Legislation } \n"+
"   } union { \n"+
"      ?dataUnitDataSet legprov:deletedGraph ?graph . \n"+
"   } \n"+
"   <http://www.legislation.gov.uk/id/dataset/topic/core> void:subset ?dataUnitDataSet . \n"+
"} \n"+
"order by desc(?time) \n"+
"limit 20 \n";

// Find the number of legislation items of each type in core data
var sampleQuery5=
"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n"+
"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \n"+
"PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> \n"+
"PREFIX leg: <http://www.legislation.gov.uk/def/legislation/> \n"+
"PREFIX void: <http://rdfs.org/ns/void#> \n"+
"PREFIX sd: <http://www.w3.org/ns/sparql-service-description#> \n"+
"PREFIX prov: <http://www.w3.org/ns/prov#> \n"+
"\n"+
"select (count (distinct ?item) as ?number) ?type \n"+
"where { \n"+
"   <http://www.legislation.gov.uk/id/dataset/topic/core> void:subset ?dataUnitDataset .\n"+
"   ?dataUnitDataset sd:namedGraph ?graph .\n"+
"   graph ?graph { ?item a leg:Legislation , ?type } \n"+
"   filter(?type!=leg:Item && ?type!=leg:Legislation) \n"+
"} \n"+
"group by ?type \n"+
"order by desc(?number ) \n"+
"limit 100\n";


// Find property chain from an item of specific legislation type
var sampleQuery6=
"prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n"+
"prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> \n"+
"prefix sd: <http://www.w3.org/ns/sparql-service-description#> \n"+
"prefix leg: <http://www.legislation.gov.uk/def/legislation/> \n"+
"prefix void: <http://rdfs.org/ns/void#> \n"+
"\n"+
"select distinct ?pp ?ppp \n"+
"where{ \n"+
"   <http://www.legislation.gov.uk/id/dataset/topic/core> void:subset ?dataUnitDataset .\n"+
"   ?dataUnitDataset sd:namedGraph ?graph .\n"+
"   graph ?graph { \n"+
"      ?item a leg:UnitedKingdomLocalAct ; \n"+
"         ?pp ?o . \n"+
"      optional {?o ?ppp ?ooo .} \n"+
"   } \n"+
"} \n"+
"order by ?pp ?ppp\n"+
"limit 100 \n";


// Find the number of legislation items in core data, grouped by year
var sampleQuery7=
"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n"+
"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \n"+
"PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> \n"+
"PREFIX leg: <http://www.legislation.gov.uk/def/legislation/> \n"+
"PREFIX sd: <http://www.w3.org/ns/sparql-service-description#> \n"+
"PREFIX void: <http://rdfs.org/ns/void#>\n"+
"\n"+
"select ?year (count(?item ) as ?number)\n"+
"where { \n"+
"   <http://www.legislation.gov.uk/id/dataset/topic/core> void:subset ?dataUnitDataset .\n"+
"   ?dataUnitDataset sd:namedGraph ?graph .\n"+
"   graph ?graph { \n"+
"      ?item a leg:Legislation ; \n"+
"         leg:year ?year\n"+
"   } \n"+
"} \n"+
"group by ?year \n"+
"order by desc(?year) \n"+
"limit 20\n";

					var flintConfig = {
						"interface" : {
							"toolbar" : true,
							"menu" : true
						},
						"namespaces" : [
								{
									"name" : "Resource Description Framework",
									"prefix" : "rdf",
									"uri" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
								},
								{
									"name" : "Resource Description Framework schema",
									"prefix" : "rdfs",
									"uri" : "http://www.w3.org/2000/01/rdf-schema#"
								},
								{
									"name" : "Friend of a friend",
									"prefix" : "foaf",
									"uri" : "http://xmlns.com/foaf/0.1/"
								},
								{
									"name" : "XML schema",
									"prefix" : "xsd",
									"uri" : "http://www.w3.org/2001/XMLSchema#",
									forceInclude : true
								},
								{
									"name" : "SIOC",
									"prefix" : "sioc",
									"uri" : "http://rdfs.org/sioc/ns#"
								},
								{
									"name" : "Dublin Core",
									"prefix" : "dc",
									"uri" : "http://purl.org/dc/elements/1.1/"
								},
								{
									"name" : "Dublin Core terms",
									"prefix" : "dct",
									"uri" : "http://purl.org/dc/terms/"
								},
								{
									"name" : "Creative Commons",
									"prefix" : "cc",
									"uri" : "http://www.creativecommons.org/ns#"
								},
								{
									"name" : "Web Ontology Language",
									"prefix" : "owl",
									"uri" : "http://www.w3.org/2002/07/owl#"
								},
								{
									"name" : "Simple Knowledge Organisation System",
									"prefix" : "skos",
									"uri" : "http://www.w3.org/2004/02/skos/core#"
								},
								{
									"name" : "Geography",
									"prefix" : "geo",
									"uri" : "http://www.w3.org/2003/01/geo/wgs84_pos#"
								},
								{
									"name" : "Geonames",
									"prefix" : "geonames",
									"uri" : "http://www.geonames.org/ontology#"
								},
								{
									"name" : "DBPedia property",
									"prefix" : "dbp",
									"uri" : "http://dbpedia.org/property/"
								},
								{
									"name" : "Open Provenance Model Vocabulary",
									"prefix" : "opmv",
									"uri" : "http://purl.org/net/opmv/ns#"
								},
								{
									"name" : "Functional Requirements for Bibliographic Records",
									"prefix" : "frbr",
									"uri" : "http://purl.org/vocab/frbr/core#"
								},
								{
									"name" : "Vocabulary of Interlinked Datasets",
									"prefix" : "void",
									"uri" : "http://rdfs.org/ns/void#"
								},
								{
									"name" : "SPARQL Service Description",
									"prefix" : "sd",
									"uri" : "http://www.w3.org/ns/sparql-service-description#"
								},
								{
									"name" : "PROV",
									"prefix" : "prov",
									"uri" : "http://www.w3.org/ns/prov#"
								},
								{
									"name" : "Legislation ontology",
									"prefix" : "leg",
									"uri" : "http://www.legislation.gov.uk/def/legislation/"
								}
						],
						"defaultEndpointParameters" : {
							"queryParameters" : {
								"format" : "output",
								"query" : "query",
								"update" : "update"
							},
							"selectFormats" : [ {
								"name" : "SPARQL-XML",
								"format" : "sparql",
								"type" : "application/sparql-results+xml"
							}, {
								"name" : "Plain text",
								"format" : "text",
								"type" : "text/plain"
							}, {
								"name" : "JSON",
								"format" : "json",
								"type" : "application/sparql-results+json"
							}, {
								"name" : "CSV",
								"format" : "csv",
								"type" : "text/csv"
							} ],
							"constructFormats" : [ {
								"name" : "Plain text",
								"format" : "text",
								"type" : "text/plain"
							}, {
								"name" : "RDF/XML",
								"format" : "rdfxml",
								"type" : "application/rdf+xml"
							}, {
								"name" : "Turtle",
								"format" : "turtle",
								"type" : "application/turtle"
							} ]
						},
						"endpoints" : [
								{
									"name" : "LDSI SPARQL Endpoint",
									"uri" : "http://localhost:8080/ld/sparql",
									"modes" : ["sparql11query","sparql10" ],
									queries : [
											{
												"name" : "1. List titles and numbers of UKPGAs from 2020",
												"description" : "Simple query on core data",
												"query" : sampleQuery1
											},
											{
												"name" : "2. Show contents of graph for a particular item",
												"description" : "Simple query on core data",
												"query" : sampleQuery2
											},
											{
												"name" : "3. Show datasets",
												"description" : "",
												"query" : sampleQuery3
											},
											{
												"name" : "4. Find the 20 most recently updated legislation items in core dataset",
												"description" : "",
												"query" : sampleQuery4
											},
											{
												"name" : "5. Find the number of legislation items of each type in core data",
												"description" : "",
												"query" : sampleQuery5
											},
											{
												"name" : "6. Find property chain from a item of the specific legislation type",
												"description" : "",
												"query" : sampleQuery6
											},
											{
												"name" : "7. Find the number of legislation items in core data, grouped by year",
												"description" : "",
												"query" : sampleQuery7
											}
										]
								}								
							],
						"defaultModes" : [ {
						
								"name" : "SPARQL 1.1 Query",
								"mode" : "sparql11query"
						}, {
							"name" : "SPARQL 1.0",
							"mode" : "sparql10"
						}, {
							"name" : "SPARQL 1.1 Update",
							"mode" : "sparql11update"
						} ]
					}

					var flintEd = new FlintEditor("flint-test",
							"/static/flint/sparql/images", flintConfig);
				});
