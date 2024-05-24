
function intitRadLexTree(args, path, id){
	if(typeof args !== 'object'){ args = {}; }
	var treepanel;
	var target = Ext.get(args.target_id) || Ext.getBody();
	var iAlreadyFocusedSomething = false;

	var nodePath = path;
	//bool
	var iBool =0;
	
	var radlexTplMarkup = getRadlexViewerTplMarkup();   
	var radlexTpl = new Ext.XTemplate(radlexTplMarkup);
	
	//var path_String = path_String;
	
	
	/**************************
		DETAILS PANEL
	**************************/
	var term_viewer = new Ext.Panel({
		id:'radlex_detail_panel'
		,title:'&nbsp;'
		,columnWidth:1
		,height:650
		
		,autoScroll:true
		,radlexTpl:radlexTpl
	});
	

	/**************************
		TREE PANEL
	**************************/
	var treepanel = new Ext.tree.TreePanel({
		id:'radlex_treepanel'
		,height:650
		,width:350
		,autoScroll:true
		,rootVisible:false
		
	//	,singleExpand:true
		
		,root: new Ext.tree.AsyncTreeNode({id:'RID1',text:'RadLex entity',expanded:true,iconCls:'radlex-tree-node'})
		
		,loader: new Ext.tree.RadlexTreeLoader({
			dataUrl:'/ajax/radlex_util.cfm'
			,baseParams:{ACTION:'GETCHILDREN'}
			,requestMethod:'POST'
			
			,listeners:{
				'beforeload':function(){
					treepanel.el.mask('Loading...','x-mask-loading');
					term_viewer.setTitle('&nbsp;');
					
				}
				,'load':function(loader, n, response){
					treepanel.el.unmask();
					
					//expand to path and focus on node by the URL RID
					if (iBool==0)
					{

						// in addition, here, we should expand any paths that are passed in as part of our new parameter
						// dependent continuant: RID0/RID1/RID29043/RID29045
						// independent continuant: RID0/RID1/RID29043/RID29044
						// radlex coordinated term: RID0/RID1/RID28638
						treepanel.expandPath('RID0/RID1/RID29043/RID29045');
						treepanel.expandPath('RID0/RID1/RID29043/RID29044');
						treepanel.expandPath('RID0/RID1/RID28638');

						treepanel.expandPath(nodePath, "id", function(s, node){
							//focus node selected in tree
							node.select();
						});


						if (id != null && !iAlreadyFocusedSomething)
						{
							iAlreadyFocusedSomething = true;
							focusRadlexTerm(id);
						}
					
					}
				}
			}
		})
		
		,listeners:{
			'click':function(node,e){
					treepanel.el.mask('Loading...','x-mask-loading');

					if(!node.expanded){node.ui.ecClick(e);}
					focusRadlexTerm(node.attributes.id);
					
					iBool=1;
				}
		}
		,tbar:{
			xtype:'toolbar'
			,autoWidth:true
			,height:25
			,cls:'x-panel-header'
			,style:{paddingLeft:'5px'}	
			,items:[
				new Ext.ux.BioportalTwinTriggerField({
					id:'basic_searchfield_demo'
					,trigger2Class:'x-form-search-trigger'
					,emptyText:'Begin typing to search...'
					,width:200
					,listWidth:300
					,store: new Ext.ux.BioportalJsonStore({ontology_id:ontology_id})
					,displayField:'Label'
					,minChars:2
					,typeAhead: false
					,loadingText: 'Searching...'
					,onTrigger1Click : function(e){
						// Hide the "Clear" button.
						this.triggers[0].hide();
						this.el.dom.value = '';
						this.concept_id = '';

						term_viewer.body.unmask();
						term_viewer.update('');
						term_viewer.body.mask('Use the RadLex Tree Browser and integrated search feature to locate terms. Simply click on a RadLex term to view more information.','radlex-viewer-mask');
						treepanel.getRootNode().reload();
						treepanel.el.unmask();

						
						// Remove or clear any of your search results here.
					}	
					//search trigger
					,onTrigger2Click : function(e){
						treepanel.el.mask('Loading...','x-mask-loading');
						// Add the "Clear" button.
						var w = this.wrap.getWidth();
						this.triggers[0].dom.style.display = '';
						this.el.setWidth(w-(this.triggers[0].getWidth()*2));
						var v;
						if (this.concept_id && this.concept_id.length){
							v = this.concept_id;
						}
						else if(this.lastQuery && this.lastQuery.length){
							v = this.lastQuery;
						}
						else{
							v = "";
						}
						
						if(v.length > 0){
							if(v.indexOf("#") >= 0){
								v = v.split("#")[1];
							}else{
								//TEMP FIX FOR MISSING # IN ID
								v = v.split("/");
								v=v[v.length-1];
							}
							window.location = '/RID/' + v;
							treepanel.selectPath(v);
							focusRadlexTerm(v);
							iAlreadyFocusedSomething = true;
							iBool=1;
						}
						else{
							treepanel.getRootNode().reload();
							treepanel.el.unmask();
						}
					}
					
					,listeners:{
						'select':function(combo,record,index){
							// Activate the search action when a result is selected.
							this.onTrigger2Click({});
						}
					}
				})
			]
		}

	}
	);

	var ct = new Ext.Container({
		id:'radlex_ct'
		,renderTo:target
		,height:650
		,width:1200
		,layout:'column'
		,items:[
			treepanel
			,term_viewer
		]
	});
	document.getElementById('ext-gen15').style.display="none";
}


function detectHeight() {
	var wh = 0;
	if(typeof(window.innerHeight)=="number"){
		wh = window.innerHeight;
	}else{	
		if(document.documentElement && document.documentElement.clientHeight) {wh = document.documentElement.clientHeight;}
		else if (document.body && document.body.clientHeight) {wh = document.body.clientHeight;}
	}
	return wh;
} 


function detectWidth() {
	var wh = 0;
	if (typeof(window.innerWidth)=="number") {
		wh = window.innerWidth;
	}else{
		if(document.documentElement && document.documentElement.clientWidth) {wh = document.documentElement.clientWidth;}
		else if (document.body && document.body.clientWidth) { wh = document.body.clientWidth; }
	}
	return wh;
} 

function launchExtWindow(image, title){
/**************************************************************************************************************
	Standardized function to open an image in a window.
	
	Params
	url (string):	The address of the site to be loaded.  Does not have to be on the same domain.
	titleitle (string):	Text used as the header of the window.
***************************************************************************************************************/
	
	var extTitle = Ext.value(title,'Radlex Sample Image');
	var myHtml = '<center><img class="radlex_img_link" src='+image+' /></center>';
	
	
	launchwin = new Ext.Window(
		{
			title:extTitle,
			modal:true,
			autoScroll:true,
			shadow:false,
			shim:false,
			html:myHtml
			,width:500
			,height:500
			,listeners:{
				'afterrender':function(win){
					var maxH = detectHeight()-10;
					var maxW = detectWidth()-10;			
					var img = Ext.DomQuery.selectNode('img.radlex_img_link',win.body.dom);
					var img_size = Ext.get(img).getSize();
					var window_width = img_size.width+35;
					var window_height = img_size.height+35;
					if( window_width > maxW ) {
						window_width = maxW;
					}
					if( window_height > maxH) {
						window_height = maxH;
					}
					
					win.setSize(window_width,window_height);
				}
			}
		}
	).show();
	
	
	/*
	if( launchwin.getHeight() > maxH ) {
		launchwin.setHeight(maxH);
	}*/
	/*if( launchwin.getWidth() > maxW ){
		launchwin.setWidth(maxW);
	}*/
	launchwin.setPosition(1,1);
	
}

function formatPropName(name){
	name = name.split('/');
	name = name[name.length-1];
	name = name.split('#');
	name = name[name.length-1];

	return name;
}

function formatPropValue(value){
	var i, fullValue = '';
	for (i = 0; i < value.length; i++) {
		if (value[i].toString().indexOf('radlex.org') !== -1) {
			value[i] = value[i].toString();
			fullValue += '<a href="'+ value[i] + '">' + value[i] + '</a>, ';
		} else {
			fullValue += value[i] + ', ';
		}
	}
	return fullValue.slice(0, -2);
}

function getPropertiesArray(JSON){
	var propKeys = Object.keys(JSON.item.properties), i, propertiesArray = [];

	for (i = 0; i < propKeys.length; i++) {
		var name = formatPropName(propKeys[i]);
		if(name != 'Preferred_name' && name != 'Synonym' && name != 'Definition' && (propKeys[i].indexOf('www.w3.org') == -1 || propKeys[i].indexOf('subClassOf') != -1) && propKeys[i].indexOf('bioontology.org') == -1){
			if(name == "subClassOf"){
				name = "Is_A"
			}
			propertiesArray.push({name: name, value: formatPropValue(JSON.item.properties[propKeys[i]])});
		}
	}

	JSON.item.propertiesArray = propertiesArray;

	return JSON;
}

function focusRadlexTerm(radlex_id){

	//testing new tabs?
	//------------

	var term_viewer = Ext.getCmp('radlex_detail_panel');
	if(term_viewer && radlex_id && term_viewer.display_id !== radlex_id){
		var radlexTpl = term_viewer.radlexTpl || new Ext.XTemplate(getRadlexViewerTplMarkup());
		Ext.Ajax.request({
			url:'/ajax/radlex_util.cfm'
			,method:'POST'
			,params:{action:'GETTERM',tid:radlex_id}
			,callback:function(){ term_viewer.body.unmask(); }
			,success:function(responseObj,optionsObj){
					var JSON = Ext.decode(responseObj.responseText);
					JSON = getPropertiesArray(JSON);
					term_viewer.setTitle(JSON.item.prefLabel);
					if(!JSON.SUPERCLASS){ JSON.SUPERCLASS = []; }
					radlexTpl.overwrite(term_viewer.body,JSON.item);
					term_viewer.display_id = radlex_id;
					Ext.getCmp("radlex_treepanel").el.unmask();
					//setTimeout(function(){updateLinks()},1000);
				}
			,failure:function(responseObj,optionsObj){
					handleActionFailure('Sorry, we were unable to retrieve more information about the selected RadLex Term.');	
				}
		});	
	}else{
		Ext.getCmp("radlex_treepanel").el.unmask();
	}
	
}

//---------------------------------
function toggle() {
	var ele = document.getElementById("toggleText");
	var text = document.getElementById("displayText");
	var ele2 = document.getElementById("toggleText2");
	if(ele.style.display == "block"){
		ele.style.display = "none";
		text.innerHTML = "Term Details";
		document.getElementById('biomixer_iframe').src = document.getElementById('biomixer_iframe').src;
	}else{
		ele.style.display = "block";
		text.innerHTML = "Visualize";
	}
	if(ele2.style.display == "block"){
		ele2.style.display = "none";
    }else{
		ele2.style.display = "block";
	}
} 
//---------------------------------

function getRadlexViewerTplMarkup(){
/*'<a id="displayText" href="javascript:toggle();">Visualize</a><br />',*/
	var tpl = [

	'<div id="toggleText" style="display: block">',
	
		'<table  style="list-style-type:disc;margin-left:10; font-size: 12px;"  align="left" width="96%">',
			'<tr>',
				'<td style="white-space:nowrap;" width="75px"><b>Preferred Name:&nbsp;&nbsp;</b></td>',
				'<td align="left" colspan="2" width="100%">{values.prefLabel}</td>',
			'</tr>',

			'<tr><td><b>RadLex&nbsp;ID:&nbsp;&nbsp;</b></td><td colspan="3"><a href="http://www.radlex.org/RID/{values.prefixIRI}">{values.prefixIRI}</a></td></tr>',
			'<tr><td><b>PURL:&nbsp;&nbsp;</b></td><td colspan="3"><a href="http://www.radlex.org/RID/{values.prefixIRI}">http://www.radlex.org/RID/{values.prefixIRI}</a></td></tr>',
			'{[!values.definition.length > 0 ? "" : "<tr><td><b>Definition:</b></td><td colspan=\'3\'>"+values.definition+"</td></tr>"]}',
			'{[!values.synonym.length > 0 ? "" : "<tr><td><b>Synonyms:</b></td><td colspan=\'3\'>"+values.synonym+"</td></tr>"]}',

			'<dl><tpl for="values.propertiesArray"><tr><td><b><dt>{name}:</dt></b></td><td colspan=\'3\'><dd>{value}</dd></td></tr></tpl></dl>',

			//COMMENTED OUT GOLDMINER
			//'<tr><td><b>&nbsp;</b></td></tr>',
			//'<tr><td><b>Sample Images:</b></td></tr>',
			//'<tr><td colspan="3">',

			//'<iframe  style="border-style: none;width: 100%; height: 190px;"  SRC="http://goldminer.arrs.org/inline-radlex.php?id={values.prefixIRI}"></iframe>',//
			//'</td></tr>',
		'</table>',
	'</div>',
	
	//commented out because it was a 404
	//'<div id="toggleText2" style="display: none">',
	//		'<iframe id="biomixer_iframe" src="http://bioportal-integration.bio-mixer.appspot.com/?mode=embed&amp;embed_mode=paths_to_root&amp;ontology_acronym=RADLEX&amp;full_concept_id={values.prefixIRI}&amp;userapikey=" data-src="http://bioportal-integration.bio-mixer.appspot.com/?mode=embed&amp;embed_mode=paths_to_root&amp;ontology_acronym=RADLEX&amp;full_concept_id={values.prefixIRI}&amp;userapikey=" style="" height="100%" width="100%" frameborder="0"></iframe>',
	//'</div>',

	];

	return tpl;
}

function handleActionFailure(msg){
	var active_win = Ext.WindowMgr.getActive();
	var zindex = (active_win != null ? active_win.el.dom.style.zIndex : 9000);
	zindex = parseInt(zindex) + 100;
	var msg = '<div align="center">' + msg + '</div>';
	
	var win = Ext.Msg.show({
			title: 'Failure!'
			,msg: msg
			,minWidth:300
			,buttons: Ext.MessageBox.OK
			,alwaysOnTop:true
			,listeners:{deactivate:function(self){self.toFront();}}
	});
}

function updateLinks(){
	$('a[href^="http://www.owl"]').each(function(i){
		var theID = $(this).attr('href').split("#")[1];
		$(this).addClass(theID);
		$.ajax({
			type: 'POST',
			url:'/ajax/radlex_util.cfm',
			data:{action:'GETCHILDREN',tid:theID},
			dataType: 'json',
			success: function(JSONData){
				$("."+ theID).attr("href", "http://www.radlex.org/RID/" + theID).text(JSONData[0].prefLabel);
			}
		});
	});
}

function checkChange() {
	if ($('#agree').prop('checked')) {
		$("#next").prop("disabled", false);
	} else {
		$("#next").prop("disabled", true);
	}
}

function checkAgreement() {
	if ($('#agree').prop('checked')) {
		$("#download").removeAttr("hidden");
		$("#terms").hide();
		// downloadContent.removeAttribute("hidden");
		// termsContent.setAttribute("hidden", true);
	} else {
		$("#next").prop("disabled", true);
	}}