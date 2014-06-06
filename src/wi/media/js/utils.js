String.prototype.endsWith = function(pattern) {
    var d = this.length - pattern.length;
    return d >= 0 && this.lastIndexOf(pattern) === d;
};

String.prototype.linebreak = function() {
	return this.replace(/\n/g, '<br />');
};

String.prototype.insertWbrs = function() {
	return this.replace(RegExp("(.{" + cc1.configs.wdr + "})(.)", "g"), function(all,text,char){
		return text + "<wbr>" + char;
	});
};

String.prototype.wbrAndLb = function() {
	return this.insertWbrs().linebreak();
};

String.prototype.escapeHTML = function() {
	return this.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
};

String.prototype.markdown = function() {
	return cc1.utils.markdownConverter(this);
};

Date.prototype.toShortString = function() {
    return	(this.getDate() < 10 ? '0' : '') +
    		this.getDate() + '.' +
    		(this.getMonth()+1 < 10 ? '0' : '') +
    		(this.getMonth()+1) + '.' +
    		this.getFullYear() + ', ' +
    		this.getHours() + ':' +
    		(this.getMinutes() < 10 ? '0' : '') +
    		this.getMinutes() + ':' +
    		(this.getSeconds() < 10 ? '0' : '') +
    		this.getSeconds();
};

Date.prototype.toShortStringUTC = function() {
    return	(this.getUTCDate() < 10 ? '0' : '') +
    		this.getUTCDate() + '.' +
    		(this.getUTCMonth()+1 < 10 ? '0' : '') +
    		(this.getUTCMonth()+1) + '.' +
    		this.getUTCFullYear() + ', ' +
    		this.getUTCHours() + ':' +
    		(this.getUTCMinutes() < 10 ? '0' : '') +
    		this.getUTCMinutes() + ':' +
    		(this.getUTCSeconds() < 10 ? '0' : '') +
    		this.getUTCSeconds();
};

//Checks that an input string is a decimal number, with an optional +/- sign character.
var isDecimal_re     = /^\s*(\+|-)?((\d+(\.\d+)?)|(\.\d+))\s*$/;
function isDecimal(s) {
   return String(s).search (isDecimal_re) != -1;
}

cc1.utils = {
	markdownConverter: new Markdown.getSanitizingConverter().makeHtml,
	html: {
		ajaxLoader: function(num) {
			var loader = $('<div/>', {
				 'class': 'ajax_loader' + num,
				 html: '&nbsp;'
			});
			return loader;
		}
	},
	createAction: function(settings) {
		return function() {
			var s = {};
			s.params = {};
			s.getParams = {};
			$.extend(s, settings);

			if (arguments.length >= 1) {
				s.url = s.url.replace('0', arguments[0]);
			}
			if (arguments.length >= 2) {
				s.url = s.url.replace('999999', arguments[1]);
			}
			if (s.calculateParams) {
				$.extend(s.params, s.calculateParams.apply(this, arguments));
				$.extend(s.getParams, s.calculateParams.apply(this, arguments));
			}
			if (s.calculatePostParams) {
				$.extend(s.params, s.calculatePostParams.apply(this, arguments));
			}
			if (s.calculateGetParams) {
				$.extend(s.getParams, s.calculateGetParams.apply(this, arguments));
			}
			cc1.utils.openDialog(s);
		};
	},
	// otwarcie dialogu
	openDialog: function(settings) {
		var urlGet = settings.url,
			urlPost = settings.url,
			dialogId = '#dialog-div',
			dialogDiv = $(dialogId),
			messagesDiv = $('#message-div'),

			setupButtons = function() {
				$('textarea').autoResize();
				$('select').selectBox(cc1.configs.selectbox);
				$('.tooltip').tooltip(cc1.configs.tooltip);

				dialogDiv.dialog('option', 'position', 'center');

				// ok button
				dialogDiv.find('form').submit(function() {
					var key, i,
						data = $(dialogId + ' input,' + dialogId + ' select,' + dialogId + ' textarea').serialize(),
						params = settings.params;

					// blur submit button to avoid resending (chromium bug)
					dialogDiv.find('.ok-button').blur();

					dialogDiv.children().hide().end()
						.append( cc1.utils.html.ajaxLoader(2) );

					for (key in params) {
						if ($.isArray(params[key])) {
							for (i in params[key]) {
								data += '&' + key + '=' + params[key][i];
							}
						} else {
							data += '&' + key + '=' + params[key];
						}
					}

					$.post(urlPost, data, function(response) {
						var postAction = function(response) {
							if (response.status === 1) {		// form not valid
								var settingsCopy = {};
								$.extend(settingsCopy, settings);
								settingsCopy.content = response.data;
								cc1.utils.openDialog(settingsCopy);
							} else {
								if (settings.action) {			// addition action after form submit (usage:
									settings.action(response);	// createAction({ action: function(resp){ ...
								}
								cc1.messages.showAjaxResponseDialog(response);
								cc1.sthTable.loadData();
							}
						};
						dialogDiv.dialog('close');
						postAction(response);
					});
					return false;
				});
				// cancel button
				dialogDiv.find('.cancel-button').unbind('click').click(function(){
					dialogDiv.dialog('close');
				}).end()
					.dialog('open').find('.ok-button').focus()
				  .end()
					.find('.inputs input').first().focus();
			};

		settings.dialogWidth = settings.dialogWidth || 400;
		settings.resizable = settings.resizable || false;
		settings.params = settings.params || {};
		settings.dialogClass = settings.dialogClass || 'prompt';
		settings.getParams = settings.getParams || {};
		settings.dialogTitle = settings.dialogTitle || gettext("Are you sure?");

		$('select').selectBox('destroy');
		$('.selectBox-options').remove();

		dialogDiv.remove();
		$('<div/>', {
			id: dialogId.substring(1),
			title: settings.dialogTitle
		}).appendTo(messagesDiv);

		dialogDiv = $(dialogId);
		dialogDiv.append(cc1.utils.html.ajaxLoader(2));

		dialogDiv.dialog({
			resizable: settings.resizable,
			close: function() {
                $(document).off('mouseup.resize');
            },
			draggable: true,
			width: settings.dialogWidth,
			modal: true,
			dialogClass: 'dialog-'+settings.dialogClass,
			hide: 'fade',
			show: 'fade',
			position: 'center',
			minWidth: 300,
			minHeight: 300
		});

		if (settings.content) {
			dialogDiv.empty().append(settings.content);
			setupButtons();
		} else {
			$.get(urlGet, settings.getParams, function(response) {
				dialogDiv.empty().append(response.data);
				setupButtons();
			});
		}
	},
	// copy to clipboard message window
	openCopyToClip: function(data) {
		var dialogId = '#dialog-div',
			dialogDiv = $(dialogId),
			messagesDiv = $('#message-div');

		dialogDiv.remove();
		$('<div/>', {
			id: dialogId.substring(1),
			title: gettext("Copy to clipboard:")
		}).appendTo(messagesDiv);

		dialogDiv = $(dialogId);
		dialogDiv.dialog({
			draggable: true,
			modal: true,
			dialogClass: 'dialog-info',
			hide: 'fade',
			show: 'fade',
			position: 'center',
			width: 400
		});
		dialogDiv.empty().append("<p/><textarea style='width:364px; max-width:364px'>" + data + "</textarea>");
		dialogDiv.find('textarea').select();
	},
	// checks if all checked items statuses are in list 'statusArray'
	stateTest: function(stateArray) {
		var i, selectedList = cc1.sthTable.getListOfSelected();
		if ( selectedList.length === 0 ) {
			return false;
		}
		for (i = 0; i < selectedList.length; i++) {
			if ( $.inArray(cc1.sthTable.getItemById(selectedList[i]).state, stateArray) === -1 ) {
				return false;
			}
		}
		return true;
	},
	// toggles between content of child .short and .full span
	toggleRowHeight: function(el) {
		var	$a = $(el),
			$td = $a.parent(),
			$short = $td.find('span.short'),
			$full = $td.find('span.full');

		$short.toggle();
		$full.toggle();

		if ($short.is(':visible')) {
			$a.removeClass('small_arrow_left').addClass('small_arrow_right').attr('title', gettext('Click to expand.'));
		} else {
			$a.removeClass('small_arrow_right').addClass('small_arrow_left').attr('title', gettext('Click to hide.'));
		}
	},
	// creates an overlay with ajaxLoader over div 'divToOverlay'
	createOverlay: function(divToOverlay) {
		var overlayCssClass = 'loader_overlay';
		if (divToOverlay.children().first().hasClass(overlayCssClass)) {
			return;
		}
		overlayDiv = $('<div/>', {'class': overlayCssClass, css: {
			width: '' + divToOverlay.width(),
			height: divToOverlay.height()
		}});
		overlayDiv.html(cc1.utils.html.ajaxLoader(1));

		// position ajaxLoader div in the middle
		overlayDiv.find('div').css({
			'margin-top': Math.max(0, divToOverlay.height()/2 - 10)
		});
		divToOverlay.prepend(overlayDiv);

		// disable selects and inputs inside 'divToOverlay'
		divToOverlay.find('select option:not(:selected)').attr('disabled', true);
		divToOverlay.find('input:visible').attr('readonly', true);
		divToOverlay.find('input:checkbox').click(function() {return false;});
		divToOverlay.find('input:checkbox').keydown(function() {return false;});

		// disable events
		divToOverlay.off();
	}
};