const http = require('http');
let raw = '';
http.get('http://localhost:3000/api/trees', res => {
  res.on('data', d => raw += d);
  res.on('end', () => {
    const trees = JSON.parse(raw);
    const t = trees.find(r => r.winnerPath === 'p4v2');
    if (!t) { console.log('no p4v2 tree'); return; }
    console.log('keys in response:', Object.keys(t).join(', '));
    console.log('p4v2 field:', JSON.stringify(t.p4v2).slice(0, 400));
    console.log('species:', t.species);
    console.log('hasStory:', t.hasStory);
    console.log('winnerPath:', t.winnerPath);
  });
});
