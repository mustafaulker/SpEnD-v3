function search_filter() {
    let input, filter, table, tr, td, i, txtValue, checkBox, alives, td2, txtValue2

    input = document.getElementById("endpointSearch")
    filter = input.value.toUpperCase()
    table = document.getElementById("endpointTable")
    tr = table.getElementsByTagName("tr")
    checkBox = document.getElementById("aliveCheckbox")

    if (checkBox.checked) {
        alives = alive_filter()
        for (i = 0; i < alives.length; i++) {
            td2 = alives[i].getElementsByTagName("td")[1]
            if (td2) {
                txtValue2 = td2.textContent || td2.innerText;
                if (txtValue2.toUpperCase().indexOf(filter) > -1) {
                    alives[i].style.display = ""
                } else {
                    alives[i].style.display = "none"
                }
            }
        }
    } else {
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
                is_alive = td.getElementsByTagName("img")[0].alt
                if (is_alive === "True") {
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