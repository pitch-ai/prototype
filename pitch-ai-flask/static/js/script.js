// Detect if file was uploaded
$("#inputFile").change(function() {
 console.log("hihi!!");
 $("#upload-img").attr("src", "static/images/bluecloud.svg");
 $("#uploadPresentation .card-start").css("border-color", "#3F47F5");
 $("#analyze-btn").css("visibility", "visible");
 $("#upload-text").html("File uploaded");
});

// Trigger file upload form
var uploadPresentation = document.getElementById("uploadPresentation");
uploadPresentation.addEventListener("click", function() {
 console.log("clicked");
 var inputFile = document.getElementById("inputFile");
 inputFile.click();
});

 // Show spinner if we can successfully analyze file
$("#analyze-btn").click(function() {
 console.log("analyze clicked!!")
 $(".new-presentation").hide();
 $("#jumbotron-presentation").css("visibility", "hidden");
 $("#upload-loading").show();
});



