cc1.initMessages = function(settings) {
	var messagesCount = 1,
		topMessagesDiv = $('#top-messages'),

	// pobiera i wyswietla komunikaty usera
	get = function() {
		$.post(settings.urlGetMessages, function(response) {
			var i, message;
			if (response !== undefined && response.status === 0 && response.data.length !== 0) {
				for (i in response.data) {
					message = response.data[i];
					add(message.message_id , message.creation_date, message.level, message.text);
				}
			}
		});
	},
	// dodanie informacji u gory
	add = function(id, date, class_name, content) {
		var fromCLM = true,
			messageDiv = $('#message' + id);
		// jak juz jest message o takim id to nie dodawaj
		if (id !== 0 && messageDiv.length !== 0) {
			return;
		}
		// dla komunikatow nie-z-CLMa
		if (id === 0) {
			id = -messagesCount;
			messagesCount++;
			fromCLM = false;
		}
		topMessagesDiv.append('<div id="message' + id + '" class="' + class_name + '"><span class="date">' + date + '</span><span class="content">'+content+'</span><span class="remove-button" onclick="cc1.messages.remove('+id+');" title="' + gettext('Remove message') + '"></span><div class="clear"></div></div>');

		messageDiv = $('#message'+id);
		messageDiv.show('fade', 600);
		if (class_name == 'success' && !fromCLM) {
			setTimeout(function() {
				closeAnim(messageDiv);
			}, 12000);
		}
	},
	remove = function(id) {
		var url = settings.urlRemoveMessage.replace('0', id),
			messageDiv = $('#message' + id);
		closeAnim(messageDiv);
		if (id > 0) {
			$.post(url, function(response){});
		}
	},
	closeAnim = function(messageDiv) {
		messageDiv.hide('puff', function() {
			$(this).remove();
		}, 400);
	},
	setAutoRefresh = function() {
		get();
		autoRefresh = setInterval(get, settings.autoRefreshTime);
	},
	// dialog po odpowiedzi ajaxowej
	showAjaxResponseDialog = function(response) {
		var dialog_class = '', i, html;

		if (response !== undefined && response.status === 7999) {
			dialog_class = "info";
		} else if (response !== undefined && response.status < 8000) {
			dialog_class = "success";
		} else {
			dialog_class = "error";
		}
		if ($.isArray(response.data)) {
			html = '<ul>';
			for (i in response.data) {
				if (response.data[i].type == 'vm'){
					html += '<li class="' + (response.data[i].status === 'ok' ? 'msg_response_ok' : 'msg_response_error') + '">'
						  + 'VM (id:' + response.data[i].vmid + '): ' + response.data[i].status_text + '</li>';
				}
				if (response.data[i].type == 'storage-node'){
					html += '<li class="' + (response.data[i].status === 'ok' ? 'msg_response_ok' : 'msg_response_error') + '">'
						  + 'Storage (id:' + response.data[i].sid + '), ' + 'Node (id:' + response.data[i].nid + '): ' + response.data[i].status_text + '</li>';
				}
			}
			html += '</ul>';
			response.data = html;
		}
		add(0, new Date().toShortString(), dialog_class, response.data);
	},
	messages = {
		get : get,
		add : add,
		remove : remove,
		showAjaxResponseDialog : showAjaxResponseDialog,
	};
	if (settings.autoRefreshTime) {
		setAutoRefresh();
	}
	return messages;
};