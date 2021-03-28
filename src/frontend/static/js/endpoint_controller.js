function createPage(){

    let xhr = new XMLHttpRequest();

    let selectedEndpointUrl = document.querySelector(".ep-class").getAttribute("about");

    xhr.open("POST", "/selectedEndpoint");
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("url="+selectedEndpointUrl);
}