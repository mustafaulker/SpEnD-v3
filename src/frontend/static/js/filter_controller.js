function search_filter() {
    let input, filter, table, tr, td, i, txtValue, checkBox

    input = document.getElementById("endpointSearch")
    filter = input.value.toUpperCase()
    table = document.getElementById("endpointTable")
    tr = table.getElementsByTagName("tr")
    checkBox = document.getElementById("aliveCheckbox")

    if (checkBox.checked) {
        tr = alive_filter()
    }

    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[1]
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = ""
            } else {
                tr[i].style.display = "none"
            }
        }
    }
}

function alive_filter() {
    let table, tr, td, i, checkBox, is_alive
    let alive_list = []

    table = document.getElementById("endpointTable")
    tr = table.getElementsByTagName("tr")
    checkBox = document.getElementById("aliveCheckbox")

    if (checkBox.checked) {
        for (i = 0; i < tr.length; i++) {
            td = tr[i].getElementsByTagName("td")[4]
            if (td) {
                is_alive = td.getElementsByTagName("span")[0].title
                if (is_alive === "Live") {
                    tr[i].style.display = ""
                    alive_list.push(tr[i])
                } else {
                    tr[i].style.display = "none"
                }
            }
        }
        return alive_list
    } else {
        search_filter()
    }
}