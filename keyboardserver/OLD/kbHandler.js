
// It's important to add an load event listener to the object,
// as it will load the svg doc asynchronously
// document.addEventListener("load",function(){

    // get the inner DOM of alpha.svg
    
// }, false);

function bindAll() {
    // var svgDoc = a.contentDocument;
    // get the inner element by id
    var delta = document.getElementById("K_0");
    // add behaviour
    delta.addEventListener("mousedown",function(){
            alert('hello world!')
    }, false);
}