from flask import Flask, request
from scheduler.algorithms import fcfs, sjf, priority_scheduling, round_robin
from scheduler.utils import parse_input, compute_metrics

app = Flask(__name__)

@app.route('/')
def form():
    return '''
    <html>
    <head>
      <title>CPU Scheduler Simulator</title>
      <style>
        body {
          font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
          background: #f4f7f8;
          color: #333;
          margin: 0; padding: 0;
          display: flex;
          flex-direction: column;
          align-items: center;
          min-height: 100vh;
        }
        h2 {
          margin-top: 40px;
          color: #004466;
        }
        form {
          background: white;
          padding: 30px;
          border-radius: 8px;
          box-shadow: 0 8px 20px rgba(0,0,0,0.1);
          width: 350px;
          margin-top: 60px;
        }
        textarea {
          width: 100%;
          height: 120px;
          border-radius: 5px;
          border: 1px solid #ccc;
          padding: 10px;
          font-family: monospace;
          font-size: 14px;
          resize: vertical;
          margin-bottom: 20px;
        }
        input, select, button {
          width: 100%;
          padding: 10px;
          margin-bottom: 20px;
          border-radius: 5px;
          border: 1px solid #ccc;
          font-size: 16px;
          box-sizing: border-box;
        }
        button {
          background-color: #004466;
          color: white;
          font-weight: bold;
          cursor: pointer;
          border: none;
          transition: background-color 0.3s ease;
        }
        button:hover {
          background-color: #006699;
        }
        label {
          font-weight: 600;
          margin-bottom: 8px;
          display: block;
          color: #222;
        }
        footer {
          margin-top: auto;
          padding: 15px;
          font-size: 12px;
          color: #aaa;
        }
      </style>
    </head>
    <body>
      <form action="/simulate" method="post">
        <h2>CPU Scheduler Simulator</h2>
        <label>Process Data (arrival burst priority):</label>
        <textarea name="data" placeholder="Example:\n0 5 2\n1 3 1\n2 8 3"></textarea>
        <label>Quantum (for Round Robin):</label>
        <input type="number" name="quantum" value="2" min="1" />
        <label>Scheduling Algorithm:</label>
        <select name="algo">
          <option>FCFS</option>
          <option>SJF</option>
          <option>Priority</option>
          <option>Round Robin</option>
        </select>
        <button type="submit">Simulate</button>
      </form>
      <footer>© 2025 CPU Scheduler Simulator</footer>
    </body>
    </html>
    '''

def render_gantt_chart(schedule):
    width_per_unit = 40  # width per time unit in px
    height = 70
    svg_width = (max(e['end'] for e in schedule) + 1) * width_per_unit
    svg = f'<svg width="{svg_width}" height="{height}" style="border:1px solid #ddd; background: #fff; border-radius: 8px;">'
    y = 25
    for e in schedule:
        x = e['start'] * width_per_unit
        w = (e['end'] - e['start']) * width_per_unit
        svg += f'<rect x="{x}" y="{y}" width="{w}" height="25" fill="#007acc" rx="5" ry="5" />'
        svg += f'<text x="{x + w/2}" y="{y + 17}" fill="white" font-size="14" font-weight="600" text-anchor="middle" font-family="Segoe UI">P{e["pid"]}</text>'
        svg += f'<text x="{x}" y="{y + 45}" fill="#555" font-size="12" font-family="Segoe UI">{e["start"]}</text>'
    # End time label
    svg += f'<text x="{(max(e["end"] for e in schedule)) * width_per_unit}" y="{y + 45}" fill="#555" font-size="12" font-family="Segoe UI">{max(e["end"] for e in schedule)}</text>'
    svg += '</svg>'
    return svg

def render_process_table(processes):
    rows = ""
    for p in processes:
        rows += f"""
        <tr>
          <td>P{p.pid}</td>
          <td>{p.arrival}</td>
          <td>{p.burst}</td>
          <td>{p.waiting}</td>
          <td>{p.turnaround}</td>
        </tr>"""
    table = f'''
    <table style="width: 80%; border-collapse: collapse; margin: 40px auto; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
      <thead style="background-color: #007acc; color: white; font-weight: 600;">
        <tr>
          <th style="padding: 10px;">Process</th>
          <th style="padding: 10px;">Arrival</th>
          <th style="padding: 10px;">Burst</th>
          <th style="padding: 10px;">Waiting</th>
          <th style="padding: 10px;">Turnaround</th>
        </tr>
      </thead>
      <tbody style="background-color: #f9f9f9;">
        {rows}
      </tbody>
    </table>
    '''
    return table

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.form['data']
    quantum = int(request.form.get('quantum', 2))
    algo = request.form['algo']
    processes = parse_input(data)

    if algo == 'FCFS':
        schedule, updated = fcfs(processes)
    elif algo == 'SJF':
        schedule, updated = sjf(processes)
    elif algo == 'Priority':
        schedule, updated = priority_scheduling(processes)
    elif algo == 'Round Robin':
        schedule, updated = round_robin(processes, quantum)
    else:
        return "Algorithm not implemented"

    avg_wait, avg_turn, utilization, throughput = compute_metrics(updated)

    gantt_svg = render_gantt_chart(schedule)
    proc_table = render_process_table(updated)

    return f'''
    <html>
    <head>
      <title>{algo} Scheduling Result</title>
      <style>
        body {{
          font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
          background: #f4f7f8;
          color: #333;
          padding: 20px;
          text-align: center;
        }}
        h1 {{
          color: #004466;
          margin-top: 30px;
        }}
        .metrics {{
          max-width: 600px;
          margin: 30px auto;
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 6px 15px rgba(0,0,0,0.1);
          text-align: left;
        }}
        .metrics ul {{
          list-style: none;
          padding-left: 0;
          font-size: 16px;
          color: #222;
        }}
        .metrics li {{
          margin-bottom: 10px;
          font-weight: 600;
        }}
        a.button {{
          display: inline-block;
          margin: 40px 0;
          background-color: #007acc;
          color: white;
          padding: 12px 30px;
          text-decoration: none;
          font-weight: 700;
          border-radius: 6px;
          transition: background-color 0.3s ease;
        }}
        a.button:hover {{
          background-color: #005f99;
        }}
    </style>
    </head>
    <body>
      <h1>{algo} Scheduling Result</h1>
      {gantt_svg}
      <h2>Process Details</h2>
      {proc_table}
      <div class="metrics">
        <h2>Performance Metrics</h2>
        <ul>
          <li>Average Waiting Time: {avg_wait:.2f}</li>
          <li>Average Turnaround Time: {avg_turn:.2f}</li>
          <li>CPU Utilization: {utilization:.2f}%</li>
          <li>Throughput: {throughput:.2f} processes/unit time</li>
        </ul>
      </div>
      <a class="button" href="/">Run Another Simulation</a>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
