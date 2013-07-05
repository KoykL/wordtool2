deleteCollectionCallback=function(data){
	location.reload();
};
deleteCollectionHandler = function(){
	var postdata={'method': 'deletecollection', 'collectionname':$(this).attr('deleteId')};
	var url = $(location).attr('href');
	var shortUrl=getParentUrl(url);
	$.xsrfPost(shortUrl, postdata, deleteCollectionCallback, 'json');
};
$(function(){
	$(".w-delete-button").click(deleteCollectionHandler)
})