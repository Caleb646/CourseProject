const axios = require('axios');
// const Swal = require('sweetalert2');
const apiBaseURL = "https://kcl2i7utrd3rfxv6c5rok4hjta0cvcjd.lambda-url.us-east-1.on.aws/";

document.getElementById('query').addEventListener('click', query);

async function query() {
    let text = document.getElementById('text').value;
    await axios.post(apiBaseURL, {query: text}).then(res => {
        let data = res.data;
        for (let d in data) {
            let info = data[d];
            let link = info.replace("([", " ").split(" ")[1];
            let x = parseInt(d) + 1;
            let result = "[" + x + "] " + link;
            if (!info.includes("coursera")) {
                result = "[" + x + "] " + info.substr(48, 148) + "...";
            }
            let doc = document.getElementById(d);
            doc.href = link;
            doc.innerText = result;
        }
    })
    document.getElementById('results').style.display = "block";
}