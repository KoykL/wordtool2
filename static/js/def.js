successHandler=function(data){
	if (data.status_code == 200){
		window.location = "/notebook/review"
	} else if (data.status_code == 210){
		window.location = "/notebook/review/"
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
	$.xsrfPost('/notebook/review', postdata,successHandler,'json')
};
forgetHandler=function(){
	var word = $('#word').text()
	var postdata = {
		word: word,
		collection: $(this).attr('collection-id'),
		list: $(this).attr('list-id'),
		state: 'forget'
	};
	$.xsrfPost('/notebook/review', postdata,successHandler,'json')
};
$(function(){
	$('#remember-btn').click(rememberHandler)
	$('#forget-btn').click(forgetHandler)
})