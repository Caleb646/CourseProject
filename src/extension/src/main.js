const axios = require('axios');
const Swal = require('sweetalert2');
const apiBaseURL = "TBD";

var div = document.createElement('div');
div.id = 'container';
div.innerHTML = 'Hi there!';
div.className = 'border pad';

document.body.appendChild(div);