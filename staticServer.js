const express = require('express');
const path = require('path');
const app = express();

app.use(express.static(path.join(__dirname, '../sambot-frontend')));

app.listen(3000, () => {
  console.log('🧠 Sambot frontend on http://localhost:3000');
});
