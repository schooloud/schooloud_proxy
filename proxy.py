import os
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def get_request():
    return render_template('input.html')


@app.route("/api/v1/ssh/add", methods=['POST'])
def add():
    project_id = request.form['project_id']
    floating_ip = request.form['floating_ip']
    port = request.form['port']
    content = (
        "server {\n"
        f"       listen      {port};\n"
        f"       proxy_pass  {floating_ip}:22;\n"
        "}\n"
    )
    print(content)
    with open(f"/etc/nginx/servers-available/{project_id}.conf", "a") as file:
        file.write(content)
    
    os.system('sudo systemctl restart nginx')

    return "append complete"

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
