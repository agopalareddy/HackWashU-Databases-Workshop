// Helper to load .env file and parse key-value pairs
async function loadEnv() {
  const response = await fetch(".env");
  const text = await response.text();
  const env = {};
  text.split("\n").forEach((line) => {
    if (line.trim() && !line.startsWith("#")) {
      const [key, ...vals] = line.split("=");
      env[key.trim()] = vals.join("=").trim();
    }
  });
  return env;
}

(async () => {
  const env = await loadEnv();
  const SUPABASE_URL = env.SUPABASE_URL;
  const SUPABASE_ANON_KEY = env.SUPABASE_ANON_KEY;
  // Correctly initialize the Supabase client
  const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

  const authView = document.getElementById("auth-view");
  const appView = document.getElementById("app-view");
  const userEmailSpan = document.getElementById("user-email");
  const todoList = document.getElementById("todo-list");

  // --- Authentication ---
  document.getElementById("signup-btn").addEventListener("click", async () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const { error } = await supabaseClient.auth.signUp({ email, password });
    if (error) alert(error.message);
    else alert("Signed up! Check your email for a confirmation link.");
  });

  document.getElementById("login-btn").addEventListener("click", async () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const { error } = await supabaseClient.auth.signInWithPassword({
      email,
      password,
    });
    if (error) alert(error.message);
  });

  document.getElementById("logout-btn").addEventListener("click", async () => {
    await supabaseClient.auth.signOut();
  });

  // --- Todo Logic (CRUD + Complete) ---
  const fetchTodos = async () => {
    const { data, error } = await supabaseClient
      .from("todos")
      .select("*")
      .order("created_at", { ascending: false });
    if (error) {
      console.error("Error fetching todos:", error);
    } else {
      todoList.innerHTML = "";
      const completedList = document.getElementById("completed-list");
      completedList.innerHTML = "";
      // Separate incomplete and complete todos
      const incomplete = data.filter((todo) => !todo.is_complete);
      const complete = data
        .filter((todo) => todo.is_complete)
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

      // Render incomplete todos
      incomplete.forEach((todo) => {
        const li = document.createElement("li");
        // Checkbox
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = false;
        checkbox.onclick = async () => {
          const { error } = await supabaseClient
            .from("todos")
            .update({ is_complete: true })
            .eq("id", todo.id);
          if (error) alert("Error marking complete: " + error.message);
          else fetchTodos();
        };
        li.appendChild(checkbox);

        // Task text span
        const taskSpan = document.createElement("span");
        taskSpan.className = "task-text";
        taskSpan.textContent = todo.task;
        li.appendChild(taskSpan);

        // Actions container
        const actions = document.createElement("div");
        actions.className = "task-actions";

        // Edit button
        const editBtn = document.createElement("button");
        editBtn.textContent = "✏️ Edit";
        editBtn.style.backgroundColor = "#ffc107";
        editBtn.style.color = "#343a40";
        editBtn.onclick = async () => {
          const newTask = prompt("Edit your todo:", todo.task);
          if (newTask && newTask !== todo.task) {
            const { error } = await supabaseClient
              .from("todos")
              .update({ task: newTask })
              .eq("id", todo.id);
            if (error) alert("Error updating todo: " + error.message);
            else fetchTodos();
          }
        };
        actions.appendChild(editBtn);

        // Delete button
        const delBtn = document.createElement("button");
        delBtn.textContent = "🗑️ Delete";
        delBtn.style.backgroundColor = "#dc3545";
        delBtn.onclick = async () => {
          if (confirm("Delete this todo?")) {
            const { error } = await supabaseClient
              .from("todos")
              .delete()
              .eq("id", todo.id);
            if (error) alert("Error deleting todo: " + error.message);
            else fetchTodos();
          }
        };
        actions.appendChild(delBtn);

        li.appendChild(actions);
        todoList.appendChild(li);
      });

      // Render completed todos
      complete.forEach((todo) => {
        const li = document.createElement("li");
        // Checkbox (checked)
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = true;
        checkbox.onclick = async () => {
          const { error } = await supabaseClient
            .from("todos")
            .update({ is_complete: false })
            .eq("id", todo.id);
          if (error) alert("Error marking incomplete: " + error.message);
          else fetchTodos();
        };
        li.appendChild(checkbox);

        // Task text span (strikethrough)
        const taskSpan = document.createElement("span");
        taskSpan.className = "task-text";
        taskSpan.textContent = todo.task;
        taskSpan.style.textDecoration = "line-through";
        taskSpan.style.color = "#999";
        li.appendChild(taskSpan);

        // Actions container
        const actions = document.createElement("div");
        actions.className = "task-actions";

        // Edit button
        const editBtn = document.createElement("button");
        editBtn.textContent = "✏️ Edit";
        editBtn.style.backgroundColor = "#ffc107";
        editBtn.style.color = "#343a40";
        editBtn.onclick = async () => {
          const newTask = prompt("Edit your todo:", todo.task);
          if (newTask && newTask !== todo.task) {
            const { error } = await supabaseClient
              .from("todos")
              .update({ task: newTask })
              .eq("id", todo.id);
            if (error) alert("Error updating todo: " + error.message);
            else fetchTodos();
          }
        };
        actions.appendChild(editBtn);

        // Delete button
        const delBtn = document.createElement("button");
        delBtn.textContent = "🗑️ Delete";
        delBtn.style.backgroundColor = "#dc3545";
        delBtn.onclick = async () => {
          if (confirm("Delete this todo?")) {
            const { error } = await supabaseClient
              .from("todos")
              .delete()
              .eq("id", todo.id);
            if (error) alert("Error deleting todo: " + error.message);
            else fetchTodos();
          }
        };
        actions.appendChild(delBtn);

        li.appendChild(actions);
        completedList.appendChild(li);
      });
    }
  };

  document
    .getElementById("add-todo-btn")
    .addEventListener("click", async () => {
      const task = document.getElementById("new-todo").value;
      if (!task) return;
      const {
        data: { user },
      } = await supabaseClient.auth.getUser();
      if (!user) return;
      const { error } = await supabaseClient
        .from("todos")
        .insert({ task: task, user_id: user.id, is_complete: false });
      if (error) console.error("Error adding todo:", error);
      else {
        document.getElementById("new-todo").value = "";
        fetchTodos();
      }
    });

  // --- Session Management ---
  supabaseClient.auth.onAuthStateChange((event, session) => {
    if (session && session.user) {
      // User is logged in
      authView.style.display = "none";
      appView.style.display = "block";
      userEmailSpan.textContent = session.user.email;
      fetchTodos();
    } else {
      // User is logged out
      authView.style.display = "block";
      appView.style.display = "none";
      todoList.innerHTML = "";
    }
  });
})();
