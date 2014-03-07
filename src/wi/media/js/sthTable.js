/*
 * Params:
 * settings {
 *	destDiv				- div to load the data (or table)
 *	template			- id of template
 *	urlGetData			- url to ajax view returning data array
 *	detailsUrl			- url to ajax view returning detail data (or null)
 *	detailsDiv			- div to place details (or null)
 *	contextFun			- function on right-click (or null)
 *	autoRefreshTime		- time in ms (or null)
 *	leftClickMenu		- selector for left click menu - same as contextmenu (or null)
 *	showSearchBox		- enable search box
 *	enableSorting		- sorting by columns
 *  scrollableContent 	- should tbody be fixed height & scrollable (requires fixed widths of tds)
 * }
 */
cc1.makeSthTable = function(settings) {
	var destElement = $(settings.destDiv),
		templateElement = $(settings.template),
		tableHeader = destElement.children('.thead'),
		tableCols = tableHeader.find('td').length,
		tableTbody = settings.scrollableContent ? $(destElement).find('.tbody tbody') : $(destElement).find('tbody'),
		overTable = $(settings.overTable),
		data = null,
		renderData = null, // template-rendered 'data' with additional sorting info
		autoRefresh = null,
		detailsDivElement = settings.detailsDiv ? $(settings.detailsDiv) : null,
		openedId = null,

		searchBox,
		searchBoxInput,
		searchBoxTimer,
		searchQuery,

		sortingColumn = settings.sortingColumnIndex ? settings.sortingColumnIndex: 0,
		sortingAsc = settings.sortingDescending ? false: true,
		max_chars = 80,

		selectAllCheckbox = $('#select-all'),
		separatorCheckbox = $('.separator-check'),
		checkboxStates = {},

		groupStates = {},
		itemDataAttr = settings.itemDataAttr ? settings.itemDataAttr: undefined,

	loadData = function(onlyRefreshTable) {
		if (onlyRefreshTable === undefined) {
			onlyRefreshTable = false;
		}
		$.ajax({ type: "GET", url: settings.urlGetData,
			success: function(response) {
				if (response !== undefined && response.status !== undefined && response.status < 8000) {
					data = response.data;

					if (data.length === 0) {
						showEmpty();
						return;
					}

					if (destElement.hasClass('tab')) {
						dataCopy = $.extend(true, [], data);

						var shorten = function (item) {
							for (var attr in item) {
								if (typeof item[attr] === "string") {
									item[attr] = item[attr].replace(/\n{2,}/g, '\n').replace(/^\s+/, '');
									if (item[attr].length > max_chars) {
										item[''+attr+'_shortened'] = item[attr].substring(0, max_chars);
									}
								}
							}
						};
						dataCopy.forEach(function(item) {
							shorten(item);
							// for nested list in 'items'
							if (item['items']) {
								item['items'].forEach(function(item2){
									shorten(item2);
								});
							}
						});
						renderData = settings.enableSorting? addSortingData(templateElement.tmpl(dataCopy)) : templateElement.tmpl(dataCopy);
						renderTable();
					} else {
						destElement.empty().append(templateElement.tmpl(data));
					}
				}
				$('.tooltip').tooltip(cc1.configs.tooltip);

				if (response !== undefined && response.status !== undefined && response.status >= 8000) {
					showError((response.data.length !== 0 && typeof(response.data) === "string")? response.data : gettext("Error occured. Please try again in a moment.") );
				}
			}
		});
		if (!onlyRefreshTable && openedId) {
			openDetails(openedId, true);
		}
		if (settings.loadAdditionalAction) {
			settings.loadAdditionalAction();
		}
	},
	renderTable = function() {
		var state;
		if (renderData) {
			var renderDataCopy = renderData.clone(true); // deep copy of prerendered data to avoid problems with sorting by several columns simul.
			if (settings.enableSorting) {
				renderDataCopy = sortData(renderDataCopy, sortingColumn, sortingAsc);
			}
			tableTbody.empty().append( renderDataCopy );
		}

		// set checkboxes states
		for (state in checkboxStates) {
			if (checkboxStates[state] === true) {
				getElementByData(tableTbody, 'input', state).attr('checked', 'true');
			}
		}

		// set checkboxes states in separators
		for (state in groupStates) {
			if (groupStates[state] === true) {
				tableTbody.find("input[data-category='" + state + "']").attr('checked', 'true');
			}
		}

		// adding class to elements hidden by separators
		var x = false;
		$.each(tableTbody.find('tr'), function() {
			var $this = $(this);
			if ($this[0].className === "separator") {
				x = $this.find('input:checkbox')[0].checked === true;
			} else {
				if (x === true) {
					$this.addClass('sep_hidden');
					$this.hide();
				}
			}
		});

		checkSelectAll();
		if (openedId) {
			getElementByData(tableTbody, 'tr', openedId).addClass('selected-row');
		}

		// filter search results
		if (searchQuery) {
			doSearch();
		}
		setRowClasses();
	},
	setRowClasses = function() {
		// set row backgrounds
		var i = 0;
		$.each(tableTbody.find('tr:visible'), function(){
			var $this = $(this);
			$this.removeClass('odd');
			(i++)%2===1 && $this.addClass('odd');
		});
	},
	bindActions = function() {
		// row left click
		if (settings.detailsUrl) {
			tableTbody.on('click', 'td:not(.selecting, .noClick)', function(e) {
				var trElement = $(this).parent(),
					itemId = trElement.data('id');
				openDetails(itemId, openedId === itemId);
				loadData(true);
				return true;
			});
		}
		// row right click
		if (settings.contextFun) {
			$.contextMenu({
		        selector: '.rclick td',
		        ignoreRightClick: false,
		        build: function($trigger, e) {
		            // this callback is executed every time the menu is to be shown
		            var itemData = getItemById(($trigger).parent().data('id'), itemDataAttr);
		            return settings.contextFun(itemData);
		        }
			});
		}
		// contextmenu on left click
		if (settings.leftClickMenu && settings.contextFun) {
			$.contextMenu({
		        selector: settings.leftClickMenu,
		        trigger: 'left',
		        ignoreRightClick: true,
		        build: function($trigger, e) {
		        	var itemData = getItemById(($trigger).parent().parent().data('id'), itemDataAttr);
		            return settings.contextFun(itemData);
		        }
		    });
		}
		// searchBox input content changed
		if (settings.showSearchBox && destElement.hasClass('tab')) {
			searchBox.on('keyup', 'input', function() {
				clearTimeout( searchBoxTimer );
				searchBoxTimer = ( searchBoxInput.value.length >= 0 ) && setTimeout(function() {
					searchQuery = searchBoxInput.value;
					doSearch();
					setRowClasses();
				}, 50);
			}).on('keypress', 'input', function(e) {
				// prevent submitting the form on Enter
				if (e.which === 13) {
					return false;
				}
			});
		}
		// sorting by column when th>td clicked
		if (settings.enableSorting && destElement.hasClass('tab')) {
			tableHeader.on('click', 'td:not(.noSort)', function() {
				var that = this;
				$(this).parent().children('td').each(function(index) {
					$this = $(this);
					if (!$this.hasClass('noSort')) {
						$this.removeClass('sorting_asc sorting_desc').addClass('sorting');
					}
					if (this === that) {
						sortingAsc = index === sortingColumn? !sortingAsc : true;
						sortingColumn = index;
						renderTable();
					}
				});
				$(that).removeClass('sorting sorting_asc sorting_desc').addClass(sortingAsc? 'sorting_asc' : 'sorting_desc');
			});
		}
		// checkboxes click
		if (selectAllCheckbox) {
			tableTbody.on('click', 'input:checkbox:not(.separator_check)', function() {
				checkboxStates[$(this).data('id')] = this.checked;
				checkSelectAll();
			});
		}

		// separator-checkboxes click
		if (separatorCheckbox) {
			tableTbody.on('click', 'input.separator_check', function() {
				groupStates[$(this).data('category')] = this.checked;
				renderTable();
			});
		}
	},
	// checks whether selectAllCheckbox should be checked
	checkSelectAll = function() {
		if (selectAllCheckbox) {
			var cbList = tableTbody.find('input:checkbox'),
			checkedCount = 0;

			cbList.each(function() {
				if (this.checked) {
					checkedCount ++;
				}
			});
			selectAllCheckbox.attr('checked', cbList.size() === 0 || cbList.size() === checkedCount);
		}
	},
	getElementByData = function(parent, elementType, id) {
		return parent.find('[data-id="' + id + '"]').filter(elementType);
	},
	openDetails = function(itemId, silent) {
		if (itemId === undefined) {
			return;
		}
		var detailsUrlWithId = settings.detailsUrl.replace('0', itemId);

		openedId = itemId;

		tableTbody.find('tr').removeClass('selected-row');
		getElementByData(tableTbody, 'tr', openedId).addClass('selected-row');

		if (!silent) {
			detailsDivElement.html(cc1.utils.html.ajaxLoader(1));
		}
		$.post(detailsUrlWithId, function(response) {
			if (response !== undefined && response.status !== undefined && response.status < 8000) {
				detailsDivElement.html(response.data);
			} else {
				detailsDivElement.empty();
			}
		});
	},
	closeDetails = function() {
		tableTbody.find('tr').removeClass('selected-row');
		detailsDivElement.empty();
		openedId = null;
	},
	setAutoRefresh = function() {
		var autoRefreshCB = $('#auto-refresh input');
		autoRefreshCB.click(function() {
			if (this.checked) {
				autoRefresh = setInterval(loadData, settings.autoRefreshTime);
			} else {
				clearInterval(autoRefresh);
			}
		});
		if (autoRefreshCB.attr('checked')) {
			autoRefresh = setInterval(loadData, settings.autoRefreshTime);
		}
	},
	setUrlGetData = function(newUrl) {
		settings.urlGetData = newUrl;
	},
	getListOfSelected = function(itemId) {
		var ret = new Array();
		if (itemId) {
			ret.push(itemId);
		} else {
			tableTbody.find('tr:visible').find('input:checked').each(function() {
				ret.push( $(this).data('id') );
			});
		}
		return ret;
	},
	getListOfSelectedNames = function(itemId) {
		 return $.map( cc1.sthTable.getListOfSelected(itemId), function(val) {
				return cc1.sthTable.getItemById(val).name;
			}).join(', ');
	},
	getListOfSelectedAdresses = function(itemId) {
		 return $.map( cc1.sthTable.getListOfSelected(itemId), function(val) {
				return cc1.sthTable.getItemById(val).address;
			}).join(', ');
	},
	getOpenedId = function() {
		return openedId;
	},
	getItemById = function(id, name) {
		if (name !== undefined) {
			return getItemByIdInName(id, name);
		} else {
			var i, j;
			for (i=0; i<data.length; i++) {
				if (data[i][settings.idKey] === id) {
					return data[i];
				}
			}
			return null;
		}
	},
	getItemByIdInName = function(id, name) {
		for (i=0; i<data.length; i++) {
			if (data[i][name] !== undefined) {
				for (j=0; j<data[i][name].length; j++) {
					if (data[i][name][j][settings.idKey] === id) {
						return data[i][name][j];
					}
				}
			}
		}
		return null;
	},
	showError = function(errorMessage) {
		if (destElement.hasClass('tab')) {
			tableTbody.html('<tr><td colspan="' + tableCols + '">' + errorMessage + '</td></tr>');
		} else {
			destElement.html('<p>' + errorMessage + '</p>');
		}
	},
	showEmpty = function() {
		var message = gettext("No items to display.");
		if (destElement.hasClass('tab')) {
			tableTbody.html('<tr><td class="noClick" colspan="' + tableCols + '">' + message + '</td></tr>');
		} else {
			destElement.html('<p>' + message + '</p>');
		}
	},
	toggleChecked = function(checked) {
		tableTbody.find('tr:visible').find('input:checkbox').each(function() {
			$(this).attr('checked', checked)
			checkboxStates[$(this).data('id')] = checked;
		});

	},
	getData = function() {
		return data;
	},
	doSearch = function() {
		var terms = searchQuery.toLowerCase().split(','),
			resultCount = 0,
			searchInTr = function(tr) {
				var r, i;
				if (terms[0].length === 0) {
					return true;
				}
				for (r=0; r<tr.children.length; r++) {
					for (i=0; i<terms.length; i++) {
						if (terms[i].length && tr.children[r].innerHTML.replace(/<[^>]+>/g, '').toLowerCase().indexOf(terms[i]) >= 0) {
							return true;
						}
					}
				}
				return false;
			};
		tableTbody.find('tr').hide().each( function(index){
			if ((searchInTr( this ) || this.children[0].className === "tab_separator" ) && !$(this).hasClass("sep_hidden")) {
				$(this).show();
				resultCount++;
			}
		});
		tableTbody.find('tr.noSearchResult').remove();
		if (resultCount === 0) {
			$('<tr/>', {
				'class': 'noSearchResult',
				html: '<td colspan=' + tableCols + '>' + gettext('Text not found.') + '</td>'
			}).appendTo(tableTbody);
		}
	},
	addSortingData = function(renderDataRaw) {
		// adding sorting data (text and numeric)
		var parseElement = function(node) {
				var parsed = $.trim(node.textContent),
					datePatt = /^\d{1,2}\.\d{1,2}\.\d{4}\, \d{1,2}:\d{2}$/,
					sizePatt = /^\d{1,4}(\.\d)? (KB|MB|GB|TB)$/;

				// for Date
				if (datePatt.test(parsed)) {
					var data = parsed.split(/\.|, |:/);
					for ( j = 0; j< 5; j++)
						if (isDecimal(data[j]) === false)
							return parsed;
					return [3, new Date(data[2], data[1]-1, data[0], data[3], data[4], 0)];
				}

				// for size (KB, MB, ...)
				if (sizePatt.test(parsed)) {
					var data = parsed.split(" "),
						multiplier = 1;
					switch (data[1]) {
					case "TB": multiplier *= 1024;
					case "GB": multiplier *= 1024;
					case "MB": multiplier *= 1024;
					}
					return [2, parseFloat(data[0]) * multiplier];
				}

				// for numbers and strings
				return isDecimal(parsed)? [1, parseFloat(parsed)] : [0, parsed.toLowerCase()];
			};

		renderDataRaw.each(function(i) {
			if (!this.children) {
				renderDataRaw.splice(i, 1);
			}
		});

		renderDataRaw.each(function(i) {
			var trData = [];
			for (var j=0; j<this.children.length; j++) {
				trData.push(parseElement(this.children[j]));
			}
			$(this).data('sort', trData);
		});
		return renderDataRaw;
	},

	sortData = function(sData, index, asc) {
		// comparing function
		var sortFunction = function(x, y) {
			var a = $(x).data('sort')[index],
				b = $(y).data('sort')[index],
				diff = 0;
			if (a[0] !== b[0]) {
				diff = ((a[0] < b[0]) ? -1 : ((a[0] > b[0]) ? 1 : 0));
			} else {
				diff = ((a[1] < b[1]) ? -1 : ((a[1] > b[1]) ? 1 : 0));
			}
			return asc ? diff : -diff;
		},
			tempData = [],
			sDataCopy = [],
			sep = "separator";

		if (sData.length > 0 && sData[0].className !== sep) {
			return sData.sort(sortFunction);
		}
		// @TODO: better way to sort than using 'push'
		sData.each(function(i) {
			if (this.className === sep) {
				tempData.sort(sortFunction);
				sDataCopy = sDataCopy.concat(tempData);

				tempData = [];
				sDataCopy.push(this);
			} else {
				tempData.push(this);
			}
		});
		tempData.sort(sortFunction);
		sDataCopy = sDataCopy.concat(tempData);

		return sDataCopy;
	},

	// create an overlay over the table and disables inputs, selets and links
	freeze = function() {
		cc1.utils.createOverlay(destElement.parent());

		// disable events
		destElement.off();
	},

	init = function() {
		if (settings.autoRefreshTime) {
			setAutoRefresh();
		}
		if (typeof settings.idKey === undefined) {
			settings.idKey = 'id';
		}
		if (settings.showSearchBox && destElement.hasClass('tab')) {
			searchBoxInput = $('<input/>', {
				type: 'text',
				title: gettext('Enter comma separated strings to search for.'),
			})[0];
			searchBox = $('<div/>', {
				id: 'searchBox',
				text: gettext('Search:')
			}).append( searchBoxInput );
			overTable.append(searchBox);
		}
		if (settings.enableSorting && destElement.hasClass('tab')) {
			$.each(tableHeader.find('td'), function(index) {
				var $this = $(this);
				if (!$this.hasClass('noSort')) {
					$this.attr('title', gettext('Click to sort by column'))
					$this.addClass('sorting pointer');
					if (sortingColumn === index) {
						$this.removeClass('sorting').addClass(sortingAsc ? 'sorting_asc' : 'sorting_desc');
					}
				}
				if ($this.hasClass('noSort') && sortingColumn === index) sortingColumn++;
			});

		}
		loadData();
		bindActions();
	};

	sthTable = {
		loadData: loadData,
		closeDetails: closeDetails,
		openDetails: openDetails,
		getOpenedId: getOpenedId,
		getListOfSelected: getListOfSelected,
        getListOfSelectedNames: getListOfSelectedNames,
        getListOfSelectedAdresses: getListOfSelectedAdresses,
		setUrlGetData: setUrlGetData,
		toggleChecked: toggleChecked,
		getData: getData,
		getItemById: getItemById,
		freeze: freeze,

		vnc: openVnc
	};

	init();
	return sthTable;
};
