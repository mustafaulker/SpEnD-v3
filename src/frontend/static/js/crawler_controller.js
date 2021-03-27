function get_crawl_parameters() {
    let desired_search_engines = []
    let desired_keywords = []
    let inputs = document.getElementsByTagName("input");

    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].type === "checkbox" && inputs[i].checked && inputs[i].name === "cb_se") {
            desired_search_engines.push(inputs[i].id)
        }
        else if (inputs[i].type === "checkbox" && inputs[i].checked && inputs[i].name === "cb_kw") {
            desired_keywords.push(inputs[i].id)
        }
    }
    let textare = document.getElementById("kw_input");
    desired_keywords = desired_keywords.concat(textare.value.split(/\r?\n/))
}