const list = document.querySelector('#tasks');
const form = document.querySelector('#task-form');
const input = document.querySelector('#title');
const message = document.querySelector('#message');

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `HTTP ${response.status}`);
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

loadTasks();
