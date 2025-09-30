const path = require("path");

module.exports = {
  entry: "./ui_src/index.ts", // Update to your actual entry file
  output: {
    filename: "bundle.js",
    path: path.resolve(__dirname, "plan_visual_django/static/dist"), // Your static folder
  },
  resolve: {
    extensions: [".ts", ".js"], // Automatically resolve these extensions
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: "ts-loader",
        exclude: /node_modules/,
      },
    ],
  },
  mode: "development",
  devtool: "source-map", // Generate source maps
};