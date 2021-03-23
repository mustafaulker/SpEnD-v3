function save_message(){
    const name = document.getElementById("contact_name")
    const subject = document.getElementById("contact_subject")
    const email = document.getElementById("contact_email")
    const message = document.getElementById("contact_message")
    const send_button = document.getElementById("send_button")

    const elements = [name, email, message]
    const config = new Map();

    try {
        config.set(subject.id, subject.value)
        for (element of elements) {
            if (element.value !== '') {
                config.set('' + element.id + '', element.value)
            } else {
                element.classList.add('is-danger')
                send_button.classList.add('is-warning')
                throw (element.name).charAt(0).toUpperCase() + (element.name).slice(1)
            }
        }
        const formJSON = Object.fromEntries(config.entries())
        let contact_post = JSON.stringify(formJSON, null, 2)
        console.log(contact_post)

        for (element of elements) { element.value = ""; element.classList.remove('is-danger') }

        send_button.innerText = "Message Sent!"
        send_button.classList.remove('is-warning')
        send_button.classList.add('is-success')
    }catch (error){
        send_button.innerText = '' + error + ' area cannot be empty!'
    }
}