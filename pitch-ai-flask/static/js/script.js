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
 $(".navbar").addClass("navbar-dropshadow");
 $("#upload-loading").show();
});
