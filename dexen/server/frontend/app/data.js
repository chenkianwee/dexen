function refreshJobDataTable() {
	var jobName = getCurrentJobNameFromTable();
	if(!jobName){
		alert('There is no job selected');
		return;
	}

	var ajaxUrl = '/data/' + jobName;
	console.log('Loading job data from ' + ajaxUrl);
	$.ajax({
        type: "GET",
        url: ajaxUrl,
        dataType: "json",
        success: function (data) {
        	var DATA_ID = "_id";
        	var BINARY_KEYS = "keys";

        	var attrSet = {};
        	var columns = [];
        	for(i=0; i<data.data.length; ++i){
        		$.each(data.data[i], function(key, item) {
        			if(!attrSet.hasOwnProperty(key)){
        				attrSet[key] = true;
        				columns.push(
        					{	"title" : escapeHtml(key), 
        						"data" : key, 
        						"render" : (function(localKey){
        										return function(cellData, type, row, meta){
        											if(type == "display" && typeof(cellData) == "string"){        												
        												var metadata = data.metadata[meta.row];
										        		if(metadata.hasOwnProperty(BINARY_KEYS)){
										        			if(metadata[BINARY_KEYS].indexOf(localKey) != -1){
										        				var dataId = row[DATA_ID];										        			
										        				var url = "/data/" + encodeURIComponent(jobName) + "/" + encodeURIComponent(dataId) + "/" + encodeURIComponent(localKey);
																return "<a href='" + url + "'>Download</a>";
										        			}										        			
										        		}
										        		return escapeHtml(cellData);
        											}

        											return cellData;
        										};
        									})(key)
        				});
        			}
        		});
        	}

        	var $table = $('#jobDataTable');
        	if ( $.fn.dataTable.isDataTable($table) ) {
			    $table.DataTable().destroy();
			}

        	$table.dataTable({
        		"data" : data.data,
        		"columns" : columns,
        		"dom": 'RC<"clear">lfrtip'
        	});

        },
        error: function (jqXHR, textStatus, errorThrown) {
        	alert("Unable to get job data. Status: " + textStatus);
        }
    })
}

function setupJobDataTable() {
    var $refreshBtn = $('#refreshJobDataTableBtn');

    $refreshBtn.on("click", refreshJobDataTable);
}
