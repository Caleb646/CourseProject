const path = require('path');

module.exports = {
	entry:{login: "./src/main.js"},
	optimization: {
		minimize: false
	},
	output: {
		filename: '[name].js',
		path: path.resolve(__dirname, "dist")
	}


};