var schema;
var evaluator;
var resolver;
var subschemas;

var TYPE;        // 'Master' or 'Transaction' (TODO... 'Custom')
var VERSION;     // the numeric version of the master (TODO... custom e.g. LIXI-CAL-Custom-LIXI-DEMO-2019_07_18-05_08)
var TRANSACTION; // 'CAL', 'DAS', 'CDA' etc.
var SUBSCHEMA;   // True if the documentation is based on a transaction subschema

///////////////////////////////////////////////////////////////////////////////////////////////
// utility functions
///////////////////////////////////////////////////////////////////////////////////////////////

// reload the main page content (not the whole page) when the browser back arrow is pressed
window.addEventListener('popstate', (event) => {
  displayContent();
});

function initialise() {
  
  toggleLoaderWheel("display");
 
  // parse Schema and Glossary from XML string variables
  parser = new DOMParser();
  schema = parser.parseFromString(schemaString,"text/xml");
  
  parserGlossary = new DOMParser();
  glossary = parserGlossary.parseFromString(glossaryString,"text/xml");  
  
  // create schema xpath engine
  evaluator = new XPathEvaluator();
  resolver = evaluator.createNSResolver(schema.documentElement);
  
  // create glossary xpath engine
  evaluatorGlossary = new XPathEvaluator();
  resolverGlossary = evaluatorGlossary.createNSResolver(glossary.documentElement);
  
  displayContent();
  appendMenus();
}

function toggleLoaderWheel(value) {
  var loader = document.getElementById("wheel");
  loader.style.display = value;
}

function displayContent() {

  
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
    

    // get the schema type from the URL or if it's not in the URL get the schema type from the schema
    TYPE        = getUrlParameter('type');
    if (!TYPE)
      TYPE = schema.evaluate("/xs:schema[1]/xs:annotation[1]/xs:appinfo[1]/lx:schemadetail[1]/@type" , schema, resolver, XPathResult.ANY_TYPE, null).iterateNext().textContent;
    
    // for 'Master' schemas, display the schema name in the HTML
    if (TYPE == 'Master'){
      VERSION = getUrlParameter('version');
      if (!VERSION)
        VERSION = schema.evaluate("/xs:schema[1]/xs:annotation[1]/xs:appinfo[1]/lx:schemadetail[1]/@version" , schema, resolver, XPathResult.ANY_TYPE, null).iterateNext().textContent;
    
      SUBSCHEMA = false;
      document.getElementById("lixi-transaction-version").textContent = "LIXI " + TYPE + " " + VERSION;  
      document.getElementById("lixi-transaction-version-mobile").textContent = "LIXI " + TYPE + " " + VERSION;  

      
    }
    
    // for 'Transaction' schemas, display the schema name in the HTML
    if (TYPE == 'Transaction') {
      VERSION = getUrlParameter('version');
      if (!VERSION) {
        VERSION = schema.evaluate("/xs:schema[1]/xs:annotation[1]/xs:appinfo[1]/lx:schemadetail[1]/@version" , schema, resolver, XPathResult.ANY_TYPE, null).iterateNext().textContent;
      }
      
      TRANSACTION = getUrlParameter('transaction');
      if (!TRANSACTION) {
        TRANSACTION = schema.evaluate("/xs:schema[1]/xs:annotation[1]/xs:appinfo[1]/lx:schemadetail[1]/@transaction" , schema, resolver, XPathResult.ANY_TYPE, null).iterateNext().textContent;
      }
      if (schema.evaluate("/xs:schema[1]/xs:annotation[1]/xs:appinfo[1]/li:subschema" , schema, resolver, XPathResult.ANY_TYPE, null).iterateNext() == null)
        SUBSCHEMA = true
      else 
        SUBSCHEMA = false
        document.getElementById("lixi-transaction-version").textContent = "LIXI " + TRANSACTION + " " + VERSION ;
        document.getElementById("lixi-transaction-version-mobile").textContent = "LIXI " + TRANSACTION + " " + VERSION ;
    }
    
    // for 'Custom' schemas, display the schema name in the HTML
    if (TYPE == 'Custom') {
      var version_transaction = schema.evaluate("/xs:schema[1]/xs:annotation[1]/xs:appinfo[1]/lx:schemadetail[1]/@transactionschemasource" , schema, resolver, XPathResult.ANY_TYPE, null).iterateNext().textContent.split(" ");
      VERSION     = version_transaction[1]
      TRANSACTION = version_transaction[0]
      document.getElementById("lixi-transaction-version").textContent = "LIXI Custom " + TRANSACTION + " " + VERSION;
      document.getElementById("lixi-transaction-version-mobile").textContent = "LIXI Custom " + TRANSACTION + " " + VERSION;
    }
    
    // set the search form to include the TYPE, TRANSACTION and VERSION
    document.getElementById("search-type").setAttribute('value', TYPE);     
    document.getElementById("search-transaction").setAttribute('value', TRANSACTION);    
    document.getElementById("search-version").setAttribute('value', VERSION);         
    
    //setVersion();
    
    // display the content for this schema item
    if(item = window.location.hash) {
      appendItem(item.substring(1));
    }
    else{
      appendItem('Package');
    }
}

function appendMenus() {
  
  // /////////////////
  //   Element Menu
  // /////////////////
  var elementsMenu = document.getElementById('elements');
   
  while (elementsMenu.firstChild) {
     elementsMenu.removeChild(elementsMenu.firstChild);
  }
  
  if (TYPE == 'Transaction' && SUBSCHEMA == false){
    var xpath = "//xs:element[contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]";
  }
  else
    var xpath = "//xs:element";
  
  result = schema.evaluate(xpath, schema, resolver, XPathResult.ANY_TYPE, null);

  elems = [];
  
  while (elem = result.iterateNext()){  
    var name = elem.getAttribute("name")
    
    if (elem.parentElement.parentElement && elem.parentElement.parentElement.parentElement && elem.parentElement.parentElement.parentElement.tagName == "xs:element" ) {
       var parentelement = elem.parentElement.parentElement.parentElement.getAttribute("name");
    }
    else if (elem.parentElement && elem.parentElement.parentElement && elem.parentElement.parentElement.tagName == "xs:complexType" ) {
       var parentelement = elem.parentElement.parentElement.getAttribute("name");
    }
    
    var path = elem.childNodes[1].childNodes[3].childNodes[1].textContent;
    
    if (path != "Package") {
      var fullname = name + " (in " + parentelement + ")";
    }
    else {
      var fullname = name + " (root element)";
    }
    
    elems.push(
      {
        'name' : fullname, 
        'path': path
      }
    );
  } 

  elems.sort(function(a, b) {
    return (a['name'] > b['name'] ? 1 : -1);
    });
  
  for(var x in elems) {
    var name = elems[x]['name'];
    var path = elems[x]['path'];

    var listitem    = document.createElement('li');
    var anchoritem  = document.createElement('a');
    var textcontent = document.createTextNode(name);     

    listitem.setAttribute("class","toctree-l2");    
    anchoritem.setAttribute("onmousedown","appendItem('" + path + "')");    

    elementsMenu.appendChild(listitem);
    listitem.appendChild(anchoritem);
    anchoritem.appendChild(textcontent);
  }

  // /////////////////
  //   Attribute Menu
  // /////////////////
  var attributesMenu = document.getElementById('attributes');
  
  while (attributesMenu.firstChild) {
    attributesMenu.removeChild(attributesMenu.firstChild);
  }
  
  if (TYPE == 'Transaction' && SUBSCHEMA == false){
    var xpath = "//xs:attribute[contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]";
  }
  else
    var xpath = "//xs:attribute";
  
  result = schema.evaluate(xpath, schema, resolver, XPathResult.ANY_TYPE, null);

  elems = [];
  
  while (elem = result.iterateNext()){  
  
    var name = elem.getAttribute("name")
    
    if (elem.parentElement.parentElement && (elem.parentElement.parentElement.tagName == "xs:complexType" || elem.parentElement.parentElement.tagName == "xs:element")) {

       var parentelement = elem.parentElement.parentElement.getAttribute("name");

    }

    var path = elem.childNodes[1].childNodes[3].childNodes[1].textContent;
    var fullname = name + " (in " + parentelement + ")";
    elems.push(
      {
        'name' : fullname, 
        'path': path
      }
    );
  } 

  elems.sort(function(a, b) {
    return (a['name'] > b['name'] ? 1 : -1);
  });
  
  for(var x in elems) {
  
    var name = elems[x]['name'];
    var path = elems[x]['path'];
    var listitem    = document.createElement('li');
    var anchoritem  = document.createElement('a');
    var textcontent = document.createTextNode(name);

    listitem.setAttribute("class","toctree-l2");    
    anchoritem.setAttribute("onmousedown","appendItem('" + path + "')");    

    attributesMenu.appendChild(listitem);
    listitem.appendChild(anchoritem);
    anchoritem.appendChild(textcontent);
  }
  
  // /////////////////
  //   Simple Types Menu
  // /////////////////
  var simpleTypesMenu = document.getElementById('simpleTypes');
  
  while (simpleTypesMenu.firstChild) {
    simpleTypesMenu.removeChild(simpleTypesMenu.firstChild);
  }
  
  if (TYPE == 'Transaction' && SUBSCHEMA == false){
    var xpath = "//xs:simpleType[contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]";
  }
  else
    var xpath = "//xs:simpleType";
        
  result = schema.evaluate(xpath, schema, resolver, XPathResult.ANY_TYPE, null);

  elems = [];
  
  while (elem = result.iterateNext()){  
    var name = elem.getAttribute("name")
  
    var path = elem.childNodes[1].childNodes[3].childNodes[1].textContent;
    var fullname = name + " in " + parentelement;
    elems.push(
      {
        'name' : name, 
        'path': path
      }
    );
  } 

  elems.sort(function(a, b) {
    return (a.name > b.name);
  });
  
  for(var x in elems) {
  
    var name = elems[x]['name'];
    var path = elems[x]['path'];
    var listitem    = document.createElement('li');
    var anchoritem  = document.createElement('a');
    var textcontent = document.createTextNode(name);     

    listitem.setAttribute("class","toctree-l2");    
    anchoritem.setAttribute("onmousedown","appendItem('" + path + "')");    

    simpleTypesMenu.appendChild(listitem);
    listitem.appendChild(anchoritem);
    anchoritem.appendChild(textcontent);
  }
  
  // /////////////////
  //   Complex Types Menu
  // /////////////////
  var complexTypesMenu = document.getElementById('complexTypes');
   
  while (complexTypesMenu.firstChild) {
    complexTypesMenu.removeChild(complexTypesMenu.firstChild);
  }
  
  if (TYPE == 'Transaction' && SUBSCHEMA == false){
    var xpath = "/xs:schema/xs:complexType[contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]";
  }
  else
    var xpath = "/xs:schema/xs:complexType";
  
  result = schema.evaluate(xpath, schema, resolver, XPathResult.ANY_TYPE, null);

  elems = [];
  
  while (elem = result.iterateNext()){  
    var name = elem.getAttribute("name")
    
    if (elem.parentElement.parentElement && elem.parentElement.parentElement.parentElement) {
       var parentelement = elem.parentElement.parentElement.parentElement.getAttribute("name");
    }
    var path = elem.childNodes[1].childNodes[3].childNodes[1].textContent;
    //var fullname = name + " in " + parentelement;
    elems.push(
      {
        'name' : name, 
        'path': path
      }
    );
  } 

  elems.sort(function(a, b) {
    return (a.name > b.name);
  });
  
  for(var x in elems) {
  
    var name = elems[x]['name'];
    var path = elems[x]['path'];
    
    var listitem    = document.createElement('li');
    var anchoritem  = document.createElement('a');
    var textcontent = document.createTextNode(name);     

    listitem.setAttribute("class","toctree-l2");    
    anchoritem.setAttribute("onmousedown","appendItem('" + path + "')");    

    complexTypesMenu.appendChild(listitem);
    listitem.appendChild(anchoritem);
    anchoritem.appendChild(textcontent);
  } 
}

function selectMenu(selectedMenu){
  var elementsMenu     = document.getElementById('elements');
  var attributesMenu   = document.getElementById('attributes');
  var simpleTypesMenu  = document.getElementById('simpleTypes');
  var complexTypesMenu = document.getElementById('complexTypes');
  
  function selectThisMenu (thisMenu) {
    if (thisMenu.previousSibling.previousSibling.className == "current") {
      thisMenu.style.display = 'none';
      thisMenu.previousSibling.previousSibling.className = ""; 
      thisMenu.parentElement.className = "toctree-l1"; 
    }
    else {
      thisMenu.removeAttribute("style");
      thisMenu.previousSibling.previousSibling.className = "current"; 
      thisMenu.parentElement.className = "toctree-l1 current"; 
    }
  }
  
  function deselectThisMenu (thisMenu) {
    thisMenu.style.display = 'none';
    thisMenu.previousSibling.previousSibling.className = ""; 
    thisMenu.parentElement.className = "toctree-l1"; 
  }
  
  if (selectedMenu == 'Elements') {
    selectThisMenu(elementsMenu);
    deselectThisMenu(attributesMenu);
    deselectThisMenu(simpleTypesMenu);
    deselectThisMenu(complexTypesMenu);
  }
  
  if (selectedMenu == 'Attributes') {
    selectThisMenu(attributesMenu);
    deselectThisMenu(elementsMenu);
    deselectThisMenu(simpleTypesMenu);
    deselectThisMenu(complexTypesMenu);
  }
  
  if (selectedMenu == 'SimpleTypes') {
    selectThisMenu(simpleTypesMenu);
    deselectThisMenu(elementsMenu);
    deselectThisMenu(attributesMenu);
    deselectThisMenu(complexTypesMenu);
  }
  
  if (selectedMenu == 'ComplexTypes') {
    selectThisMenu(complexTypesMenu);
    deselectThisMenu(elementsMenu);
    deselectThisMenu(attributesMenu);
    deselectThisMenu(simpleTypesMenu);
  }
}

function getVersion() {
  
  if (TYPE == 'Custom')
    return schema.evaluate("/xs:schema[1]/xs:annotation[1]/xs:appinfo[1]/lx:schemadetail[1]/@transactionschemasource" , schema, resolver, XPathResult.ANY_TYPE, null).iterateNext().textContent.split(" ")[1];    
  else
    return schema.evaluate("/xs:schema[1]/xs:annotation[1]/xs:appinfo[1]/lx:schemadetail[1]/@version" , schema, resolver, XPathResult.ANY_TYPE, null).iterateNext().textContent;
}

function setVersion(type_, transaction_, version_) {

/*   version = version_; */
  if (type_)        TYPE        = type_;
  if (transaction_) TRANSACTION = transaction_;
  if (version_)     VERSION     = version_; 
  
  // set the search form to include the TYPE, TRANSACTION and VERSION
  document.getElementById("search-type").setAttribute('value', TYPE);     
  document.getElementById("search-transaction").setAttribute('value', TRANSACTION);    
  document.getElementById("search-version").setAttribute('value', VERSION);     
  
  if (TYPE == 'Master'){
    url = window.location.href.split('#')[0].split('?')[0] + "?type=" + TYPE + "&version=" + VERSION + window.location.hash;
    document.getElementById("lixi-transaction-version").textContent = "LIXI Master " + VERSION;
    document.getElementById("lixi-transaction-version-mobile").textContent = "LIXI Master " + VERSION;
  }
  else {
    url = window.location.href.split('#')[0].split('?')[0] + "?type=" + TYPE + "&transaction=" + TRANSACTION + "&version=" + VERSION + window.location.hash;
    document.getElementById("lixi-transaction-version").textContent = "LIXI " + TRANSACTION + " " + VERSION;
    document.getElementById("lixi-transaction-version-mobile").textContent = "LIXI " + TRANSACTION + " " + VERSION;
  }
  
  history.pushState('wot', 'eva', url);
  
  appendMenus();
  
  // display the content for this schema item
  if(item = window.location.hash) {
    appendItem(item.substring(1));
  }
  else{
    appendItem('Package');
  }
}

function getSubschemas() {
  if (!subschemas){
    var result = schema.evaluate("/xs:schema[1]/xs:annotation[1]/xs:appinfo[1]/li:subschema" , schema, resolver, XPathResult.ANY_TYPE, null);
    var subs = {};
    while(subschema = result.iterateNext()){ 
      subs[subschema.getAttribute("transactiontype")] = subschema.getAttribute("version");
    }
    subschemas = subs;
  }
  return subschemas
}

function titleCase(str) {
  var splitStr = str.toLowerCase().split(/[ ()-\/][ ]?/);
  for (var i = 0; i < splitStr.length; i++) {
     var capitalised = splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);  
     splitStr[i]= capitalised.replace("'","&apos;");   
  }
  return splitStr.join(' '); 
}

function showEnumerations () {

  
  var enumerationTableRows = document.getElementsByClassName("enumeration-row");
  for (var i = 0; i < enumerationTableRows.length; i++) { 
      enumerationTableRows[i].setAttribute('style','');
  }

  var showmore = document.getElementById("show-more-table-row");
  showmore.style.display = "none"; 
}


///////////////////////////////////////////////////////////////////////////////////////////////
// Schema Item Class Definition
///////////////////////////////////////////////////////////////////////////////////////////////

class SchemaItem {
   
  constructor(node, evaluateXPath, contextNode) {
    
    // the constructor can accept either a DOM node or a string as the 'node' argument
    // if the argument is a string, it should be a path string e.g "Package.Content"
    if (evaluateXPath) {
      var xpath = "//xs:annotation[xs:appinfo/lx:path/text()='" +  node.replace("'","&apos;") +  "']/..";
      this.Node = schema.evaluate(xpath , schema, resolver, XPathResult.ANY_TYPE, null).iterateNext();
      this.Path = node;
    }
    
    // otherwise, a DOM node is provided as an argument and the path is read from the DOM node 'xs:path' element
    else if (typeof node != 'string') {
      this.Node = node;
      this.Path = this.Node.childNodes[1].childNodes[3].childNodes[1].textContent;
    }
    
    // if the node value is a string (e.g "Package.Content") and we are not evaluating the xpath (when evaluateXPath parameter is 'false')
    // the SchemaItem properties will need to be set manually 
    else if (typeof node == 'string' && !evaluateXPath) {
      this.Path = node;
    }
  }

  toString() {
    return ("ItemType:      " + this.ItemType + "\n" +
            "Transactions:  " + this.Transactions + "\n" +    
            "Path:          " + this.Path + "\n" + 
            "Name:          " + this.Name + "\n" + 
            "Docs:          " + this.Documentation + "\n" + 
            "Mins:          " + this.MinOccurs + "\n" + 
            "Maxs:          " + this.MaxOccurs + "\n" + 
            "Label:         " + this.Label + "\n" +
            "Base:          " + this.Base + "\n" +
            "Pattern:       " + this.Pattern + "\n" +
            "Use:           " + this.Use + "\n" +
            "Type:          " + this.Type + "\n")
  }

  getChoice(){
    if (!this.Choice){
       if (this.Node.parentNode.tagName == "xs:choice"){
         this.Choice = true;
       }
    }
    return this.Choice;
  }
  
  getParent(){
    if (!this.Parent) {
      
      if (this.Path != "Package" && this.ItemType == 'element') {
        var parentNode = this.Node.parentNode.parentNode.parentNode;
         if (parentNode.nodeName == "xs:schema") {
          parentNode = this.Node.parentNode.parentNode
          this.Parent = new SchemaItem(parentNode, false);
        }
        else {
          this.Parent = new SchemaItem(parentNode, false);
        }
      }
      
      else if (this.Path != "Package" && this.ItemType == 'attribute') {
        var parentNode = this.Node.parentNode.parentNode;
        if (parentNode.nodeName == "xs:schema") {
          parentNode = this.Node.parentNode
          this.Parent = new SchemaItem(parentNode, false);
        }
        else {
          this.Parent = new SchemaItem(parentNode, false);
        }
      } 
    }
    return this.Parent;
  }
  
  getTransactions(){
    if (!this.Transactions && this.Node.childNodes[1].childNodes[3].childNodes[5]) 
      this.Transactions = this.Node.childNodes[1].childNodes[3].childNodes[5].textContent;
    return this.Transactions
  }
  
  getItemType(){
    if (!this.ItemType) this.ItemType = this.Node.tagName.replace("xs:","");
    return this.ItemType
  }
  
  getPath(){
    return this.Path;
  }
  
  getName() {
    if (!this.Name && this.Node) this.Name = this.Node.getAttribute("name");
    return this.Name;
  }
    
  getValue() {
    if (!this.Value) this.Value = this.Node.getAttribute("value");
    return this.Value;
  }
  
  getDocumentation() {
    //console.log("Documentation: " + this.Node);
    if (!this.Documentation) this.Documentation = this.Node.childNodes[1].childNodes[1].textContent;
    return this.Documentation;
  }
  
  getCustomDocumentation(){
    if (!this.CustomDocumentation && this.Node.childNodes[1].childNodes[3].childNodes[5] && this.Node.childNodes[1].childNodes[3].childNodes[5].tagName == "lx:CustomDocumentation") this.CustomDocumentation = marked(this.Node.childNodes[1].childNodes[3].childNodes[5].textContent);
    return this.CustomDocumentation
  }
  
  getMinOccurs() {
    if (!this.MinOccurs && this.Node) this.MinOccurs = this.Node.getAttribute("minOccurs");
    return this.MinOccurs;
  }
  
  getMaxOccurs() {
    if (!this.MaxOccurs && this.Node) this.MaxOccurs = this.Node.getAttribute("maxOccurs");
    return this.MaxOccurs
  }
  
  getLabel() {
    if (!this.Label && this.Node && this.Node.childNodes[1].childNodes[3].childNodes[3].tagName == "lx:label") this.Label = this.Node.childNodes[1].childNodes[3].childNodes[3].textContent;
    return this.Label
  }
  
  getBase() {
    if (!this.Base && this.Node.childNodes[3] && (this.Node.childNodes[3].tagName == "xs:restriction")) this.Base = this.Node.childNodes[3].getAttribute("base");
    return this.Base
  }
  
  getPattern() {
    if (!this.Pattern && this.Node.childNodes[3] && (this.Node.childNodes[3].tagName == "xs:restriction") && this.Node.childNodes[3].childNodes[1] && (this.Node.childNodes[3].childNodes[1].tagName == "xs:pattern")) this.Pattern = this.Node.childNodes[3].childNodes[1].getAttribute("value");
    return this.Pattern
  }
  
  getUse() {
    if (!this.Use) this.Use = this.Node.getAttribute("use");
    return this.Use
  }

  getType() {
    if (!this.Type) this.Type = this.Node.getAttribute("type");
    return this.Type
  }
  
  getTypeObj (){
      if (!this.TypeObj) {
      this.TypeObj = new SchemaItem(this.Node.getAttribute("type"), true);
    }
    return this.TypeObj
  }

  getChildren() {
    if (!this.Children){
      if (this.getItemType() == "complexType"){
        if (TYPE == 'Transaction' && SUBSCHEMA == false)
          var xpath = "./*/xs:element[contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]";
        else
          var xpath = "./*/xs:element";
        var result = schema.evaluate(xpath , this.Node, resolver, XPathResult.ANY_TYPE, null);
      }
      else {
        if (TYPE == 'Transaction' && SUBSCHEMA == false ){
          var xpath = "./xs:complexType/*/xs:element[contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]";
        }
        else {
          var xpath = "./xs:complexType/*/xs:element";
        }
        var result = schema.evaluate(xpath , this.Node, resolver, XPathResult.ANY_TYPE, null);
      }
      var children = [];
      var childnode = null;
      while(childnode = result.iterateNext()) {
        children.push(new SchemaItem(childnode, false));
      }
      this.Children = children
    }
    return this.Children
  }    

  getAttributes() {
    if (!this.Attributes){
      if (this.getItemType() == "complexType"){
        if (TYPE == 'Transaction' && SUBSCHEMA == false ) {
          var xpath = "./xs:attribute[contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]";
        }
        else{
          var xpath = "./xs:attribute";
        }
        var result = schema.evaluate(xpath , this.Node, resolver, XPathResult.ANY_TYPE, null);
      }
      else{
        if (TYPE == 'Transaction' && SUBSCHEMA == false ) {
          var xpath = "./xs:complexType/xs:attribute[contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]";
        }
        else{
          var xpath = "./xs:complexType/xs:attribute";  
        }
        var result = schema.evaluate(xpath , this.Node, resolver, XPathResult.ANY_TYPE, null);
      }
      var attributes = [];
      var attributeNode = null;
      while(attributeNode = result.iterateNext()){ 
        var schemaItem = new SchemaItem(attributeNode, false);
        attributes.push(schemaItem);
      }
      this.Attributes = attributes;
    }
    return this.Attributes
  }

  getEnumerations(fullList) {
        
    if (!this.Enumerations){
      
      // Attributes that use a simple type list (a simpletype with a name that ends with 'List'), get the enumerations of the simple type...
      
      if ((this.getItemType() == "attribute") && (this.getType().endsWith("List"))){

        var enumerations = [];
        
        var xpath = "//xs:simpleType[@name='" + this.getType() + "']"
        var simpleTypeNode = schema.evaluate(xpath , schema, resolver, XPathResult.ANY_TYPE, null).iterateNext();
        
        var enumerations = [];
        var enumerationNodes = simpleTypeNode.childNodes[3].childNodes;
        
        for (var i = 1; i < enumerationNodes.length; i = i + 2) { 
        
          var value         = enumerationNodes[i].getAttribute("value");
          var documentation = enumerationNodes[i].childNodes[1].childNodes[1].textContent;
          var path          = enumerationNodes[i].childNodes[1].childNodes[3].childNodes[1].textContent;
          var label         = enumerationNodes[i].childNodes[1].childNodes[3].childNodes[3].textContent;

          var enumerationObj = new SchemaItem(enumerationNodes[i], false);
          
          enumerationObj.Value         =  value;
          enumerationObj.Documentation =  documentation;
          enumerationObj.Label         =  label;
          
          if (TYPE == 'Master') {
            var transactions  = enumerationNodes[i].childNodes[1].childNodes[3].childNodes[5].textContent;            
            enumerationObj.Transactions  =  transactions;
            enumerations.push(enumerationObj);
          }
          else if (TYPE == 'Transaction' && SUBSCHEMA == false ) {
            var transactions  = enumerationNodes[i].childNodes[1].childNodes[3].childNodes[5].textContent;  
            if (transactions.includes(TRANSACTION)){
              enumerations.push(enumerationObj);
            }
          }
          else if (TYPE == 'Custom'){
            enumerations.push(enumerationObj);
          }
        }
        
        this.Enumerations = enumerations;
      }
      
      // Simple types that are enumerated lists (a simpletype with a name that ends with 'List')...
      
      else if ((this.getItemType() == "simpleType") && (this.getName().endsWith("List"))) {
                
        var enumerations = [];
        var enumerationNodes = this.Node.childNodes[3].childNodes;
        
        for (var i = 1; i < enumerationNodes.length; i = i + 2) { 
        
          var value         = enumerationNodes[i].getAttribute("value");
          var documentation = enumerationNodes[i].childNodes[1].childNodes[1].textContent;
          var path          = enumerationNodes[i].childNodes[1].childNodes[3].childNodes[1].textContent;
          var label         = enumerationNodes[i].childNodes[1].childNodes[3].childNodes[3].textContent;
          
          var enumerationObj = new SchemaItem(enumerationNodes[i], false);
          
          enumerationObj.Value         =  value;
          enumerationObj.Documentation =  documentation;
          enumerationObj.Label         =  label;
          
          if (TYPE == 'Master') {
            var transactions  = enumerationNodes[i].childNodes[1].childNodes[3].childNodes[5].textContent;
            enumerationObj.Transactions =  transactions;
            enumerations.push(enumerationObj);
          }
          else if (TYPE == 'Transaction' && SUBSCHEMA == false ) {
            var transactions  = enumerationNodes[i].childNodes[1].childNodes[3].childNodes[5].textContent;  
            if (transactions.includes(TRANSACTION)){
              enumerations.push(enumerationObj);
            }
          }
          else if (TYPE == 'Custom'){
            enumerations.push(enumerationObj);
          }
        }
        this.Enumerations = enumerations;
      }
    }
    return this.Enumerations;
  }
  
  getUsedBy() {
    
    if (!this.UsedBy && ((this.getItemType() == "simpleType") || (this.getItemType() == "complexType"))) {
      
      if (this.getItemType() == "simpleType") {
        if (TYPE == "Transaction" && SUBSCHEMA == false)
          var xpath = "//xs:attribute[@type='" + this.getName() + "' and contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]";
        else 
        var xpath = "//xs:attribute[@type='" + this.getName() + "']";
      }
      if (this.getItemType() == "complexType") {
        if (TYPE == "Transaction" && SUBSCHEMA == false)
          var xpath = "//xs:element[@type='" + this.getName() + "' and contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]";
        else 
        var xpath = "//xs:element[@type='" + this.getName() + "']";
      }

      var result = schema.evaluate(xpath, schema, resolver, XPathResult.ANY_TYPE, null);
      var usedBy = [];
      var usedByNode = null;
      
      while(usedByNode = result.iterateNext()){
        
        var name          = usedByNode.getAttribute("name");
        var type          = usedByNode.getAttribute("type");
        var use           = usedByNode.getAttribute("use");
        var documentation = usedByNode.childNodes[1].childNodes[1].textContent;
        var path          = usedByNode.childNodes[1].childNodes[3].childNodes[1].textContent;
        var label         = usedByNode.childNodes[1].childNodes[3].childNodes[3].textContent;
        var itemType      = usedByNode.tagName.replace("xs:","");
        
        var usedByObj     = new SchemaItem(path, false);
        
        usedByObj.Name          = name;
        usedByObj.Type          = type;
        usedByObj.Use           = use;
        usedByObj.Documentation = documentation;
        usedByObj.ItemType      = itemType;
        usedByObj.Node          = usedByNode;

        usedBy.push(usedByObj);
      }
      
      usedBy.sort(function(a, b) {
        return (a.getName() > b.getName() ? 1 : -1);
      });
      
      this.UsedBy = usedBy;
    }
    return this.UsedBy
  }
  
  getCrossReferences() {
    if (!this.CrossReferences){

      if ((TYPE == "Custom" && this.Node.childNodes[1].childNodes[3].childNodes[5]) || this.Node.childNodes[1].childNodes[3].childNodes[7]){
        
        if (TYPE == "Custom") {
          var targets = this.Node.childNodes[1].childNodes[3].childNodes[5].childNodes;
        }
        else {
          var targets = this.Node.childNodes[1].childNodes[3].childNodes[7].childNodes;
        }
        
        var crossReferences = [];
        
        for (var i = 1; i < targets.length; i = i + 2) {
          var targetPath = targets[i].textContent;
          
          // if the target path is in the subschema
          if (TYPE == "Transaction" && SUBSCHEMA == false){
            var xpath = "//xs:element[(./xs:annotation/xs:appinfo/lx:path/text()='" + targetPath + "') and contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]";
            var result = schema.evaluate(xpath, schema, resolver, XPathResult.ANY_TYPE, null);
            
            if (result.iterateNext()){
              crossReferences.push(new SchemaItem(targetPath, true));
            }
          }
          else {
            crossReferences.push(new SchemaItem(targetPath, true));
          }
        } 
        
        this.CrossReferences = crossReferences;
      }
      
    }
    return this.CrossReferences;
  }


  getUniqueIDs() {
    if (!this.UniqueIDs){
      var uniqueIDs = [];
      var path = this.getPath()

      if (TYPE == "Transaction" && SUBSCHEMA == false){
        var xpath = "//xs:attribute[./xs:annotation/xs:appinfo/lx:references/lx:target/text()='"+path+"' and contains(./xs:annotation/xs:appinfo/li:transactions,'" + TRANSACTION + "')]/xs:annotation/xs:appinfo/lx:path/text()";
      }
      else {
        var xpath = "//xs:attribute[./xs:annotation/xs:appinfo/lx:references/lx:target/text()='"+path+"']/xs:annotation/xs:appinfo/lx:path/text()";
      }
      var result = schema.evaluate(xpath, schema, resolver, XPathResult.ANY_TYPE, null);
      var uniqueIDNode = null;
      while(uniqueIDNode = result.iterateNext()){
        uniqueIDs.push(new SchemaItem(uniqueIDNode.textContent, true));   
      }
      this.UniqueIDs = uniqueIDs;
    }
    return this.UniqueIDs;
  }
}




///////////////////////////////////////////////////////////////////////////////////////////////
// Append Full Item to HTML
///////////////////////////////////////////////////////////////////////////////////////////////

function appendItem (item, abbreviated, showAllEnumerations, showAllUsedBy, showAllReferencedBy, scrollToTop) {
  
  if (event && (event.ctrlKey || event.buttons == 4)) {
    open(window.location.href.replace(location.hash,"#" + item));
  }
  else {

    window.location.hash = item;
    
    // set default values of parameters
    if (typeof(showAllEnumerations)==='undefined') showAllEnumerations = false;
    if (typeof(showAllUsedBy)==='undefined') showAllUsedBy = false;
    if (typeof(showAllReferencedBy)==='undefined') showAllReferencedBy = false;
    if (typeof(abbreviated)==='undefined') abbreviated = false;
    if (typeof(scrollToTop)==='undefined') scrollToTop = true;
    if (typeof(useSchemaItemObject)==='undefined') useSchemaItemObject = false;
    
    appendToNode = document.getElementById('appendToNode');
    
    while (appendToNode.firstChild) {
      appendToNode.removeChild(appendToNode.firstChild);
    }
    
    if (scrollToTop) {
      $('html,body').scrollTop(0);
    }
      
      var ItemObj = new SchemaItem(item, true);
    
    // display the item name on the browser tab
    appendTitle(ItemObj);

    // display the name of the items i.e. "AccommodationBond (element)"
    appendHeading (appendToNode, ItemObj);

    // display documentation i.e. 'Account details for an account held that identifies the party as an existing customer'
    appendDocumentation (appendToNode, ItemObj);

    // display the path of the item i.e. 'Path: Package.Content.Application.LoanDetails.EquityRelease.AccommodationBond'
    appendPath(appendToNode, ItemObj, true);

    // display the min and max occurences i.e. 'minOccurs="0" maxOccurs="1"'
    appendOccurences(appendToNode, ItemObj);   

    // display label i.e. 'Label: Account'
    appendLabel(appendToNode, ItemObj);

    // display type base i.e. 'Type Base: xs:token'
    appendTypeBase(appendToNode, ItemObj);

    // display type pattern  i.e. 'Type Pattern: \d{6}'
    appendTypePattern(appendToNode, ItemObj);

    // display use i.e. 'Use: optional'
    appendUse(appendToNode, ItemObj);

    // display transactions i.e. 'Use in derived Transaction Schema: CAL,DAS'
    appendTransactions(appendToNode, ItemObj);

    // display master schema source i.e. 'Derived from: Master'
    appendSource(appendToNode, ItemObj); 

    // display parent path i.e. 'A direct descendent of : Package.Content.Application.LoanDetails.EquityRelease'
    appendParentPath (appendToNode, ItemObj);

    // display data type i.e. 'This element uses the type: financialAccountType'
    appendDataType (appendToNode, ItemObj, tooltip = true);

    // display custom documentation 
    appendCustomDocumentation (appendToNode, ItemObj);

    // display contents of element heading and table i.e. 'Contents of Element'
    appendContentsOfElement (appendToNode, ItemObj, tooltip = true);

    // display the contents of the complex type that an attribute uses
    appendComplexContent(appendToNode, ItemObj, tooltip = true);

    // display the enumerations of the type, heading and table i.e. 'Enumerations'
    appendEnumerations (appendToNode, ItemObj, showAllEnumerations = false, tooltip = true, showMoreButton = true);

    // display the attributes, or elements, that use this item as thier type i.e. "This Type is used by:"   
    appendUsedBy (appendToNode, ItemObj, showAllUsedBy, showMoreButton = true);    
    
    // display the enumerations of the type, heading and table i.e. 'Enumerations'
    appendCrossReferences (appendToNode, ItemObj, CrossReferences = false, tooltip = true, showMoreButton = true);

    appendUniqueIDs(appendToNode, ItemObj);

    // display the items that reference this type i.e. "This Item is Referenced by:"   
    //appendReferencedBy (appendToNode, ItemObj, showAllReferencedBy, true);    

    // display the paths of the ref attributes that lead to this item i.e. "ApplicationBatch.Application.FinancialSegment"
    // appendReferencePaths (appendToNode, ItemObj);

    // display the related glossary terms heading and table i.e. 'Related Glossary Terms'
    //appendRelatedGlossaryTerms (appendToNode, ItemObj);

    // display a code snippet of the XSD
    appendCodeSnippet(appendToNode, ItemObj)

    // display a code snippet of the JSONS
    appendJsonSchemaSnippet(appendToNode, ItemObj)        

    // display a code snippet of the XML
    appendXMLCodeSnippet(appendToNode, ItemObj) 

    // display confidentiality clause
    //appendConfidentialityClause (appendToNode);  
  }
}

///////////////////////////////////////////////////////////////////////////////////////////////
// Append Sections of HTML
///////////////////////////////////////////////////////////////////////////////////////////////

function appendTitle(itemObj){
  document.title = "LIXI " + itemObj.getName();
}

function appendHeading (appendToNode, itemObj) {
  if (nameText = itemObj.getName()) {
    var itemType  = itemObj.getItemType();
    var parentObj = itemObj.getParent();
    //var parentName = parentObj.getName();
    var headingNode = document.createElement('h3');
    appendToNode.appendChild(headingNode);
    if (itemObj.getPath() == "Package")
      headingNode.innerHTML = '' + nameText + " (root element)";
    else if ((itemType == "simpleType") || (itemType == "complexType"))
      headingNode.innerHTML = '' + nameText + " (" + itemType + ")";
    else
      headingNode.innerHTML = '' + nameText + " (" + itemType + " in " + parentObj.getName() + ")";
  }
}

function appendDocumentation (appendToNode, itemObj) {

  var documentationText = itemObj.getDocumentation();

  if (documentationText != '')
  {
    var documentationNode = document.createElement('p');
    documentationNode.setAttribute('class','description');
    appendToNode.appendChild(documentationNode);
    
    documentationText = insertGlossaryLinks(documentationText);
    
    html = marked(documentationText); 
    html = html.replace('<table>', '<table class="docutils">')   
    documentationNode.innerHTML = html; 
  }
}

function appendCustomDocumentation (appendToNode, itemObj) {

  var documentationText = itemObj.getCustomDocumentation();
  
  if (documentationText)
  {
    appendToNode.appendChild(document.createElement('br'));
    var documentationNode = document.createElement('p');
    appendToNode.appendChild(documentationNode);
    
    documentationText = insertGlossaryLinks(documentationText);
    
    html = documentationText; 
    html = html.replace('<table>', '<table class="docutils">')   
    documentationNode.innerHTML = html; 
  }
}

function appendPath(appendToNode, itemObj, showCopyButton) {

  var pathNode = document.createElement('small');
  var textNode = document.createTextNode('Path: ' + itemObj.Path);
  pathNode.appendChild(textNode);
  
  if (showCopyButton) {
    var copyButton = document.createElement("input");
    copyButton.setAttribute("style","vertical-align:text-bottom");
    copyButton.setAttribute("style","width:15px");
    copyButton.setAttribute("style","height:15px");
    copyButton.style.marginLeft = '5px';
    copyButton.style.marginBottom = '0px';
    copyButton.src = "./img/clip.png";
    copyButton.type = "image";
    //copyButton.addEventListener ("click", copyPath, true);
    copyButton.myParam = itemObj.Path;
    
    var showMoreNode = document.createElement('small');
    showMoreNode.className = 'tooltip-parent';        
    showMoreNode.style.textAlign = 'center';
    showMoreNode.setAttribute('onmousedown', 'copyPath("' + itemObj.Path +'")');
    showMoreNode.setAttribute('onmouseout', 'copyTextReset()');
    showMoreNode.appendChild(copyButton);
    appendCopyTooltip (showMoreNode);
    pathNode.appendChild(showMoreNode);
  }
  
  appendToNode.appendChild(pathNode);
  appendLineBreak (appendToNode);
}

function appendOccurences(appendToNode, itemObj) {
  
  var minOccurs = itemObj.getMinOccurs();
  var maxOccurs = itemObj.getMaxOccurs();
  
  if (minOccurs && maxOccurs){           
    if (maxOccurs === 'unbounded') maxOccurs = '∞';     
    if (minOccurs === '') minOccurs = 'undefined';        
    if (maxOccurs === '') maxOccurs = 'undefined';     
    var occurencesNode = document.createElement('small');
    var textNode = document.createTextNode('minOccurs="' + minOccurs + '" maxOccurs="' + maxOccurs + '"');
    appendToNode.appendChild(occurencesNode);    
    occurencesNode.appendChild(textNode);
    appendToNode.appendChild(document.createElement('br'));
  }
}

function appendLabel (appendToNode, itemObj) {
  var label = itemObj.getLabel();
  var labelNode = document.createElement('small');
  var textNode = document.createTextNode('Label: ' + label);
  appendToNode.appendChild(labelNode);
  labelNode.appendChild(textNode);
  appendToNode.appendChild(document.createElement('br'));
}

function appendTypeBase (appendToNode, itemObj) {
  if (typeBase = itemObj.getBase()){
    var typeBaseNode = document.createElement('small');
    var textNode = document.createTextNode('Type Base: ' + typeBase);
    appendToNode.appendChild(typeBaseNode);
    typeBaseNode.appendChild(textNode);
    appendToNode.appendChild(document.createElement('br'));
  }
  
}

function appendTypePattern (appendToNode, itemObj) {
  if (typePattern = itemObj.getPattern()){
    var typePatternNode = document.createElement('small');
    var textNode = document.createTextNode('Type Pattern: ' + typePattern);
    appendToNode.appendChild(typePatternNode);
    typePatternNode.appendChild(textNode);
    appendToNode.appendChild(document.createElement('br'));
  }
}

function appendUse (appendToNode, itemObj) {
  if (use = itemObj.getUse()){
      var useNode = document.createElement('small');
      var textNode = document.createTextNode('Use: ' + use);
      appendToNode.appendChild(useNode);
      useNode.appendChild(textNode);
      appendToNode.appendChild(document.createElement('br'));
  }
}

function appendSource (appendToNode, itemObj) {
  
    if (TYPE == 'Transaction' && SUBSCHEMA == false){
      
      var itemType = itemObj.getItemType();

      var sourceNode = document.createElement('small');
      var textNode = document.createTextNode('Derived From: ');        
      sourceNode.appendChild(textNode);
      
      var masterVersion = getVersion();

      // text to display for link e.g. "Master 2.5.0"
      var schemaName = "Master " + masterVersion;
      var textNode = document.createTextNode(schemaName);

      // anchor node
      var anchorNode = document.createElement('a');
      anchorNode.appendChild(textNode);
      anchorNode.setAttribute('onmousedown', 'setVersion("Master","undefined", "' + masterVersion + '")')
      
      // tooltip
      appendCustomTooltip(anchorNode, "View " + schemaName + " schema documentation");

      sourceNode.appendChild(anchorNode);
      appendToNode.appendChild(sourceNode);
      appendToNode.appendChild(document.createElement('br'));
    }
}

function appendParentPath (appendToNode, itemObj) {

  var ancestorsStr= itemObj.Path.substr(0, itemObj.Path.lastIndexOf("."));

  itemType = itemObj.getItemType();

  // if (item == 'Package')
  if (ancestorsStr == '')
  {
      var descendantNode = document.createElement('small');

      appendToNode.appendChild(descendantNode);
      var textNode = document.createTextNode('This element is at the root level of the schema.');
      descendantNode.appendChild(textNode);
      appendToNode.appendChild(descendantNode);
      appendToNode.appendChild(document.createElement('br'));
  }
  else if (itemType != 'complexType' && itemType != 'simpleType')
  {
      // get the ancestor path and split it into its elements
      var ancestorsArray = ancestorsStr.split('.');

      // create new node to display the parent path in
      var descendantNode = document.createElement('small');
      appendToNode.appendChild(descendantNode);
      var textNode = document.createTextNode('A direct descendant of: ');
      descendantNode.appendChild(textNode);

      // loop through each element in the path
      for (var i = 0; i < ancestorsArray.length; i++) 
      {
          // get the item name
          var text = ancestorsArray[i];
          var textNode = document.createTextNode(text);  

          // add an anchor element
          anchorNode = document.createElement('a');
          anchorNode.className = 'tooltip-parent';
          descendantNode.appendChild(anchorNode);
          anchorNode.appendChild(textNode);

          // set the href of the link
          var compositePath = (ancestorsArray.slice(0, i + 1)).join('.');
          
          ////////////////////////////////////////////
          // create the objct for the child 
          ///////////////////////////////////////////
          
          var ancestorObj = new SchemaItem(compositePath, true);

          //var itemType = ancestorObj.getItemType();
          
          /* var href = "./index.html#" + compositePath;
          anchorNode.href = href; */
          
          anchorNode.setAttribute('onmousedown', 'appendItem(\'' + ancestorObj.Path +'\')');
          
          // add the tool tip to the element 
          appendTooltip(anchorNode, ancestorObj, tooltip = false);
          
          // add a period between each element in the path
          var textNode = document.createTextNode('.');
          descendantNode.appendChild(textNode);
      }

      // remove the last period at the end of the path
      descendantNode.removeChild(descendantNode.lastChild);
      appendToNode.appendChild(document.createElement('br'));  
  }
}

function appendDataType (appendToNode, itemObj, tooltip)  {  
  // set default value of tooltip to false
  if (typeof(tooltip)==='undefined') tooltip = false;
  var itemDataType = itemObj.getType();

  if (itemDataType)
  {
    // prefix
    var smallNode = document.createElement('small');
    var itemType = itemObj.getType();

    if (itemType == 'attribute')
    {
      var textNode = document.createTextNode('This attribute uses the type: ');
    }
    else 
    {
      var textNode = document.createTextNode('This element uses the type: ');      
    }
    // anchor
    var usesTextNode = document.createTextNode(itemDataType);
    var anchorNode = document.createElement('a');

    //var unique_name = clean(uniqueJSON[itemDataType]);
    // href
    
    ////////////////////////////////////////////////////////////////////
    // Create a new Object for the Simple or Complex type that is used
    /////////////////////////////////////////////////////////////////////
    
    var typeObj = new SchemaItem(itemDataType, true);
    
    
/*     var href = "./index.html#" + itemObj.Path;
    href = href.toLowerCase();
    anchorNode.href = href;  */
    
    anchorNode.setAttribute('onmousedown', 'appendItem(\'' + itemObj.Type +'\')');
    
    if (tooltip) anchorNode.className = 'tooltip-parent';
    
    // append all the nodes
    appendToNode.appendChild(smallNode);
    smallNode.appendChild(textNode);
    anchorNode.appendChild(usesTextNode);
    smallNode.appendChild(anchorNode);
    appendToNode.appendChild(smallNode);
    appendToNode.appendChild(document.createElement('br'));

    // tool tip
    if (tooltip) appendTooltip(anchorNode, typeObj);  
     
    else
    {
      appendToNode.appendChild(smallNode);
      smallNode.appendChild(textNode);
      var textNode = document.createTextNode(itemDataType);
      smallNode.appendChild(textNode);
      appendToNode.appendChild(document.createElement('br'));
    }
  }
}

function appendTransactions (appendToNode, itemObj) {
  
  if (TYPE == 'Master'){

    var transactions = itemObj.getTransactions();
    
    //console.log("transactions: ",transactions);
  
     if (transactions){

      var transactionsNode = document.createElement('small');

      var textNode = document.createTextNode('Use in derived Transaction Schema: ');
      transactionsNode.appendChild(textNode);
      appendToNode.appendChild(transactionsNode);
      appendToNode.appendChild(document.createElement('br'));

      transactionsArray = transactions.split(",");

      for (var i = 0; i < transactionsArray.length; i++) 
      {
          // name of transaction and version, in a safe to use format
          var transaction = transactionsArray[i];
          //console.log("transaction: ",transaction);

          // replace all dots using a regular expression
          // var subSchema = transactionsJSON[transaction].toLowerCase().replace(/\./g, '_');  
          
          var transactionLow = transaction.toLowerCase();
          var versionnumber = getSubschemas()[transaction].replace(/\./g, '_')
          
          //console.log("transactionLow: ", transactionLow);
          //console.log("subschemas: ", versionnumber);        
          
          // create a safe version of the transaction sub schema name i.e. 'CAL 2.5.0' becomes 'cal-2_5_0'

           var itemType = itemObj.getItemType();
          //var href = "../../../" + transactionLow + "/" + versionnumber + "/" + itemObj.getItemType().toLowerCase() + "/index.html#" + itemObj.getPath()

          var anchorNode = document.createElement('a');
          var textNode = document.createTextNode(transaction + " " + subschemas[transaction]);
          
          anchorNode.setAttribute('onmousedown', 'setVersion("Transaction","' + transaction + '", "' + getSubschemas()[transaction] + '")')

          anchorNode.appendChild(textNode);
          //anchorNode.href = href;
          anchorNode.className = 'tooltip-parent';
          
          transactionsNode.appendChild(anchorNode);  
          var textNode = document.createTextNode(", ");
          transactionsNode.appendChild(textNode);
          appendCustomTooltip(anchorNode, "View " + transaction + " " + getSubschemas()[transaction] + " schema documentation");  
      }

      // remove the last trailing comma
      transactionsNode.removeChild(transactionsNode.lastChild);
    } 
  }
}

function appendContentsOfElement (appendToNode, itemObj, tooltip = false, heading) {
  
    // set default value of tooltip to false
    if (typeof(tooltip)==='undefined') tooltip = false;

    // set default value of heading to ''
    if (typeof(heading)==='undefined') heading = '';
    
    //console.log("Schema Item Object: " + itemObj);
    
    // and if the item uses a complexType, don't append contents of element
    if (itemObj.getItemType()) {
      
      // only append this table if the type is 'element' or 'complexType'
      // because 'attribute' and 'simpleType' never have any children
      var itemType = itemObj.getItemType();

      if (itemType == 'element' || itemType == 'complexType')
      {

        if (heading == '' && itemType == 'complexType')
            heading = 'Contents of Complex Type';

        if (heading == '' && itemType == 'element')
            heading = 'Contents of Element';

        // get the children of this item
        var childrenArray = itemObj.getChildren();
        
        // get the children of this item
        var attributeArray = itemObj.getAttributes();
        
        childrenArray = childrenArray.concat(attributeArray);

        //var childrenArray = hierarchyJSON[item]; 
        if (childrenArray.length > 0) 
        {
          // heading
          var textNode = document.createTextNode(heading);
          var headingNode = document.createElement('h4');
          headingNode.appendChild(textNode);
          appendToNode.appendChild(document.createElement('br'));
          appendToNode.appendChild(headingNode)

          // table
          var tableNode = document.createElement('table');
          tableNode.className = 'docutils';
          appendToNode.appendChild(tableNode);

          // table header
          var headerNode = document.createElement('thead');
          tableNode.appendChild(headerNode);

          // table row 
          var headerRowNode = document.createElement('tr');
          headerNode.appendChild(headerRowNode);

          // heading column one: 'Type'
          var headOne = document.createElement('th');
          headerRowNode.appendChild(headOne);
          var headOneText = document.createTextNode('Type');
          headOne.appendChild(headOneText);

          // heading column two: 'Item'
          var headTwo = document.createElement('th');
          headerRowNode.appendChild(headTwo);
          var headTwoText = document.createTextNode('Item');
          headTwo.appendChild(headTwoText);

          // heading column three: 'Definition'
          var headThree = document.createElement('th');
          headerRowNode.appendChild(headThree);
          var headThreeText = document.createTextNode('Definition');
          headThree.appendChild(headThreeText); 
          
          // heading column four: 'Schema(s)'
          if (TYPE == 'Master'){
            var headFour = document.createElement('th');
            headerRowNode.appendChild(headFour);
            var headFourText = document.createTextNode('Schema(s)');
            headFour.appendChild(headFourText); 
          }

          // table body
          var bodyNode = document.createElement('tbody');
          tableNode.appendChild(bodyNode);

          for (var i = 0; i < childrenArray.length; i++) 
          {
            // table row
            var rowNode = document.createElement('tr');
            bodyNode.appendChild(rowNode);

            // child info
            var childObj = childrenArray[i];
            var childCustomizedExcerpt = null;
          
            var childName = childObj.getName();
            var childType = childObj.getItemType()
            var childDef =  childObj.getDocumentation();
            var childCustomDocumentation = childObj.getCustomDocumentation();

            // TODO customised excerpts
  /*                     if (childObj[19] !== "" && childObj[19] != null){
                childCustomizedExcerpt = childObj[19];
              childCustomizedExcerpt = marked(childCustomizedExcerpt);
            } else if(childObj[15] !== ""){
                var temp = childObj[15];
                childCustomizedExcerpt = marked(temp);
            }  */

            // column one
            var colOneNode = document.createElement('td');
            
            // TODO choice
            // var childIsChoice = childObj[18];
            var childIsChoice = childObj.getChoice();

            if (childIsChoice == true) {
                var textNode = document.createTextNode(childType + " (choice)");
            }
            else{
                var textNode = document.createTextNode(childType);
            }
            
            // info icon
            //var colTwoContent  = document.createElement('p');
            //colTwoContent.setAttribute('class','col-two-content');


            rowNode.appendChild(colOneNode);
            colOneNode.appendChild(textNode);
     

            // column two
            var colTwoNode = document.createElement('td');
            colTwoNode.setAttribute('class','coltwo');
            var textNode = document.createTextNode(childName);

            var anchorNode = document.createElement('a');
            
            anchorNode.setAttribute('onmousedown', 'appendItem(\'' + childObj.Path +'\')');
            
            rowNode.appendChild(colTwoNode);
            colTwoNode.appendChild(anchorNode);
            anchorNode.appendChild(textNode);
            
            if (tooltip == true) {
              var iconNode = document.createElement('a');
              var imageNode = document.createElement('img');
              imageNode.setAttribute('src','img/info-icon.png');
              imageNode.setAttribute('class','info');
              iconNode.className = 'tooltip-parent';  
              iconNode.setAttribute('onmousedown', 'appendItem(\'' + childObj.Path +'\')');
              colTwoNode.appendChild(iconNode);
              iconNode.appendChild(imageNode);
              appendTooltip(iconNode, childObj); 
            }              

            // column three
            var colThreeNode = document.createElement('td');
            rowNode.appendChild(colThreeNode);

            var textNode = document.createTextNode(childDef);
            colThreeNode.appendChild(textNode);
            
            if (childCustomDocumentation) {
              var textNode = document.createElement('p');
              textNode.innerHTML = childCustomDocumentation;
              appendLineBreak(colThreeNode)
              appendLineBreak(colThreeNode)
              colThreeNode.appendChild(textNode);
            }
            
            // column four (only displayed in master schema documentation)
            if (TYPE == 'Master'){
              var enumTransactions;
              if (enumTransactions = childObj.getTransactions()) {
                  var colFourNode = document.createElement('td');
                  rowNode.appendChild(colFourNode);
                  var textNode = document.createTextNode(enumTransactions);
                  colFourNode.appendChild(textNode);
              }
            }
          }
        }
      }
/*       else 
      {
        // heading
        var textNode = document.createTextNode('Contents of Element');
        var headingNode = document.createElement('h4');
        headingNode.appendChild(textNode);
        appendToNode.appendChild(document.createElement('br'));
        appendToNode.appendChild(headingNode)
        // this Element has no children
        var textNode = document.createTextNode('This element has no children.');
        var noChildrenNode = document.createElement('p');
        noChildrenNode.appendChild(textNode);
        appendToNode.appendChild(noChildrenNode)
      } */
    }
}

function appendComplexContent(appendToNode, itemObj, tooltip = false){
  // set default value of tooltip to false
  if (typeof(tooltip)==='undefined') tooltip = false;


  // check the complex type attribtute exists
  if (itemDataType = itemObj.getType()) {
    
    //console.log("Create complex type object: " + itemDataType);
    
    // create Schema Item object for complex type 
    var complexTypeObj = new SchemaItem(itemDataType, true);
    
    // get the type of the type
    var dataTypeType = complexTypeObj.getItemType();
    
    // check is the type type 'complexType'
    if (dataTypeType == 'complexType') {
        var headingValue = 'Contents of Complex Type: ' + itemDataType;
        
        appendContentsOfElement(appendToNode, complexTypeObj, tooltip=tooltip, heading = headingValue);
    }
  }
}

function appendEnumerations(appendToNode, itemObj, showAllEnumerations, tooltip, showMoreButton) {

  // TODO display all enumerations (showAllEnumerations == true)
  var enumerations = itemObj.getEnumerations(true);
  
  // set default value of showAllEnumerations to false
  if (typeof(showAllEnumerations) === 'undefined') showAllEnumerations = false;
  if (typeof(tooltip) === 'undefined') tooltip = false;
  if (typeof(showMoreButton) === 'undefined') showMoreButton = false;

  if (enumerations) {

    // heading
    var textNode = document.createTextNode('Enumerations');
    var headingNode = document.createElement('h4');
    headingNode.appendChild(textNode);
    appendToNode.appendChild(document.createElement('br'));
    appendToNode.appendChild(headingNode);

    // table
    var tableNode = document.createElement('table');
    tableNode.className = 'docutils';
    tableNode.id = item + "-enumerations";
    appendToNode.appendChild(tableNode);

    // table header
    var headerNode = document.createElement('thead');
    tableNode.appendChild(headerNode);

    // table row 
    var headerRowNode = document.createElement('tr');
    headerNode.appendChild(headerRowNode);

    // heading column one: 'Enumerations'
    var headOne = document.createElement('th');
    headerRowNode.appendChild(headOne);
    var headOneText = document.createTextNode('Enumeration');
    headOne.appendChild(headOneText);

    // heading column two: 'Definition'
    var headTwo = document.createElement('th');
    headerRowNode.appendChild(headTwo);
    var headTwoText = document.createTextNode('Definition');
    headTwo.appendChild(headTwoText);
    
    if (TYPE == 'Master'){
      // heading column three: 'Schema(s)'
      var headThree = document.createElement('th');
      headerRowNode.appendChild(headThree);
      var headTwoText = document.createTextNode('Schema(s)');
      headThree.appendChild(headTwoText);
    }

    // table body
    var bodyNode = document.createElement('tbody');
    tableNode.appendChild(bodyNode);

    for (var i = 0; i < enumerations.length; i++) {

      // table row
      var rowNode = document.createElement('tr');
      
      if (!showAllEnumerations && (i > 9)) {
        rowNode.setAttribute('style','display: none;');
        rowNode.setAttribute('class', 'enumeration-row');
      }
      
      bodyNode.appendChild(rowNode);
      
      // enumeration info
      var enumeration = enumerations[i];
      
      // enumeration definition
      var definition = enumeration.getDocumentation();
      var definitionToShow = definition;
      
      // TODO Custom Definitions
    /*   if (enumerationsDict[enumeration][5] != null && enumerationsDict[enumeration][5] != '') {
          definition = definition + '\n\n' + enumerationsDict[enumeration][5]
          definitionToShow = marked(definition);
      } */

      // append the transaction schema info to the end of the definition
      if (TYPE == "Master")
        var enumTransactions = enumeration.getTransactions();

      // column one, enumeration name and link to attribute
      var colOneNode = document.createElement('td');
      var textNode = document.createTextNode(enumeration.getValue());
      // var anchorNode = document.createElement('a');              
      // anchorNode.href =  "../attribute/index.html#" + enumeration.toLowerCase().replace(' ', '-');

      rowNode.appendChild(colOneNode);
      colOneNode.appendChild(textNode);

      // column two
      var colTwoNode = document.createElement('td');
      colTwoNode.innerHTML = marked(definitionToShow).replace("<p>", "").replace("</p>", "");
      rowNode.appendChild(colTwoNode);
      
      // column three (only displayed in master schema documentation)
      if (TYPE == 'Master'){
        var enumTransactions;
        if (enumTransactions = enumeration.getTransactions()) {
            var colThreeNode = document.createElement('td');
            rowNode.appendChild(colThreeNode);
            var textNode = document.createTextNode(enumTransactions);
            colThreeNode.appendChild(textNode);
        }
      }
    }
                      
    if (showMoreButton && (enumerations.length > 10)) {      
      // onmousedown
      var rowNode = document.createElement('tr');
      rowNode.setAttribute('id', 'show-more-table-row')
      bodyNode.appendChild(rowNode);
      var colNode = document.createElement('td');
      rowNode.appendChild(colNode);

      if (TYPE == "Master")
        colNode.setAttribute('colspan', '3');
      else
        colNode.setAttribute('colspan', '2');
          
      var showMoreNode = document.createElement('small');
      showMoreNode.className = 'show-more tooltip-parent';
      showMoreNode.setAttribute('onmousedown', 'showEnumerations()');
      colNode.appendChild(showMoreNode);
      var textNode = document.createTextNode("show more...");
      showMoreNode.appendChild(textNode);
      appendCustomTooltip(showMoreNode, 'Only 10 enumerations are currently displayed. Click here to view all enumerations.');    
    }
  } 
}

function appendUsedBy (appendToNode, itemObj, showAllUsedBy, showMoreButton) {
  
  var usedBy = itemObj.getUsedBy();
  
  if (usedBy && usedBy.length > 0) {

    var textNode = document.createTextNode('This Type is Used By:');
    var headingNode = document.createElement('h4');
    headingNode.appendChild(textNode);
    appendToNode.appendChild(document.createElement('br'));
    appendToNode.appendChild(headingNode);

    // table
    var tableNode = document.createElement('table');
    tableNode.className = 'docutils';
    tableNode.id = item + "-usedBy";
    appendToNode.appendChild(tableNode);

    // table header
    var headerNode = document.createElement('thead');
    tableNode.appendChild(headerNode);

    // table row 
    var headerRowNode = document.createElement('tr');
    headerNode.appendChild(headerRowNode);

    // heading column one: 'Item'
    var headOne = document.createElement('th');
    headerRowNode.appendChild(headOne);
    var headOneText = document.createTextNode('Item');
    headOne.appendChild(headOneText);

    // heading column two: 'Path'
    // var headTwoA = document.createElement('th');
    // headerRowNode.appendChild(headTwoA);
    // var headTwoText = document.createTextNode('Path');
    // headTwoA.appendChild(headTwoText);
    
    //   heading column three: 'Definition'
    var headTwo = document.createElement('th');
    headerRowNode.appendChild(headTwo);
    var headTwoText = document.createTextNode('Definition');
    headTwo.appendChild(headTwoText);

    // table body
    var bodyNode = document.createElement('tbody');
    tableNode.appendChild(bodyNode);

    for (var i = 0; i < usedBy.length; i++) {

      // table row
      var rowNode = document.createElement('tr');
      
      if (!showAllUsedBy && (i > 9)) {
        rowNode.setAttribute('style','display: none;');
        rowNode.setAttribute('class', 'enumeration-row');
      }
      
      bodyNode.appendChild(rowNode);

      // info
      var path       = usedBy[i].getPath();
      var itemName   = usedBy[i].getName();
      var definition = usedBy[i].getDocumentation();
      var itemType   = usedBy[i].getItemType();
      var parentName = usedBy[i].getParent().getName();

      // column one
      var colOneNode = document.createElement('td');
      var textNode = document.createTextNode(itemName + " (in " + parentName + ")");
      var anchorNode = document.createElement('a');   
      
      // onmousedown
      anchorNode.setAttribute('onmousedown', 'appendItem(\'' + path +'\')');

      rowNode.appendChild(colOneNode);
      colOneNode.appendChild(anchorNode);
      anchorNode.appendChild(textNode)
      
      // tooltip
 /*       if (tooltip == true) {
        var iconNode = document.createElement('a');
        var imageNode = document.createElement('img');
        imageNode.setAttribute('src','img/info-icon.png');
        imageNode.setAttribute('class','info');
        iconNode.className = 'tooltip-parent';  
        iconNode.setAttribute('onmousedown', 'appendItem(\'' + path +'\')');
        colOneNode.appendChild(iconNode);
        iconNode.appendChild(imageNode);
        appendTooltip(iconNode, usedBy[i]); 
      }   */     
            
      // column two A
      // var colTwoANode = document.createElement('td');
      // rowNode.appendChild(colTwoANode);

      // var textNode = document.createTextNode(path);
      // colTwoANode.appendChild(textNode);   
      
      // column two
      var colTwoNode = document.createElement('td');
      rowNode.appendChild(colTwoNode);

      var textNode = document.createTextNode(definition);
      colTwoNode.appendChild(textNode);                    
    }
    
    if (showMoreButton && (usedBy.length > 10)) {      
      // onmousedown
      var rowNode = document.createElement('tr');
      rowNode.setAttribute('id', 'show-more-table-row')
      bodyNode.appendChild(rowNode);
      var colNode = document.createElement('td');
      rowNode.appendChild(colNode);

      if (TYPE == "Master")
        colNode.setAttribute('colspan', '3');
      else
        colNode.setAttribute('colspan', '2');
          
      var showMoreNode = document.createElement('small');
      showMoreNode.className = 'show-more tooltip-parent';
      showMoreNode.setAttribute('onmousedown', 'showEnumerations()');
      colNode.appendChild(showMoreNode);
      var textNode = document.createTextNode("show more...");
      showMoreNode.appendChild(textNode);
      appendCustomTooltip(showMoreNode, 'Only 10 items are currently displayed. Click here to view all items.');    
    }
    
    // line break            
    appendToNode.appendChild(document.createElement('br'));
  }
}

function appendUniqueIDs (appendToNode, itemObj, showAllCrossReferences, tooltip, showMoreButton) {

  var crossReferences = itemObj.getUniqueIDs();

  // set default value of showAllCrossReferences to false
  if (typeof(showAllCrossReferences) === 'undefined') showAllCrossReferences = false;
  if (typeof(tooltip) === 'undefined') tooltip = true;
  if (typeof(showMoreButton) === 'undefined') showMoreButton = false;

  if (crossReferences.length > 0) {

    // heading
    var textNode = document.createTextNode('Cross Referenced By');
    var headingNode = document.createElement('h4');
    headingNode.appendChild(textNode);
    appendToNode.appendChild(document.createElement('br'));
    appendToNode.appendChild(headingNode);
    
    // description of what this table is (to explain to the user of the documentation what they are looking at)
    var textNode = document.createTextNode('\'' + itemObj.getName() +  '\' can be cross referenced from the attributes shown in this table:');
    var explainationNode = document.createElement('small');
    explainationNode.appendChild(textNode);
    appendToNode.appendChild(explainationNode);
    appendToNode.appendChild(document.createElement('br'));
    appendToNode.appendChild(document.createElement('br'));

    // table
    var tableNode = document.createElement('table');
    tableNode.className = 'docutils';
    tableNode.id = item + "-crossReferences";
    appendToNode.appendChild(tableNode);

    // table header
    var headerNode = document.createElement('thead');
    tableNode.appendChild(headerNode);

    // table row 
    var headerRowNode = document.createElement('tr');
    headerNode.appendChild(headerRowNode);

    // heading column one: 'Target'
    var headOne = document.createElement('th');
    headerRowNode.appendChild(headOne);
    var headOneText = document.createTextNode('Target');
    headOne.appendChild(headOneText);

    // heading column two: 'Definition'
    var headTwo = document.createElement('th');
    headerRowNode.appendChild(headTwo);
    var headTwoText = document.createTextNode('Definition');
    headTwo.appendChild(headTwoText);
    
    if (TYPE == 'Master'){
      // heading column three: 'Schema(s)'
      var headThree = document.createElement('th');
      headerRowNode.appendChild(headThree);
      var headTwoText = document.createTextNode('Schema(s)');
      headThree.appendChild(headTwoText);
    }

    // table body
    var bodyNode = document.createElement('tbody');
    tableNode.appendChild(bodyNode);

    for (var i = 0; i < crossReferences.length; i++) {

      // table row
      var rowNode = document.createElement('tr');
      
      if (!showAllCrossReferences && (i > 9)) {
        rowNode.setAttribute('style','display: none;');
        rowNode.setAttribute('class', 'enumeration-row');
      }
      
      bodyNode.appendChild(rowNode);
      
      // enumeration info
      var crossReference = crossReferences[i];
      
      // enumeration definition
      var definition = crossReference.getDocumentation();
      var definitionToShow = definition;
      
      // TODO Custom Definitions
    /*   if (enumerationsDict[enumeration][5] != null && enumerationsDict[enumeration][5] != '') {
          definition = definition + '\n\n' + enumerationsDict[enumeration][5]
          definitionToShow = marked(definition);
      } */

      // append the transaction schema info to the end of the definition
      if (TYPE == "Master")
        var enumTransactions = crossReference.getTransactions();

      // column one, enumeration name and link to attribute
      var colOneNode = document.createElement('td');
      var textNode = document.createTextNode(crossReference.getName());
      
      var anchorNode = document.createElement('a');  
      anchorNode.setAttribute('onmousedown', 'appendItem(\'' + crossReference.getPath() +'\')');      


      rowNode.appendChild(colOneNode);
      colOneNode.appendChild(anchorNode);
      anchorNode.appendChild(textNode);
      
      if (tooltip == true) {
        var iconNode = document.createElement('a');
        var imageNode = document.createElement('img');
        imageNode.setAttribute('src','img/info-icon.png');
        imageNode.setAttribute('class','info');
        iconNode.className = 'tooltip-parent'; 
        iconNode.setAttribute('onmousedown', 'appendItem(\'' + crossReference.getPath() +'\')');             
        colOneNode.appendChild(iconNode);
        iconNode.appendChild(imageNode);
        appendTooltip(iconNode, crossReference); 
      }  

      // column two
      var colTwoNode = document.createElement('td');
      colTwoNode.innerHTML = marked(definitionToShow).replace("<p>", "").replace("</p>", "");
      rowNode.appendChild(colTwoNode);
      
      // column three (only displayed in master schema documentation)
      if (TYPE == 'Master'){
        var enumTransactions;
        if (enumTransactions = crossReference.getTransactions()) {
            var colThreeNode = document.createElement('td');
            rowNode.appendChild(colThreeNode);
            var textNode = document.createTextNode(enumTransactions);
            colThreeNode.appendChild(textNode);
        }
      }
    }
                      
    if (showMoreButton && (crossReferences.length > 10)) {      
      // onmousedown
      var rowNode = document.createElement('tr');
      rowNode.setAttribute('id', 'show-more-table-row')
      bodyNode.appendChild(rowNode);
      var colNode = document.createElement('td');
      rowNode.appendChild(colNode);

      if (TYPE == "Master")
        colNode.setAttribute('colspan', '3');
      else
        colNode.setAttribute('colspan', '2');
          
      var showMoreNode = document.createElement('small');
      showMoreNode.className = 'show-more tooltip-parent';
      showMoreNode.setAttribute('onmousedown', 'showEnumerations()');
      colNode.appendChild(showMoreNode);
      var textNode = document.createTextNode("show more...");
      showMoreNode.appendChild(textNode);
      appendCustomTooltip(showMoreNode, 'Only 10 enumerations are currently displayed. Click here to view all enumerations.');    
    }
  } 
}

    
function appendCrossReferences(appendToNode, itemObj, showAllCrossReferences, tooltip, showMoreButton) {

  // TODO display all enumerations (showAllEnumerations == true)
  var crossReferences = itemObj.getCrossReferences(true);
  
  // set default value of showAllCrossReferences to false
  if (typeof(showAllCrossReferences) === 'undefined') showAllCrossReferences = false;
  if (typeof(tooltip) === 'undefined') tooltip = false;
  if (typeof(showMoreButton) === 'undefined') showMoreButton = false;

  if (crossReferences) {

    // heading
    var textNode = document.createTextNode('Cross Reference');
    var headingNode = document.createElement('h4');
    headingNode.appendChild(textNode);
    appendToNode.appendChild(document.createElement('br'));
    appendToNode.appendChild(headingNode);
    
    // description of what this table is (to explain to the user of the documentation what they are looking at)
    var textNode = document.createTextNode('\'' + itemObj.getName() +  '\' should cross reference the \'UniqueID\' attribute of one of the elements shown in this table:');
    var explainationNode = document.createElement('small');
    explainationNode.appendChild(textNode);
    appendToNode.appendChild(explainationNode);
    appendToNode.appendChild(document.createElement('br'));
    appendToNode.appendChild(document.createElement('br'));

    // table
    var tableNode = document.createElement('table');
    tableNode.className = 'docutils';
    tableNode.id = item + "-crossReferences";
    appendToNode.appendChild(tableNode);

    // table header
    var headerNode = document.createElement('thead');
    tableNode.appendChild(headerNode);

    // table row 
    var headerRowNode = document.createElement('tr');
    headerNode.appendChild(headerRowNode);

    // heading column one: 'Target'
    var headOne = document.createElement('th');
    headerRowNode.appendChild(headOne);
    var headOneText = document.createTextNode('Target');
    headOne.appendChild(headOneText);

    // heading column two: 'Definition'
    var headTwo = document.createElement('th');
    headerRowNode.appendChild(headTwo);
    var headTwoText = document.createTextNode('Definition');
    headTwo.appendChild(headTwoText);
    
    if (TYPE == 'Master'){
      // heading column three: 'Schema(s)'
      var headThree = document.createElement('th');
      headerRowNode.appendChild(headThree);
      var headTwoText = document.createTextNode('Schema(s)');
      headThree.appendChild(headTwoText);
    }

    // table body
    var bodyNode = document.createElement('tbody');
    tableNode.appendChild(bodyNode);

    for (var i = 0; i < crossReferences.length; i++) {

      // table row
      var rowNode = document.createElement('tr');
      
      if (!showAllCrossReferences && (i > 9)) {
        rowNode.setAttribute('style','display: none;');
        rowNode.setAttribute('class', 'enumeration-row');
      }
      
      bodyNode.appendChild(rowNode);
      
      // enumeration info
      var crossReference = crossReferences[i];
      
      // enumeration definition
      var definition = crossReference.getDocumentation();
      var definitionToShow = definition;
      
      // TODO Custom Definitions
    /*   if (enumerationsDict[enumeration][5] != null && enumerationsDict[enumeration][5] != '') {
          definition = definition + '\n\n' + enumerationsDict[enumeration][5]
          definitionToShow = marked(definition);
      } */

      // append the transaction schema info to the end of the definition
      if (TYPE == "Master")
        var enumTransactions = crossReference.getTransactions();

      // column one, enumeration name and link to attribute
      var colOneNode = document.createElement('td');
      var textNode = document.createTextNode(crossReference.getName());
      
      var anchorNode = document.createElement('a');  
      anchorNode.setAttribute('onmousedown', 'appendItem(\'' + crossReference.getPath() +'\')');      


      rowNode.appendChild(colOneNode);
      colOneNode.appendChild(anchorNode);
      anchorNode.appendChild(textNode);
      
      if (tooltip == true) {
        var iconNode = document.createElement('a');
        var imageNode = document.createElement('img');
        imageNode.setAttribute('src','img/info-icon.png');
        imageNode.setAttribute('class','info');
        iconNode.className = 'tooltip-parent'; 
        iconNode.setAttribute('onmousedown', 'appendItem(\'' + crossReference.getPath() +'\')');             
        colOneNode.appendChild(iconNode);
        iconNode.appendChild(imageNode);
        appendTooltip(iconNode, crossReference); 
      }  

      // column two
      var colTwoNode = document.createElement('td');
      colTwoNode.innerHTML = marked(definitionToShow).replace("<p>", "").replace("</p>", "");
      rowNode.appendChild(colTwoNode);
      
      // column three (only displayed in master schema documentation)
      if (TYPE == 'Master'){
        var enumTransactions;
        if (enumTransactions = crossReference.getTransactions()) {
            var colThreeNode = document.createElement('td');
            rowNode.appendChild(colThreeNode);
            var textNode = document.createTextNode(enumTransactions);
            colThreeNode.appendChild(textNode);
        }
      }
    }
                      
    if (showMoreButton && (crossReferences.length > 10)) {      
      // onmousedown
      var rowNode = document.createElement('tr');
      rowNode.setAttribute('id', 'show-more-table-row')
      bodyNode.appendChild(rowNode);
      var colNode = document.createElement('td');
      rowNode.appendChild(colNode);

      if (TYPE == "Master")
        colNode.setAttribute('colspan', '3');
      else
        colNode.setAttribute('colspan', '2');
          
      var showMoreNode = document.createElement('small');
      showMoreNode.className = 'show-more tooltip-parent';
      showMoreNode.setAttribute('onmousedown', 'showEnumerations()');
      colNode.appendChild(showMoreNode);
      var textNode = document.createTextNode("show more...");
      showMoreNode.appendChild(textNode);
      appendCustomTooltip(showMoreNode, 'Only 10 enumerations are currently displayed. Click here to view all enumerations.');    
    }
  } 
}

///////////////////////////////////////////////////////////////////////////////////////////////
// Append Code Snippets to HTML
///////////////////////////////////////////////////////////////////////////////////////////////  
  
function appendCodeSnippet(appendToNode, itemObj) {


  // line break            
  appendToNode.appendChild(document.createElement('br'));
    
   // /////////////////////////////////
  // put the xml string together
  // /////////////////////////////////
  
  // get the element info
  var itemtype = itemObj.getItemType();
  
   // for an attribute display the parents code snippet
  if (itemtype=='attribute') {
    itemObj = itemObj.getParent();
    itemtype = itemObj.getItemType();
  } 
  
  var name      = itemObj.getName();
  var minOccurs = itemObj.getMinOccurs();
  var maxOccurs = itemObj.getMaxOccurs();
  var type      = itemObj.getType();
  var use       = itemObj.getUse();
  
   // find whether the type is a complex type
  if (itemtype == 'element' &&  use)
      var typetype = 'complexType';

  
  // opening tag 
  var code = '&lt;xs:'+itemtype+' ';

  // name attribute
  code += 'name="' + name + '"';

  // type attribute
  var type_link =  '<a class="xml-complextype-name" onmousedown="appendItem(\'' + type + '\')">' + type + '</a>';
  
  // special case for 'Comment' and 'InlineAttachment'
  if (name=="Comment" || name=="InlineAttachment" )  {
    var type_link = '<a class="xml-simpletype-name" onmousedown="appendItem(\'' + type + '\')">' + type + '</a>';
    code += ' type="'+ type_link +'"';
  }    
  else if ((type) && (type!="complexType") ) {
    code += ' type="'+ type_link +'"';
  }
  
  // use attribute
  if (use) {
    code += ' use="'+ use +'"';
  }
  // minOccurs attribute
  if (minOccurs) {
    code += ' minOccurs="'+ minOccurs +'"';
  }
  // maxOccurs attribute
  if (maxOccurs) {  
    code += ' maxOccurs="'+ maxOccurs +'"';
  }
  
  if (typetype == 'complexType') {
    code += "/&gt;</br></br>";
    code += ". . ." ;
    code += "</br></br>";
    item = type;
  }
  else {
    code += "&gt;</br>";
  }
  
  // separate the elements and attributes
  var childElements = itemObj.getChildren();
  var childAttributes = itemObj.getAttributes();
  
  // /////////////////////////////////
  // do the child elements
  // /////////////////////////////////
  
  if (((childElements.length + childAttributes.length) > 0) && (itemtype != "complexType")) {
    if (typetype == 'complexType') {
      var type_link =  '<a class="xml-complextype-name" href="../complextype/index.html#' + type + '">' + type + '</a>';
      code += '  &lt;xs:complexType name="'+ type_link +'"&gt;</br>';
    }
    else{
      code += "  &lt;xs:complexType&gt;</br>";
    }
  }
  
  if (childElements.length > 0) {
    var childItem = childElements[0];
    var childIsChoice = childItem.getChoice();
    if (childIsChoice == true) {
      code += "    &lt;xs:choice&gt;</br>";
    }
    else {
      code += "    &lt;xs:sequence&gt;</br>";
    }
  }

  for (var i = 0; i < childElements.length; i++) {
  
    var childObj = childElements[i];
    
    // get the child info
    var child_name      = childObj.getName();
    var child_path      = childObj.getPath();
    var child_minOccurs = childObj.getMinOccurs();
    var child_maxOccurs = childObj.getMaxOccurs();
    var child_type      = childObj.getType();
    var child_use       = childObj.getUse();
    
    var child_link =  '<a class="xml-element-name" onmousedown="appendItem(\'' + child_path + '\')">' + child_name + '</a>';
    
    code += '      &lt;xs:element ';
    // name attribute
    code += 'name="' + child_link + '"';
    // type attribute
    if ((child_type) && (child_type!="complexType") ) {
      code += ' type="'+ child_type +'"';
    }
    // use attribute
    if (child_use) {
      code += ' use="'+ child_use +'"';
    }
    // minOccurs attribute
    if (child_minOccurs) {
      code += ' minOccurs="'+ child_minOccurs +'"';
      }
    // maxOccurs attribute 
    if (child_maxOccurs) {
      code += ' maxOccurs="'+ child_maxOccurs +'"';
    }
    
    code += '&gt;...    ...&lt;/xs:element&gt;</br>';
  }

  // close elements
  if (childElements.length > 0) {
    var childItem = childElements[0];
    var childIsChoice = childItem.getChoice();
    if (childIsChoice == true) {
      code += "    &lt;x/s:choice&gt;</br>";
    }
    else {
      code += "    &lt;/xs:sequence&gt;</br>";
    }
  }
  
  // /////////////////////////////////
  // do the attributes
  // /////////////////////////////////
  
  for (var i = 0; i < childAttributes.length; i++) {
    
    var childObj = childAttributes[i];
    
    // get the child info
    var child_name      = childObj.getName();
    var child_minOccurs = childObj.getMinOccurs();
    var child_maxOccurs = childObj.getMaxOccurs();
    var child_type      = childObj.getType();
    var child_use       = childObj.getUse();
    var child_path      = childObj.getPath();
    
    var child_link =  '<a class="xml-attribute-name" onmousedown="appendItem(\'' + child_path + '\')">' + child_name + '</a>';
    var type_link = '<a class="xml-simpletype-name" onmousedown="appendItem(\'' + child_type + '\')">' + child_type + '</a>'
      
    code += '    &lt;xs:attribute';
    // name attribute
    code += ' name="' + child_link + '"';
    // type attribute
    if ((child_type) && (child_type!="complexType") ) {
      code += ' type="'+ type_link +'"';
    }
    // use attribute
    if (child_use) {
      code += ' use="'+ child_use +'"';
    }
    
    code += '/&gt;</br>';
  }
  
  if (((childElements.length + childAttributes.length) > 0)  && (itemtype != "complexType")) {
    code += "  &lt;/xs:complexType&gt;</br>";
  }
  
  // /////////////////////////////////
  // do the simple type enumerations
  // /////////////////////////////////
  
  var enumerations = itemObj.getEnumerations();
  
  if (enumerations) {
    code += '  &lt;xs:restriction base="xs:token"&gt;</br>';  
    for (var i = 0; i < enumerations.length; i++) {
      code += '    &lt;xs:enumeration value="'+enumerations[i].getValue()+'"/&gt;</br>';
    }
    code += '  &lt;/xs:restriction&gt;</br>';
  }
  
  // /////////////////////////////////
  // do the simple type patterns
  // /////////////////////////////////
  
  var pattern = itemObj.getPattern();

  if (pattern) {
    code += '  &lt;xs:restriction base="xs:string"&gt;</br>';  
    code += '    &lt;xs:pattern value="'+pattern+'"/&gt;</br>';
    code += '  &lt;/xs:restriction&gt;</br>';
  }
  
  // /////////////////////////////////
  // do the simple type, native XML types
  // /////////////////////////////////
  
  var basetype = itemObj.getBase();
  
  if (basetype && (itemtype='simpleType') && name.endsWith('Type')) {
    code += '  &lt;xs:restriction base="' + basetype + '"/&gt;</br>';  
  }
  
  // close top tag

  if (typetype != 'complexType') {
    code += "&lt;/xs:"+itemtype+"&gt;";
  }     
  
  /////// tabbed message
  
  var exampleHeading = document.createTextNode('Schema Excerpt and Message Example');  
  var tabHeadingNode = document.createElement('h4');  
  tabHeadingNode.appendChild(exampleHeading);   
  appendToNode.appendChild(tabHeadingNode);
  
  var buttondiv = document.createElement('div');
  buttondiv.className = 'tab';
  
  var xmlbutton = document.createElement('button'); 
  xmlbutton.class='stablinks'; 
  xmlbutton.innerHTML='XML';
  xmlbutton.addEventListener ("click", openSchemaTab, false);
  xmlbutton.myParam = 'XML_sTAB';
  xmlbutton.id = 'xmlSButton';
  buttondiv.appendChild(xmlbutton);
  
  var jsonbutton = document.createElement('button'); 
  jsonbutton.class='stablinks'; 
  jsonbutton.innerHTML='JSON';
  jsonbutton.addEventListener ("click", openSchemaTab, false);
  jsonbutton.myParam = 'JSON_sTAB';
  jsonbutton.id = 'jsonSButton';
  buttondiv.appendChild(jsonbutton);
  
  appendToNode.appendChild(buttondiv);
  
  var exampleHeading = document.createTextNode('XML Schema Excerpt:');
  
  var pre = document.createElement('pre');
  pre.innerHTML = code;  
  
  var tab1div = document.createElement('div');
  tab1div.id = 'XML_sTAB';
  tab1div.className = 'stabcontent';
  
  tab1div.appendChild(exampleHeading);
  tab1div.appendChild(pre);
  
  appendToNode.appendChild(tab1div);

}
  
function appendJsonSchemaSnippet (appendToNode, itemObj) {

  baseJsonTypes = {
    "string" : ",</br>   &quotstring&quot: {</br>      &quottype&quot: [&quotstring&quot, &quotnull&quot]",
    "token" : ",</br>   &quottoken&quot: {</br>      &quottype&quot: &quotstring&quot</br>      }, {</br>         &quottype&quot: &quotnull&quot</br>      }]",
    "ID" : ",</br>   &quotID&quot: {</br>      &quottype&quot: &quotstring&quot,</br>      &quotpattern&quot: &quot^[a-zA-Z_][a-zA-Z0-9-_.]*$&quot,</br>      &quotformat&quot: &quotlixi-ID&quot",
    "IDREF": ",</br>   &quotIDREF&quot: &quot{</br>      type&quot: &quotstring&quot,</br>      &quotpattern&quot: &quot^[a-zA-Z_][a-zA-Z0-9-_.]*$&quot,</br>      &quotformat&quot: &quotlixi-IDREF&quot",
    "base64Binary": ",</br>   &quotbase64Binary&quot: {</br>      &quottype&quot: &quotstring&quot,</br>      &quotpattern&quot: &quot^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$&quot",
    "decimal": ",</br>   &quotdecimal&quot: {</br>      &quottype&quot: [&quotnumber&quot, &quotnull&quot]",
    "integer": ",</br>   &quotinteger&quot: {</br>      &quottype&quot: [&quotinteger&quot, &quotnull&quot]",
    "double": ",</br>   &quotdouble&quot: {</br>      &quottype&quot: [&quotnumber&quot, &quotnull&quot]",
    "dateTime": ",</br>   &quotdateTime&quot: {</br>      &quottype&quot: &quotstring&quot,</br>      &quotformat&quot: &quotlixi-datetime&quot",
    "date": ",</br>   &quotdate&quot: {</br>      &quottype&quot: &quotstring&quot,</br>      &quotformat&quot: &quotlixi-fulldate&quot",
    "gYear": ",</br>   &quotgYear&quot: {</br>      &quottype&quot: &quotstring&quot,</br>      &quotformat&quot: &quotlixi-year&quot"
  };
  
  var refers_complex_type = false;
  var childIsChoice = false;
  var properties_string = '';
  var attribute_string = '';
  var elements_string = '';
  
  var child_required_string = '';
  var attribute_required_string = '';
  var elements_required_string = '';
  
  var typetype = '';
  
  // get the element info
  var itemtype = itemObj.getItemType();
  
  // ////////////////////////////////////////////////////////////////
  // for an attribute display the parents code snippet 
  // ////////////////////////////////////////////////////////////////
  
  if (itemtype=='attribute') {
    itemObj = itemObj.getParent();
    itemtype = itemObj.getItemType();
  }
  
  // ////////////////////////////////////////////////////////////////
  // Get items attributes
  // ////////////////////////////////////////////////////////////////
  
  var name      = itemObj.getName();
  var minOccurs = itemObj.getMinOccurs();
  var maxOccurs = itemObj.getMaxOccurs();
  var type      = itemObj.getType();
  var use       = itemObj.getUse();
  var base      = itemObj.getBase();
  
  // find whether the type is a complex type
       // find whether the type is a complex type
  if (itemtype == 'element' &&  use)
      var typetype = 'complexType';
  
  // type for definitions reference
  var complex_type_link =  '<a class="xml-complextype-name" onmousedown="appendItem(\'' + type + '\')">' + type + '</a>';

  // /////////////////////////////////////////////////////////////////
  // Get items child elements and attributes in a properties string (if any)
  // /////////////////////////////////////////////////////////////////  
 
  // separate the elements and attributes
  var childElements = itemObj.getChildren();
  var childAttributes = itemObj.getAttributes();
  
  if (name=="Comment" || name=="InlineAttachment" )  
  {
    var type_link = '<a class="xml-simpletype-name" onmousedown="appendItem(\'' + type + '\')">' + type + '</a>';
    properties_string += '</br>AsA&quot$&quot: {';
    properties_string += ' &quot$ref&quot: &quot#/definitions/'+ type_link +'&quot';
    properties_string += ' }';
  }
  else if (type && (type!="complexType") ) {
    refers_complex_type = true;
  }
    
  // display each of the attributes   
    
  for (var i = 0; i < childAttributes.length; i++) {
    if (i!=0) { attribute_string += ','; }
  
    var childObj  = childAttributes[i];
    
    var child_path = childObj.getPath();
    var child_name = childObj.getName();
    var child_type = childObj.getType();
    var child_use  = childObj.getUse();
    
    var child_link =  '<a class="xml-attribute-name" onmousedown="appendItem(\'' + child_path + '\')">' + child_name + '</a>';
    var type_link = '<a class="xml-simpletype-name" onmousedown="appendItem(\'' + child_type + '\')">'+ child_type + '</a>'

    //child name and link to simpletype/complextype
    attribute_string += '</br>AsA&quot@' + child_link + '&quot: {';
    attribute_string += ' &quot$ref&quot: &quot#/definitions/'+ type_link +'&quot';
    attribute_string += ' }';
    
    // use, to be put in required
    if (child_use=='required') {
      attribute_required_string += '</br>AsA&quot@' +child_name+'&quot';
    }
  }
  
  if (childAttributes.length > 0 && childElements.length > 0) {
    elements_string += ',';
  }
  
  // display each of the child elements
  
  for (var i = 0; i < childElements.length; i++) {
    if (i!=0) { elements_string += ','; }
  
    var childObj = childElements[i];
    
    var child_path      = childObj.getPath();
    var child_name      = childObj.getName();
    var child_type      = childObj.getType();
    var child_is_choice = childObj.getChoice();
    
    var child_link =  '<a class="xml-element-name" onmousedown="appendItem(\'' + child_path + '\')">' + child_name + '</a>';
    
    if (child_is_choice) {
      childIsChoice = true;
      break;
    }
    
    //child name
    elements_string += '</br>AsA&quot' + child_link + '&quot: { ... }';
    
    if (child_use=='required') {
      elements_required_string += '</br>AsA&quot' + child_name +'&quot';
    }
  }
  
  if (itemtype=='simpleType') {
    if(name.endsWith('Type')) {
      properties_string += '</br>      &quot$ref&quot: &quot#/definitions/' +base.replace("xs:", "")+ '&quot</br>   }';
      properties_string += baseJsonTypes[base.replace("xs:", "")];
    } 
    else if (name.endsWith('Pattern')) {
      var pattern = itemObj.getPattern();
    
      properties_string += '</br>      &quotpattern&quot: &quot^' +pattern+ '$&quot,';
      properties_string += '</br>      &quottype&quot: &quotstring&quot';
    } 
    else if (name.endsWith('List')) {
      properties_string += '</br>      &quotenum&quot: [';
      
      var enumerations = itemObj.getEnumerations();

      
      if (enumerations.length > 0) {
        for (var i = 0; i < enumerations.length; i++) {
          if (i!=0) {
            properties_string += ',' ;
          }
          properties_string += '</br>         &quot' + enumerations[i].getValue() + '&quot';
        }
      }
      properties_string += '</br>      ]';
    }
  }
  
  properties_string += attribute_string + elements_string;
  child_required_string += attribute_required_string + elements_required_string;
  
// /////////////////////////////////////////////////////////////////
// adding stuff for json schema 
// /////////////////////////////////////////////////////////////////    
  
  // opening tag and name.
  var jsonCode =''
  if (itemtype=='complexType' || itemtype=='simpleType'){
    jsonCode += 'definitions: {</br>   &quot'+name+'&quot: {';
  } else {
    jsonCode += '{</br>   &quot'+name+'&quot: {';
  }
  
  //adding opening braces for Object/Array based on maxOccurs
  if (itemtype=='simpleType') {
    jsonCode += properties_string;
  }
  else if (childIsChoice == true) {
    jsonCode += '</br>      &quotoneOf&quot: [';

    for (var i = 0; i < childElements.length; i++) {
      if (i!=0) { jsonCode += ','; }
      jsonCode += '</br>         {';
       
      var childObj = childElements[i];
    
      var child_path      = childObj.getPath();
      var child_name      = childObj.getName();
      var child_type      = childObj.getType();
      var child_use       = childObj.getUse();
      var child_minOccurs = childObj.getMinOccurs();
      var child_maxOccurs = childObj.getMaxOccurs();

      var child_link =  '<a class="xml-element-name" onmousedown="appendItem(\'' + child_path + '\')">' + child_name + '</a>';
   
      if (child_minOccurs == '1'){
        jsonCode += addJsonObjectInSnippet('            ', 
                        attribute_string + '</br>AsA&quot' + child_link + '&quot: { ... }', 
                        '</br>AsA&quot' +child_name+'&quot', 
                        refers_complex_type, 
                        complex_type_link);
      }
      else{
        jsonCode += addJsonObjectInSnippet('            ', 
                        attribute_string + '</br>AsA&quot' + child_link + '&quot: { ... }', 
                        '', 
                        refers_complex_type, 
                        complex_type_link);
      }
      jsonCode += '</br>         }';
    }
    
    jsonCode += '</br>      ],';
    if (attribute_required_string != '') {
      jsonCode += '</br>      &quotrequired&quot: [';
      jsonCode += attribute_required_string.replaceAll('AsA','         ');
      jsonCode += '</br>      ],';
    }
    jsonCode += '</br>      &quottype&quot: &quotobject&quot';
  }
  else{
    if (maxOccurs == 'unbounded') {
      jsonCode += addJsonArrayInSnippet('      ', properties_string, child_required_string, refers_complex_type, complex_type_link, minOccurs);
    }else{
      jsonCode += addJsonObjectInSnippet('      ', properties_string, child_required_string, refers_complex_type, complex_type_link);
    }
  }
  
  // closing tag
  jsonCode += '</br>   }</br>}';
  
  // case where type is an element but its referenced complex type is also displayed.
  if (typetype == 'complexType') {
    jsonCode += "</br></br>. . .</br></br>" ;
    
    //var typeObj = itemObj.getTypeObj();
    
    
    var refers_complex_type = false;
    var properties_string = '';
    var attribute_string = '';
    var elements_string = '';
    
    var child_required_string = '';
    var attribute_required_string = '';
    var elements_required_string = '';
        
    var name      = itemObj.getName();
    var minOccurs = itemObj.getMinOccurs();
    var maxOccurs = itemObj.getMaxOccurs();
    var type      = itemObj.getType();
    var use       = itemObj.getUse();

      var childElements = itemObj.getChildren();
      var childAttributes = itemObj.getAttributes();
    
    if ((type) && (type!="complexType") ) {
      refers_complex_type = true;
    }
    
    
    for (var i = 0; i < childAttributes.length; i++) {
      if (i!=0) { attribute_string += ','; }
      
      var childObj = childAttributes[i];
    
      // get the child info
      var child_name      = childObj.getName();
      var child_path      = childObj.getPath();
      var child_minOccurs = childObj.getMinOccurs();
      var child_maxOccurs = childObj.getMaxOccurs();
      var child_type      = childObj.getType();
      var child_use       = childObj.getUse();

        var child_link =  '<a class="xml-attribute-name" onmousedown="appendItem(\'' + child_path + '\')">' + child_name + '</a>';
      var type_link =  '<a class="xml-complextype-name" onmousedown="appendItem(\'' + child_type + '\')">' + child_type + '</a>';

      
      //child name and link to simpletype/complextype
      attribute_string += '</br>AsA&quot@' + child_link + '&quot: {';
      attribute_string += ' &quot$ref&quot: &quot#/definitions/'+ type_link +'&quot';
      attribute_string += ' }';
      
      // use, to be put in required
      if (child_use=='required') {
        attribute_required_string += '</br>AsA&quot@' + child_name + '&quot';
      }
    }
    
    if (childAttributes.length > 0 && childElements.length > 0) {
      elements_string += ',';
    }
    
    for (var i = 0; i < childElements.length; i++) {
      if (i!=0) { elements_string += ','; }
    
      var childObj = childAttributes[i];
    
      // get the child info
      var child_name      = childObj.getName();
      var child_path      = childObj.getPath();
      var child_minOccurs = childObj.getMinOccurs();
      var child_maxOccurs = childObj.getMaxOccurs();
      var child_type      = childObj.getType();
      var child_use       = childObj.getUse()
      
      var child_link =  '<a class="xml-element-name" onmousedown="appendItem(\'' + child_path + '\')">' + child_name + '</a>';
      var parentContainsChoice = childObj.getChoice();

      if (parentContainsChoice == true) {
        childIsChoice = true;
        break;
      }
      
      elements_string += '</br>AsA&quot' + child_link + '&quot: { ... }';
      
      if (child_use=='required') {
        elements_required_string += '</br>AsA&quot' +schemaJSON[childItem][0]+'&quot';
      }
    }
    
    properties_string += attribute_string + elements_string;
    child_required_string += attribute_required_string + elements_required_string;    
    
    // opening tag and name.
    jsonCode += '&quotdefinitions&quot:{</br>   &quot'+complex_type_link+'&quot: {';
    
    if (maxOccurs == 'unbounded') {
      jsonCode += addJsonArrayInSnippet('      ', properties_string, child_required_string, refers_complex_type, complex_type_link, minOccurs);
    }else{
      jsonCode += addJsonObjectInSnippet('      ', properties_string, child_required_string, refers_complex_type, complex_type_link);
    }
    
    // closing tag
    jsonCode += '</br>   }</br>}';
      
  }
  
  var exampleHeading = document.createTextNode('JSON Schema Excerpt:');
  
  var pre = document.createElement('pre');
  pre.innerHTML = jsonCode;  

  /////// tabbed message
  var tab2div = document.createElement('div');
  tab2div.id = 'JSON_sTAB';
  tab2div.className = 'stabcontent';
  
  tab2div.appendChild(exampleHeading);
  tab2div.appendChild(pre);
  
  appendToNode.appendChild(tab2div);
  
  document.getElementById("xmlSButton").click();
  
  appendToNode.appendChild(document.createElement('br'));
  
}

function appendXMLCodeSnippet(appendToNode, itemObj) { 

    examples = {
    "abnPattern":"12345678901",
    "acnPattern":"123456789",
    "aubicPattern":"12345",
    "auPostCodePattern":"1234",
    "bsbPattern":"123456",
    "emailPattern":"admin@lixi.org.au",
    "gicsCodePattern":"12345678",
    "irdNumberPattern":"12345678",
    "nzbicPattern":"A123456",
    "nzbnPattern":"1234567890123",
    "urlPattern":"lixi.org.au",
    "base64BinaryType":"Sample Data",
    "currencyType":"24999.99",
    "dateTimeType":"1980-03-23T08:46:40",
    "dateType":"1980-03-23",
    "decimalType":"100240.99",
    "gYearType":"1980",
    "integerType":"12",
    "nzPostCodePattern":"1234",
    "percentType":"3.75",
    "referenceType":"x123456",
    "uniqueIDType":"x123456"
  };


  // get the element info 
  var itemtype = itemObj.getItemType();

  // for an attribute display the parents code snippet 
  if (itemtype=='attribute') { 
    itemObj = itemObj.getParent();
    itemtype = itemObj.getItemType();
  } 
 
  var name      = itemObj.getName();
  var minOccurs = itemObj.getMinOccurs();
  var maxOccurs = itemObj.getMaxOccurs();
  var type      = itemObj.getType();
  var use       = itemObj.getUse();
  
  var name_of_element = name;  // save the name for later
  var name_length = name.length;
  
  ////////////////////////////////////
  //  if its a simple type, display an element with an attribute that uses this type. 
  /////////////////////////////////

  if (itemtype == 'simpleType') {
    
    if (usedByObj = itemObj.getUsedBy()[0]) {
      
      if (parentObj = usedByObj.getParent()) {
        var name      = parentObj.getName();
        var minOccurs = parentObj.getMinOccurs();
        var maxOccurs = parentObj.getMaxOccurs();
        var type      = parentObj.getType();
        var use       = parentObj.getUse();
        
        var name_length = name.length;
        itemObj = parentObj;
      }
    }
  }
  
  // ///////////////////////////////////////
  // if this element is a complex type, display an element that uses the complex type
  // ////////////////////////////////////////

  if (itemtype == "element"){
    
    itemDataType =  itemObj.getType();
    if (itemDataType) {
      var typetype = itemObj.getTypeObj().getItemType()
      if (typetype == "complexType") {
        itemObj = itemObj.getTypeObj();
      }
    }
     var name      = itemObj.getName();
     var minOccurs = itemObj.getMinOccurs();
     var maxOccurs = itemObj.getMaxOccurs();
     var type      = itemObj.getType();
     var use       = itemObj.getUse();
    
    name_of_element = name;
    var name_length = name.length;
  }  

  var code = '';
  var jsonCode = '';
  
   // opening tag  
  if (typetype == 'complexType') {
    code += '&lt;'+name_of_element;
    jsonCode += '{</br>   &quot'+name_of_element+'&quot: ';
  }
  else { 
    code += '&lt;'+name;
    jsonCode += '{</br>   &quot'+name+'&quot: ';
  }

  var isJsonArray = false;
  if(itemtype == 'element') {
    if(maxOccurs == 'unbounded') { 
      jsonCode += '[</br>      {';
      isJsonArray = true;
    } else { 
      jsonCode += '{';
    }
  } else {
    jsonCode += '{';
  }

  // //////////////////////////////
  // Special cases for "Comment" and "InlineAttatchment"
  // ///////////////////////////////
  
  if (name=="InlineAttachment")  {
    code += "&gt;U2FtcGxlIEJhc2U2NA==&lt;/InlineAttatchment";
    jsonCode += '</br>        &quot$&quot : &quotU2FtcGxlIEJhc2U2NA==&quot';
  }
  
  if (name=="Comment")  {
    code += "&gt;Sample Data&lt;/xs:"+name+"&gt;";
    jsonCode += '</br>        &quot$&quot : &quotSample Data&quot';
  }

  // separate the elements and attributes 
  var childElements = itemObj.getChildren();
  var childAttributes = itemObj.getAttributes();
 
  var loremipsum = "Sample Data";
  var jsonLoremipsum = "Sample Data";  

  // ///////////////////////////////// 
  // do the attributes 
  // ///////////////////////////////// 
 
  for (var i = 0; i < childAttributes.length; i++) { 
   
    var childObj = childAttributes[i];
    
    // get the child info
    var child_name      = childObj.getName();
    var child_path      = childObj.getPath();
    var child_type      = childObj.getType();
    var child_use       = childObj.getUse();
    var child_label     = childObj.getLabel();
    
    var child_link =  '<a class="xml-attribute-name" onmousedown="appendItem(\'' + child_path + '\')">' + child_name + '</a>'

    // get the item that is the type used here
    var typeObj = childObj.getTypeObj();
    
    if (child_type in examples){ 
      loremipsum = examples[child_type];
    }

    else if (typeObj.getEnumerations()) {
      var type_enumerations = typeObj.getEnumerations();
      if (type_enumerations) {
        var loremipsum = type_enumerations[0].getValue();
        var jsonLoremipsum = loremipsum;
      }
    }

    else if (child_type in examples) {
      loremipsum = examples[child_type];

      if(child_type=='currencyType' || child_type=='integerType' || child_type=='decimalType' || child_type=='percentType'){
        jsonLoremipsum = '<font color="green">'+examples[child_type].replace('"','')+'</font>';
      } else {
        jsonLoremipsum =  examples[child_type];
      }
    }

    ////stringType
    else if (child_type == 'stringType') {
      loremipsum = "Sample " + child_label;
      jsonLoremipsum = "Sample " + child_label ;
    }
    else loremipsum = "Sample Data";
    
    if (i != 0) {
      code += "</br>  " + Array(name_length).join(" ");
      jsonCode += ',';
    }
    code += ' ' + child_link + '="' + loremipsum + '"' ;

    if (isJsonArray == true) {
      jsonCode +='</br>         ';
    } else {
      jsonCode +='</br>      ';
    }

    jsonCode += '&quot@'+ child_link +'&quot: &quot' + jsonLoremipsum +'&quot';     
  } 
 
  if ((childElements.length == 0) && (name!="InlineAttachment") && (name!="Comment")) { 
    code += '/&gt;</br>'; 
  } 
  else { 
    code += '&gt;</br>';
    jsonCode += ','; 
  } 
 
  //// ///////////////////////////////// 
  //// do the child elements 
  //// ///////////////////////////////// 
 
  for (var i = 0; i < childElements.length; i++) { 
   
    var childObj = childElements[i];
    
    // get the child info
    var child_name      = childObj.getName();
    var child_path      = childObj.getPath();
    var child_minOccurs = childObj.getMinOccurs();
    var child_maxOccurs = childObj.getMaxOccurs();
    var child_type      = childObj.getType();
    var child_use       = childObj.getUse();
    
    var child_link =  '<a class="xml-element-name" onmousedown="appendItem(\'' + child_path + '\')">' + child_name + '</a>'
    code += '   &lt;' + child_link + '...    .../&gt;</br>';

    if (i != 0) {
      jsonCode += ',';
    }

    if (isJsonArray == true) {
      jsonCode +='</br>         ';
    } else {
      jsonCode +='</br>      ';
    }

    jsonCode += '&quot'+ child_link +'&quot: ';

    if(child_maxOccurs == 'unbounded') { 
      jsonCode += '[...    ...]';
    } else { 
      jsonCode += '{...    ...}';
    } 
  } 

  // ///////////////////////////////// 
  //   close the tag
  // ///////////////////////////////// 
  if (typetype == 'complexType') {
    code += "&lt;/" + name_of_element + "&gt;";
  }
  else if (childElements.length > 0){ 
    code += "&lt;/" + name + "&gt;";
  }
  
  if(itemtype == 'element') {
    if(maxOccurs == 'unbounded') { 
      jsonCode += '</br>      }</br>   ]</br>}';
    } else { 
      jsonCode += '</br>   }</br>}';
    }
  } else {
    jsonCode += '</br>   }</br>}';
  }


  
  var xmlHeading = document.createTextNode('XML Example:');
  var jsonHeading = document.createTextNode('JSON Example:');
  
  var xmlpre = document.createElement('pre');
  xmlpre.innerHTML = code;

  var jsonpre = document.createElement('pre');
  jsonpre.innerHTML = jsonCode;    

  /////// tabbed message
  document.getElementById("XML_sTAB").appendChild(xmlHeading);
  document.getElementById("XML_sTAB").appendChild(xmlpre);
  
  document.getElementById("JSON_sTAB").appendChild(jsonHeading);
  document.getElementById("JSON_sTAB").appendChild(jsonpre);
} 

///////////////////////////////////////////////////////////////////////////////////////////////
// Append Tool Tip to HTML
///////////////////////////////////////////////////////////////////////////////////////////////

function appendTooltip (appendToNode, itemObj) {
  // create tooltip element and append
  var tooltipNode = document.createElement('span');
  tooltipNode.className = 'tooltiptext-under';
  appendToNode.appendChild(tooltipNode);

  // creat tooltip after (the little arrow pointer) tooltiptext-after
  var pointer = document.createElement('span');
  pointer.className = 'tooltiptext-after';
  appendToNode.appendChild(pointer);

  //// create content of tooltip
  appendDefinition(tooltipNode, itemObj); 
  appendPath(tooltipNode, itemObj, false);
  appendOccurences(tooltipNode, itemObj); 
  appendLabel(tooltipNode, itemObj);
  // TODO add back into tooltip
  //appendDataType(tooltipNode, itemObj);
  //appendTypeBase(tooltipNode, itemObj);
  //appendTypePattern(tooltipNode, itemObj);
  
  if (itemObj.getItemType() != 'attribute') {
    appendContentsOfElement(tooltipNode, itemObj);
    appendComplexContent(tooltipNode, itemObj);   
  }
  appendEnumerations(tooltipNode, itemObj); 
  //appendReferencedBy(tooltipNode, item, true, false);  
}

function appendDefinition (appendToNode, itemObj) {

    var fullname = itemObj.getName();
    var desc = itemObj.getDocumentation();
  
    var customizedExcerpt = null;
    
    // TODO: Customised Documentation
    
/*     if (schemaJSON[item][19] !== "" && schemaJSON[item][19] != null)
    {
      customizedExcerpt = schemaJSON[item][19];
      customizedExcerpt = marked(customizedExcerpt);
    } 
    else if(schemaJSON[item][15] !== "")
    {
      var temp = schemaJSON[item][15]
      customizedExcerpt = marked(temp);
    } */

    definitionNode = document.createElement('medium')
    appendToNode.appendChild(definitionNode); 

    //  unique name i.e. ""OccupationCode (attribute in SelfEmployed)""
    var textNode = document.createTextNode(fullname);
    var headNode = document.createElement('h4');
    headNode.appendChild(textNode);
    definitionNode.appendChild(headNode); 

    // definition
    var textNode = document.createTextNode(desc);
    definitionNode.appendChild(textNode);
    
    if (customizedExcerpt != null){
        appendLineBreak(definitionNode)
        appendLineBreak(definitionNode)
        
        //bold = document.createElement('strong')
        //var boldText = document.createTextNode("Custom Documentation: ");
        //bold.appendChild(boldText)
        //var textNode = document.createTextNode(customizedExcerpt);
      
      var textNode = document.createElement('p');
      textNode.innerHTML = customizedExcerpt      
      
        //definitionNode.appendChild(bold); 
        definitionNode.appendChild(textNode); 
    } 

    // line break
    appendLineBreak(appendToNode);
    appendLineBreak(appendToNode);
  
}

///////////////////////////////////////////////////////////////////////////////////////////////
// insert glossary links into a string (documentation or definiton)
///////////////////////////////////////////////////////////////////////////////////////////////

function insertGlossaryLinks (sentence) {
  
  documentationWords = sentence.split(/[ '-][ ]?/);
  documentationWordsWithLinks = [];
  
  var index;
  for (index = 0; index < documentationWords.length; index++) {
    getGlossaryWordsMatched(documentationWords[index]);
  }

  documentationText = documentationWordsWithLinks.join(' ');
  return documentationText;
  
  function matchGlossaryTerm (phrase) {
    var xpath = "//Glossary/Term[@Name='" + titleCase(phrase) + "']";
    //console.log(xpath);
    node = glossary.evaluate(xpath , glossary, resolverGlossary, XPathResult.ANY_TYPE, null).iterateNext();
    //console.log(node);
    return node;
  }
  
  function getLinkHTML (trimmedphrase, phrase) {
    var xpath = "//Glossary/Term[@Name='" + titleCase(trimmedphrase) + "']/Definition";
    //console.log(xpath);
    var definition = glossary.evaluate(xpath , glossary, resolverGlossary, XPathResult.ANY_TYPE, null).iterateNext().textContent;
    //console.log(definition);
    
    var replacement = '<a><span onmousedown="appendGlossaryItem(\'' + titleCase(phrase) + '\')" class="tooltip-parent">' + trimmedphrase + '<span class="tooltiptext-under"><small>' + definition + '</small></span><span class="tooltiptext-after"/></span></a>' + phrase.replace(trimmedphrase, "");
    return replacement;
  }
  
  function getGlossaryWordsMatched(word) {
    
    //console.log('Searching definitions for glossary words: ' + word)
    
    // remove special characters from beginning and end of word;
    function trimWord (word){
      if (word){
        word = word.replace("'","\'");
        word = word.replace(/^[\s;]+|[s][\s;]$/g,'');
      }
      return word
    }
    
    var firstword  = documentationWords[index];
    var secondword = documentationWords[index + 1];
    var thirdword  = documentationWords[index + 2];
    
    var firstWordTrimmed  = trimWord(firstword);
    var secondWordTrimmed = trimWord(secondword);
    var thirdWordTrimmed  = trimWord(thirdword);

    var twoWords         = documentationWords[index] + " " + documentationWords[index + 1];
    var threeWords       = documentationWords[index] + " " + documentationWords[index + 1] + " " + documentationWords[index + 2];
    
    var twoWordsTrimmed   = documentationWords[index] + " " + secondWordTrimmed;
    var threeWordsTrimmed = documentationWords[index] + " " + documentationWords[index + 1] + " " + thirdWordTrimmed;
    
    // match three word prases
    var threewordsNode = matchGlossaryTerm(threeWordsTrimmed);
    if (threewordsNode) 
    {
      documentationWordsWithLinks.push(getLinkHTML(threeWordsTrimmed, threeWords));
      //console.log("match: " + threeWords);
      index = index + 2;
    }
    else {
      // match two word prases
      var twoWordNode = matchGlossaryTerm(twoWordsTrimmed);
      if (twoWordNode){
        //console.log("match: " + twoWords);
        documentationWordsWithLinks.push(getLinkHTML(twoWordsTrimmed, twoWords));
        index = index + 1;
      }
      else {
        // match single words
        var oneWordNode = matchGlossaryTerm(firstWordTrimmed);
        if (oneWordNode){
          //console.log("match: " + word);
          documentationWordsWithLinks.push(getLinkHTML(firstWordTrimmed, firstword));
        }
        else
          documentationWordsWithLinks.push(word);
      }
    }
  }
}

///////////////////////////////////////////////////////////////////////////////////////////////
//  
///////////////////////////////////////////////////////////////////////////////////////////////

$.ajaxSetup({
  timeout: 0
});

String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};

function appendWheel (){
  if(window.location.hash) {
    var wheel = document.createElement('div');
    wheel.id = 'wheel';
    document.body.appendChild(wheel);
  //  alert('wheel');
  }
}

function removeWheel () {

  if ($('#wheel').length > 0) {
    var wheel = document.getElementById('wheel');
    wheel.parentNode.removeChild(wheel);
  //  alert('remove wheel');
  }

}

function openSchemaTab(evt) {
    var i, stabcontent, stablinks;
    stabcontent = document.getElementsByClassName("stabcontent");
    for (i = 0; i < stabcontent.length; i++) {
        stabcontent[i].style.display = "none";
    }
  
  document.getElementById("xmlSButton").style.backgroundColor  = "#F0F0F0";
  document.getElementById("jsonSButton").style.backgroundColor  = "#F0F0F0";
  
    document.getElementById(evt.target.myParam).style.display = "block";
    evt.currentTarget.className += " active";
  evt.currentTarget.style.background = "#ccc";
}

function openMessageTab(evt) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

  document.getElementById("xmlMButton").style.backgroundColor  = "#F0F0F0";
  document.getElementById("jsonMButton").style.backgroundColor  = "#F0F0F0";
  
    document.getElementById(evt.target.myParam).style.display = "block";
    //evt.currentTarget.className += " active";
  evt.currentTarget.style.backgroundColor  = "#ccc";
}

function appendLineBreak (appendToNode){
    appendToNode.appendChild(document.createElement('br'));
}

function appendConfidentialityClause(appendToNode) {
    var confidentialityClauseNode = document.createElement('p');
    var textNode = document.createTextNode('This standard is confidential to LIXI Limited and may not be disclosed, duplicated, or used for any purpose, in whole or in part, without prior consent.')
    confidentialityClauseNode.style.color = 'orange';
    confidentialityClauseNode.style.fontSize = 'x-small';
    confidentialityClauseNode.appendChild(textNode);
    appendToNode.appendChild(confidentialityClauseNode);
}

function copyTextReset() {
  
  document.getElementById("copyToolTip").innerHTML = '<medium>Click to copy Path to clipboard</medium>';
}

function copyPath(e) {
  var dummy = document.createElement("input");
  document.body.appendChild(dummy);
  dummy.setAttribute("id", "dummy_id");
  document.getElementById("dummy_id").value=e;  
  dummy.select();
  document.execCommand("copy");
  document.body.removeChild(dummy);
  
  document.getElementById("copyToolTip").innerHTML = '<medium>Copied!</medium>';
}

function appendCopyTooltip (appendToNode) { // seperate function neeed as CSS needs to be different to tooltip
    // create tooltip element and append
    tooltipNode = document.createElement('span');
    tooltipNode.className = 'tooltiptext-under';
  tooltipNode.style.position = 'absolute';
  tooltipNode.style.left = 'auto';
  tooltipNode.style.width = 'auto';
  tooltipNode.style.marginLeft = '-25px';
  tooltipNode.id = 'copyToolTip';
    appendToNode.appendChild(tooltipNode);

    // creat tooltip after (the little arrow pointer) tooltiptext-after
    var pointer = document.createElement('span');
    pointer.className = 'tooltiptext-after';
  pointer.style.position = 'absolute';
  pointer.style.left = 'auto';
  pointer.style.width = 'auto';
  pointer.style.marginLeft = '-12px';
    appendToNode.appendChild(pointer);

    // create content of tooltip
    tooltipNode.innerHTML = '<medium>Click to copy Path to clipboard</medium>';
}   

function appendCustomTooltip (appendToNode, tooltiptext) {
    // create tooltip element and append
    tooltipNode = document.createElement('span');
    tooltipNode.className = 'tooltiptext-under';
    appendToNode.appendChild(tooltipNode);

    // creat tooltip after (the little arrow pointer) tooltiptext-after
    var pointer = document.createElement('span');
    pointer.className = 'tooltiptext-after';
    appendToNode.appendChild(pointer);

    // create content of tooltip
    tooltipNode.innerHTML = tooltiptext;
}

function addJsonObjectInSnippet(starting_space, text_in_properties, text_in_required, refers_complex_type, complex_type_link) {
  
  var output_string ='';

  if(refers_complex_type == true) {
    output_string += '</br>'+ starting_space +'&quot$ref&quot: &quot#/definitions/'+ complex_type_link +'&quot';
  }
  else {
    output_string += '</br>'+ starting_space +'&quotadditionalProperties&quot: false,';
    output_string += '</br>'+ starting_space +'&quotproperties&quot: {';
    output_string += text_in_properties.replaceAll('AsA',starting_space+'   ');
    output_string += '</br>'+ starting_space +'},';
    if (text_in_required != '') {
      output_string += '</br>'+ starting_space +'&quotrequired&quot: [';
      output_string += text_in_required.replaceAll('AsA',starting_space+'   ');
      output_string += '</br>'+ starting_space +'],';
    }
    output_string += '</br>'+ starting_space +'&quottype&quot: &quotobject&quot';
  }
  
  return output_string;
}

function addJsonArrayInSnippet(starting_space, text_in_properties, text_in_required, refers_complex_type, complex_type_link, minOccurs) {
  
  var output_string ='';

  //output_string += '</br>'+ starting_space +'&quotoneOf&quot: [';
  //output_string += '</br>'+ starting_space +'   {';
  //output_string += addJsonObjectInSnippet(starting_space +'      ', text_in_properties, text_in_required, refers_complex_type, complex_type_link);
  //output_string += '</br>'+ starting_space +'   },';
  
  output_string += '</br>'+ starting_space +'{';
  output_string += '</br>'+ starting_space +'   &quotadditionalItems&quot: false,';
  output_string += '</br>'+ starting_space +'   &quotitems&quot: {';
  output_string += addJsonObjectInSnippet(starting_space +'      ', text_in_properties, text_in_required, refers_complex_type, complex_type_link);
  output_string += '</br>'+ starting_space +'   },';
  output_string += '</br>'+ starting_space +'   &quotminItems&quot: '+minOccurs+',';
  output_string += '</br>'+ starting_space +'   &quottype&quot: &quotarray&quot';
  output_string += '</br>'+ starting_space +'}';

  //output_string += '</br>'+ starting_space +']';
  
  return output_string;
}