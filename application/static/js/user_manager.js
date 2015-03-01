$(document).ready(function() {
	$("#userdata").dataTable({
		"ajax": "/users",
		"columns": [
			{"data": "full_name"},
			{"data": "nickname"},
			{
				"data": "active",
				"render": function(data, type, full, meta) {
					if (data == true) {
						return '<a style="color: #00FF00">Active</a>';
					}
					return '<a style="color: #FF0000">Inactive</a>';
				}
			},
			{
				"targets": 0,
				"data": "id",
				"render": function(data, type, full, meta) {
					return '<a class="btn btn-primary" href="/dashboard/users/'
							+ data + '">Edit</a>';
				}
			}
		]
	});
})
