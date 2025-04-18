// marketAPI.js
const mockData = require('./mockData');

async function getMarketData() {
  return mockData;
}

module.exports = {
  getMarketData,
};
