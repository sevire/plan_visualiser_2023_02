const path = require('path')

module.exports = {
    mode: 'development',
    entry: './ui_src/index.ts',
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: 'ts-loader',
                include: [path.resolve(__dirname ,'ui_src')]
            }
        ]
    },
    resolve: {
        extensions: ['.ts', '.js']
    },
    output: {
        publicPath: "./",
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'plan_visual_django/static/dist')
    }
}
