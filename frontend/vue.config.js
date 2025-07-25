const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
   devServer: {
    port: 6060, // Change this to your desired port
  }
})
