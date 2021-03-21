function search_filter() {
    let input, filter, table, tr, td, i, txtValue
    input = document.getElementById("endpointSearch")
    filter = input.value.toUpperCase()
    table = document.getElementById("endpointTable")
    tr = table.getElementsByTagName("tr")

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
    let table, tr, td, i, txtValue, checkBox
    table = document.getElementById("endpointTable")
    tr = table.getElementsByTagName("tr")
    checkBox = document.getElementById("aliveCheckbox")

    if (checkBox.checked) {
        for (i = 0; i < tr.length; i++) {
            td = tr[i].getElementsByTagName("td")[4]
            if (td) {
                txtValue = td.textContent || td.innerText
                if (txtValue === "True") {
                    tr[i].style.display = ""
                } else {
                    tr[i].style.display = "none"
                }
            }
        }
    } else {
        for (i = 0; i < tr.length; i++) {
            tr[i].style.display = ""
        }
    }
}