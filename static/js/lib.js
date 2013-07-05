function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
};
getParentUrl = function(url){
	return url.substring(0,url.lastIndexOf("/"));
};
$(function(){
	$.xsrfPost=function(url, data, callback, datatype){
		data._xsrf=getCookie("_xsrf");
		$.post(url, data, callback, datatype)
	} 
});