$("ul.subnav").parent().append("<span></span>");

var config = {
	over: function () {
		$(this).find("ul.subnav").slideDown(100);
	},
	timeout: 500, // number = milliseconds delay before onMouseOut
	interval: 10,
	out: function () {
		$(this).find("ul.subnav").slideUp(100);
	}
};

$("ul.topnav li").hoverIntent(config);