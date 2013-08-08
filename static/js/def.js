successHandler=function(data){
	if (data.status_code == 200){
		window.location = "/notebook/reviewlist/reviewsystem"
	} else if (data.status_code == 210){
		window.location = "/notebook/reviewlist"
	}
}
rememberHandler=function(){
	var word = $('#word').text()
	var postdata = {
		word: word,
		collection: $(this).attr('collection-id'),
		list: $(this).attr('list-id'),
		state: 'remember'
	};
	$.xsrfPost('/notebook/reviewlist/reviewsystem', postdata,successHandler,'json')
};
forgetHandler=function(){
	var word = $('#word').text()
	var postdata = {
		word: word,
		collection: $(this).attr('collection-id'),
		list: $(this).attr('list-id'),
		state: 'remember'
	};
	$.xsrfPost('/notebook/reviewlist/reviewsystem', postdata,successHandler,'json')
};
$(function(){
	$('#remember-btn').click(rememberHandler)
	$('#forget-btn').click(forgetHandler)
})