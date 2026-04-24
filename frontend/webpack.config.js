const path = require("path");
const webpack = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

const isDev = process.env.NODE_ENV !== "production";

module.exports = {
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "[name].[contenthash].js",
    publicPath: "/",
    clean: true,
  },
  resolve: {
    extensions: [".js", ".jsx"],
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: { loader: "babel-loader" },
      },
      {
        test: /\.css$/,
        use: [
          isDev ? "style-loader" : MiniCssExtractPlugin.loader,
          "css-loader",
          "postcss-loader",
        ],
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif|ico)$/i,
        type: "asset/resource",
      },
    ],
  },
  plugins: [
    new webpack.DefinePlugin({
      "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV || "development"),
      "process.env.API_BASE_URL": JSON.stringify(process.env.API_BASE_URL || ""),
      "process.env": JSON.stringify({}),
    }),
    new HtmlWebpackPlugin({
      template: "./public/index.html",
      favicon: "./public/favicon.ico",
    }),
    ...(isDev ? [] : [new MiniCssExtractPlugin({ filename: "[name].[contenthash].css" })]),
  ],
  devServer: {
    port: 3000,
    historyApiFallback: true,
    hot: true,
    webSocketServer: "ws",
    client: { webSocketURL: "ws://localhost:3000/hmr-ws" },
    proxy: [
      {
        context: ["/api"],
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      {
        context: ["/ws"],
        target: "http://localhost:8000",
        ws: true,
        changeOrigin: true,
      },
    ],
  },
  optimization: {
    splitChunks: { chunks: "all" },
  },
};
