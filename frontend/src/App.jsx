import { useState, useEffect } from "react";

const API = "https://task-manager-backend-production-1f80.up.railway.app";

const priorityColors = {
  high: { bg: "#fee2e2", text: "#dc2626", border: "#fca5a5" },
  medium: { bg: "#fef9c3", text: "#ca8a04", border: "#fde047" },
  low: { bg: "#dcfce7", text: "#16a34a", border: "#86efac" },
};

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    title: "",
    description: "",
    priority: "medium",
  });
  const [submitting, setSubmitting] = useState(false);
  const [filter, setFilter] = useState("all");

  const fetchTasks = async () => {
    const [tasksRes, statsRes] = await Promise.all([
      fetch(`${API}/tasks`),
      fetch(`${API}/tasks/stats/summary`),
    ]);

    setTasks(await tasksRes.json());
    setStats(await statsRes.json());
    setLoading(false);
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const createTask = async (e) => {
    e.preventDefault();
    if (!form.title.trim()) return;

    setSubmitting(true);

    await fetch(`${API}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    setForm({ title: "", description: "", priority: "medium" });
    await fetchTasks();
    setSubmitting(false);
  };

  const toggleComplete = async (task) => {
    await fetch(`${API}/tasks/${task.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: !task.completed }),
    });

    fetchTasks();
  };

  const deleteTask = async (id) => {
    await fetch(`${API}/tasks/${id}`, { method: "DELETE" });
    fetchTasks();
  };

  const filtered = tasks.filter((t) => {
    if (filter === "pending") return !t.completed;
    if (filter === "completed") return t.completed;
    return true;
  });

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f8fafc",
        fontFamily: "'Inter', sans-serif",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: 24,
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 900,
          background: "#ffffff",
          borderRadius: 20,
          boxShadow: "0 10px 40px rgba(0,0,0,0.08)",
          overflow: "hidden",
          border: "1px solid #e2e8f0",
        }}
      >
        {/* Header */}
        <div
          style={{
            background:
              "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
            padding: "28px 32px",
          }}
        >
          <h1
            style={{
              color: "#fff",
              margin: 0,
              fontSize: 26,
              fontWeight: 700,
            }}
          >
            Task Manager
          </h1>

          <div
            style={{
              display: "flex",
              gap: 18,
              marginTop: 18,
              flexWrap: "wrap",
            }}
          >
            {[
              { label: "Total", value: stats.total || 0 },
              { label: "Completed", value: stats.completed || 0 },
              { label: "Pending", value: stats.pending || 0 },
              { label: "High Priority", value: stats.high_priority || 0 },
            ].map((s) => (
              <div
                key={s.label}
                style={{
                  background: "rgba(255,255,255,0.15)",
                  borderRadius: 12,
                  padding: "10px 16px",
                  color: "#fff",
                }}
              >
                <div style={{ fontSize: 20, fontWeight: 700 }}>
                  {s.value}
                </div>
                <div style={{ fontSize: 11, opacity: 0.8 }}>
                  {s.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Body */}
        <div style={{ padding: 28 }}>
          {/* Form */}
          <form onSubmit={createTask} style={{ marginBottom: 20 }}>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <input
                value={form.title}
                onChange={(e) =>
                  setForm({ ...form, title: e.target.value })
                }
                placeholder="Task title..."
                style={{
                  flex: 2,
                  padding: "10px 12px",
                  borderRadius: 8,
                  border: "1px solid #e2e8f0",
                }}
              />

              <select
                value={form.priority}
                onChange={(e) =>
                  setForm({ ...form, priority: e.target.value })
                }
                style={{
                  flex: 1,
                  padding: "10px 12px",
                  borderRadius: 8,
                  border: "1px solid #e2e8f0",
                }}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>

              <button
                disabled={submitting}
                style={{
                  padding: "10px 18px",
                  borderRadius: 8,
                  background: "#6366f1",
                  color: "#fff",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                {submitting ? "Adding..." : "Add"}
              </button>
            </div>

            <input
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              placeholder="Description..."
              style={{
                width: "100%",
                marginTop: 10,
                padding: "10px 12px",
                borderRadius: 8,
                border: "1px solid #e2e8f0",
              }}
            />
          </form>

          {/* Filters */}
          <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
            {["all", "pending", "completed"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                style={{
                  padding: "6px 14px",
                  borderRadius: 8,
                  border: "1px solid #e2e8f0",
                  background: filter === f ? "#6366f1" : "#fff",
                  color: filter === f ? "#fff" : "#475569",
                  cursor: "pointer",
                }}
              >
                {f}
              </button>
            ))}
          </div>

          {/* Tasks */}
          {loading ? (
            <div>Loading...</div>
          ) : filtered.length === 0 ? (
            <div>No tasks</div>
          ) : (
            filtered.map((task) => {
              const pc =
                priorityColors[task.priority] || priorityColors.medium;

              return (
                <div
                  key={task.id}
                  style={{
                    border: "1px solid #e2e8f0",
                    borderRadius: 10,
                    padding: 14,
                    marginBottom: 10,
                    display: "flex",
                    justifyContent: "space-between",
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600 }}>{task.title}</div>
                    <div style={{ fontSize: 12, color: "#64748b" }}>
                      {task.description}
                    </div>

                    <span
                      style={{
                        fontSize: 11,
                        padding: "2px 8px",
                        borderRadius: 20,
                        background: pc.bg,
                        color: pc.text,
                        border: `1px solid ${pc.border}`,
                      }}
                    >
                      {task.priority}
                    </span>
                  </div>

                  <div style={{ display: "flex", gap: 8 }}>
                    <button onClick={() => toggleComplete(task)}>✓</button>
                    <button onClick={() => deleteTask(task.id)}>×</button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}