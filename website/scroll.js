// Scroll Observer
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.15 });

document.querySelectorAll('.scroll-fade').forEach(section => {
  observer.observe(section);
});

// Scroll Chatbot UI Logic
const fab = document.getElementById('open-chatbot');
const chatbot = document.getElementById('scroll-chatbot');
const closeBtn = document.getElementById('close-chatbot');
fab.onclick = () => { chatbot.classList.remove('scroll-chatbot-closed'); fab.style.display = 'none'; };
closeBtn.onclick = () => { chatbot.classList.add('scroll-chatbot-closed'); fab.style.display = 'block'; };

// Chatbot Messaging Logic
const form = document.getElementById('chatbot-form');
const input = document.getElementById('chatbot-input');
const messages = document.getElementById('chatbot-messages');
form.onsubmit = async (e) => {
  e.preventDefault();
  const userMsg = input.value;
  messages.innerHTML += `<div><b>You:</b> ${userMsg}</div>`;
  input.value = '';
  const res = await fetch('/scroll-chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: userMsg })
  });
  const data = await res.json();
  messages.innerHTML += `<div><b>Scroll Scribe:</b> ${data.reply}</div>`;
  messages.scrollTop = messages.scrollHeight;
};