/**
 * Supabase Todo App - JavaScript
 * ================================
 * A beginner-friendly todo application using Supabase for:
 * - User authentication (sign up, login, logout)
 * - Database storage (create, read, update, delete todos)
 * - Row Level Security (users only see their own todos)
 *
 * Created for HackWashU Databases Workshop
 */

// ============================================
// STEP 1: LOAD CONFIGURATION
// ============================================

/**
 * Load Supabase credentials from .env file
 * This keeps sensitive data separate from code
 */
async function loadConfig() {
  const response = await fetch(".env");
  const text = await response.text();
  const config = {};

  // Parse each line of the .env file
  text.split("\n").forEach((line) => {
    if (line.trim() && !line.startsWith("#")) {
      const [key, ...values] = line.split("=");
      config[key.trim()] = values.join("=").trim();
    }
  });

  return config;
}

// ============================================
// STEP 2: INITIALIZE SUPABASE
// ============================================

(async () => {
  // Load configuration
  const config = await loadConfig();
  const SUPABASE_URL = config.SUPABASE_URL;
  const SUPABASE_ANON_KEY = config.SUPABASE_ANON_KEY;

  // Create Supabase client (this connects to your database)
  const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

  // ============================================
  // STEP 3: GET HTML ELEMENTS
  // ============================================

  // Get references to important HTML elements
  const authView = document.getElementById("auth-view");
  const appView = document.getElementById("app-view");
  const userEmailSpan = document.getElementById("user-email");
  const todoList = document.getElementById("todo-list");
  const completedList = document.getElementById("completed-list");

  // ============================================
  // STEP 4: HELPER FUNCTIONS
  // ============================================

  /**
   * Create HTML element for a single todo
   * This builds the checkbox, text, and action buttons
   */
  const createTodoElement = (todo, isCompleted) => {
    // Create list item
    const li = document.createElement("li");

    // Create checkbox
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = isCompleted;
    checkbox.addEventListener("click", () => {
      toggleTodoComplete(todo.id, isCompleted);
    });
    li.appendChild(checkbox);

    // Create task text
    const taskSpan = document.createElement("span");
    taskSpan.className = "task-text";
    taskSpan.textContent = todo.task;

    // Style completed todos differently
    if (isCompleted) {
      taskSpan.style.textDecoration = "line-through";
      taskSpan.style.color = "#999";
    }
    li.appendChild(taskSpan);

    // Create actions container
    const actionsDiv = document.createElement("div");
    actionsDiv.className = "task-actions";

    // Create Edit button
    const editBtn = document.createElement("button");
    editBtn.textContent = "✏️ Edit";
    editBtn.style.backgroundColor = "#ffc107";
    editBtn.style.color = "#343a40";
    editBtn.addEventListener("click", () => {
      editTodo(todo.id, todo.task);
    });
    actionsDiv.appendChild(editBtn);

    // Create Delete button
    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "🗑️ Delete";
    deleteBtn.style.backgroundColor = "#dc3545";
    deleteBtn.addEventListener("click", () => {
      deleteTodo(todo.id);
    });
    actionsDiv.appendChild(deleteBtn);

    li.appendChild(actionsDiv);
    return li;
  };

  // ============================================
  // STEP 5: TODO CRUD OPERATIONS
  // ============================================

  /**
   * FETCH TODOS - Read all todos from database
   * This function gets todos and displays them on the page
   */
  const fetchTodos = async () => {
    // Get all todos for current user (RLS handles filtering)
    const { data, error } = await supabaseClient
      .from("todos")
      .select("*")
      .order("created_at", { ascending: false });

    if (error) {
      console.error("Error fetching todos:", error);
      return;
    }

    // Clear the lists
    todoList.innerHTML = "";
    completedList.innerHTML = "";

    // Separate incomplete and completed todos
    const incompleteTodos = data.filter((todo) => !todo.is_complete);
    const completedTodos = data.filter((todo) => todo.is_complete);

    // Display incomplete todos
    incompleteTodos.forEach((todo) => {
      const todoElement = createTodoElement(todo, false);
      todoList.appendChild(todoElement);
    });

    // Display completed todos
    completedTodos.forEach((todo) => {
      const todoElement = createTodoElement(todo, true);
      completedList.appendChild(todoElement);
    });
  };

  /**
   * UPDATE TODO - Mark todo as complete/incomplete
   */
  const toggleTodoComplete = async (todoId, isComplete) => {
    const { error } = await supabaseClient
      .from("todos")
      .update({ is_complete: !isComplete })
      .eq("id", todoId);

    if (error) {
      alert("Error updating todo: " + error.message);
    } else {
      fetchTodos();
    }
  };

  /**
   * UPDATE TODO - Edit todo text
   */
  const editTodo = async (todoId, currentTask) => {
    const newTask = prompt("Edit your todo:", currentTask);

    // Only update if user entered something different
    if (newTask && newTask.trim() !== currentTask) {
      const { error } = await supabaseClient
        .from("todos")
        .update({ task: newTask.trim() })
        .eq("id", todoId);

      if (error) {
        alert("Error updating todo: " + error.message);
      } else {
        fetchTodos();
      }
    }
  };

  /**
   * DELETE TODO - Remove a single todo
   */
  const deleteTodo = async (todoId) => {
    if (!confirm("Delete this todo?")) {
      return;
    }

    const { error } = await supabaseClient
      .from("todos")
      .delete()
      .eq("id", todoId);

    if (error) {
      alert("Error deleting todo: " + error.message);
    } else {
      fetchTodos();
    }
  };

  // ============================================
  // STEP 6: EVENT LISTENERS
  // ============================================

  /**
   * Sign Up Button - Create a new user account
   */
  document.getElementById("signup-btn").addEventListener("click", async () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // Call Supabase to create new user
    const { error } = await supabaseClient.auth.signUp({ email, password });

    if (error) {
      alert("Error: " + error.message);
    } else {
      alert("Success! Check your email for a confirmation link.");
    }
  });

  /**
   * Login Button - Sign in existing user
   */
  document.getElementById("login-btn").addEventListener("click", async () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    // Call Supabase to log in
    const { error } = await supabaseClient.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      alert("Error: " + error.message);
    }
    // On success, the app will automatically update (see Session Management below)
  });

  /**
   * Logout Button - Sign out current user
   */
  document.getElementById("logout-btn").addEventListener("click", async () => {
    await supabaseClient.auth.signOut();
  });

  /**
   * Add Todo Button - Create a new todo
   */
  document
    .getElementById("add-todo-btn")
    .addEventListener("click", async () => {
      const taskInput = document.getElementById("new-todo");
      const task = taskInput.value.trim();

      // Don't add empty todos
      if (!task) {
        alert("Please enter a task!");
        return;
      }

      // Get current user
      const {
        data: { user },
      } = await supabaseClient.auth.getUser();
      if (!user) {
        alert("You must be logged in to add todos!");
        return;
      }

      // Insert new todo into database
      const { error } = await supabaseClient.from("todos").insert({
        task: task,
        user_id: user.id,
        is_complete: false,
      });

      if (error) {
        console.error("Error adding todo:", error);
        alert("Error adding todo: " + error.message);
      } else {
        // Clear input and refresh list
        taskInput.value = "";
        fetchTodos();
      }
    });

  /**
   * Delete All Tasks Button - Remove all user's todos
   */
  document
    .getElementById("delete-all-tasks-btn")
    .addEventListener("click", async () => {
      if (
        !confirm("Are you sure? This will permanently delete all your todos.")
      ) {
        return;
      }

      const {
        data: { user },
      } = await supabaseClient.auth.getUser();
      if (!user) {
        alert("No user found.");
        return;
      }

      // Delete all todos for this user
      const { error } = await supabaseClient
        .from("todos")
        .delete()
        .eq("user_id", user.id);

      if (error) {
        alert("Error deleting todos: " + error.message);
      } else {
        alert("All your todos have been deleted.");
        fetchTodos();
      }
    });

  // ============================================
  // STEP 7: SESSION MANAGEMENT
  // ============================================

  /**
   * Listen for authentication changes
   * This automatically updates the UI when user logs in/out
   */
  supabaseClient.auth.onAuthStateChange((event, session) => {
    if (session && session.user) {
      // User is logged in - show the app
      authView.style.display = "none";
      appView.style.display = "block";
      userEmailSpan.textContent = session.user.email;

      // Load user's todos
      fetchTodos();
    } else {
      // User is logged out - show login form
      authView.style.display = "block";
      appView.style.display = "none";
      todoList.innerHTML = "";
      completedList.innerHTML = "";
    }
  });
})();
