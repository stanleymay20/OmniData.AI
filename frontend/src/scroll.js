const res = await fetch('http://localhost:8000/scroll-chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userMsg })
}); 