const path = require('path');

module.exports = {
	entry:{login: "./src/login.js"},
	optimization: {
		minimize: false
	},
	output: {
		filename: '[name].js',
		path: path.resolve(__dirname, "dist")
	}


};