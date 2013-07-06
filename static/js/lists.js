listGetLastRow=function(){
	return $("#wordtablebody tr:last-child").filter(":last");
};
makeDeleteBtn=function(word){
	return $('<a>').addClass('btn btn-danger btn-mini pull-right delete-word-btn').text('delete').attr('delete-id', word);
}
appendColumn=function(lastrow, word){
	lastrow.append($("<td>").append($("<p>").text(word).addClass('text-center').append(makeDeleteBtn(word))));
};
newWordCallback=function(data){
	var lastrow = listGetLastRow();
	var numOfColumninLastRow= lastrow.children().length;
	var word = data.word;
	if (numOfColumninLastRow < 3){
		appendColumn(lastrow, word);
	} else {
		var tbody = lastrow.parent();
		lastrow = $('<tr>');
		appendColumn(lastrow, word);
		tbody.append(lastrow);
	}
	
};
newWordHandler=function(){
	var newword = $("#newwordinput").val();
	$("#newwordinput").val('');
	var postdata = {'method':'newword', 'word': newword};
	var url = $(location).attr('href');
	$.xsrfPost(url, postdata, newWordCallback, 'json');
};
newListCallback=function(data){
	var url = $(location).attr('href');
	var shortUrl=getParentUrl(url);
	if (data.status_code == '200'){
		listnum = $('#lists').children().length + 1
		var item = $('<li>').append($('<a>').attr('href', shortUrl + '/list' + listnum).text('list' + listnum));
		$('#lists').append(item);
	}
};
newListHandler=function(){
	var url = $(location).attr('href');
	var shortUrl=getParentUrl(url)
	$.xsrfPost(shortUrl,{method: 'newlist'}, newListCallback, 'json');
};
removeBanner=function(){
	$('#success-banner').remove()
};
deleteWordCallback=function(){
	location.reload()
};
deleteWordHandler=function(){
	var word = $(this).attr('delete-id')
	var postdata = {
		'method': 'deleteword',
		'word': word
	};
	var url = $(location).attr('href');
	$.xsrfPost(url, postdata, deleteWordCallback, 'json');
};
addReviewListCallback=function(data){
	p = $('<p>').addClass('lead').addClass('text-center').addClass('text-success').attr('id', 'success-banner').text('Added');
	$('#top-line').prepend(p);
	window.setTimeout(removeBanner, 3000)
};
addReviewListHandler=function(){
	var collection = $(this).attr('submit-id-collection');
	var listnum = $(this).attr('submit-id-listnum');
	var postdata = {
		'method': 'addlist',
		'collectionname': collection,
		'listnum': listnum
	};
	$.xsrfPost('/notebook/reviewlist', postdata, addReviewListCallback, 'json');
};
$(function(){
	$('#newlistbtn').click(newListHandler);
	$('#addreviewlist').click(addReviewListHandler);
	$('.delete-word-btn').click(deleteWordHandler);
});