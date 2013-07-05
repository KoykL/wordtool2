deleteListCallback=function(data){
	location.reload();
};
deleteListHandler = function(listNum){
	var postdata={'method': 'deletelist', 'listnum':$(this).attr('deleteId')};
	var url = $(location).attr('href');
	var shortUrl=getParentUrl(url);
	$.xsrfPost(shortUrl, postdata, deleteListCallback, 'json');
};
$(function(){
	$(".w-delete-button").click(deleteListHandler)
})