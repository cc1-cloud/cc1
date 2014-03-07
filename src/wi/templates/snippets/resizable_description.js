{% load i18n %}
{% load formtags %}

{% templatetag openvariable %}if description_shortened{% templatetag closevariable %}
	<span class="short">
		{% templatetag openvariable %}html description_shortened.escapeHTML().wbrAndLb(){% templatetag closevariable %}
	</span>				
	<span class="full">
		{% templatetag openvariable %}html description.escapeHTML().wbrAndLb(){% templatetag closevariable %}
	</span>
	<a class="td-toggle small_arrow_right" onclick="cc1.utils.toggleRowHeight(this);" title="{% trans "Click to expand." %}"></a>
{% templatetag openvariable %}else{% templatetag closevariable %}
	{% templatetag openvariable %}html description.escapeHTML().wbrAndLb(){% templatetag closevariable %}
{% templatetag openvariable %}/if{% templatetag closevariable %}