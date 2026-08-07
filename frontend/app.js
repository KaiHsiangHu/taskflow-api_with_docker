const list = document.querySelector('#tasks');
const form = document.querySelector('#task-form');
const input = document.querySelector('#title');
const message = document.querySelector('#message');
const loginView = document.querySelector('#login-view');
const appView = document.querySelector('#app-view');
const loginForm = document.querySelector('#login-form');
const passwordInput = document.querySelector('#password');
const loginMessage = document.querySelector('#login-message');
const logoutButton = document.querySelector('#logout');
const tabButtons = document.querySelectorAll('.tab');
const tasksPanel = document.querySelector('#tasks-panel');
const zodiacPanel = document.querySelector('#zodiac-panel');
const zodiacSearch = document.querySelector('#zodiac-search');
const zodiacOptions = document.querySelector('#zodiac-options');
const zodiacResults = document.querySelector('#zodiac-results');
const zodiacMessage = document.querySelector('#zodiac-message');
let zodiacSigns = [];
const selectedSigns = new Set();

function showLogin() {
  loginView.hidden = false;
  appView.hidden = true;
  passwordInput.focus();
}

function showApp() {
  loginView.hidden = true;
  appView.hidden = false;
}

function switchTab(tab) {
  tasksPanel.hidden = tab !== 'tasks';
  zodiacPanel.hidden = tab !== 'zodiac';
  tabButtons.forEach(button => button.classList.toggle('active', button.dataset.tab === tab));
  if (tab === 'zodiac' && !zodiacSigns.length) loadZodiac();
}

function renderZodiacOptions(signs) {
  zodiacOptions.replaceChildren(...signs.map(sign => {
    const label = document.createElement('label');
    label.className = 'zodiac-option';
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = selectedSigns.has(sign.id);
    checkbox.addEventListener('change', () => {
      checkbox.checked ? selectedSigns.add(sign.id) : selectedSigns.delete(sign.id);
      renderZodiacResults();
    });
    const text = document.createElement('span');
    text.textContent = `${sign.symbol} ${sign.name}`;
    label.append(checkbox, text);
    return label;
  }));
}

function renderZodiacResults() {
  const selected = zodiacSigns.filter(sign => selectedSigns.has(sign.id));
  zodiacResults.replaceChildren(...selected.map(sign => {
    const card = document.createElement('article');
    card.className = `zodiac-card element-${sign.element.slice(0, 1)}`;
    const traits = sign.traits.map(trait => `<li>${trait}</li>`).join('');
    card.innerHTML = `
      <div class="zodiac-card-heading">
        <span class="zodiac-symbol">${sign.symbol}</span>
        <div><h2>${sign.name}</h2><p>${sign.english} · ${sign.dates} · ${sign.element}</p></div>
      </div>
      <ul class="traits">${traits}</ul>
      <p><strong>特色：</strong>${sign.strength}</p>
      <p><strong>提醒：</strong>${sign.watchout}</p>`;
    return card;
  }));
  zodiacMessage.textContent = selected.length ? `已選擇 ${selected.length} 個星座` : '請勾選想了解的星座。';
}

async function loadZodiac() {
  try {
    zodiacSigns = await request('/api/zodiac');
    renderZodiacOptions(zodiacSigns);
    renderZodiacResults();
  } catch (error) {
    zodiacMessage.textContent = error.message;
  }
}

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const error = new Error(body.error || `HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return response.status === 204 ? null : response.json();
}

function render(tasks) {
  list.replaceChildren(...tasks.map(task => {
    const item = document.createElement('li');
    item.className = task.completed ? 'completed' : '';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = task.completed;
    checkbox.addEventListener('change', async () => {
      await request(`/api/tasks/${task.id}`, {
        method: 'PATCH', body: JSON.stringify({ completed: checkbox.checked }),
      });
      loadTasks();
    });

    const title = document.createElement('span');
    title.textContent = task.title;

    const remove = document.createElement('button');
    remove.className = 'delete';
    remove.textContent = '刪除';
    remove.addEventListener('click', async () => {
      await request(`/api/tasks/${task.id}`, { method: 'DELETE' });
      loadTasks();
    });

    item.append(checkbox, title, remove);
    return item;
  }));
}

async function loadTasks() {
  try {
    render(await request('/api/tasks'));
    message.textContent = '';
  } catch (error) {
    if (error.status === 401) showLogin();
    message.textContent = error.message;
  }
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  try {
    await request('/api/tasks', {
      method: 'POST', body: JSON.stringify({ title: input.value }),
    });
    input.value = '';
    input.focus();
    loadTasks();
  } catch (error) {
    message.textContent = error.message;
  }
});

loginForm.addEventListener('submit', async event => {
  event.preventDefault();
  try {
    await request('/api/login', {
      method: 'POST', body: JSON.stringify({ password: passwordInput.value }),
    });
    passwordInput.value = '';
    loginMessage.textContent = '';
    showApp();
    loadTasks();
  } catch (error) {
    loginMessage.textContent = error.message;
    passwordInput.select();
  }
});

logoutButton.addEventListener('click', async () => {
  await request('/api/logout', { method: 'POST', body: '{}' });
  list.replaceChildren();
  showLogin();
});

tabButtons.forEach(button => button.addEventListener('click', () => switchTab(button.dataset.tab)));

zodiacSearch.addEventListener('input', () => {
  const query = zodiacSearch.value.trim().toLocaleLowerCase();
  const filtered = zodiacSigns.filter(sign =>
    sign.name.toLocaleLowerCase().includes(query)
    || sign.english.toLocaleLowerCase().includes(query)
    || sign.element.includes(query)
  );
  renderZodiacOptions(filtered);
});

async function initialize() {
  try {
    const auth = await request('/api/auth');
    if (auth.authenticated) {
      showApp();
      loadTasks();
    } else {
      showLogin();
    }
  } catch (error) {
    showLogin();
    loginMessage.textContent = error.message;
  }
}

initialize();
