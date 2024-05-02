function refreshImages() {
	var img_trg = document.getElementById("img_trg");
	var img_prd = document.getElementById("img_prd");
	img_trg.src = img_trg.src + "?t=" + new Date().getTime();
	img_prd.src = img_prd.src + "?t=" + new Date().getTime();
	console.log("one time")
}
setInterval(refreshImages, 3000)