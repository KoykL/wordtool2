successHandler=function(data){
	if (data.status_code == 200){
		window.location.reload()
	} else if (data.status_code == 210){
		window.location = "/notebook/reviewlist"
	}
}
rememberHandler=function(){
	var word = $('#word').attr('word-id')
	var postdata = {
		word: word,
		state: 'remember'
	};
	$.xsrfPost('/notebook/reviewlist/reviewsystem', postdata,successHandler,'json')
};
forgetHandler=function(){
	var word = $('#word').attr('word-id')
	var postdata = {
		word: word,
		state: 'forget'
	};
	$.xsrfPost('/notebook/reviewlist/reviewsystem', postdata,successHandler,'json')
};
$(function(){
	$('#remember-btn').click(rememberHandler)
	$('#forget-btn').click(forgetHandler)
})